# Work in progress was dropped on every scale-down

**Found by:** [experiment 002](../experiments/002-job-conservation), and
independently by a property sweep written while investigating it.
**Repository:** `simlab-api` · `internal/queue/queue.go` · `serve()`
**Severity:** results-corrupting. Flattered the controller in published numbers.

## What happened

`serve()` filtered its in-progress work in place:

```go
stillRunning := s.running[:0]
for _, item := range s.running {
    ...
    stillRunning = append(stillRunning, item)
    if budget <= 0 {
        break          // <- everything not yet reached is now unreachable
    }
}
s.running = stillRunning
```

`stillRunning` aliases `s.running`'s backing array. On `break`, the assignment
truncates the slice to what had been visited, and every job after that point
left the simulation — neither completed nor requeued.

## When it fired

Whenever the executor budget for an interval was smaller than the work already
in progress: that is, whenever the fleet shrank while long jobs were running.
Every scale-down, in other words — the ordinary case, not an edge case.

A worked example: ten long jobs are picked up by ten executors, the controller
then drops to one, and the single executor's budget reaches only the first.
Nine jobs disappear.

## Why it mattered more than it looks

A dropped job is invisible in both directions. It never completes, so it is
absent from the wait statistics; and **it never breaches**, because breaches are
counted against jobs that are still waiting. So the defect quietly improved the
controller's reported SLA performance.

It also let `Done()` return true with `Completed < Submitted`, so a run could
finish "successfully" having lost work, and `BreachRate` — which divides by
completed, not submitted — could in principle exceed 1.

The effect on the published figure was small but real and in the flattering
direction: the on-premise-only run in `platform-deploy/verify.sh` moved from
10689 breaches to 10690 once jobs stopped vanishing. Under the tighter caps of
experiment 002, 13 of 14288 jobs were lost.

## Why nothing caught it

Every example test in `internal/queue` either kept capacity constant or only
raised it. The one scenario that loses work — capacity falling while long jobs
are in flight — was never written, because nobody thinks to write it.

`verify.sh` did not catch it either: it checks that both runs replayed the
*same* number of jobs, and both lost jobs, so the comparison still balanced.

## The fix

Carry the untouched tail forward rather than truncating it.

## Guarded by

- `simlab-api/internal/queue/queue_test.go` —
  `TestWorkInProgressSurvivesAnIntervalTooSmallToTouchAllOfIt`, the minimal
  worked case.
- `simlab-api/internal/queue/property_test.go` —
  `TestNoJobIsEverLostHoweverTheFleetChanges`, a randomised sweep over 400
  trials with the executor count jumping around. Confirmed to fail against the
  original code.
- [Experiment 002](../experiments/002-job-conservation) at the system level.
