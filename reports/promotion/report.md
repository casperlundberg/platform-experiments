# How far and how high to promote

> Promotion finishes exposing events' locations far sooner but has cost breaches and cloud time. Does promoting less high, only at very high ground motion, or with a fresh deadline keep the benefit and lose the cost?

60 runs: 10 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:57:11+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=promotion
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `a192cfb4a0d55570…`.

## Reading

**No variant of promotion tested keeps its benefit without its cost.**

- **Promoting only at very high ground motion** never fires in these scenarios:
  very high motion needs about magnitude 2.9 at the source, and the largest main
  shock is 2.5. Those arms are decay alone — with deadlines restarted on a change
  where that was set, which is what moves their numbers.
- **Promoting to 100 instead of 400** changes little. The promoted work is still
  late at 100's one-minute deadline and still ahead of most other work.
- **Restarting the deadline on a change** removes promotion's extra breaches
  (2,809 → 1,616, just under no intent's 1,687) but leaves cloud time about a fifth
  above no intent, and the SLA as submitted 26 % worse.

What all high-level promotion buys is the same: exposing events finished in
500–550 s rather than 1,113 s with decay alone and 5,025 s with no intent. If
that is the goal, promotion delivers it; if SLA and cost are, decay does better.

**Worth trying:** promotion that raises only the next few picks an event needs for
a better location, rather than all of its remaining work.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off · to 400 · at high · from arrival | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| decay, restored exempt · to 400 · at high · from arrival | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| both · to 400 · at high · from arrival | 2,808<br><sub>1,762–4,692</sub> | 2,132<br><sub>1,656–2,785</sub> | 71.7<br><sub>65.3–82.6</sub> | 2.6<br><sub>2.0–3.9</sub> | 58<br><sub>39–88</sub> | 22<br><sub>6–44</sub> | 105<br><sub>58–201</sub> | 455<br><sub>162–887</sub> | 515<br><sub>316–756</sub> | 113<br><sub>73–210</sub> | 3<br><sub>0–6</sub> | 550<br><sub>368–637</sub> |
| both · to 400 · at high · from the change | 1,616<br><sub>1,165–2,174</sub> | 2,132<br><sub>1,687–2,775</sub> | 73.9<br><sub>65.9–83.3</sub> | 2.5<br><sub>2.0–4.2</sub> | 57<br><sub>40–88</sub> | 22<br><sub>6–44</sub> | 103<br><sub>56–198</sub> | 449<br><sub>147–872</sub> | 534<br><sub>334–717</sub> | 110<br><sub>72–207</sub> | 3<br><sub>0–6</sub> | 547<br><sub>364–634</sub> |
| both · to 400 · at very-high · from arrival | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| both · to 400 · at very-high · from the change | 913<br><sub>470–1,616</sub> | 1,712<br><sub>968–2,247</sub> | 58.6<br><sub>53.4–62.2</sub> | 12.3<br><sub>10.6–15.0</sub> | 31<br><sub>24–43</sub> | 22<br><sub>6–44</sub> | 76<br><sub>46–98</sub> | 350<br><sub>124–434</sub> | 1,669<br><sub>338–2,612</sub> | 74<br><sub>60–95</sub> | 2<br><sub>0–5</sub> | 568<br><sub>422–655</sub> |
| both · to 100 · at high · from arrival | 2,594<br><sub>1,624–4,180</sub> | 2,122<br><sub>1,663–2,796</sub> | 70.5<br><sub>64.2–82.9</sub> | 2.7<br><sub>2.0–3.8</sub> | 57<br><sub>39–87</sub> | 22<br><sub>6–44</sub> | 104<br><sub>57–197</sub> | 450<br><sub>162–869</sub> | 502<br><sub>314–756</sub> | 112<br><sub>69–209</sub> | 3<br><sub>0–6</sub> | 551<br><sub>375–637</sub> |
| both · to 100 · at high · from the change | 1,728<br><sub>1,087–3,129</sub> | 2,092<br><sub>1,531–2,851</sub> | 71.4<br><sub>54.9–83.8</sub> | 3.5<br><sub>2.0–8.1</sub> | 53<br><sub>32–84</sub> | 22<br><sub>6–44</sub> | 98<br><sub>49–171</sub> | 449<br><sub>147–869</sub> | 550<br><sub>345–856</sub> | 105<br><sub>68–184</sub> | 3<br><sub>0–5</sub> | 550<br><sub>371–635</sub> |
| both · to 100 · at very-high · from arrival | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| both · to 100 · at very-high · from the change | 913<br><sub>470–1,616</sub> | 1,712<br><sub>968–2,247</sub> | 58.6<br><sub>53.4–62.2</sub> | 12.3<br><sub>10.6–15.0</sub> | 31<br><sub>24–43</sub> | 22<br><sub>6–44</sub> | 76<br><sub>46–98</sub> | 350<br><sub>124–434</sub> | 1,669<br><sub>338–2,612</sub> | 74<br><sub>60–95</sub> | 2<br><sub>0–5</sub> | 568<br><sub>422–655</sub> |

### Against off · to 400 · at high · from arrival

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| decay, restored exempt · to 400 · at high · from arrival | -24 % | -1 % | -4 % | -13 % | -78 % |
| both · to 400 · at high · from arrival | +67 % | +26 % | +17 % | +21 % | -90 % |
| both · to 400 · at high · from the change | -4 % | +26 % | +21 % | +19 % | -89 % |
| both · to 400 · at very-high · from arrival | -24 % | -1 % | -4 % | -13 % | -78 % |
| both · to 400 · at very-high · from the change | -46 % | +2 % | -4 % | -13 % | -67 % |
| both · to 100 · at high · from arrival | +54 % | +26 % | +15 % | +20 % | -90 % |
| both · to 100 · at high · from the change | +2 % | +24 % | +17 % | +13 % | -89 % |
| both · to 100 · at very-high · from arrival | -24 % | -1 % | -4 % | -13 % | -78 % |
| both · to 100 · at very-high · from the change | -46 % | +2 % | -4 % | -13 % | -67 % |

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

Axes: **intent** (3); **promote to** (2); **promote at** (2); **deadline** (2). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
