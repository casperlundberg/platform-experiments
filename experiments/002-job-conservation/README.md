# 002 — Does a completed run account for every job it admitted?

**Status:** regression guard. Found a real defect; now protects the fix.

## The question

A run's whole purpose is to be evidence. Two runs of one scenario are compared
on two numbers — did it hold the SLA, and what did that cost — and the argument
only works if the runs replayed the same work and reported all of it.

So the most basic property is conservation: a run that reports `completed`
should have completed every job it admitted. A job that goes missing is
invisible twice over. It never completes, so it does not appear in the wait
statistics; and it never breaches, so **it makes the controller look better than
it was.**

## Why this is an experiment and not a unit test

There is a unit test for it now, in `simlab-api/internal/queue` — and it is the
better place for the fast feedback. But the property is about the *run*, which
is three components deep: the queue simulator, the autoscaler's decisions, and
the run engine that paces them. Only the assembled system decides how often
capacity actually drops while long jobs are in flight, and that is the state
that loses work.

The scenario here is chosen accordingly: repeated bursts with long jobs and
tight caps, so the controller is forced up and down repeatedly. A flat workload
would not reproduce anything.

## Method

One scenario, replayed under three policies — tight caps, generous caps, and
on-premise only. For each completed run, assert `jobs_completed ==
jobs_submitted`, and that breaches never exceed the jobs that existed. Then
assert all three admitted the identical number of jobs, since the seed is
supposed to fix the workload.

## Result

**It found a defect.** `queue.serve()` filtered its in-progress work in place
and stopped at the first interval where the executor budget ran out, discarding
every job it had not yet reached. Those jobs were neither completed nor
requeued — they left the simulation entirely.

It triggers whenever the fleet shrinks while more jobs are in flight than the
smaller fleet's budget covers, which is what every scale-down looks like.

The three-policy design is what makes the result legible. With the bug present:

| Policy | Admitted | Completed |
|---|---|---|
| Tight caps | 14288 | 14275 |
| Generous caps | 14288 | 14288 |
| On-premise only | 14288 | 14280 |

The generous run passes — it never has to scale down hard — which is exactly
why a single happy-path scenario had never caught this.

Breach counts moved too, in the direction that matters: 13798 → 13791 with the
bug, because a dropped job cannot miss a deadline. The controller was being
flattered.

Fixed in `simlab-api` by carrying the untouched tail forward, guarded there by
`TestWorkInProgressSurvivesAnIntervalTooSmallToTouchAllOfIt` and by the
property sweep `TestNoJobIsEverLostHoweverTheFleetChanges`.

## Running it

```bash
./run.sh
```

Needs Docker and Go, and the service repositories checked out alongside. Takes
a couple of minutes — three full replays. Exits non-zero if any check fails.
