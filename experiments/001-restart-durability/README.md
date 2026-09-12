# 001 — Does a target survive a restart, and keep being scaled?

**Status:** regression guard. Found a real defect; now protects the fix.

## The question

The autoscaler keeps its registered targets in a file, because a service that
forgot its targets on restart would come back unable to scale anything. A
restart happens on every deploy, every node drain, every pod reschedule — so
anything that does not survive one is lost routinely, not rarely.

What has to come back is not just "a target with the same id". It is every
property the control loop reads: the platform, the config, the credentials, the
tuned settings, **and the mode** — because the runner cycles autonomous targets
and skips driven ones.

## Why this is an experiment and not a unit test

A unit test can check that `FileStore` round-trips a struct. It cannot check
that the thing which actually runs — the built binary, writing its real state
file, restarted for real, answering over HTTP — comes back the same. The defect
below lived underneath a passing unit suite precisely because the suite's own
restart test used a target whose mode was already the default.

## Method

Register a target, tune its settings, record what the API reports. Kill the
autoscaler process, start it again against the same state file, and ask the
same questions. Then ask about the mode separately, in the terms that matter.

## Result

**It found a defect.** `persistedTarget`, the on-disk shape, had no `Mode`
field. `Save` never wrote it; `Load` never restored it. Every target came back
with mode `""`.

Because the runner reads

```go
if snapshot.Target.Mode != platform.ModeAutonomous { continue }
```

an autonomous target came back **listed, healthy, with its settings and
credentials intact, and was never cycled again.** Nothing logs that. The
service's own headline capability — "it provisions autonomously" — silently
stopped working after any restart.

It never showed up in a simulation run because the `simulation` platform cannot
be autonomous: it cannot see its own queue. So this only ever bit real
infrastructure.

Fixed in `autoscaler` by persisting `Mode` on both sides, guarded there by
`TestAnAutonomousTargetIsStillAutonomousAfterARestart` and by
`TestEveryFieldOfATargetSurvivesARestart`, which compares the whole struct so
the next field added fails too.

## Running it

```bash
./run.sh
```

Needs Docker and Go, and the service repositories checked out alongside. Exits
non-zero if any check fails.

The autonomous half of the check needs a reachable ColonyOS server to register
against, which this harness does not stand up; where that is unavailable it
says so and defers to the unit test named above, which covers the same ground
without a server.
