# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Experiments against the assembled autoscale platform, and the findings they
produced. One of five repositories checked out side by side (`autoscaler`,
`simlab-api`, `simlab-web`, `platform-deploy`, `platform-experiments`).

## What belongs here

Decide by **what owns the property**, not by how big the test is:

- A property of one repository's code → a test in that repository.
- A property of the deployment contract → `platform-deploy/verify.sh`.
- A property of the assembled system → here.

`verify.sh` is a gate and stays where it is; experiments here are
investigations whose output is evidence. When an experiment finds a defect, the
fix gets a fast unit test in the repository that owns the code, and the
experiment stays as the system-level check. Each experiment's README names the
tests guarding its finding — keep that link current.

Do not move a passing unit test here to "make it end-to-end". It would run
slower, later, and stop failing the build that broke it.

## Commands

```bash
make list        # every experiment, its question and status
make all         # run them all in order; non-zero if any fails
make run N=001   # run one
make lint        # shellcheck (CI runs this; it may not be installed locally)
```

Needs Docker and Go and the sibling repositories. `AUTOSCALER_DIR`,
`SIMLAB_DIR` relocate them; `POSTGRES_URL` reuses a database. The harness uses
ports 18290/18291/15434, deliberately distinct from `verify.sh` and from a
development stack, so experiments can run alongside either.

## Writing an experiment

```
experiments/NNN-short-name/
├── README.md    the question, why it is not a unit test, the method, the result
└── run.sh       sources lib/harness.sh, exits non-zero on any failed check
```

Numbers are assigned in order and never reused, so findings can cite them.

Rules that came from getting these wrong:

- **Write the README first.** If the method cannot distinguish a healthy system
  from a broken one, that is a problem with the experiment.
- **Make it fail on purpose before trusting it.** Revert the fix and confirm it
  reports the defect. Both findings here were confirmed that way, and an
  experiment never seen to fail is not evidence.
- **Establish the invariant before observing it.** 003's first version reported
  its own setup as a torn read.
- **Never use a bare `wait`.** The harness runs the services as background jobs
  of your shell; a bare `wait` hangs on them. Collect PIDs and wait on those.
- **Record "no defect found" too.** 003 is kept for that reason.

## The harness

`lib/harness.sh` is sourced, not executed. `harness::start` builds both
binaries, starts Postgres and both services, and tears everything down on exit.
`harness::stop_autoscaler` / `harness::start_autoscaler` restart the autoscaler
against the same state file, which is what restart experiments need.

Assertions go through `harness::expect <what> <actual> <expected>`, which
records a failure rather than aborting, so one experiment reports every problem
it found in a single run. End with `harness::finish`, which sets the exit
status.

## Findings

`findings/NNN-*.md`, one per defect: what happened, when it fired, why it
mattered, why nothing caught it, the fix, and what now guards it. The "why
nothing caught it" section is the load-bearing one — both findings so far came
from a whole class of blind spot rather than a one-off slip, and naming the
class is what stops the next one.
