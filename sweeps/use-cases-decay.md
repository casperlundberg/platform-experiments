## Reading

The first time decay is measured against the decisions it is for rather than
against the queue. The three calibrated days on autoscaler 2.0.0 and
simlab-api 4.0.0-dev, where the mine knows where people are but not where they
will walk; each run scored for every decision of three kinds over an event's
true moderate zone: **turn-back** (a unit about to enter the zone must be told
before it does), **way-out** (one inside it must be told before it would have
left anyway) and **reroute** (one heading in must be told before the last
junction on the way). Each is scored twice: waiting on the event's **first
location**, and on a **warning** — the first location whose own zone, widened by
the 50 m allowance for location error, reaches the unit. The window (30 min
after the event) and the reaction time (30 s) are assumptions. The world is the
same in every arm: 735 turn-back decisions on the workday, 769 under the rock
burst and 1,140 under the earthquake, per day.

**Any location usually arrives in time, even with no intent.** The median first
location comes 36–38 s after the event, and a unit reaches a zone minutes later.

| Share in time: off → decay → oracle | turn-back | way-out | reroute |
|---|---:|---:|---:|
| workday | 93 → 94 → 95 % | 68 → 70 → 70 % | 83 → 84 → 83 % |
| rock burst | 92 → 94 → 95 % | 73 → 74 → 76 % | 83 → 84 → 84 % |
| earthquake | 85 → 89 → 94 % | 73 → 77 → 86 % | 76 → 80 → 83 % |

Decay helps where contention makes the tail late: under the earthquake it gets
four more turn-back decisions in a hundred their location in time, five more
reroutes and four more ways out. The oracle's ceiling is the same ordering
told the truth; it doubles those gains. Way-out stays lowest because a unit
already inside a zone often leaves within a minute, and reroute cannot rise
above what the tunnels allow: 13 % of reroute decisions come after the unit's
last junction and cannot be won by any processing.

**A location good enough to warn is much rarer in time, and there decay does
more.**

| Share in time, warned: off → decay → oracle | turn-back | way-out | reroute |
|---|---:|---:|---:|
| workday | 70 → 77 → 91 % | 58 → 61 → 68 % | 63 → 68 → 78 % |
| rock burst | 67 → 72 → 90 % | 60 → 63 → 74 % | 60 → 64 → 77 % |
| earthquake | 58 → 64 → 85 % | 62 → 67 → 83 % | 52 → 57 → 74 % |

A first location from four or five picks is often too far out for its zone to
reach the unit, and the warning waits for the final location — which is where
ordering matters: decay adds five to seven decisions in a hundred on every day,
and the oracle twenty more. **The gap between decay and the oracle is the
finding.** With locations good enough to act on as the measure, decay from the
mine's own estimates recovers about a quarter to a third of what perfect
knowledge of which events matter would (turn-back under the earthquake: 58 →
64 % against 85 %). What stands between is knowing sooner which events those
are, and how accurately they are located — not how fast processing is.

**Machines** (turn-back for the autonomous fleet only, use case 10) follow the
same pattern: 82 → 87 → 93 % under the earthquake.

**At what price.** The same arms' breaches and cloud time are the decay
findings already reported: on the quiet workday decay costs breaches (16 →
1,435 a day) for 15 % less cloud; under the earthquake it cuts breaches by a
fifth for the same cloud. The decisions it serves improve on every day.

**Caveats.** Four seeds, one mine, one workforce. The zone is the true moderate
zone; the window and reaction time are unswept assumptions, and the warning's
allowance is intent's own 50 m. A decision is scored on whether its information
arrived, not on what the mine then did — units follow their tracks whatever is
decided (the closed loop is still to come). Every unit's position is known
exactly; detection does not yet depend on distance or magnitude.
