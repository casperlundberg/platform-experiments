## Reading

Use case 2, asked of the calibrated days. Not "was this decision made in time"
but "**is the picture right**": take every location the mine had at a moment,
draw each one's zone, and compare the closed ground with the ground the events
really made dangerous. Measured over the tunnels in metre-seconds — so many
metres of drift shut for so many seconds — with each event's ground dangerous,
and its zone closed, for 30 minutes. Four maps are drawn of every run, which
costs nothing: at moderate and at high ground motion, each as the run's own
locations drew it (the mine's 50 m allowance) and again with 150 m more.

**Location error decides whether the map covers the ground. Processing does
not.** On the workday, at the moderate level, as drawn:

| Pick error | Dangerous ground closed | Of what was closed, needlessly | Mine shut, on average |
|---|---:|---:|---:|
| 5 ms | 89 % | 64 % | 25 % |
| 20 ms | 62 % | 69 % | 20 % |
| 50 ms | **37 %** | 75 % | 15 % |

Tripling the pick error halves what the map covers, and the mine is shut *less*
— it closes the wrong ground, not more ground. This is the pick-jitter
sweep's finding in the terms an operator would use: a fixed allowance stops
describing the hazard once picks get noisy, and what it then closes is mostly
somewhere else.

**Even at its best the map is mostly needless closure.** At 5 ms — the
calibrated day, the array as installed — a quarter of the mine is shut on
average and 64 % of that closure was never over dangerous ground. The mine's
own 50 m allowance is what buys the 89 %.

**Covering everything means closing everything.** With 150 m more allowance:

| | Dangerous ground closed | Mine shut, on average |
|---|---:|---:|
| moderate, as drawn | 89 % | 25 % |
| moderate, +150 m | 99 % | **85 %** |
| high, as drawn | 69 % | 5 % |
| high, +150 m | 98 % | **69 %** |

There is no allowance that both covers the hazard and leaves a mine to work in.
The way out of that trade is a better location, not a wider circle — which is
what a per-location allowance (the residual each estimate already carries) is
for, and the reason it is the open item on case 2.

**Decay improves both sides of the map.** Unlike its effect on breaches, where
it buys cloud at the cost of harmless work missing deadlines, ordering the
queue by intent makes the picture strictly better — it covers more and closes
less needlessly, because the events that endanger someone are located sooner:

| Moderate, off → decay | Ground covered | Needless closure | Events never covered whole |
|---|---|---|---|
| workday, 5 ms | 89 → **92 %** | 64 → 63 % | 99 → 69 |
| workday, 20 ms | 62 → **69 %** | 69 → 64 % | 415 → 378 |
| workday, 50 ms | 37 → **41 %** | 75 → 71 % | 664 → 630 |
| earthquake, 5 ms | 86 → **88 %** | 44 → 44 % | 134 → 99 |
| earthquake, 50 ms | 63 → **67 %** | 51 → 49 % | 546 → 490 |

**A busy day's map is better, not worse.** Case 2 was written expecting the
opposite — that overlapping zones would hide an estimate badly out behind one
that is right. They do hide it, and that *helps*: on the earthquake day half of
all events have their dangerous ground already closed **at the moment they
happen** (median time to a complete map: 0 s, against 34 s on the workday),
because a neighbour's zone is already over it. Coverage at 50 ms pick error is
63 % on the earthquake day against 37 % on the quiet one, and needless closure
is 51 % against 75 %. Where events cluster, the union is forgiving.

**How long the map takes to be right.** Median 34 s on the workday at 5 ms, but
the 95th percentile is 806–923 s, and 1,400–1,600 s once pick error grows. A
map that is right for half the events within a minute is wrong at its edges for
a quarter of an hour.

**The high level, where the decisions matter most, is barely covered at all on
a quiet day**: 69 % at 5 ms, 19 % at 20 ms, 8 % at 50 ms — a zone tens of
metres across cannot survive a location tens of metres out, and 99.6 % of what
is closed at that level was never dangerous. On the earthquake day, where big
events make big high zones, it holds up: 81 → 75 → 58 % across the same pick
errors. **The quiet day's high-level figures come from a handful of events**
(per-seed coverage ranges from 0.0 to 0.22 at 50 ms), which is exactly why
scripted encounters exist.

**Caveats.** Four seeds, one mine. The map assumes the mine closes exactly the
zones its locations drew, for 30 minutes, and re-opens: no re-entry protocol
(case 7), no operator judgement. "Needless" means the true zone never reached
that ground, which is not the same as safe — aftershocks are not counted
against it. The allowance in the recorded zones is intent's own 50 m; a
per-location allowance is not yet built.
