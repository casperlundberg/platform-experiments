## Reading

The calibrated mine asks for about 13 executors on average — 1,680 jobs an hour
at 28 s each ([`docs/calibration.md`](../docs/calibration.md)). Four local caps
around that, against four cloud caps, on the three days, with intent off and
every other setting pinned. The comparison table below is against the
calibrated 12 local and 60 cloud on the same day.

**On a normal day, local capacity decides the day, and the cloud cap hardly
matters.**

| Workday | Breaches | Cloud h | Wait p95 |
|---|---:|---:|---:|
| local 12, no cloud | 9,595 | 0 | 83,634 s |
| local 12, cloud 20 to 200 | 16 | 51–54 | 4,596–5,025 s |
| local 16, no cloud | 40 | 0 | 8,446 s |
| local 16, cloud 20 to 200 | 15 | 18.4 | 1,110 s |
| local 24, any cloud | 14 | 0–0.8 | 405 s |

Twelve local executors are just short of the average, so the day runs on cloud
— 53 cloud-hours, bought all day — and without cloud the backlog grows all day
and takes another to clear. A third more local hardware (16) cuts the cloud to
18 hours; twice as much (24) to under one. Above 20, the cloud cap changes
nothing on a workday: it is never what binds. The floor of 14–16 breaches is
the day's own cold start; the coldstart sweep takes it to 4 with local
executors that start at once.

**Under a burst, the cloud cap decides the breaches, and local capacity the
bill.**

| Breaches / cloud h | cloud 20 | cloud 60 | cloud 200 |
|---|---:|---:|---:|
| rock burst, local 12 | 12,100 / 121 | 6,338 / 134 | 2,347 / 145 |
| rock burst, local 24 | 8,568 / 42 | 5,406 / 50 | 2,168 / 59 |
| earthquake, local 12 | 55,786 / 337 | 24,974 / 357 | 4,516 / 368 |
| earthquake, local 24 | 38,760 / 170 | 19,579 / 197 | 3,129 / 208 |

Each step up in cloud cap takes 37–84 % off the breaches for 3–20 % more
cloud-hours: the extra executors are held only while the burst lasts. Doubling
local capacity takes 43–66 % off the cloud bill and 8–31 % off the breaches.
At the earthquake's peak even 224 executors are short: 13–17 overload
decisions remain at cloud 200.

**Low-priority work waits for its deadline, not for capacity.** Under the
earthquake, with any cloud at all, the 95th-percentile wait is within minutes
of a day (86,195–87,268 s), and every run takes 48 hours to drain. Priority 0's
deadline is 24 hours, and the autoscaler buys capacity to meet deadlines, not
to empty the queue. With 24 local executors it held 11 of them on average
(549 local-hours over 48): hardware the mine owns stood idle while work waited
for it. The scale-down and engine sweeps measure what holding it would have
done.

**For a mine:** size the local tier at or above the average day's demand — 16
or more against 13 here — and set the cloud cap by the bursts it has to
survive, since a normal day never reaches it.

**Caveats.** Four seeds, one mine, intent off, and the autoscaler's shipped
deadlines. Demand here is the calibrated catalogue's; a mine with a different
job mix or duration needs its own average.
