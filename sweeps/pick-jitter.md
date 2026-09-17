## Reading

**Breaches falling here is not good news.** As pick error grows, decay cuts more
breaches (−21 % at 0 ms, −42 % at 50 ms) — because worse locations put more events
outside everyone's zone, including events that were not:

| Pick error | Exposing events decayed, of 21.5 per seed | Finish exposing events |
|---|---:|---:|
| 0 ms | 0.5 | 642 s |
| 5 ms | 2.3 | 1,113 s |
| 20 ms | 9.7 | 1,518 s |
| 50 ms | 14.3 | 2,378 s |

At 20 ms — about 116 m of travel in rock — the fixed ±50 m allowance no longer
covers location error, and nearly half the events that truly exposed someone
are decayed at some point. At 50 ms two-thirds are.

The oracle is untouched by pick error by construction; it is the ceiling.

**What this asks for.** An allowance tied to the location's own uncertainty —
its residual, or the spread of solutions that fit its picks — rather than one
number for every event. Until then, the allowance should be set for the worst
pick error a mine expects, not the typical one.
