## Reading

The first sweep that sets the deadline instead of observing it. Forty
encounters are scripted into each calibrated day: an event of Nuttli 2.5
placed a zone's radius ahead of where a unit's own track is taking it, timed so
that unit reaches the edge of the high-ground-motion zone exactly the stated
notice after the event happens. Each is scored for the unit it was scripted
for and no other. Everything else is the workday as before — and the day's own
735 turn-back decisions are scored beside them, unchanged across every arm,
which is the control.

**A decision needs about two minutes of notice. Below that, nothing the
platform does matters.**

| Notice | Budget after a 30 s reaction | In time: off → decay → oracle |
|---|---:|---|
| 30 s | ~0 s | 0 → 0 → 0 % |
| 60 s | 30 s | 31 → 31 → **48 %** |
| 120 s | 90 s | 90 → **97** → 99 % |
| 300 s | 270 s | 100 → 100 → 100 % |

At 30 s the reaction time eats the whole notice and every one of the 40
decisions is lost however fast the queue runs — the median first location comes
30–39 s after the event, and the decision has already closed. At 300 s every
decision is won by every arm. **The platform's ordering only decides anything
in between**, and that window is narrow: one to five minutes of notice.

**Where in that window ordering pays is not where knowing pays.** At 60 s,
decay is worth nothing at all (31 % either way) while the oracle — the same
ordering told which events matter — is worth 17 points. At 120 s decay is worth
7 points and the oracle 9. The reason is in the latencies: the median first
location moves 37.9 → 37.2 s under decay, but 30.0 s under the oracle. Decay
reorders by what it can infer; when the budget is 30 s, inferring wrongly costs
the whole decision.

**A warning is much harder than a location, at every notice.** Scored on a
location whose own zone, widened by the 50 m allowance, actually reaches the
unit:

| Notice | Warned in time: off → decay → oracle |
|---|---|
| 60 s | 20 → 18 → 28 % |
| 120 s | 62 → 70 → **84 %** |
| 300 s | 73 → 84 → **98 %** |

Even with five minutes' notice, a mine reading its own estimates warns the unit
in time three times in four; the same processing told the truth warns it
essentially always. That gap — 25 points at 300 s, 22 at 120 s — is the cost of
imperfect hypocentres, not of slow processing, and it is the same gap the
closure map measures in ground.

**Rerouting needs far more notice than turning back.** A unit can wait or take
another path only until the last junction before the zone, which it passes long
before it reaches the zone itself:

| Notice | Reroute in time | Decisions that could not be won |
|---|---:|---:|
| 30 s | 0 % | 40 of 40 |
| 60 s | 0 % | 34 of 40 |
| 120 s | 30–36 % | 21 of 40 |
| 300 s | **73–74 %** | 9.5 of 40 |

At two minutes' notice half the reroute decisions are already unwinnable — the
unit is past its last junction when the event happens. This is a property of
the tunnels, not of the platform: no processing speed recovers them, and the
only remedy is to know sooner, which means predicting rather than reacting.

**The control held.** The day's own 735 turn-back decisions score 93.4–94.4 %
in time in every arm, moving only with intent (93.4 off → 93.8 decay → 94.4
oracle) and not at all with the notice axis — as they should, since scripting
an encounter does not touch them. **And the cost is the usual one**: 14–16
breaches a day with intent off against about 1,480 under decay and 2,730 under
the oracle, on a day with capacity to spare.

**Caveats.** Four seeds, one mine, one magnitude (2.5, whose high zone reaches
about 140 m). The reaction time is fixed at 30 s and the window at 30 min; both
are assumptions, swept separately. The scripted unit follows its track whatever
is decided — the closed loop is still to come — so "in time" means the
information arrived, not that anybody acted on it.
