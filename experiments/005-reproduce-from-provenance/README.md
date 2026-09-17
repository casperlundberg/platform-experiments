# 005 — Can a run be reproduced from nothing but what it recorded about itself?

**Status:** regression guard. Passes: a run replays identically from its
provenance alone, even after its scenario was edited.

## The question

A result is evidence only if someone else can produce it again. For a run that
takes two services, a database and a seeded workload, that needs three things:
the exact code of both services, the exact inputs, and a replay that is
deterministic given both.

Each run records its **provenance** as it begins: both services' builds
(semantic version, full commit, whether the tree was modified, Go version and
platform), the mine and scenario copied as they were, the autoscaler's whole
effective settings, and the intent the mine was to reorder its work by. Changes
to intent while the run is in flight — planned, or made by hand — are recorded
with the cycle they took effect from, and are replayed as a schedule. The question is whether that is *enough* — whether a run
can be rebuilt and replayed from the provenance, with nothing taken from the
current state of any database or repository.

## Why this is an experiment and not a unit test

Each part has its tests where it lives: `simlab-api` tests that a run records
its provenance (`TestARunRecordsItsProvenanceAsItBegins`) and says in words why
one is not reproducible (`TestAProvenanceIsReproducibleOnlyFromCleanCommitsOfBothServices`);
the workload's determinism is pinned by
`TestGeometryChangesNotOneJobOfAnExistingScenario`. None of them can show that
the recorded provenance is *sufficient*: that needs two separate builds, two
databases, and a comparison of everything a run records. Only the assembled
system can answer it.

## Method

1. Build both services from their last commits, in clean worktrees, so the
   provenance names commits that exist.
2. Record a run of a scenario that uses every dial a replay must carry: a burst
   with a stated main shock, pick error, and a workforce; intent that both
   decays and promotes, a change to it planned for a later cycle, and a change
   made by hand through the API while the run is in flight.
3. **Edit the scenario afterwards**, as a person tidying up would. A
   reproduction that read the scenario instead of the provenance would now
   replay different work.
4. Run `lib/reproduce.sh` on the run: it reads the provenance, checks out both
   commits, builds them with the recorded Go toolchain, starts them against a
   fresh database, recreates the recorded mine and scenario, replays under the
   recorded settings and intent, replaying every recorded intent change at the
   cycle it took effect from, and compares metrics, every cycle, every seismic
   event, every track and every intent change.
5. **Show the comparison can fail:** change one cycle's plan in a copy of the
   results and check the comparison finds it and names where.
6. Build `simlab-api` with an uncommitted file in its tree, record a run, and
   check reproduction **refuses** it, naming the modified build — rather than
   rebuilding the commit and claiming a reproduction of code that never ran.

## Result

```
✓ the original recorded its planned and its hand-made intent change
✓ the run was rebuilt at its commits and replayed identically
    SAME    metrics (16 fields)
    SAME    cycles (1765 rows)
    SAME    seismicity (173 rows)
    SAME    entities (11 rows)
    SAME    intent (2 rows)
✓ a single changed plan is found and named
✓ refused, naming the modified build
```

The first run with intent failed, and was right to. The hand edit landed before
the run's first cycle, so the intent the run was created with never took effect
and the edit was the first change recorded; reproduction took "every change
after the first" as the schedule and dropped the edit. The replay disagreed
from cycle 0 (`intent.version: recorded 2, replayed 1`). The schedule is now
every change after version 1.

The replay matches to the last field: the queue, every autoscaler decision,
every seismic location and magnitude, every person's and vehicle's track, and
every change of intent with the cycle it took effect from.

## Reproducing a run of your own

```bash
make reproduce RUN=run-w4fi4c2o-0sm7m5za     # a run on the deployed platform
SOURCE_URL=http://127.0.0.1:8081 SOURCE_TOKEN= make reproduce RUN=...   # any other
```

It exits zero only if the replay is identical, and otherwise reports the first
field where the two runs part ways. A run recorded before provenance existed, a
live run, or one from a modified build is refused with the reason.
