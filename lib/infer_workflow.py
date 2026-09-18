"""Infer the mine's processing workflow from the operational extract.

One streaming pass over `../data/prod_processes_muj.csv`, writing aggregates to
stdout as JSON. **It prints counts, medians and shares only — never a row.** The
extract is production data from a named mine and never leaves that directory;
see ../data/README.md and CLAUDE.md.

    python3 lib/infer_workflow.py > /tmp/workflow.json

What it answers, and why each question is here:

  cadence       Is `associate` really a 10 s timer? (docs/calibration.md assumed
                it from the dataset README; this measures it.)
  window        How long a span does a sweep read?
  emission      What submits a `locate`? The pick->associate->locate DAG is not
                expressed in the data (README caveat 3), so the only evidence
                available is timing: if a sweep emits its locates, they land
                inside its own execution.
  productivity  How often does a sweep emit anything, and how much?
  cost          Does a sweep cost more when it emits more? A simulator that
                varies the sweep policy changes emission per sweep, so a flat
                cost would make every alternative policy look free.
  trigger       Do completing picks predict a productive sweep? This decides
                whether an event-driven trigger is even well-founded.
  shape         What is one `pick` job? (Not one seismogram — it is a batch.)
"""

import bisect
import collections
import csv
import datetime
import json
import os
import random
import re
import statistics
import sys

# args/input/output hold large quoted payloads; the default limit throws on them.
csv.field_size_limit(10_000_000)

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', 'data', 'prod_processes_muj.csv')
# Everything before 2025-03 is a trickle of 145 rows in total (README).
CUT = datetime.datetime(2025, 3, 1, tzinfo=datetime.timezone.utc).timestamp()
STAGES = ('pick', 'associate', 'locate')
# `input`/`output` on an associate are "<start ns>,<end ns>": the window it swept.
WINDOW = re.compile(r'(\d{17,20})\s*,\s*(\d{17,20})')
# `args` on a pick is a list of "<uuid>,<ns>" pairs: the seismograms in the batch.
SEISMOGRAM = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                        r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\s*,\s*(\d{17,20})')


def parse(ts):
    try:
        return datetime.datetime.fromisoformat(ts).timestamp()
    except (ValueError, TypeError):
        return None


def quantile(values, p):
    if not values:
        return None
    v = sorted(values)
    return v[min(len(v) - 1, int(p * len(v)))]


def read(path):
    sweeps = []          # (submission, end|None) per associate
    locates = []         # submission per locate
    pick_ends = []       # end per pick
    submitted_rows = collections.Counter()
    durations = collections.defaultdict(list)
    windows = []
    batch_items = []
    batch_span = []
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            stage = row['funcname']
            if stage not in STAGES:
                continue
            submitted = parse(row['submission_time'])
            if submitted is None or submitted < CUT:
                continue
            submitted_rows[stage] += 1
            started, ended = parse(row['start_time']), parse(row['end_time'])
            # A backup job runs for hours; the cap keeps a stray row from
            # dominating a mean. Pipeline jobs are seconds.
            if started and ended and 0 < ended - started < 1e5:
                durations[stage].append(ended - started)
            if stage == 'associate':
                # The end timestamp, not submission+execution: a sweep's locates
                # are submitted while it runs, and the couple of hundredths it
                # waits to start belong inside that span too.
                sweeps.append((submitted, ended))
                m = WINDOW.search(row.get('input') or '')
                if m:
                    windows.append((int(m.group(2)) - int(m.group(1))) / 1e9)
            elif stage == 'locate':
                locates.append(submitted)
            else:
                if ended:
                    pick_ends.append(ended)
                stamps = [int(x) / 1e9 for x in SEISMOGRAM.findall(row.get('args') or '')]
                if stamps:
                    batch_items.append(len(stamps))
                    batch_span.append(max(stamps) - min(stamps))
    sweeps.sort()
    locates.sort()
    pick_ends.sort()
    return (sweeps, locates, pick_ends, submitted_rows, durations, windows,
            batch_items, batch_span)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    (sweeps, locates, pick_ends, submitted_rows, durations, windows,
     batch_items, batch_span) = read(path)
    starts = [s for s, _ in sweeps]

    gaps = [b - a for a, b in zip(starts, starts[1:])]

    # Attribute each locate to the sweep running when it was submitted. If the
    # sweep emits them, every locate falls inside one sweep's execution — which
    # is the claim, so it is measured rather than assumed.
    emitted = collections.Counter()
    offset, inside = [], 0
    for t in locates:
        i = bisect.bisect_right(starts, t) - 1
        if i < 0:
            continue
        emitted[i] += 1
        offset.append(t - starts[i])
        end = sweeps[i][1]
        if end is not None and t <= end:
            inside += 1

    counts = list(emitted.values())
    productive = [(starts[i], emitted[i], sweeps[i][1]) for i in sorted(emitted)]
    productive_gaps = [b[0] - a[0] for a, b in zip(productive, productive[1:])]

    # Sweep cost against what the sweep emitted, by least squares, plus the
    # observed medians per band — a line fitted to a curve would look the same
    # in its coefficients, so the bands are what show it is really linear.
    xs = [emitted.get(i, 0) for i, (s0, e0) in enumerate(sweeps) if e0 is not None]
    ys = [e0 - s0 for s0, e0 in sweeps if e0 is not None]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x - mx) ** 2 for x in xs))
    bands = collections.defaultdict(list)
    for x, y in zip(xs, ys):
        bands[min(x // 10 * 10, 50)].append(y)
    empty = [y for x, y in zip(xs, ys) if x == 0]

    # Does the emitted set change slowly (a resident window being re-located) or
    # arrive in bursts? Compare consecutive productive sweeps against randomly
    # paired ones. Restricted to sweeps close in time, so a quiet night between
    # them is not read as a change in the set.
    adjacent = [abs(b[1] - a[1]) for a, b in zip(productive, productive[1:])
                if b[0] - a[0] < 120]
    rng = random.Random(7)
    paired = [abs(rng.choice(counts) - rng.choice(counts)) for _ in adjacent]

    # Do picks completing in the preceding interval predict a productive sweep?
    given = collections.defaultdict(lambda: [0, 0])
    landed_productive, landed_empty = [], []
    for i in range(1, len(starts)):
        n = (bisect.bisect_left(pick_ends, starts[i])
             - bisect.bisect_left(pick_ends, starts[i - 1]))
        bucket = given[min(n, 6)]
        bucket[0] += 1
        if emitted.get(i, 0) > 0:
            bucket[1] += 1
            landed_productive.append(n)
        else:
            landed_empty.append(n)

    span_hours = (starts[-1] - starts[0]) / 3600
    residency = 1800 / statistics.median(productive_gaps)

    json.dump({
        'rows': {s: submitted_rows[s] for s in STAGES},
        'span_hours': round(span_hours, 1),
        'cadence_s': {
            'median': statistics.median(gaps), 'p05': quantile(gaps, .05),
            'p95': quantile(gaps, .95),
            'share_10s': sum(1 for g in gaps if 9.5 <= g <= 10.5) / len(gaps),
        },
        'window_s': {
            'n': len(windows), 'median': statistics.median(windows),
            'share_1800': sum(1 for w in windows if abs(w - 1800) < 1) / len(windows),
        },
        'emission': {
            'n': len(offset),
            'share_inside_sweep_execution': inside / len(offset),
            'offset_median_s': statistics.median(offset),
            'offset_p95_s': quantile(offset, .95),
        },
        'productivity': {
            'sweeps': len(sweeps), 'productive': len(counts),
            'share_productive': len(counts) / len(sweeps),
            'locates_per_productive_mean': statistics.fmean(counts),
            'locates_per_productive_median': statistics.median(counts),
            'locates_per_productive_p95': quantile(counts, .95),
            'locates_per_productive_max': max(counts),
            'productive_gap_s_median': statistics.median(productive_gaps),
            'productive_gap_s_p95': quantile(productive_gaps, .95),
        },
        'cost_s': {
            'intercept': round(my - slope * mx, 4), 'per_locate': round(slope, 5),
            'empty_median': round(statistics.median(empty), 4), 'empty_n': len(empty),
            'median_by_locates': {str(k): {'n': len(v), 'median': round(statistics.median(v), 3)}
                                  for k, v in sorted(bands.items())},
        },
        'emitted_set_changes_slowly': {
            'n': len(adjacent),
            'consecutive_abs_delta_median': statistics.median(adjacent),
            'randomly_paired_abs_delta_median': statistics.median(paired),
        },
        'trigger': {
            'picks_landed_before_productive_median': statistics.median(landed_productive),
            'picks_landed_before_empty_median': statistics.median(landed_empty),
            'productive_with_no_pick_landed':
                sum(1 for n in landed_productive if n == 0) / len(landed_productive),
            'empty_with_picks_landed':
                sum(1 for n in landed_empty if n > 0) / len(landed_empty),
            'p_productive_given_picks_landed':
                {str(k): {'n': v[0], 'p': round(v[1] / v[0], 4)} for k, v in sorted(given.items())},
        },
        'pick_batch': {
            'n': len(batch_items), 'items_mean': statistics.fmean(batch_items),
            'items_median': statistics.median(batch_items), 'items_max': max(batch_items),
            'span_s_median': statistics.median(batch_span),
            'span_s_p95': quantile(batch_span, .95),
        },
        'duration_s': {
            s: {'n': len(v), 'mean': statistics.fmean(v), 'median': statistics.median(v),
                'p95': quantile(v, .95)} for s, v in durations.items()
        },
        # Two independent routes to the candidate-event rate: how many events a
        # sweep sees resident in its 30-minute window, and how many distinct
        # events that implies once each is re-located on every productive sweep
        # it stays resident for.
        'implied_events_per_hour': {
            'from_window_occupancy': statistics.median(counts) / 0.5,
            'from_residency': len(locates) / residency / span_hours,
        },
    }, sys.stdout, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
