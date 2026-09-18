# Calibrating a mine to an operational catalogue

The `workday` mine and the day the `scenario-shapes` sweep runs on are not
chosen numbers. They are fitted to an extract of a real seismic-processing
pipeline — ColonyOS process records of `pick`, `associate` and `locate` jobs —
so that a simulated day carries about the work a real one did.

**The extract stays out of every repository**, and nothing here quotes a row
from it. What follows are aggregates, which is what a reader needs to check the
fit or redo it.

## What the extract says

A streaming pass over the production file, restricted to its dense window
(2025-03 onwards: 29 days, 1,087,951 rows in total):

| | |
|---|---|
| Jobs on a typical day | 39,162 (median), 37,510 (mean) |
| Jobs an hour, averaged over 26 typical days | 1,644 |
| Busiest hour of the day | 1,962 — 1.19× the mean |
| Quietest hour | 1,039 — 0.63× the mean |
| Job mix | `locate` 51.0 %, `pick` 26.7 %, `associate` 22.2 % |
| Execution time, mean | `locate` 47.2 s, `pick` 14.6 s, `associate` 1.3 s |
| Execution time, weighted mean | 28.3 s |
| Priority, static per type | `associate` 100, `locate` 50, `pick` 0 |

Waiting time in the extract is negligible — a median of 0.03 s — so it says
nothing about queueing, and nothing about deadlines. It fixes the *arrival*
side: how much work, of what mix, at what cost, and how the rate moves over a
day. The SLA it is replayed against is the autoscaler's own, and the contention
is induced by capping capacity.

## How the mine follows from it

Simlab generates work per seismic event: each event is picked by
`sensors × 0.6` of the array, and each pick is one job. So

```
jobs an hour = events an hour × sensors × 0.6
```

With **30 sensors** — the array size earlier sweeps used, kept so results are
comparable — matching 1,644 jobs an hour needs about **91 events an hour**,
which is the mine's `background_rate_per_hour`. Generating a day at that rate
gives 39,000–40,300 jobs across seeds: within about 2 % of the measured day.

The scenario takes the rest directly: `job_seconds` 28, and a `priority_mix` of
22.2 % at priority 100, 51.0 % at 50 and 26.7 % at 0 — the extract's own mix
mapped onto the levels its own scheduler used.

## What the fit does not carry

- **The daily swing is stronger in the model.** Simlab modulates the background
  rate by ±35 %, against the ±19 % / −37 % the extract shows. The amplitude is a
  constant in the workload generator, not a scenario setting; changing it would
  move every recorded job stream, so it is a MAJOR change and is left alone.
- **One execution time, not three.** Simlab draws every job's duration from one
  log-normal around `job_seconds`, so the spread within a day is narrower than
  the extract's three job types, whose means run from 1.3 s to 47.2 s.
- **Arrival is event-driven, not timer-driven.** In the real pipeline
  `associate` is a timer job every 10 s; here every job belongs to an event.
  The counts match; the mechanism does not.
  [`workflow-inference.md`](workflow-inference.md) measures that mechanism, and
  explains why its ~27 candidate events an hour and this mine's 91 are both
  right: 91 is a job-count parameter, because simlab derives picks from events
  and production does not.
- **Nothing about deadlines or queueing** comes from the extract, because it
  contains neither.

## Redoing it

The aggregates above come from a streaming pass with `csv.DictReader` over the
production file, counting rows per (date, hour, `funcname`) from 2025-03
onwards and taking execution times as `end_time − start_time`. The dataset's
own README, beside the extract, documents its columns and the traps in it —
raise `csv.field_size_limit`, and do not parse it with `awk`.
