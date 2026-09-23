## Reading

The same worked mine, with the two things about *how* it is worked that the
activity model exposes: how many faces are worked at once (2, 4 or 8, rotating
each 12-hour shift), and where the day's seismicity comes from — **mostly
blasting** (0.6 blast / 0.3 work / 0.1 background), **balanced** (0.3 / 0.5 /
0.2) or **mostly working** (0.1 / 0.7 / 0.2). The night schedule (four blasts,
01:15–01:45) and the 91 events an hour are the same in all eighteen arms, so
again only *where and when* the day's events fall changes.

**The mix is the load.** A blast's events are drawn from an Omori sequence, so
the more of the day comes from blasting, the more of it arrives in the hour
after 01:15:

| Mix | Breaches, off | with decay | Cloud h, off | with decay |
|---|---:|---:|---:|---:|
| mostly blasting | 1,774 | **1,246–1,338** | 89.2 | 90.5–92.5 |
| balanced | 33 | 514–637 | 61.0 | 56.0–57.9 |
| mostly working | 15 | 358–426 | 46.1 | 38.2–38.4 |

Same 2,160 events, same fleet, a factor of 118 in breaches and twice the cloud.
This is the second place a calibrated workday congests at all — and, as with a
single blast a day, it is where decay **earns**: 25–30 % fewer breaches, for
cloud within 4 % of the baseline. Where the day is spread (mostly working) decay
does what it has always done on a quiet day: costs breaches on harmless work,
and takes 17 % off the cloud bill.

**Decay is worth most to the decisions in exactly the same place.** Warned
shares (the first location whose zone, widened by the 50 m allowance, reaches
the unit), off → decay:

| Mix | Turn-back warned | Way-out warned | Reroute warned |
|---|---|---|---|
| mostly blasting | 60–63 % → **70–74 %** | 73–78 % → 84–87 % | 49–53 % → 56–63 % |
| balanced | 70–71 % → 76 % | 84–88 % → 87–92 % | 55–57 % → 57–61 % |
| mostly working | 70–76 % → 76–77 % | 89–93 % → 89–93 % | 57–63 % → 62–64 % |

A blast-dominated mine is the hardest one to be warned in (turn-back warned as
low as 60 %) and the one where reordering recovers most (+10 to +12 points,
median warning latency 66 s → 43 s at two faces). In a mine whose seismicity
follows its work rather than its rounds, warnings already arrive and decay adds
1–6 points. **Decay's value tracks how peaked the day is, not how many events it
has.**

**Faces worked change who is in the way, not the queue.** With intent off, every
arm at a given mix records *identical* breaches and cloud hours across 2, 4 and
8 faces — the load depends on when events happen, and the number of faces moves
only where. What it moves is exposure:

| Faces worked (mostly blasting) | Exposing events | Turn-back decisions | Way-out decisions |
|---|---:|---:|---:|
| 2 | 81 | 275 | **467** |
| 4 | 71 | 175 | 248 |
| 8 | 68 | 216 | **153** |

Concentrating the whole crew into two faces puts three times as many people
inside the zone of an event that has already happened as spreading them over
eight — the same seismicity, the same people, three times the ways out to find.
Spreading work also raises the baseline warned share (60 % → 63 % at two versus
eight faces) simply because fewer decisions compete for the same processing.
Decay's gain is roughly constant across the three (+10 to +12 points), so it
neither depends on nor substitutes for how work is laid out.

**Caveats.** Four seeds, one mine, one workforce, one blast schedule
(`activity-blasting` varies that). The "mostly blasting" mix is deliberately
extreme — 60 % of a day's events from four rounds — and is a stress case, not a
measurement of any mine. Every unit's position is known exactly and detection
does not depend on distance or magnitude, so these are upper bounds on what the
warnings could be. Decisions are scored on whether their information arrived,
not on what the mine then did.
