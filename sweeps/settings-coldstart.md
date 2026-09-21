## Reading

Coldstart here is a fact of the platform, not a dial: it sets both what the
autoscaler assumes and how long the simulated fleet actually takes, so each arm
is a different platform — an on-premise executor that starts at once, in a
minute or in five; a cloud executor in one, three or ten minutes.

**How fast the cloud starts decides whether it can help at all.**

| Breaches against local 1 min, cloud 3 min | cloud 1 min | cloud 10 min |
|---|---:|---:|
| workday | −14 % | +2,958 % (16 → 497) |
| rock burst | −10 % | +16 % |
| earthquake | −6 % | +8 % |

The top level's deadline is 60 seconds and the next is 5 minutes, so cloud
capacity that takes 10 minutes to start can rescue neither. On the workday the
engine saw 257 decisions where no capacity within both caps avoided a breach, up
from none. The cloud time bought barely changed (+1–9 %); what changed is how
much of it arrived in time to count. A one-minute cloud also cut the
95th-percentile wait by 35–44 % on the workday and rock burst.

**On-premise coldstart matters at the edges of the day.** Local executors that
start at once took the workday from 16 breaches to 4 — the floor the other
sweeps share is the day's own cold start — and five minutes more than doubled
it (39); under the bursts either way moved breaches by 3 % or less.

**For a mine:** measure the coldstart of the platform the cloud tier runs on,
and weigh it against the shortest deadline that tier is meant to rescue. A
container platform that starts in a minute is worth more here than a larger cap
on one that takes ten.

**Caveats.** Four seeds, one mine, intent off. The autoscaler's assumed
coldstart and the fleet's real one are the same value in every arm; a mismatch
between them — an autoscaler told 3 minutes on a platform that takes 10 — was
not swept.
