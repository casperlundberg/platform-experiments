# The mine's workflow, inferred from the operational extract

[`docs/calibration.md`](calibration.md) fitted a mine to *how much* work the real
pipeline does — counts, mix, durations. It says nothing about *how the work is
produced*, and it says so itself: "Arrival is event-driven, not timer-driven …
The counts match; the mechanism does not."

This document is the mechanism, measured. It exists because the next step is a
simulator of the pipeline end to end — pick → associate → locate — and the point
of that simulator is to compare ways of running the workflow. A comparison
against a baseline that was assumed rather than observed proves nothing.

Everything here is an aggregate over 671.9 hours (2025-03-01 → 2025-04-07) of
`prod_processes_muj.csv`. **No row from the extract appears here or anywhere
else**; the extract is production data from a named mine and never leaves
`../data`. Regenerate the numbers with:

```bash
python3 lib/infer_workflow.py > workflow.json
```

## What the pipeline does

```
   pick        290,883 jobs   a batch of up to 20 raw seismograms
     │
     ▼
   associate   241,742 jobs   a timer, every 10.0 s, over a 30-minute window
     │                        — and 84 % of the time it produces nothing
     ▼
   locate      555,153 jobs   submitted BY the sweep, while the sweep runs
```

### associate is a timer, and the dataset README was right

| | |
|---|---|
| Gap between sweeps | median **10.0066 s**, p05 9.98, p95 10.05 |
| Within 9.5–10.5 s | **98.8 %** of 241,741 gaps |
| Window swept (`input`) | median **1800.0 s**; exactly 1800 s on 69.6 % |

29 days at 8,640 sweeps a day is 86,400 ÷ 10: the timer does not stop, day or
night, busy or idle.

### A sweep emits its own locates — this is the dependency

The pick → associate → locate DAG **is not expressed in the data**. `parents`,
`children` and `dependencies` are empty on every pipeline row, jobs were
submitted independently rather than as a ColonyOS workflow, and `locate`'s args
is a timestamp rather than an event key, so nothing links a locate back to the
picks that produced it (dataset README, caveats 2 and 3). Timing is the only
evidence available — and it is unambiguous:

| | |
|---|---|
| Locates submitted **inside** a sweep's own execution | **555,153 of 555,153 — 100 %** |
| Offset from that sweep's submission | median 2.42 s, p05 1.31, p95 5.30 |

Not one locate in 29 days was submitted outside a running sweep. A sweep groups
what is ready and submits the locates for it before returning.

> An earlier pass reported the opposite — median lag 11.3 s and *no* locate
> within a second of a sweep — by comparing against the nearest preceding sweep
> **end**. A locate submitted mid-execution precedes its own sweep's end, so it
> was attributed to the previous sweep and picked up a whole 10 s cadence. The
> tell was p05 = 10.09 s: a floor at exactly one interval is an off-by-one-sweep,
> not a physical lag. `lib/infer_workflow.py` measures against submission.

### Most sweeps do nothing, and the ones that work cost more

| | |
|---|---|
| Sweeps producing at least one locate | **15.6 %** (37,767 of 241,742) |
| Gap between *productive* sweeps | median **60.1 s**, p95 130.1 s |
| Locates per productive sweep | mean 14.7, median 13, p95 34, max 102 |

A sweep's cost follows what it emits, by least squares over all 241,742 sweeps:

```
sweep seconds ≈ 1.126 + 0.080 × locates emitted
```

and the observed medians per band confirm it is really a line and not a curve
the coefficients would hide: 1.11 s at 0–9 locates (217,751 sweeps, mostly the
empty ones), 2.06 s at 10–19, 2.81 s at 20–29, 3.70 s at 30–39, 4.75 s at 40–49,
6.49 s at 50+. An empty sweep costs 1.10 s (median over 203,975 of them); a
sweep emitting 50 costs six times that.

**This is why the simulator must model the sweep's cost and not just its
cadence.** Sweeping half as often does not halve the associate work — it makes
each sweep emit roughly twice as much and cost proportionally more. A flat
per-sweep cost would make every slower policy look free.

### Completing picks do *not* predict a productive sweep

The obvious event-driven trigger is "sweep when a pick lands". The data does not
support it:

| Picks completed in the preceding 10 s | Sweeps | P(sweep produces a locate) |
|---:|---:|---:|
| 0 | 136,650 | 8.9 % |
| 1 | 50,271 | **40.4 %** |
| 2 | 12,960 | 14.5 % |
| 3 | 11,007 | 9.3 % |
| 4 | 9,189 | 7.5 % |
| 5 | 7,205 | 6.6 % |
| 6+ | 14,459 | 9.2 % |

Non-monotone, and weak in both directions: **32 % of productive sweeps had no
pick complete before them**, and **39 % of empty sweeps did have picks land**.
That is what a 30-minute sliding window implies — a pick landing now joins a
group that may have formed twenty minutes ago, or may not be complete for
another ten — but it means an event-driven arm is a *design proposal to be
measured*, not a reconstruction of production. Stated as a tradeoff rather than
an assumption, that is one of the more interesting arms to sweep.

### A pick job is a batch, not a seismogram

| | |
|---|---|
| Seismogram references per pick job (`args`) | mean 17.0, median 20, max **20** |
| Time span of a batch | median 11.4 s, p95 45.0 s |
| Gap between pick submissions | median 1.5 s; 26 % under 1 s; only 0.6 % near 10 s |

Picks are batched to a cap of 20 and submitted as data arrives, not on a timer.

### Execution times

| stage | n | mean | median | p95 |
|---|---:|---:|---:|---:|
| `pick` | 290,883 | 14.47 s | 15.47 s | 22.19 s |
| `associate` | 241,742 | 1.27 s | 1.12 s | 2.39 s |
| `locate` | 555,125 | 47.73 s | 42.19 s | 100.29 s |

## How many events are there really?

Two independent routes agree, and both disagree with the mine's current setting:

- **From window occupancy.** A productive sweep emits a median of 13 locates for
  a 30-minute window — 26 events an hour.
- **From residency.** Productive sweeps come every ~60 s, so an event stays
  resident for about 30 of them; 555,153 locates ÷ 30 ÷ 671.9 h ≈ **27.6 events
  an hour**.

Both land at **26–28 candidate events an hour**, against the `workday` mine's
`background_rate_per_hour` of **91**.

**Both numbers are right, because they are not the same quantity.** The mine's
91 was fitted so that `events × sensors × 0.6` reproduces the measured ~1,644
jobs an hour, on the model that every pick job belongs to an event. Production
does not work that way: a pick job is a batch of up to 20 seismograms submitted
as data arrives, whether or not anything seismic happened. So 91 is a *job-count*
parameter and 27 is the *candidate-event* rate. Do not "fix" one to match the
other — the fit in `calibration.md` is still correct for what it claims, and this
is the gap that section four of it predicted.

The end-to-end simulator is what removes the conflict: with real stages it can
carry ~27 events an hour *and* the job counts, because picks are no longer
derived from events.

## What this does not settle

- **Whether a locate re-runs for the same event.** The residency route assumes
  it does. Consecutive productive sweeps differ by a median of 6 locates against
  9 for randomly paired sweeps — correlated, so the emitted set changes slowly
  rather than being a fresh burst each time, but that is suggestive, not proof.
  Nothing in the data links a locate to an event (caveat 2).
- **Anything about queueing or deadlines.** Median wait is 0.03 s; the pipeline
  never contended. Contention has to be induced by capping capacity, and the SLA
  is the autoscaler's own (caveat 1).
- **Whether priority was ever changed after submission.** It never varies within
  a job type here, so this is a static-priority baseline and no evidence either
  way about mutable priority (caveat 5).

## What the simulator takes from this

1. Three real stages, with pick and locate as work and associate as a **sweep**
   whose cost is `1.126 + 0.080 × locates emitted`.
2. The sweep policy is the parameter under test. Production's fixed 10 s is the
   control; the alternatives are the triggers in simlab-api's
   `internal/pipeline` (drained, just-in-time, adaptive, under-pressure) and an
   event-driven arm with no interval — which the trigger table above says is a
   real design change, not a reconstruction.
3. An event is located when its locate **finishes**, so a sweep policy that
   defers a sweep defers the location by the sweep interval plus ~42 s.
4. Per-stage priority is a free parameter, and the production assignment
   (`associate` 100, `locate` 50, `pick` 0) is one arm among several rather than
   the baseline to build on.
