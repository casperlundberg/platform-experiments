# A job a few seconds late sent the engine to both caps

**Found by:** reading a recorded run's cycles after the report that cloud was
kept when it was not needed (run `run-w4f3hwst-v235e3h6` on the deployed
platform), then replaying its cycle 11 through the engine.
**Repository:** `autoscaler` · `internal/policy/simulate.go`, `requirement.go`
**Severity:** results-corrupting. Every run bought cloud it did not need at a
cold start, and the numbers built on it.

## What happened

`Simulate` checked for a breach at elapsed zero, before serving anything:

```go
// A job that is already late is a breach now, not a predicted one.
check(0)
```

A job already past its deadline therefore breached the projection of every
candidate — any executor count, on any ramp — and also under capacity serving
from the first instant, the test `Required` used to tell an unavoidable breach
from an overload. So the search found no count within both caps, found no
steady state either, and returned **Overloaded: run flat out.**

Cycle 11 of that run, replayed through the engine with the same settings:

| Oldest job | Outcome | Executors asked for |
|---|---|---|
| 59 s (of a 60 s deadline) | unavoidable | 6 |
| 65 s | overloaded | 250 — both caps |

Forty-nine jobs arriving at 0.17 a second.

## When it fired

At the start of every run. Nothing is running at a cold start, the local
coldstart (one or two minutes) is longer than the top level's 60-second
deadline, so the first jobs are always a few seconds late by the time anything
can serve them. It fired again whenever a burst made a job late.

## Why it mattered

On the two-hour burst scenario autoscaler 1.1.0 bought the whole cloud cap in
its fifth minute and spent 17–22 cloud executor-hours before the burst began,
for a queue the local tier served alone. Combined with finding 006, that
capacity was still dripping back when the burst arrived at minute 30 — so 1.1.0
met the burst with 25–30 cloud executors already warm, by accident, and its
breach counts on that scenario owe part of their size to capacity bought for
nothing. Every sweep report on autoscaler 1.x carries both effects: absolute
cloud hours are inflated, and breach counts on the two-hour shape are flattered
by the leftover.

## Why nothing caught it

The rule was deliberate and documented — *a job that is already late is a
breach now* — and it is true of the queue. What nobody asked was what it did to
a search that treats "breach at every count" as "no count is enough". The
coldstart work (finding 003) had just taught the engine to tell an unavoidable
breach from an overload, and the test it used for "overload" was capacity
serving from the first instant — which a job already late fails too.

The example tests all used queues whose oldest job was inside its deadline.
Recorded runs showed it at once, but nobody had read the first minutes of one.

## The fix (autoscaler 2.0.0)

- A breach already in the observation is not judged: the projection starts at
  the first step. Late work still drives the requirement — it is served first,
  and the plan has to clear it before the work behind it goes late.
- An unavoidable breach is sized for the queue as it will be once capacity has
  arrived, backlog built up during the coldstart included
  (`SimulateOnceArrived`), and overloaded means even both caps, once started,
  cannot hold that queue.
- The reasoning names the levels already past their deadline.

## Guarded by

- `autoscaler/internal/policy/late_test.go`:
  `TestAJobJustPastItsDeadlineDoesNotSendTheEngineToTheCeiling` (cycle 11 at
  59 s and 65 s), `TestLateWorkIsStillScaledFor`,
  `TestALateBacklogBeyondBothCapsStillRunsFlatOut`, and the property
  `TestAQueueBothCapsCouldClearAtOnceIsNeverAnOverload`.
- `autoscaler/internal/policy/coldstart_test.go`:
  `TestAnUnavoidableBreachIsSizedForTheQueueAsItWillBeWhenCapacityArrives`.
- [Experiment 006](../experiments/006-cloud-bought-and-given-back), check one:
  a quiet start buys no cloud (1.1.0: 22 executor-hours).

## The general lesson

A predicate's edge case is a search's regime change. "Breach at elapsed zero"
was a harmless fact about one projection and a cliff for the binary search
built on top of it: six executors at 59 seconds, two hundred and fifty at 65.
When a search classifies by *whether any count works*, test the inputs where no
count can work for reasons that have nothing to do with capacity.
