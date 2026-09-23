## Reading

The first sweep over a mine that is actually worked. Until now the day's
events were spread evenly along every production tunnel around the clock; here
they come from where mining puts them — half from around the four faces being
worked, a fifth background, and **three tenths from the blasts and the
sequences that decay after them** (modified Omori, p = 1, over twelve hours).
The day's total rate is unchanged at 91 events an hour, so this sweep varies
*when* the mine's seismicity happens, not how much of it there is. Crews are
cleared from the production areas 30 minutes before the first blast and re-enter
three hours after the last.

Four schedules, each 24 h × 4 seeds: **night, four blasts** (01:15–01:45 every
ten minutes, as LKAB fires at Kiruna), **day, four blasts** (13:00–13:30),
**through the night** (01:00–05:00, nine blasts half an hour apart) and **one a
day** (a single round at 01:15 carrying the whole day's blast share).

**The schedule decides whether there is a queue problem at all.**

| Schedule | Breaches, intent off | with decay | p95 time-to-locate, off |
|---|---:|---:|---:|
| night, four blasts | 33 | 514 | 125 s |
| day, four blasts | 51 | 566 | 128 s |
| through the night | 36 | 607 | 149 s |
| one a day | 2,186 | **1,470** | 210 s |

Spreading the round over four or nine blasts spreads the aftershock sequences
with it, and the fleet keeps up: a few dozen breaches a day, and decay costs
breaches exactly as it does on the calibrated quiet day — deferring harmless
work past its deadline to buy 5–19 % less cloud. Fire the whole round at once
and the same daily total arrives in one peak: 2,186 breaches. That is the first
schedule in any sweep where **decay reduces breaches on a calibrated workday**
(−33 %), and the oracle −65 %, because there is finally contention for it to
resolve. Blast scheduling is therefore a platform-capacity decision as much as a
ventilation one.

**What the decisions see.** Any location almost always arrives in time (91–94 %
of turn-back decisions), and neither the schedule nor the intent moves that
much. The measure that separates them is the **warning** — the first location
whose own zone, widened by the 50 m allowance for location error, reaches the
unit:

| Turn-back warned, in time | off | decay | oracle |
|---|---:|---:|---:|
| night, four blasts | 70 % | 76 % | 89 % |
| day, four blasts | 72 % | 75 % | 87 % |
| through the night | 74 % | 72 % | 88 % |
| one a day | **65 %** | **75 %** | 86 % |

The single round is both the worst day to be warned on (65 %) and the day decay
helps most (+9 pp, median warning latency 63 s → 52 s). Way-out warned moves
85 → 89 → 96 % and reroute warned 54 → 62 → 69 % on the same day. On the three
spread schedules decay adds 3–6 pp, and on *through the night* it adds nothing
at all (74 → 72 %) — there is no congestion, so reordering can only move work
about.

**When the mine blasts also decides who is exposed.** The schedules produce
different numbers of events that catch somebody inside a moderate zone, though
every day has the same 2,160 events:

| Schedule | Exposing events a day | Turn-back decisions | Way-out decisions |
|---|---:|---:|---:|
| through the night | **65** | 146 | 231 |
| night, four blasts | 88 | 176 | 298 |
| one a day | 96 | 212 | 307 |
| day, four blasts | **104** | 184 | 336 |

Blasting through the night keeps the production areas cleared across the whole
window and the busiest part of every sequence, and exposes a third fewer events
than blasting in the middle of the day shift — where the sequences decay with
crews back at the faces. This is a result about the mine, not about the
platform: it holds with intent off, and the platform can only make the best of
whichever schedule the mine keeps.

**At what price.** The oracle's cost is visible in the tail: it decays 2,045
events a day against decay's 1,610, and the p95 time-to-locate over *all* events
goes from 80–130 s to 1.6–2.2 h. Deferred harmless work is genuinely deferred;
what the run buys with it is the exposing events' p95 falling from 116 s to
52 s.

**Caveats.** Four seeds, one mine, one workforce, 4 faces worked and the
balanced mix throughout (`activity-shape` varies those). Clear and re-entry are
fixed at 30 min and 3 h; re-entry protocols in the surveyed mines run 2–12 h, and
case 7 will sweep them. Blast timing is exact and known; the application is not
yet told about it. A decision is scored on whether its information arrived, not
on what the mine then did.
