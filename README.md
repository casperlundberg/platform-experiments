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
