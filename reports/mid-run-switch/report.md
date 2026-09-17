# Changing intent while a run is in flight

> What happens when an operator changes intent at the moment of a rock burst (cycle 120) or once it has passed (cycle 240), compared with holding one intent throughout?

36 runs: 6 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:50:21+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=mid-run-switch
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `6332db2605bb7343…`.

## Reading

**Intent's effect is almost entirely in the burst.** Switching decay on at the
burst gives the same result as decay throughout; switching it off at the burst
gives the same result as no intent. Before the burst there is little queue to
reorder.

Switching to both decay and promotion at the burst costs what promotion costs
throughout (breaches +66 %, cloud +17 %), and dropping promotion again thirty
minutes after the burst recovers only part of it (+55 %, +8 %): the promoted work
is already late and already dispatched.

Every change here is a schedule. The same changes made by hand through the API
while a run is in flight are recorded with the cycle they took effect from and
replay identically — experiment 005 checks exactly that.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off throughout | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| decay throughout | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| off, decay at the burst | 1,281<br><sub>651–1,791</sub> | 1,665<br><sub>966–2,107</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 548<br><sub>413–633</sub> |
| decay, off at the burst | 1,686<br><sub>950–2,119</sub> | 1,686<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,837</sub> | 131<br><sub>79–199</sub> | 0 | 24<br><sub>18–32</sub> |
| decay, both at the burst | 2,800<br><sub>1,762–4,692</sub> | 2,131<br><sub>1,651–2,785</sub> | 71.7<br><sub>65.3–82.6</sub> | 2.6<br><sub>2.0–3.9</sub> | 58<br><sub>39–88</sub> | 22<br><sub>6–44</sub> | 105<br><sub>58–201</sub> | 455<br><sub>162–887</sub> | 515<br><sub>316–756</sub> | 113<br><sub>73–210</sub> | 3<br><sub>0–6</sub> | 551<br><sub>368–637</sub> |
| both at the burst, decay after | 2,612<br><sub>1,495–4,412</sub> | 2,134<br><sub>1,685–2,803</sub> | 66.2<br><sub>60.8–76.8</sub> | 3.8<br><sub>2.1–6.5</sub> | 55<br><sub>34–87</sub> | 22<br><sub>6–44</sub> | 104<br><sub>56–199</sub> | 455<br><sub>162–887</sub> | 699<br><sub>350–1,076</sub> | 113<br><sub>75–210</sub> | 3<br><sub>0–6</sub> | 554<br><sub>376–637</sub> |

### Against off throughout

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| decay throughout | -24 % | -1 % | -4 % | -13 % | -78 % |
| off, decay at the burst | -24 % | -1 % | -4 % | -13 % | -78 % |
| decay, off at the burst | -0 % | -0 % | +0 % | +0 % | -0 % |
| decay, both at the burst | +66 % | +26 % | +17 % | +21 % | -90 % |
| both at the burst, decay after | +55 % | +27 % | +8 % | +20 % | -86 % |

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

Axes: **intent** (6). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
