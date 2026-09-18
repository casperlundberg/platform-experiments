## Reading

Three days on one mine fitted to an operational catalogue
([`docs/calibration.md`](../docs/calibration.md)): a normal workday of about
40,000 jobs, the same day with a rock burst (55,000), and the same day with a
medium earthquake — a Nuttli 4 main shock and a six-hour aftershock tail
(93,000). Each is a 24-hour day with 59 to 123 events that truly exposed
someone, against 6 to 44 in the two-hour scenario the earlier sweeps used.

**Intent's value follows contention, and on a quiet day it is a cost.**

| | Breaches vs no intent | Cloud h | Locate exposing |
|---|---:|---:|---:|
| workday | **+2,281 %** (49 → 1,161) | −3 % | −20 % |
| rock burst | −8 % (6,164 → 5,669) | −16 % | −22 % |
| earthquake | −27 % (20,661 → 15,054) | −1 % | −57 % |

On the workday the fleet keeps up on its own — 49 breaches in a day — and
anything intent relaxes is work that would have been served on time. It shows
up as a hundredfold rise in breaches off a tiny base, and as 4,800 jobs past the
deadline they arrived with. Under the earthquake the same settings cut breaches
by a quarter and more than halve the wait for a location on events that exposed
someone, at no extra cloud time. The mid-run-switch sweep already showed intent
can be switched on at the burst and off after; these numbers say when it is
worth doing.

**Decayed work needs a level of its own.** The arms differ only in `decay_to`:
0, which this job mix also submits a quarter of its work at, against −1, below
everything.

| Finish exposing events | no intent | decay to 0 | decay to its own level |
|---|---:|---:|---:|
| workday | 1,566 s | 2,151 s | **760 s** |
| rock burst | 6,421 s | 9,047 s | **1,767 s** |
| earthquake | 49,439 s | 46,657 s | **7,154 s** |

Decaying into a level that carries submitted work puts relaxed work in front of
the low-priority picks of the very events intent kept, and those events then
finish *later* than with no intent at all. Below the floor they finish five to
seven times sooner, for the same breaches and slightly less cloud time. This is
why simlab-api 3.0.0 decays to −1 by default; the arms here are pinned to the
old and new values, so both are on the record.

**The earlier sweeps are not wrong, but they were lucky.** Their mix submitted
nothing below priority 25, so decaying to 0 was already below everything, and
the collision could not appear. A job mix from a real pipeline found it in its
first run.

**Promotion** still buys the fastest finish for exposing events on every shape
and still costs breaches and cloud time, except under the earthquake where its
first locations are also better than no intent (−44 %).

**Caveats.** Four seeds. One mine, one workforce, one array. The earthquake is a
main shock of Nuttli 4 with aftershocks capped 1.5 below it, which is the first
scenario here where very high ground motion occurs at all — and it reaches only
one or two events per day, so promotion at that level is still barely tested.
