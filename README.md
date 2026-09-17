# platform-experiments

Experiments against the assembled autoscale platform: questions that only the
whole system can answer, and the findings they produced.

One of five repositories checked out side by side — `autoscaler`, `simlab-api`,
`simlab-web`, `platform-deploy`, and this one.

## What belongs here, and what does not

The rule is about **what owns the property being checked**, not about how big
the test is.

| | Where it goes |
|---|---|
| A property of one repository's code | A test in that repository |
| A property of the deployment contract | `platform-deploy/verify.sh` |
| A property of the assembled system | Here |

So:

- **A test on code stays with the code.** `queue.serve()` must not drop work —
  that is a fact about `simlab-api`, and it is tested in `simlab-api`, where it
  runs in a second and fails the build that broke it. Moving it here would make
  it slower, later, and someone else's problem.
- **`verify.sh` stays in `platform-deploy`.** It is that repository's own proof
  that the deployment contract it publishes actually holds, and its CI gates on
  it. It is a gate, not an investigation.
- **An experiment belongs here** when the question is about the system rather
  than about any one part of it: what happens across a restart, whether a run's
  results are internally consistent, whether a promise about concurrency
  survives real concurrency. These need real binaries, a real database, and
  services genuinely talking to each other — and their output is *evidence*,
  not a pass mark.

The two are not in competition. Several experiments here found a defect, and
the fix was then guarded by a fast unit test in the repository that owned it.
The experiment stays as the system-level check; the unit test is what fails
first. Each experiment's README names the tests that guard its finding.

## Layout

```
experiments/NNN-short-name/
├── README.md    the question, the method, the result
└── run.sh       the experiment, exiting non-zero if a check fails
findings/        write-ups of what was found, one per defect
lib/harness.sh   builds and starts the stack; shared assertions
lib/reproduce.sh rebuilds a recorded run's code and replays it (make reproduce)
lib/results.py   fetches a run's results and compares two runs field by field
```

Experiments are numbered in the order they were written and are not renumbered,
so a finding can cite one by number and keep citing it.

## Running them

```bash
make list        # what is here
make all         # every experiment, in order
make run N=001   # one of them
```

Needs Docker and Go, and the four sibling repositories checked out alongside.
`AUTOSCALER_DIR` and `SIMLAB_DIR` override where they are looked for;
`POSTGRES_URL` reuses a database instead of starting one.

The harness runs on its own ports (18290, 18291, 15434) so an experiment can
run while a development stack or `verify.sh` is up.

## Reproducing a run

Every run records its provenance as it begins: both services' semantic
versions, commits, whether their trees were modified, Go versions and platform,
and copies of the mine, scenario and effective settings it was given. The
database is tied to the code by commit hash; nothing about the data is checked
in.

```bash
make reproduce RUN=<run-id>
```

checks out both services at the recorded commits, builds them with the recorded
Go toolchain, replays the run from its provenance on a fresh database, and
compares every metric, cycle, seismic event and track with the original. It
exits zero only on an identical replay, and refuses — with the reason — a run
that cannot be reproduced: one from before provenance, a live run, or one from a
build with uncommitted changes. By default it reads the deployed platform
through `platform-deploy/scripts/simlab-env.sh`; `SOURCE_URL` and
`SOURCE_TOKEN` point it anywhere else. Experiment 005 is the proof that this
works, and that it can fail.

Versions are cut in each service repository with `make release
VERSION=x.y.z`; see the "Versions" section of each README for what a MAJOR,
MINOR or PATCH release promises.

## Sweeps and reports

An experiment checks a property and passes or fails. A **sweep** measures: it
runs every combination of its axes — intent, autoscaler settings, scenario
changes — on every seed, and writes a report to read.

```bash
make sweep S=intent-modes   # one sweep
make sweeps                 # all of them
make report S=intent-modes  # rewrite a report from what was recorded, e.g. after editing its reading
```

```
docs/calibration.md  how the workday mine was fitted to an operational catalogue
sweeps/NAME.json   the definition: mine, scenario, settings, intent, seeds, axes, baseline
sweeps/NAME.md     the reading: what the numbers say, written by a person, kept with the definition
reports/NAME/      what the sweep produced
  report.md        the tables, the reading, and how to regenerate them
  runs.csv         every run, every measured column
  sweep.json       the definition as it was run
  provenance.json  both services' builds, this repository's commit, the digest of runs.csv
```

Both services are built from clean checkouts of each repository's committed
HEAD, never the working tree, so a report can say truthfully which code
produced every number. Everything is deterministic in the commits and the
definition: rerunning a sweep at the same commits reproduces `runs.csv` byte for
byte, which its recorded digest lets anyone check. Reports hold aggregates of
simulated runs only.

Each definition pins the whole intent it starts from, so a later change to a
default cannot quietly change what an arm means. A baseline may name only some
axes: each arm is then compared with the baseline on those axes and its own
labels on the rest — intent against no intent at the same cloud cap, say.

[`reports/README.md`](reports/README.md) lists the reports and what each found.
One mine and one day in them are fitted to a real pipeline's records rather than
chosen: [`docs/calibration.md`](docs/calibration.md) says how, in aggregates.
That extract lives outside every repository and stays there.

## Writing one

Start from the question, not the code. An experiment that cannot say what it
would mean for the answer to be "no" is not yet an experiment.

Then, in order:

1. **Write the README first** — the question and the method. If the method does
   not obviously distinguish a healthy system from a broken one, fix that
   before writing any script.
2. **Make it fail on purpose.** Revert the fix, or break the thing deliberately,
   and confirm the experiment says so. An experiment never seen to fail is not
   evidence of anything. Every finding in `findings/` was confirmed this way.
3. **Establish the invariant before observing it.** The first version of 003
   reported its own setup as a defect; see that README.
4. **Never use a bare `wait`.** The harness runs the services as background
   jobs of your shell, so a bare `wait` hangs on them. Collect PIDs.
5. **Record the result either way.** "No defect found" is a result, and 003 is
   kept for exactly that reason — the next person to doubt the compare-and-swap
   should find out it has been checked.
