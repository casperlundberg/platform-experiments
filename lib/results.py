#!/usr/bin/env python3
"""Reads a run's results from Simlab, and compares two runs' results.

Used by reproduce.sh. Kept in Python rather than shell because comparing
thousands of cycles and events field by field, and saying exactly where two
runs first part ways, is not something to do with grep.

    results.py fetch BASE_URL TOKEN RUN_ID OUT.json
    results.py plan DETAIL.json            prints shell assignments for reproduce.sh
    results.py compare ORIGINAL.json REPLAY.json
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime


def get(base, token, path):
    request = urllib.request.Request(base.rstrip("/") + path)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def paged(base, token, path, key):
    """Every page of a paged listing, following `next` until it stops moving."""
    out, cursor = [], 0
    while True:
        page = get(base, token, f"{path}?from={cursor}&limit=20000")
        rows = page.get(key) or []
        if not rows:
            return out
        out.extend(rows)
        if page["next"] <= cursor:
            return out
        cursor = page["next"]


def intent_of(base, token, run_id):
    """A run's intent record, or None for a run with none — a live run, or one
    created before intent existed, which reordered nothing."""
    try:
        return get(base, token, f"/api/runs/{run_id}/intent")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise


def fetch(base, token, run_id, out_path):
    results = {
        "detail": get(base, token, f"/api/runs/{run_id}"),
        "intent": intent_of(base, token, run_id),
        "metrics": get(base, token, f"/api/runs/{run_id}/metrics"),
        "cycles": paged(base, token, f"/api/runs/{run_id}/cycles", "cycles"),
        "seismicity": paged(base, token, f"/api/runs/{run_id}/seismicity", "events"),
        "entities": get(base, token, f"/api/runs/{run_id}/entities")["entities"],
    }
    with open(out_path, "w") as f:
        json.dump(results, f)
    print(f"{len(results['cycles'])} cycles, {len(results['seismicity'])} events, "
          f"{len(results['entities'])} people and vehicles")


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalise(results):
    """A run's results with everything a replay legitimately changes removed:
    its id, and the wall-clock instant its simulated clock started at. Cycle
    times become seconds into the run, which is what has to match."""
    start = instant(results["detail"]["run"]["simulated_start"])
    strip = lambda row: {k: v for k, v in row.items() if k != "run_id"}
    cycles = []
    for cycle in results["cycles"]:
        row = strip(cycle)
        row["at"] = (instant(cycle["at"]) - start).total_seconds()
        cycles.append(row)
    intent = results.get("intent")
    changes = [{k: v for k, v in c.items() if k != "recorded_at"} for c in (intent or {}).get("changes", [])]
    return {
        "metrics": strip(results["metrics"]),
        "cycles": cycles,
        "seismicity": [strip(e) for e in results["seismicity"]],
        "entities": results["entities"],
        "intent": changes,
    }


def first_difference(a, b, path=""):
    """The first place two JSON values differ, as a path and the two values."""
    if type(a) is not type(b):
        return path or "(root)", a, b
    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                return f"{path}.{key}", a.get(key, "(absent)"), b.get(key, "(absent)")
            found = first_difference(a[key], b[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path} (length)", len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            found = first_difference(x, y, f"{path}[{i}]")
            if found:
                return found
        return None
    return None if a == b else (path, a, b)


def compare(original_path, replay_path):
    with open(original_path) as f:
        original = normalise(json.load(f))
    with open(replay_path) as f:
        replay = normalise(json.load(f))

    differences = 0
    for section in ("metrics", "cycles", "seismicity", "entities", "intent"):
        found = first_difference(original[section], replay[section], section)
        size = len(original[section]) if isinstance(original[section], list) else len(original[section])
        if found:
            where, recorded, replayed = found
            print(f"DIFFERS {section}: first at {where}: recorded {recorded!r}, replayed {replayed!r}")
            differences += 1
        else:
            print(f"SAME    {section} ({size} {'rows' if isinstance(original[section], list) else 'fields'})")
    return 1 if differences else 0


def plan(detail_path):
    """Shell assignments describing what to rebuild, or why nothing can be."""
    with open(detail_path) as f:
        detail = json.load(f)
    run = detail["run"]
    provenance = detail.get("provenance")
    reasons = list(detail.get("not_reproducible_because") or [])
    if run["mode"] != "simulation":
        reasons.append(f"it is a {run['mode']} run, which watched real infrastructure and replays nothing")
    if provenance is None:
        reasons.append("it was recorded before runs carried their provenance")

    quote = lambda s: "'" + str(s).replace("'", "'\\''") + "'"
    lines = [f"REASONS={quote('; '.join(reasons))}"]
    if provenance:
        autoscaler = provenance.get("autoscaler") or {}
        lines += [
            f"SIMLAB_COMMIT={quote(provenance['simlab_api']['commit'])}",
            f"SIMLAB_VERSION={quote(provenance['simlab_api']['version'])}",
            f"AUTOSCALER_COMMIT={quote(autoscaler.get('commit', ''))}",
            f"AUTOSCALER_VERSION={quote(autoscaler.get('version', ''))}",
            f"INTERVAL={quote(run['decision_interval_seconds'])}",
            f"SIMLAB_GO={quote(provenance['simlab_api'].get('go_version', ''))}",
            f"AUTOSCALER_GO={quote(autoscaler.get('go_version', ''))}",
            f"RECORDED_PLATFORM={quote(provenance['simlab_api'].get('platform', ''))}",
        ]
    print("\n".join(lines))


if __name__ == "__main__":
    command, args = sys.argv[1], sys.argv[2:]
    if command == "fetch":
        fetch(*args)
    elif command == "plan":
        plan(*args)
    elif command == "compare":
        sys.exit(compare(*args))
    else:
        sys.exit(f"unknown command {command}")
