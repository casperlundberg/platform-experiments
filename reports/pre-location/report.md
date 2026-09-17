# Acting before a location exists

> Does judging an event from the sensors that triggered, before four picks are processed, help or hurt — and how much does the assumed magnitude matter?

30 runs: 5 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:54:50+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=pre-location
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `0b6be31923ba1702…`.

## Reading

**With this array, acting before a location changes nothing for decay and is
harmful for promotion.** Thirty sensors across a 1.6 km mine put the fourth to
trigger hundreds of metres from the first, and that spread is the allowance: at
any assumed magnitude the zone reaches someone, so no event is decayed before it
is located, and decay arms with and without pre-location are indistinguishable.

Promotion from the same footing promotes nearly everything to the top level
as soon as it arrives: breaches rise nearly sixfold (1,687 → 9,665), overloads
more than triple, and exposing events are located five times later. It does
finish them sooner — but no sooner than promotion after location does.

**Worth trying:** a denser array near active workings, or a spread measured from
arrival-time differences rather than sensor distances, before pre-location is
worth using.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| decay, restored exempt | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| pre-location, m 0.5 | 1,284<br><sub>651–1,790</sub> | 1,668<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.4<br><sub>4.7–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 76<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,101<br><sub>342–1,827</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 573<br><sub>433–661</sub> |
| pre-location, m 1.5 | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| both, pre-location, m 1.5 | 9,665<br><sub>9,132–10,374</sub> | 4,477<br><sub>4,251–4,836</sub> | 70.5<br><sub>65.3–76.2</sub> | 2.0 | 178<br><sub>169–191</sub> | 22<br><sub>6–44</sub> | 451<br><sub>284–519</sub> | 911<br><sub>843–1,019</sub> | 514<br><sub>312–632</sub> | 511<br><sub>425–588</sub> | 1<br><sub>0–4</sub> | 490<br><sub>267–574</sub> |

### Against off

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| decay, restored exempt | -24 % | -1 % | -4 % | -13 % | -78 % |
| pre-location, m 0.5 | -24 % | -1 % | -4 % | -12 % | -78 % |
| pre-location, m 1.5 | -24 % | -1 % | -4 % | -13 % | -78 % |
| both, pre-location, m 1.5 | +473 % | +165 % | +15 % | +420 % | -90 % |

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

Axes: **intent** (5). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
