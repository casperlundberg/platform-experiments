# 004 — When no executor count avoids the breach, what does it ask for?

**Status:** standing check. Found a reporting gap of its own; guards both.

## The question

The engine simulates a candidate executor count and looks for the smallest one
with no predicted breach. Coldstart makes that question sharper than it sounds,
because an executor that has been requested is not an executor that is
working: on the cloud tier it is minutes away.

So for a cold pool facing a deadline shorter than its coldstart, **there is no
executor count that avoids the breach.** Nothing can start in time. That is
not an edge case — it is every quiet pool waking up.

What the controller does about it is the whole question, and there are two very
different right-looking answers:

1. Ask for what the queue needs once capacity has arrived.
2. Ask for everything, on the grounds that nothing was enough.

The second is what an engine gets if it treats "no count is sufficient" as an
overload. It is also ruinous: both tiers to their caps, every time a pool wakes
up, against a breach that was already committed before the decision was taken.
The cloud tier is billed by the minute.

This experiment asks the assembled system which it does, and checks that the
distinction has not collapsed in either direction — that a genuine overload
*does* still run flat out.

## Why it is not a unit test

It is, and it should be: `autoscaler/internal/policy/coldstart_test.go` covers
the three outcomes directly, and `property_test.go` sweeps them. Those are
faster and they fail the build that breaks them.

What they cannot do is answer the question about the thing that runs. The
executor counts here come out of a cycle taken over HTTP, against settings read
from the live versioned store, through the real platform adapter, with the
coldstarts configured the way an operator would configure them. Every one of
those is a place the pure function's answer could fail to reach the wire — and
the defect this guards was itself exactly that shape: a setting that existed,
was validated, was serialised, and was read by nothing that decided anything.

## Method

One `simulation` target, generous caps (20 local, 200 cloud) so that "ask for
everything" would be unmistakable, and coldstarts an operator would recognise
— 2 minutes local, 5 minutes cloud.

- **A cold pool against a tight deadline.** Nothing running, P100 already 55s
  into its 60s deadline. No count can avoid the breach. Check the plan is a
  handful of executors and not the 220 the caps allow, that the reasoning says
  the breach was unavoidable and names coldstart, and that the projection still
  reports the breach — unavoidable is not absent.
- **The same queue, a deadline beyond the coldstart.** Now capacity can arrive
  in time, so this must read as an ordinary requirement again, and must still
  stay on the local tier: cloud is overflow, not a first resort.
- **A genuine overload.** Arrivals far past what both caps can serve from the
  first instant. This one *must* run flat out — coldstart must not have
  swallowed the case the ceiling exists for.
- **Capacity that is starting is reported as starting.** On a second target, so
  the fleet has a history of exactly one cycle rather than three sections of
  it: cycle once from cold so the engine asks for capacity, then cycle the same
  observation again, when that capacity exists but cannot have finished a
  two-minute coldstart. The decision has to say how much of its fleet cannot
  work yet. This is a check on reporting rather than on the model — see below,
  because that distinction is the one thing writing this experiment taught.

## Result

**No defect found in the running system**, once the engine modelled the ramp.

```
✓ asked for 4 executors, not the 220 its caps allow
✓ the reasoning says the breach was unavoidable
✓ and it names coldstart as the reason
✓ the projection still reports the breach
✓ with room before the deadline it is an ordinary requirement again
✓ and it stayed on the local tier
✓ a genuine overload still runs flat out at both caps
✓ capacity that cannot work yet is reported as starting, not as throughput
✓ and it says how much: all 1 of them
```

Four since autoscaler 2.0.0, which sizes an unavoidable breach for the queue
as it will be once capacity has started — the backlog that builds during the
coldstart included — rather than the queue as it stood; 1.x asked for two.

It did find one thing, on its first run: the unavoidable branch of the
reasoning did not say how much capacity was already starting. It reported
giving up beside a fleet of 220 executors, every one of them still pulling an
image — which reads as a bug rather than an explanation, on precisely the
branch an operator is most likely to want to argue with. Fixed, and guarded by
`autoscaler/internal/policy/coldstart_test.go` —
`TestAnUnavoidableBreachSaysHowMuchCapacityIsAlreadyStarting`.

## Making it fail on purpose

An experiment never seen to fail is not evidence. Make the engine ignore the
ramp, which is the model as it was:

```go
// internal/policy/simulate.go
remaining := float64(available.Total()) * throughput * step.Seconds()
```

Three checks fail: the breach stops being reported as unavoidable, coldstart
stops being named, and the projection stops predicting the breach at all —
because with every requested executor serving from the first step, there is a
count that avoids it, and the engine believes it has found one.

To see the expensive failure, revert `Required`'s `Unavoidable` branch so that
"no count avoids it" means the ceiling again. The first check then reports a
cold pool asking for 220 executors.

## What writing it taught

**Two of these checks do not test the model, and it took a mutation to notice.**

The last pair look like the sharpest checks here — the same observation, once
with capacity ready and once with it starting. They are not, because the
"(n still starting)" annotation is read straight off the observation's pending
count. It survives the mutation above intact: an engine with no ramp at all
still reports the fleet honestly and then ignores what it reported.

So they guard something real but narrower than they appear — that the pending
count reaches the operator — and the checks that guard the *model* are the
three about the unavoidable branch. Worth writing down, because the first
version of this experiment had the comparison as its headline check and would
have passed against the original defect.

The other lesson is duller and cost more time: the pending-capacity section now
uses **its own target**. On the first target it inherited the overload
section's fleet of 220 and the scale-down step limit that follows it, so the
plan read 215 while the reasoning said 5 — both correct, and completely
unreadable as a check. A check whose setup is three sections of history is a
check nobody can debug.

## Running it

```bash
./run.sh
```

Needs Docker and Go, and the service repositories checked out alongside. Exits
non-zero if any check fails.
