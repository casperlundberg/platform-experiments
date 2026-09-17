# Intent against pick error

> How good do the mine's locations have to be before ordering by them stops helping, measured against the oracle that knows where every event was?

72 runs: 12 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:53:36+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=pick-jitter
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `7b3b7b2e98c0212c…`.

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

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| jitter 0 ms · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| jitter 0 ms · decay, restored exempt | 1,334<br><sub>774–1,850</sub> | 1,674<br><sub>989–2,087</sub> | 58.8<br><sub>53.6–62.2</sub> | 7.1<br><sub>5.0–10.7</sub> | 35<br><sub>24–44</sub> | 22<br><sub>6–44</sub> | 77<br><sub>54–98</sub> | 347<br><sub>109–434</sub> | 642<br><sub>274–1,234</sub> | 78<br><sub>60–98</sub> | 0<br><sub>0–2</sub> | 559<br><sub>400–664</sub> |
| jitter 0 ms · decay, restored exempt, truth | 460<br><sub>162–861</sub> | 1,994<br><sub>1,542–2,283</sub> | 40.2<br><sub>35.3–61.1</sub> | 9.8<br><sub>5.1–13.1</sub> | 17<br><sub>12–24</sub> | 22<br><sub>6–44</sub> | 57<br><sub>30–93</sub> | 224<br><sub>46–355</sub> | 211<br><sub>96–478</sub> | 1,080<br><sub>415–1,617</sub> | 0 | 651<br><sub>586–693</sub> |
| jitter 5 ms · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| jitter 5 ms · decay, restored exempt | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| jitter 5 ms · decay, restored exempt, truth | 460<br><sub>162–861</sub> | 1,994<br><sub>1,542–2,283</sub> | 40.2<br><sub>35.3–61.1</sub> | 9.8<br><sub>5.1–13.1</sub> | 17<br><sub>12–24</sub> | 22<br><sub>6–44</sub> | 57<br><sub>30–93</sub> | 224<br><sub>46–355</sub> | 211<br><sub>96–478</sub> | 1,080<br><sub>415–1,617</sub> | 0 | 651<br><sub>586–693</sub> |
| jitter 20 ms · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| jitter 20 ms · decay, restored exempt | 1,063<br><sub>491–1,429</sub> | 1,626<br><sub>1,006–1,946</sub> | 58.5<br><sub>52.9–62.2</sub> | 7.7<br><sub>5.3–10.6</sub> | 30<br><sub>22–37</sub> | 22<br><sub>6–44</sub> | 72<br><sub>38–98</sub> | 344<br><sub>109–418</sub> | 1,518<br><sub>348–2,340</sub> | 73<br><sub>58–86</sub> | 10<br><sub>2–24</sub> | 606<br><sub>534–646</sub> |
| jitter 20 ms · decay, restored exempt, truth | 460<br><sub>162–861</sub> | 1,994<br><sub>1,542–2,283</sub> | 40.2<br><sub>35.3–61.1</sub> | 9.8<br><sub>5.1–13.1</sub> | 17<br><sub>12–24</sub> | 22<br><sub>6–44</sub> | 57<br><sub>30–93</sub> | 224<br><sub>46–355</sub> | 211<br><sub>96–478</sub> | 1,080<br><sub>415–1,617</sub> | 0 | 651<br><sub>586–693</sub> |
| jitter 50 ms · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| jitter 50 ms · decay, restored exempt | 971<br><sub>484–1,368</sub> | 1,630<br><sub>1,052–1,969</sub> | 58.5<br><sub>52.9–62.2</sub> | 7.7<br><sub>6.2–11.9</sub> | 30<br><sub>23–37</sub> | 22<br><sub>6–44</sub> | 70<br><sub>35–98</sub> | 344<br><sub>94–430</sub> | 2,378<br><sub>414–4,262</sub> | 71<br><sub>57–84</sub> | 14<br><sub>2–35</sub> | 630<br><sub>597–668</sub> |
| jitter 50 ms · decay, restored exempt, truth | 460<br><sub>162–861</sub> | 1,994<br><sub>1,542–2,283</sub> | 40.2<br><sub>35.3–61.1</sub> | 9.8<br><sub>5.1–13.1</sub> | 17<br><sub>12–24</sub> | 22<br><sub>6–44</sub> | 57<br><sub>30–93</sub> | 224<br><sub>46–355</sub> | 211<br><sub>96–478</sub> | 1,080<br><sub>415–1,617</sub> | 0 | 651<br><sub>586–693</sub> |

### Against off, at the same jitter

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| jitter 0 ms · decay, restored exempt | -21 % | -1 % | -4 % | -11 % | -87 % |
| jitter 0 ms · decay, restored exempt, truth | -73 % | +18 % | -34 % | -34 % | -96 % |
| jitter 5 ms · decay, restored exempt | -24 % | -1 % | -4 % | -13 % | -78 % |
| jitter 5 ms · decay, restored exempt, truth | -73 % | +18 % | -34 % | -34 % | -96 % |
| jitter 20 ms · decay, restored exempt | -37 % | -4 % | -4 % | -17 % | -70 % |
| jitter 20 ms · decay, restored exempt, truth | -73 % | +18 % | -34 % | -34 % | -96 % |
| jitter 50 ms · decay, restored exempt | -42 % | -3 % | -4 % | -19 % | -53 % |
| jitter 50 ms · decay, restored exempt, truth | -73 % | +18 % | -34 % | -34 % | -96 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were
  served at, measured from their deadline origin. **As submitted**: against the
  level each job arrived at, from arrival — what intent cost against the SLA the
  work was submitted under.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Drained h**: simulated hours until the queue was empty.
- **Overloads**: decisions where no capacity within both caps avoided a predicted
  breach, so the autoscaler ran flat out — often a job already late when seen.
- **Locate exposing**: seconds from an event to its first location, for events
  that truly exposed someone to at least moderate ground motion when they
  happened (judged by the simulator from the truth). The operator-facing measure
  of whether ordering helped the people it was meant to.
- **Process exposing**: seconds from such an event to every one of its picks
  processed — its final location. Promotion acts once an event is located, so
  this, not the first location, is where it can help.
- **Exposing decayed**: of those, how many intent decayed at some point — the
  misses. **Events decayed**: events whose work intent decayed at some point.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **jitter** (4); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

```json
{
  "mine": {
    "id": "storhall",
    "name": "Storhall",
    "sensors": 30,
    "background_rate_per_hour": 90
  },
  "scenario": {
    "duration_seconds": 7200,
    "job_seconds": 20,
    "pick_jitter_seconds": 0.005,
    "priority_mix": {
      "100": 1,
      "50": 1,
      "25": 2
    },
    "bursts": [
      {
        "at_seconds": 1800,
        "magnitude": 45,
        "aftershock_decay_seconds": 1800
      }
    ]
  },
  "settings": {
    "local_executor_cap": 12,
    "cloud_executor_cap": 60,
    "local_coldstart_seconds": 60,
    "cloud_coldstart_seconds": 180
  },
  "intent": {
    "mode": "decay",
    "knowledge": "estimate",
    "pre_location": false,
    "pre_location_magnitude": 1.5,
    "protect": [
      "person",
      "crewed-vehicle",
      "autonomous-vehicle"
    ],
    "lookahead_seconds": 300,
    "protect_level": "moderate",
    "promote_level": "high",
    "margin_m": 0,
    "location_uncertainty_m": 50,
    "decay_to": 0,
    "promote_to": 400,
    "deadline_from": "arrival",
    "restore": true,
    "burst_exempt": []
  },
  "run": {
    "decision_interval_seconds": 15
  }
}
```

Per-seed figures, with every measured column, are in [`runs.csv`](runs.csv).

<sub>Tables rendered by platform-experiments `c94700a2d78c`.</sub>
