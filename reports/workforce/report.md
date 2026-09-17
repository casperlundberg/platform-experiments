# Intent against how many people are underground

> How does the benefit of intent change with the size of the workforce, when more people means more of the mine is protected?

54 runs: 9 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:59:16+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=workforce
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `2900de928d36431b…`.

## Reading

**The more people underground, the less decay has to relax, and the more there is
to miss.**

| Crew | Exposing events per seed | Breaches, decay vs no intent | Exposing events decayed |
|---|---:|---:|---:|
| 4 people, 2 crewed, 1 autonomous | 16.5 | −28 % | 1.3 |
| 8, 4, 3 (default) | 21.5 | −24 % | 2.3 |
| 24, 12, 9 | 37 | −17 % | 4.5 |

A larger crew protects more of the mine, so less work is decayed (611 → 505
events) and the breaches it saves shrink; misses grow roughly with the number of
exposing events, at around one in ten.

**Both, exempt** gets worse as the crew grows (breaches +53 % → +109 %), because
more events are near someone and promoted. Its finish time for exposing events
stays the best of the three arms at every size.

**Caveat.** Crews move on their own tracks from their own streams; a larger crew
is a different set of routes, not the same routes with more people on them.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small crew · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 16<br><sub>4–38</sub> | 86<br><sub>69–120</sub> | 387<br><sub>314–452</sub> | 3,805<br><sub>2,051–5,308</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| small crew · decay, restored exempt | 1,222<br><sub>615–1,739</sub> | 1,676<br><sub>996–2,108</sub> | 58.6<br><sub>53.2–62.2</sub> | 7.4<br><sub>5.7–10.3</sub> | 34<br><sub>23–42</sub> | 16<br><sub>4–38</sub> | 78<br><sub>50–120</sub> | 367<br><sub>330–418</sub> | 686<br><sub>281–1,394</sub> | 75<br><sub>58–93</sub> | 1<br><sub>0–4</sub> | 611<br><sub>491–679</sub> |
| small crew · both, exempt | 2,579<br><sub>1,445–4,139</sub> | 2,127<br><sub>1,686–2,753</sub> | 68.3<br><sub>62.0–76.9</sub> | 2.6<br><sub>2.1–4.3</sub> | 54<br><sub>29–71</sub> | 16<br><sub>4–38</sub> | 94<br><sub>57–138</sub> | 465<br><sub>375–677</sub> | 418<br><sub>251–708</sub> | 103<br><sub>66–171</sub> | 2<br><sub>0–5</sub> | 588<br><sub>481–660</sub> |
| default crew · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| default crew · decay, restored exempt | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| default crew · both, exempt | 2,808<br><sub>1,762–4,692</sub> | 2,132<br><sub>1,656–2,785</sub> | 71.7<br><sub>65.3–82.6</sub> | 2.6<br><sub>2.0–3.9</sub> | 58<br><sub>39–88</sub> | 22<br><sub>6–44</sub> | 105<br><sub>58–201</sub> | 455<br><sub>162–887</sub> | 515<br><sub>316–756</sub> | 113<br><sub>73–210</sub> | 3<br><sub>0–6</sub> | 550<br><sub>368–637</sub> |
| large crew · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 37<br><sub>14–91</sub> | 93<br><sub>61–152</sub> | 413<br><sub>337–494</sub> | 5,852<br><sub>3,628–9,322</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| large crew · decay, restored exempt | 1,399<br><sub>735–1,840</sub> | 1,692<br><sub>988–2,111</sub> | 59.0<br><sub>53.6–62.2</sub> | 8.4<br><sub>5.7–12.6</sub> | 39<br><sub>27–53</sub> | 37<br><sub>14–91</sub> | 81<br><sub>61–136</sub> | 384<br><sub>337–434</sub> | 1,510<br><sub>705–2,396</sub> | 83<br><sub>64–102</sub> | 4<br><sub>1–8</sub> | 504<br><sub>314–596</sub> |
| large crew · both, exempt | 3,532<br><sub>2,421–5,771</sub> | 2,313<br><sub>1,882–3,008</sub> | 73.5<br><sub>66.1–88.3</sub> | 2.3<br><sub>2.0–3.0</sub> | 70<br><sub>45–107</sub> | 37<br><sub>14–91</sub> | 129<br><sub>72–243</sub> | 601<br><sub>392–1,007</sub> | 547<br><sub>449–609</sub> | 139<br><sub>84–249</sub> | 6<br><sub>1–11</sub> | 468<br><sub>269–574</sub> |

### Against off, at the same workforce

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| small crew · decay, restored exempt | -28 % | -1 % | -4 % | -9 % | -82 % |
| small crew · both, exempt | +53 % | +26 % | +12 % | +9 % | -89 % |
| default crew · decay, restored exempt | -24 % | -1 % | -4 % | -13 % | -78 % |
| default crew · both, exempt | +67 % | +26 % | +17 % | +21 % | -90 % |
| large crew · decay, restored exempt | -17 % | +0 % | -3 % | -13 % | -74 % |
| large crew · both, exempt | +109 % | +37 % | +20 % | +38 % | -91 % |

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

Axes: **workforce** (3); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
