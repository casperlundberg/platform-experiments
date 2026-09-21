## Reading

The dials of the decision itself, one at a time, against what autoscaler 2.0
ships: safety factor 1.15, a 15-minute horizon simulated in 15-second steps,
growth of up to 50 executors a decision with no cooldown, and a floor of one
local executor. Local cap 12, cloud cap 60.

**The horizon has to see past the deadlines it protects.** A 5-minute horizon
multiplied a workday's breaches by eight (16 → 132). Priority 50's deadline is
also 5 minutes, so a horizon that short likely sees such a job breach only once
capacity started for it would arrive too late. Under the bursts it did no harm
to breaches (−2 %, −8 %) but bought 11–30 % more cloud. 30 or 60 minutes cut
workday breaches by 22 %, for 22–36 % more cloud, and by 4–8 % under the
bursts. The horizon is a structural choice — at least the longest deadline
scaled for plus the slower coldstart — rather than a dial to turn.

**Headroom is the honest runtime trade.**

| Safety factor against 1.15 | 1.0 | 1.3 | 1.5 |
|---|---:|---:|---:|
| workday: breaches / cloud h | +115 % / −18 % | −23 % / +33 % | −31 % / +87 % |
| rock burst | +16 % / −12 % | −4 % / +18 % | −5 % / +43 % |
| earthquake | +18 % / −4 % | −8 % / +7 % | −14 % / +18 % |

No headroom costs breaches everywhere; more of it buys fewer, at a price that
falls as the burst grows — during a large burst the cap binds, and there is
less left to buy.

**Growing slowly only hurts.** A 5-minute scale-up cooldown multiplied workday
breaches by nine (+769 %) and added 20–23 % under the bursts; one minute cost
3–20 %. Limiting growth to 5 or 20 executors a decision changed little (0–2 %),
so a limit there rarely binds.

**The simulation step** matters only when coarse: 60 seconds added 7–25 % to
breaches, while 5 seconds took 2–6 % off for three times the arithmetic.

**Keeping every local executor on was the best single change.** A floor at the
local cap (12) took 60 % off workday breaches (16 → 6), 4 % under the rock
burst and 18 % under the earthquake, and cut the 95th-percentile wait by 7–37 %,
for 2–4 % more local executor-hours and 1–3 % less cloud. A floor of 0 instead
of 1 added 3–8 %.

**For a mine:** keep the horizon, step, growth limit and cooldown as shipped;
treat the safety factor as a runtime dial — 1.3 while a burst is under way —
and hold owned capacity rather than hand it back.

**Caveats.** Four seeds, one mine, intent off, one change at a time. Dials that
interact (horizon and coldstart, floor and local window) were not crossed.
