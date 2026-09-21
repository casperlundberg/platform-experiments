#!/usr/bin/env python3
"""Runs a sweep against a running Simlab, and writes its report.

A sweep is every combination of its axes, on every seed. Each combination is a
run of the same mine and scenario under a different intent, autoscaler settings
or scenario tweak; a seed is a whole different workload, mine layout and
workforce. What comes out is evidence to read, not a pass mark, so the report
is written to be read: what was run, on which code, what came of it, and the
command that produces the same numbers again.

    sweep.py run API SWEEP.json REPORTS_DIR [PARALLEL]
    sweep.py report REPORT_DIR          rewrite report.md from what was recorded
    sweep.py ref SWEEP.json REPO        what the sweep builds REPO from

Everything a run produces is deterministic in its commits and inputs, so
regenerating a report at the same commits reproduces runs.csv byte for byte;
its digest is recorded so that can be checked.
"""

import csv
import hashlib
import itertools
import json
import math
import os
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone


# ------------------------------------------------------------------ the API

def call(base, method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(base.rstrip("/") + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{method} {path} = {err.code}: {err.read().decode()}") from None


def paged(base, path, key):
    out, cursor = [], 0
    while True:
        page = call(base, "GET", f"{path}?from={cursor}&limit=20000")
        rows = page.get(key) or []
        if not rows:
            return out
        out.extend(rows)
        if page["next"] <= cursor:
            return out
        cursor = page["next"]


def merge(base, patch):
    """A deep merge of JSON objects: patch wins, and nested objects merge."""
    out = dict(base)
    for key, value in (patch or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out


# ------------------------------------------------------------ the combinations

def combinations(sweep):
    """Every combination of the axes, as (labels, contribution), in the order
    the axes and their values are listed, less any the sweep excludes."""
    axes = sweep["axes"]
    out = []
    for values in itertools.product(*(axis["values"] for axis in axes)):
        labels = {axis["name"]: value["label"] for axis, value in zip(axes, values)}
        if any(all(labels.get(k) == v for k, v in rule.items()) for rule in sweep.get("exclude", [])):
            continue
        contribution = {"intent": {}, "settings": {}, "scenario": {}, "intent_schedule": []}
        for value in values:
            contribution["intent"] = merge(contribution["intent"], value.get("intent"))
            contribution["settings"] = merge(contribution["settings"], value.get("settings"))
            contribution["scenario"] = merge(contribution["scenario"], value.get("scenario"))
            contribution["intent_schedule"] += value.get("intent_schedule", [])
        out.append((labels, contribution))
    return out


def arm_name(labels):
    return " · ".join(labels.values())


BUILDS = ("autoscaler", "simlab-api")


def build_ref(sweep, repo):
    """What a sweep builds a service from: HEAD, unless the sweep pins it, as to
    a release tag. A pin keeps a sweep off whatever else is committed locally —
    work in progress that has not been released, someone else's included — and,
    being in the definition, reruns with it."""
    pins = sweep.get("build", {})
    unknown = sorted(set(pins) - set(BUILDS))
    if unknown:
        raise ValueError(f"{sweep['name']}: build names {', '.join(unknown)}; a sweep builds {', '.join(BUILDS)}")
    return pins.get(repo, "HEAD")


# ------------------------------------------------------------------ running

def run_sweep(base, sweep_path, reports_dir, parallel=4):
    with open(sweep_path) as f:
        sweep = json.load(f)
    name = sweep["name"]
    # A column the report cannot show is refused now, not after every run.
    headline(sweep), compared(sweep)
    out_dir = os.path.join(reports_dir, name)
    os.makedirs(out_dir, exist_ok=True)

    call(base, "POST", "/api/mines", sweep["mine"])
    combos = combinations(sweep)
    seeds = sweep["seeds"]
    interval = sweep.get("run", {}).get("decision_interval_seconds", 15)

    # One scenario per seed and scenario tweak, created once and shared by
    # every run that uses it.
    scenarios = {}

    def scenario_for(seed, tweak):
        key = json.dumps([seed, tweak], sort_keys=True)
        if key not in scenarios:
            scenario = merge(sweep["scenario"], tweak)
            scenario.update({
                "id": f"{name}-{len(scenarios) + 1}", "mine_id": sweep["mine"]["id"], "seed": seed,
                "name": f"{sweep.get('title', name)} (seed {seed})",
            })
            call(base, "POST", "/api/scenarios", scenario)
            scenarios[key] = scenario["id"]
        return scenarios[key]

    jobs = []
    for labels, contribution in combos:
        for seed in seeds:
            jobs.append((labels, contribution, seed, scenario_for(seed, contribution["scenario"])))

    started = time.time()
    total = len(jobs)
    done = [0]

    def execute(job):
        labels, contribution, seed, scenario_id = job
        body = {
            "name": f"{name}: {arm_name(labels)} (seed {seed})",
            "mode": "simulation", "scenario_id": scenario_id,
            "decision_interval_seconds": interval, "time_compression": 10_000_000,
            "settings": merge(sweep.get("settings", {}), contribution["settings"]),
            "intent": merge(sweep.get("intent", {}), contribution["intent"]),
        }
        if contribution["intent_schedule"]:
            body["intent_schedule"] = contribution["intent_schedule"]
        run_id = call(base, "POST", "/api/runs", body)["id"]
        while True:
            detail = call(base, "GET", f"/api/runs/{run_id}")
            status = detail["run"]["status"]
            if status in ("completed", "failed", "cancelled"):
                break
            time.sleep(0.5)
        if status != "completed":
            raise RuntimeError(f"run {run_id} ({arm_name(labels)}, seed {seed}) ended {status}: "
                               f"{detail['run'].get('error', '')}")
        row = measure(base, run_id, interval)
        row.update(labels)
        row["seed"] = seed
        done[0] += 1
        print(f"  [{done[0]}/{total}] {arm_name(labels)} seed {seed}: "
              f"{row['sla_breaches']} breaches, {row['cloud_hours']} cloud h, "
              f"{row['ttl_exposing_mean_s']} s to locate exposing events", flush=True)
        return row

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        rows = list(pool.map(execute, jobs))

    axis_names = [axis["name"] for axis in sweep["axes"]]
    fields = axis_names + ["seed"] + METRICS
    with open(os.path.join(out_dir, "runs.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fields})

    with open(os.path.join(out_dir, "sweep.json"), "w") as f:
        json.dump(sweep, f, indent=2)
        f.write("\n")

    versions = call(base, "GET", "/api/version")
    here = os.path.dirname(os.path.abspath(__file__))
    git = lambda *args: subprocess.run(["git", "-C", here, *args], capture_output=True, text=True).stdout.strip()
    with open(os.path.join(out_dir, "runs.csv"), "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    provenance = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": f"make -C platform-experiments sweep S={name}",
        "simlab_api": versions.get("simlab_api"),
        "autoscaler": versions.get("autoscaler"),
        # The sweep definition and what is measured live here, so this
        # repository's version and commit are part of what produced the numbers
        # too. Modified means the measuring code or the definitions differ from
        # the commit; anything else in this repository cannot change a number.
        "platform_experiments": {"version": own_version(), "commit": git("rev-parse", "HEAD"),
                                 "modified": bool(git("status", "--porcelain", "--", "lib", "sweeps"))},
        "runs": total,
        "wall_seconds": round(time.time() - started),
        "runs_csv_sha256": digest,
    }
    with open(os.path.join(out_dir, "provenance.json"), "w") as f:
        json.dump(provenance, f, indent=2)
        f.write("\n")

    write_report(out_dir, notes_path=os.path.splitext(sweep_path)[0] + ".md")
    print(f"\n{total} runs in {provenance['wall_seconds']} s; report in {out_dir}/report.md")


# ---------------------------------------------------------------- measuring

METRICS = [
    "sla_breaches", "sla_breaches_as_submitted", "cloud_hours", "local_hours", "drained_hours",
    "mean_wait_s", "p95_wait_s", "jobs_reprioritised", "overload_decisions", "accepted_breach_cycles",
    "events", "exposing_events", "exposing_high_events",
    "ttl_exposing_mean_s", "ttl_exposing_p95_s", "ttl_exposing_max_s", "ttl_exposing_high_mean_s",
    "ttl_all_mean_s", "ttl_all_p95_s",
    "ttp_exposing_mean_s", "ttp_exposing_p95_s", "ttp_all_mean_s",
    "exposing_ever_decayed", "exposing_promoted", "decayed_events", "promoted_events",
    "harmless_kept_events",
]


def percentile(values, q):
    if not values:
        return ""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def rounded(value, places=1):
    return "" if value == "" or value is None else round(value, places)


def measure(base, run_id, interval):
    metrics = call(base, "GET", f"/api/runs/{run_id}/metrics")
    cycles = paged(base, f"/api/runs/{run_id}/cycles", "cycles")
    events = paged(base, f"/api/runs/{run_id}/seismicity", "events")

    def located_after(event):
        if event["located_at_seconds"] is None:
            return None
        return event["located_at_seconds"] - event["origin_seconds"]

    def processed_after(event):
        if event["processed_at_seconds"] is None:
            return None
        return event["processed_at_seconds"] - event["origin_seconds"]

    def ever(event, state):
        return any(t["state"] == state for t in (event.get("intent") or []))

    exposing = [e for e in events if e["exposed"]]
    exposing_high = [e for e in exposing if any(x["level"] in ("high", "very-high") for x in e["exposed"])]
    located = lambda es: [d for d in (located_after(e) for e in es) if d is not None]
    processed = lambda es: [d for d in (processed_after(e) for e in es) if d is not None]
    mean = lambda xs: statistics.fmean(xs) if xs else ""

    return {
        "sla_breaches": metrics["sla_breaches"],
        "sla_breaches_as_submitted": metrics.get("sla_breaches_as_submitted", ""),
        "cloud_hours": rounded(metrics["cloud_executor_seconds"] / 3600),
        "local_hours": rounded(metrics["local_executor_seconds"] / 3600),
        "drained_hours": rounded(metrics["cycles"] * interval / 3600, 2),
        "mean_wait_s": rounded(metrics["mean_wait_seconds"]),
        "p95_wait_s": rounded(metrics["p95_wait_seconds"]),
        "jobs_reprioritised": metrics.get("jobs_reprioritised", ""),
        "overload_decisions": sum(1 for c in cycles if c["reason"].startswith("overload")),
        "accepted_breach_cycles": sum(1 for c in cycles if c.get("breaches_exempt_only")),
        "events": len(events),
        "exposing_events": len(exposing),
        "exposing_high_events": len(exposing_high),
        "ttl_exposing_mean_s": rounded(mean(located(exposing))),
        "ttl_exposing_p95_s": rounded(percentile(located(exposing), 0.95)),
        "ttl_exposing_max_s": rounded(max(located(exposing), default="")),
        "ttl_exposing_high_mean_s": rounded(mean(located(exposing_high))),
        "ttl_all_mean_s": rounded(mean(located(events))),
        "ttl_all_p95_s": rounded(percentile(located(events), 0.95)),
        "ttp_exposing_mean_s": rounded(mean(processed(exposing))),
        "ttp_exposing_p95_s": rounded(percentile(processed(exposing), 0.95)),
        "ttp_all_mean_s": rounded(mean(processed(events))),
        "exposing_ever_decayed": sum(1 for e in exposing if ever(e, "decayed")),
        "exposing_promoted": sum(1 for e in exposing if ever(e, "promoted")),
        "decayed_events": sum(1 for e in events if ever(e, "decayed")),
        "promoted_events": sum(1 for e in events if ever(e, "promoted")),
        "harmless_kept_events": sum(1 for e in events if not e["exposed"] and e.get("intent")
                                    and not ever(e, "decayed")),
    }


# ---------------------------------------------------------------- reporting

# Every column a report can show: field → (heading, decimal places).
COLUMNS = {
    "sla_breaches": ("Breaches", 0),
    "sla_breaches_as_submitted": ("As submitted", 0),
    "cloud_hours": ("Cloud h", 1),
    "local_hours": ("Local h", 1),
    "drained_hours": ("Drained h", 1),
    "overload_decisions": ("Overloads", 0),
    "mean_wait_s": ("Wait mean s", 0),
    "p95_wait_s": ("Wait p95 s", 0),
    "exposing_events": ("Exposing events", 0),
    "ttl_exposing_mean_s": ("Locate exposing, mean s", 0),
    "ttl_exposing_p95_s": ("p95 s", 0),
    "ttp_exposing_mean_s": ("Process exposing, mean s", 0),
    "ttl_all_mean_s": ("Locate all, mean s", 0),
    "ttl_all_p95_s": ("Locate all, p95 s", 0),
    "ttp_all_mean_s": ("Process all, mean s", 0),
    "exposing_ever_decayed": ("Exposing decayed", 0),
    "decayed_events": ("Events decayed", 0),
}

# What a sweep reports unless it names its own `columns` and `compare`: what
# intent changes. A sweep of the autoscaler's own settings runs with intent off,
# where half of these are zeros and "as submitted" repeats "breaches", so it
# names the columns that settings move instead.
INTENT_COLUMNS = [
    "sla_breaches", "sla_breaches_as_submitted", "cloud_hours", "drained_hours", "overload_decisions",
    "exposing_events", "ttl_exposing_mean_s", "ttl_exposing_p95_s", "ttp_exposing_mean_s", "ttl_all_mean_s",
    "exposing_ever_decayed", "decayed_events",
]
INTENT_COMPARED = [
    "sla_breaches", "sla_breaches_as_submitted", "cloud_hours", "ttl_exposing_mean_s", "ttp_exposing_mean_s",
]


def named(sweep, key, default):
    fields = sweep.get(key, default)
    unknown = [f for f in fields if f not in COLUMNS]
    if unknown:
        raise ValueError(f"{sweep['name']}: {key} names {', '.join(unknown)}, which a report cannot show; "
                         f"it can show {', '.join(COLUMNS)}")
    return fields


def headline(sweep):
    """The results table's columns, as (field, heading, places)."""
    return [(field, *COLUMNS[field]) for field in named(sweep, "columns", INTENT_COLUMNS)]


def compared(sweep):
    """The comparison table's columns, as (field, heading). A heading loses its
    unit there, since what the table shows is a change in per cent."""
    return [(field, COLUMNS[field][0].removesuffix(" s")) for field in named(sweep, "compare", INTENT_COMPARED)]


# What each column means, for a sweep that names its columns.
DEFINED = {
    "sla_breaches": "**Breaches**: jobs that waited longer than the deadline of the level they were "
                    "served at, measured from their deadline origin.",
    "sla_breaches_as_submitted": "**As submitted**: against the level each job arrived at, from "
                                 "arrival — what intent cost against the SLA the work was submitted under.",
    "cloud_hours": "**Cloud h**: cloud executor-hours of ready capacity, the billed tier.",
    "local_hours": "**Local h**: on-premise executor-hours of ready capacity — hardware the mine "
                   "already owns, so these hours are not billed.",
    "drained_hours": "**Drained h**: simulated hours until the queue was empty.",
    "overload_decisions": "**Overloads**: decisions where no capacity within both caps avoided a "
                          "predicted breach, so the autoscaler ran flat out.",
    "mean_wait_s": "**Wait mean s**: seconds a job waited in the queue before an executor took it, "
                   "over every job.",
    "p95_wait_s": "**Wait p95 s**: the 95th percentile of the seconds a job waited in the queue "
                  "before an executor took it.",
    "exposing_events": "**Exposing events**: events that truly exposed someone to at least moderate "
                       "ground motion when they happened (judged by the simulator from the truth).",
    "ttl_exposing_mean_s": "**Locate exposing**: seconds from an event that truly exposed someone to at "
                           "least moderate ground motion (judged by the simulator from the truth) to its "
                           "first location.",
    "ttl_exposing_p95_s": "**p95 s**: the 95th percentile of the seconds to locate an exposing event.",
    "ttp_exposing_mean_s": "**Process exposing**: seconds from an exposing event to every one of its "
                           "picks processed — its final location.",
    "ttl_all_mean_s": "**Locate all, mean s**: seconds from an event to its first location, over "
                      "every event.",
    "ttl_all_p95_s": "**Locate all, p95 s**: the 95th percentile of the seconds from an event to its "
                     "first location.",
    "ttp_all_mean_s": "**Process all, mean s**: seconds from an event to its final location, over "
                      "every event.",
    "exposing_ever_decayed": "**Exposing decayed**: exposing events intent decayed at some point — "
                             "the misses.",
    "decayed_events": "**Events decayed**: events whose work intent decayed at some point.",
}


def definitions(sweep):
    if "columns" not in sweep and "compare" not in sweep:
        return DEFINITIONS
    fields = list(dict.fromkeys(f for f, *_ in headline(sweep) + compared(sweep)))
    return "".join(f"- {DEFINED[f]}\n" for f in fields) + \
        "- Every figure is the mean over seeds, with the range across seeds beneath where\n  the seeds disagree.\n"


# What an intent sweep's columns mean, worded together.
DEFINITIONS = """\
- **Breaches**: jobs that waited longer than the deadline of the level they were
  served at, measured from their deadline origin. **As submitted**: against the
  level each job arrived at, from arrival — what intent cost against the SLA the
  work was submitted under.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Drained h**: simulated hours until the queue was empty.
- **Overloads**: decisions where no capacity within both caps avoided a predicted
  breach, so the autoscaler ran flat out — often a job already late when seen.
- **Locate exposing**: seconds from an event to its first location, for events
  that truly exposed someone to at least moderate ground motion when they
  happened (judged by the simulator from the truth). The operator-facing measure
  of whether ordering helped the people it was meant to.
- **Process exposing**: seconds from such an event to every one of its picks
  processed — its final location. Promotion acts once an event is located, so
  this, not the first location, is where it can help.
- **Exposing decayed**: of those, how many intent decayed at some point — the
  misses. **Events decayed**: events whose work intent decayed at some point.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.
"""


def read_rows(out_dir):
    with open(os.path.join(out_dir, "runs.csv")) as f:
        return list(csv.DictReader(f))


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def aggregate(rows, field):
    values = [v for v in (number(r[field]) for r in rows) if v is not None]
    if not values:
        return None
    return statistics.fmean(values), min(values), max(values)


def change(arm_rows, base_rows, field):
    """The change in a measure summed over seeds, as a fraction of the reference's
    total, pairing each run with the reference run on the same seed.

    Totals rather than a mean of per-seed percentages, which a seed with a
    handful of breaches would dominate. None when no seed pairs or the
    reference total is zero. Briefs chart this same function, so a figure and
    the report table it came from cannot disagree."""
    ours = theirs = 0.0
    paired = 0
    for row in arm_rows:
        ref = next((b for b in base_rows if b["seed"] == row["seed"]), None)
        a, b = number(row[field]), number(ref[field]) if ref else None
        if a is not None and b is not None:
            ours, theirs, paired = ours + a, theirs + b, paired + 1
    return (ours - theirs) / theirs if paired and theirs else None


def cell(stats, places):
    if stats is None:
        return "–"
    mean, low, high = stats
    fmt = lambda v: f"{v:,.{places}f}"
    if fmt(low) == fmt(high):
        return fmt(mean)
    return f"{fmt(mean)}<br><sub>{fmt(low)}–{fmt(high)}</sub>"


def measured_by(ours):
    """This repository's part in a report's provenance. A report recorded
    before this repository had versions names its commit alone, as it did."""
    commit = f"`{ours.get('commit', '')[:12]}`"
    modified = ", modified" if ours.get("modified") else ""
    if ours.get("version"):
        return f"{ours['version']} ({commit}{modified})"
    return commit + modified


def own_version():
    """This repository's semantic version, as of its commit.

    scripts/version.sh marks any uncommitted change as .dirty, down to a local
    .gitignore that no number depends on. What could move a number — the
    measuring code and the sweep definitions — is recorded as `modified`
    beside the version, so the mark is dropped here rather than stamped on
    every report made from a checkout with an unrelated edit."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run([os.path.join(root, "scripts", "version.sh"), root], capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    version = result.stdout.strip().removesuffix(".dirty")
    # On a release tag the script adds the commit only to say it is dirty.
    core, _, build = version.partition("+")
    return core if build and "-" not in core else version


def write_report(out_dir, notes_path=None):
    with open(os.path.join(out_dir, "sweep.json")) as f:
        sweep = json.load(f)
    with open(os.path.join(out_dir, "provenance.json")) as f:
        provenance = json.load(f)
    rows = read_rows(out_dir)
    axis_names = [axis["name"] for axis in sweep["axes"]]
    arms = []
    for labels, _ in combinations(sweep):
        arm_rows = [r for r in rows if all(r[k] == v for k, v in labels.items())]
        arms.append((labels, arm_rows))

    notes = ""
    notes_path = notes_path or os.path.join(os.path.dirname(os.path.dirname(out_dir)), "sweeps", sweep["name"] + ".md")
    if os.path.exists(notes_path):
        with open(notes_path) as f:
            notes = f.read().strip()

    build = lambda b: f"{b['version'] or 'unversioned'} (`{b['commit'][:12]}`{', modified' if b['modified'] else ''})" if b else "unknown"
    lines = [
        f"# {sweep.get('title', sweep['name'])}",
        "",
        f"> {sweep['question']}",
        "",
        f"{provenance['runs']} runs: {len(arms)} arms × {len(sweep['seeds'])} seeds "
        f"({', '.join(str(s) for s in sweep['seeds'])}). Produced {provenance['recorded_at']} "
        f"by autoscaler {build(provenance['autoscaler'])} and simlab-api {build(provenance['simlab_api'])}, "
        f"built from clean checkouts of those commits, measured by platform-experiments "
        f"{measured_by(provenance.get('platform_experiments', {}))}.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        provenance["command"],
        "```",
        "",
        f"At the same commits every number here comes out the same: `runs.csv` has "
        f"SHA-256 `{provenance['runs_csv_sha256'][:16]}…`.",
        "",
    ]
    if notes:
        lines += [notes, ""]

    columns = headline(sweep)
    lines += ["## Results", "", "| Arm | " + " | ".join(h for _, h, _ in columns) + " |",
              "|---|" + "---:|" * len(columns)]
    for labels, arm_rows in arms:
        lines.append(f"| {arm_name(labels)} | " + " | ".join(
            cell(aggregate(arm_rows, field), places) for field, _, places in columns) + " |")
    lines.append("")

    # The baseline names some or all of the axes. Each arm is compared with the
    # arm that has the baseline's labels on those axes and its own on the rest,
    # so a sweep across cloud caps compares intent with no intent at the same
    # cap rather than everything with one cap.
    baseline = sweep.get("baseline")
    if baseline:
        others = [a for a in axis_names if a not in baseline]
        heading = f"### Against {arm_name(baseline)}" + (f", at the same {' and '.join(others)}" if others else "")
        lines += [heading, "",
                  "The change in each measure summed over seeds, against the reference arm on the same "
                  "seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful "
                  "of breaches would dominate.", "",
                  "| Arm | " + " | ".join(h for _, h in compared(sweep)) + " |",
                  "|---|" + "---:|" * len(compared(sweep))]
        for labels, arm_rows in arms:
            reference = {**labels, **baseline}
            if labels == reference:
                continue
            base_rows = [r for r in rows if all(r[k] == v for k, v in reference.items())]
            if not base_rows:
                continue
            deltas = []
            for field, _ in compared(sweep):
                delta = change(arm_rows, base_rows, field)
                deltas.append(f"{delta * 100:+.0f} %" if delta is not None else "–")
            lines.append(f"| {arm_name(labels)} | " + " | ".join(deltas) + " |")
        lines.append("")

    lines += [
        "## What the columns mean", "", definitions(sweep),
        "## Setup", "",
        f"Axes: {'; '.join(f'**{a['name']}** ({len(a['values'])})' for a in sweep['axes'])}. "
        "Each arm's own intent, settings and scenario changes are in `sweep.json`.",
        "",
        "```json",
        json.dumps({k: sweep[k] for k in ("mine", "scenario", "settings", "intent", "run") if k in sweep}, indent=2),
        "```",
        "",
        "Per-seed figures, with every measured column, are in [`runs.csv`](runs.csv).",
        "",
    ]
    rendered = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(__file__)), "rev-parse", "--short=12", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    if rendered:
        lines += [f"<sub>Tables rendered by platform-experiments `{rendered}`.</sub>", ""]
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    command, args = sys.argv[1], sys.argv[2:]
    if command == "run":
        run_sweep(args[0], args[1], args[2], int(args[3]) if len(args) > 3 else 4)
    elif command == "report":
        write_report(args[0], args[1] if len(args) > 1 else None)
    elif command == "ref":
        with open(args[0]) as f:
            print(build_ref(json.load(f), args[1]))
    else:
        sys.exit(f"unknown command {command}")
