# Breaches were counted at the wrong moments, both too few and too many

**Found by:** a property test, when a second count of breaches was added. Intent
moves jobs between levels, so the queue started counting each job also against
the deadline of the level it was *submitted* at. Without intent the two counts
must be identical, and a property test saying so
(`TestWithoutReprioritisationBothBreachCountsAgree`) failed on its first trial:
106 against 103.
**Repository:** `simlab-api` · `internal/queue/queue.go`
**Severity:** every recorded `sla_breaches` before simlab-api 2.0.0 is off, in
both directions, by an amount that depends on job length. Comparisons between
runs of one version stood; absolute breach counts did not.

## What happened

A breach is a wait longer than the deadline. The queue measured it in two
places, once per interval, after serving:

1. every job **still waiting**, whose age had passed its deadline; and
2. every job **running**, whose age since submission had passed its deadline.

The first missed jobs. An executor that picked up a job already past its
deadline and finished it inside the same interval removed it from both lists
before anything looked: a short job, late, was never late. Jobs shorter than
the 15-second interval are about a quarter of the workload.

The second over-counted. A job picked up in time is not late however long it
then runs, but a five-minute job started ten seconds after arriving became a
breach once it had been running for a minute. Its comment described the case it
was meant for — *"an executor picking a job up after its deadline has already
missed it"* — and its test measured something else.

## Why nothing caught it

Every test of breaches asserted a count for a scenario someone had worked out by
hand, and every one of those scenarios had jobs longer than the interval and
executors too few to start anything late. Nothing tied breaches to the one
quantity they are defined by: the waiting time the queue already recorded for
every job, and reported in `mean_wait_seconds` and `p95_wait_seconds`. Two
numbers derived from the same wait were never compared.

The class: **a quantity counted by sampling state at intervals, where the thing
counted can begin and end between samples.** The fix for that class is to count
at the event — here, the moment a job starts — rather than at the sample.

## The fix

A job's breach is settled when it starts: its wait is known then and cannot
change, and running jobs are no longer judged at all. Jobs still waiting are
still counted each interval, so the timeline shows lateness while it happens.

Without intent, verification's cloud-burst run went from 1,452 breaches to
1,498, and its on-premise run stayed at 10,722. Breaches reach nothing the
autoscaler decides from, so decisions, cloud hours and waits were unchanged;
only the breach counts, in total and per cycle, moved.

## What guards it

- `TestAShortJobThatStartsAfterItsDeadlineIsStillABreach`
- `TestALongJobPickedUpInTimeIsNotABreach`
- `TestWithoutReprioritisationBothBreachCountsAgree`, the property that found it:
  300 random workloads, in which the count against each job's own level and the
  count against its submitted level must agree exactly when nothing moves.
