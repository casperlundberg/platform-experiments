# 006 — Is cloud bought only when the queue needs it, and given back when it does not?

**Status:** regression guard. Written for two defects found in recorded runs; guards their fixes.

## The question

Cloud capacity is the billed tier. The autoscaler is meant to buy it only as
proven overflow of work the local tier cannot keep on time, and to give it back
once nothing wants it. Two things can go wrong, and both did:

1. **Buying it for nothing.** Every run starts cold, and a local coldstart of a
   minute or two is longer than the top level's 60-second deadline, so the first
   job or two is always a few seconds late. Autoscaler 1.x counted a job already
   late as a breach no capacity could prevent — at every executor count, even
   serving from the first instant — concluded that nothing within both caps
   could hold the queue, and ran flat out. Recorded run `run-w4f3hwst-v235e3h6`
   bought 200 cloud executors in its fifth minute for 49 jobs that six could
   serve.
2. **Keeping it.** A tier came down five executors a cycle at most, and no
   scale-down could follow another within five minutes. Sixty cloud executors
   took 65 minutes to hand back; that run's two hundred were still being
   dripped back an hour later with the queue empty.

## Why this is an experiment and not a unit test

The engine's rules are unit-tested in `autoscaler/internal/policy`
(`late_test.go`, `release_test.go`), including a property test that the
capacity held is exactly what the scale-down windows and per-executor
lifetimes justify, and those fail first. What they cannot show is what the
assembled system buys: the queue a real replay presents at a cold start, the
arrival rate simlab reports, the settings the run actually used, and the
capacity the simulation adapter reports back cycle after cycle. The defect was
invisible to every unit suite for exactly that reason — the engine tests
switched hysteresis off, and no test looked at a whole run's cloud bill.

## Method

One two-hour scenario: a quiet background for thirty minutes, then a rock burst
that raises the event rate 45-fold and decays over ten minutes, then an hour of
background again. Work at P100 and P50 only, so the queue empties after the
burst instead of holding twelve-hour work for hours. Replayed with 24 local and
60 cloud executors — background work needs about ten, so afterwards the local
tier plainly serves it alone — coldstarts of one and three minutes, and every
other setting at its default. From the recorded cycles:

- **A quiet start buys no cloud.** Before the burst, under one cloud
  executor-hour in total, and the plan never reaches the cloud cap.
- **The burst is still served.** The plan reaches the cloud cap during it —
  the other checks must not pass by never bursting.
- **Cloud is given back.** From thirty minutes after the burst began — three
  times its aftershock decay, with arrivals back to what the local tier serves
  alone — the cloud used is at most the whole cap held for the longer of the
  cloud scale-down window and the cloud minimum lifetime. A per-cycle bound
  would need the engine's requirement on every cycle, which a recorded run does
  not carry; `release_test.go` in the autoscaler holds that, cycle by cycle.

## Result

Against autoscaler 2.0.0 (local build, 2026-09-21):

```
✓ a quiet start bought 0.0 cloud executor-hours, planning at most 0 cloud executors
✓ the burst still reached the cloud cap of 60
✓ in the 60 minutes after the burst, 0.1 cloud executor-hours (the rules allow at most 10.0)
```

## Making it fail on purpose

Against autoscaler 1.1.0 (`AUTOSCALER_DIR` pointing at a checkout of its last
1.x commit, `14f2ca0`), both defects show:

```
✗ a quiet start bought 22.0 cloud executor-hours and planned 60 of 60 cloud executors
✓ the burst still reached the cloud cap of 60
✗ in the 61 minutes after the burst, 12.6 cloud executor-hours, over the 10.0 the window and lifetime allow
```

The first version of the release check counted consecutive cycles holding
cloud, and passed 1.1.0 while failing 2.0: a window renewed by each spike of an
aftershock tail is a legitimate hold, and 1.1.0's drip broke its holds into
short runs. A check has to measure the property, not a symptom of one
implementation of it.

## Running it

```bash
./run.sh
```

Needs Docker and Go, and the service repositories checked out alongside. Exits
non-zero if any check fails.
