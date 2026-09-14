# The decision engine never read the coldstart it was configured with

**Found by:** reading the code against its own documentation, not by running
it. [Experiment 004](../experiments/004-coldstart-and-the-cloud-bill) was
written afterwards, as the system-level check — and found a second, smaller
gap of its own.
**Repository:** `autoscaler` · `internal/policy/simulate.go`,
`internal/policy/requirement.go`
**Severity:** the central claim was narrower than the prose around it. Optimistic
in the one situation that matters.

## What happened

`config.Settings` had `LocalColdstart` and `CloudColdstart`, defaulting to two
and five minutes, and the field comment said what they were for:

```go
// Coldstart is how long a newly requested executor takes before it can
// take work. It is what makes acting early rational.
LocalColdstart time.Duration
CloudColdstart time.Duration
```

Nothing in `policy` read them.

```
$ grep -rn 'Coldstart' internal/policy internal/controller internal/domain
  (no matches)
```

They were consumed by the `simulation` adapter, which ages its own fleet, and
by `config`, which validates and serialises them. That is all. `Simulate`
served the whole candidate executor count from the first step, and
`Capacity.AsPlan` folded pending executors into the count the projection ran
against — so ten executors requested ten seconds ago were modelled as ten
executors already doing work.

## Why it mattered

The question the engine answered was *what is the smallest executor count that
would avoid this breach if capacity were instant.*

That is not the question an SLA asks, and the gap between the two is widest
exactly during a ramp — which is the only time a scale-up decision matters. A
threshold rule was rejected for being unable to answer "will anything miss its
deadline"; the simulation could answer it, and then answered a different one.

It was also optimistic rather than pessimistic, which is the wrong direction
for a deadline. `Simulate(ramp)` breaches whenever `Simulate(instant)` does and
sometimes when it does not — now a property test
(`TestARampIsNeverMoreOptimisticThanInstantCapacity`).

The reasoning strings inherited it. "No breach predicted at 10 executors" was
printed for a fleet where none of the ten could take a job yet, and read
identically to the same sentence about ten working executors.

The frontend's own note — *"the gap between planned and ready is coldstart, and
that gap is the whole reason acting early is worth anything"* — was a true
statement about the chart and not about the model drawing the conclusions.

## Why nothing caught it

Nothing was wrong. Every test passed, `verify.sh` passed, and the numbers it
published were self-consistent. A setting that is declared, validated,
serialised, documented and read by nothing that decides anything does not fail
— it quietly narrows a claim, and no test asserts the absence of a term nobody
remembered should be there.

The one thing that would have caught it is a test comparing a ready fleet
against an identical pending one. There is now one, and it is the shortest
statement of the defect available:
`TestTenExecutorsStartingAreNotTenExecutorsWorking`.

## The fix

`Simulate` takes an `Availability` — what can serve now, and what joins once
its tier's coldstart has elapsed — rather than an executor count. Capacity
given back is immediate, since releasing an executor takes no provisioning. A
pending executor is charged its whole coldstart again, because an observation
reports how many are pending and never how long they have been; that is
pessimistic by at most one coldstart, in the only safe direction, and reporting
pending ages from the adapters would remove it.

**And a second change the first one forced.** Once capacity arrives late, "no
executor count avoids this breach" stops being exceptional — any cold pool
facing a deadline shorter than its coldstart is in that state. The old response
to it was to run flat out at both caps, which would have spent the entire cloud
budget every time a quiet pool woke up, against a breach already committed
before the decision was taken. `Required` now distinguishes:

| Outcome | What it means | What it asks for |
|---|---|---|
| `Achievable` | Some count inside the caps avoids every breach | That count, plus headroom |
| `Unavoidable` | Nothing can start inside the deadline | What the queue needs once capacity arrives |
| `Overloaded` | Arrivals outrun both caps serving from the first instant | The ceiling |

Getting that distinction wrong in either direction is worse than the original
defect, so it has tests on both sides: a cold pool must not reach for the
ceiling, and a genuine overload must still get there.

## Guarded by

- `autoscaler/internal/policy/coldstart_test.go` — the ramp's effect on a
  decision, the three outcomes, and the reasoning that explains each.
- `autoscaler/internal/policy/availability_test.go` — the ramp itself: per-tier
  coldstarts, scale-down being immediate, pending not counted as throughput.
- `autoscaler/internal/policy/property_test.go` — that a ramp is never more
  optimistic than instant capacity, and that avoiding a breach stays monotone
  in the executor count. The second was the binary search's precondition, until
  now argued only in a comment.
- [Experiment 004](../experiments/004-coldstart-and-the-cloud-bill) at the
  system level.

Every one of those was checked by reintroducing the behaviour it guards
against, which is the only way to know a passing test is doing anything.

## The general lesson

A settings field is not a feature. This one was declared with a comment saying
why it mattered, validated with a message explaining what a bad value would
do, given a place on the wire, rendered in a form, and documented in the
OpenAPI spec — the whole apparatus of a real setting, around a number that
changed no decision.

The cheap check is mechanical and worth running against any knob that claims
to matter: **grep for it in the package that is supposed to use it.** That is
all this took.
