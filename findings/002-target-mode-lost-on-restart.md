# Autonomous targets silently stopped being scaled after a restart

**Found by:** [experiment 001](../experiments/001-restart-durability)
**Repository:** `autoscaler` · `internal/registry/store.go`
**Severity:** silent production outage of the service's primary function.

## What happened

`persistedTarget`, the on-disk shape of a registered target, had no `Mode`
field. `Save` never wrote it and `Load` never restored it, so every target came
back from a restart with `Mode == ""`.

The runner reads:

```go
if snapshot.Target.Mode != platform.ModeAutonomous {
    continue
}
```

so a target registered as `autonomous` came back as neither — and was skipped
forever.

## Why it mattered

The autoscaler's stated purpose is that it "provisions autonomously": a target
is registered with the keys for its platform and from then on the controller
adds and removes replicas on its own.

After any restart, that stopped. The target was **still listed, still healthy,
still holding its credentials, still reporting its tuned settings** — and never
cycled again. Nothing logs it. Nothing reports it. The only symptom is that the
workload stops being scaled, which looks like a workload problem, not a
controller problem.

Restarts are not rare: a deploy, a node drain, a pod reschedule, an OOM kill.

## Why nothing caught it

Three things lined up.

1. The existing restart test used a `simulation` target, whose mode is the
   default — so a dropped mode was indistinguishable from a preserved one.
2. Named-field assertions. The test checked the settings and the credentials
   came back, which they did. Nobody names a field they have forgotten exists.
3. `simulation` cannot be autonomous — it cannot see its own queue — so no
   simulation run and no part of `verify.sh` ever exercised autonomous mode.
   The defect only ever bit real infrastructure.

## The fix

Persist `Mode` on both sides of the store.

## Guarded by

- `autoscaler/internal/registry/registry_test.go` —
  `TestAnAutonomousTargetIsStillAutonomousAfterARestart`, the specific case.
- `autoscaler/internal/registry/registry_test.go` —
  `TestEveryFieldOfATargetSurvivesARestart`, which refuses a fixture with any
  zero field and then compares the whole struct, so the *next* field added to
  `Target` fails here rather than in production.
- [Experiment 001](../experiments/001-restart-durability) at the system level.

## The general lesson

This is a class, not an incident: **a round-trip test that names fields can only
catch the fields someone remembered.** The same class was then swept for
deliberately elsewhere — `simlab-api/internal/store/roundtrip_test.go` now does
the whole-struct comparison for stored cycles and metrics, and found them
sound.
