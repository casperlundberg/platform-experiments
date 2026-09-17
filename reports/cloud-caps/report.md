# Intent against the cloud budget

> Does what intent buys depend on how much cloud capacity there is to spend — none, a little, the default, or plenty?

96 runs: 16 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:41:13+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=cloud-caps
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `8915fff0c42b0588…`.

## Reading

**Intent matters most when capacity is scarce, and stops mattering when it is
not.** Compared with no intent at the same cloud cap:

- **No cloud at all:** decay with restored work exempt cuts breaches by 36 % and
  its SLA as submitted by 24 %, locates exposing events 18 % sooner and finishes
  them 58 % sooner. The queue is hours deep, and ordering is the only lever left.
- **20 cloud executors:** decay also cuts cloud time by a third (37.6 → 23.5 h
  with restored work exempt, 27.7 h made final): with less urgent work waiting, the
  autoscaler buys less. Exposing events are located 35–41 % sooner. Decay made final
  lets the SLA as submitted slide 38 % — decayed work that is never restored waits
  for hours.
- **60 (the default):** as in the intent-modes sweep — a quarter to a half fewer
  breaches, no more cloud time, exposing events located 13–18 % sooner.
- **200:** capacity absorbs almost everything and every run drains in two hours.
  Decay still trims breaches (−7 to −16 %) but the SLA as submitted rises by half
  — on counts small enough (301 → 445 breaches over six seeds) that decaying a few
  hundred jobs shows. Exposing events are located within a few seconds of each
  other whatever the intent.

**Both, exempt** finishes exposing events fastest at every cap but the largest
(−74 to −90 %), but
locates them later and breaches more once there is enough capacity for the
promoted work to crowd out the rest.

**Caveat.** Exemption lets restored work be late without buying cloud; with no
cloud to buy it changes what counts as late for the autoscaler's projection but
not the fleet, which is why the arms still differ at cap 0.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cloud 0 · off | 10,166<br><sub>9,799–10,566</sub> | 10,166<br><sub>9,799–10,566</sub> | 0.0 | 14.6<br><sub>14.5–14.7</sub> | 1,153<br><sub>1,112–1,193</sub> | 22<br><sub>6–44</sub> | 2,942<br><sub>1,927–3,905</sub> | 6,698<br><sub>6,516–6,866</sub> | 36,636<br><sub>29,020–43,575</sub> | 2,930<br><sub>2,607–3,215</sub> | 0 | 0 |
| cloud 0 · decay, final | 8,652<br><sub>8,328–9,153</sub> | 10,403<br><sub>10,150–10,873</sub> | 0.0 | 26.5<br><sub>26.4–26.6</sub> | 898<br><sub>858–941</sub> | 22<br><sub>6–44</sub> | 2,248<br><sub>1,631–2,712</sub> | 5,167<br><sub>4,895–5,429</sub> | 22,008<br><sub>6,648–29,811</sub> | 2,202<br><sub>2,038–2,411</sub> | 4<br><sub>0–9</sub> | 628<br><sub>561–688</sub> |
| cloud 0 · decay, restored exempt | 6,514<br><sub>6,141–7,079</sub> | 7,768<br><sub>7,422–8,085</sub> | 0.0 | 18.2<br><sub>16.5–19.8</sub> | 757<br><sub>721–802</sub> | 22<br><sub>6–44</sub> | 2,414<br><sub>1,682–2,972</sub> | 5,407<br><sub>5,113–6,021</sub> | 15,207<br><sub>9,318–23,311</sub> | 2,331<br><sub>2,098–2,695</sub> | 4<br><sub>0–8</sub> | 628<br><sub>554–693</sub> |
| cloud 0 · both, exempt | 8,134<br><sub>7,253–9,355</sub> | 6,361<br><sub>6,092–6,647</sub> | 0.0 | 15.2<br><sub>12.8–16.9</sub> | 899<br><sub>792–1,023</sub> | 22<br><sub>6–44</sub> | 3,881<br><sub>2,714–4,691</sub> | 7,979<br><sub>6,500–10,942</sub> | 9,501<br><sub>7,425–12,479</sub> | 3,763<br><sub>2,805–5,521</sub> | 5<br><sub>0–11</sub> | 586<br><sub>444–659</sub> |
| cloud 20 · off | 5,433<br><sub>4,965–6,221</sub> | 5,433<br><sub>4,965–6,221</sub> | 37.6<br><sub>36.0–39.6</sub> | 13.9<br><sub>13.7–14.0</sub> | 288<br><sub>270–315</sub> | 22<br><sub>6–44</sub> | 560<br><sub>365–1,056</sub> | 1,571<br><sub>1,393–1,730</sub> | 31,124<br><sub>23,409–39,704</sub> | 727<br><sub>504–871</sub> | 0 | 0 |
| cloud 20 · decay, final | 3,827<br><sub>3,463–4,497</sub> | 7,479<br><sub>7,009–8,055</sub> | 27.7<br><sub>26.2–30.4</sub> | 25.8<br><sub>25.6–26.0</sub> | 174<br><sub>155–189</sub> | 22<br><sub>6–44</sub> | 330<br><sub>288–372</sub> | 1,320<br><sub>1,200–1,397</sub> | 10,840<br><sub>1,072–25,063</sub> | 376<br><sub>343–419</sub> | 4<br><sub>0–9</sub> | 610<br><sub>539–670</sub> |
| cloud 20 · decay, restored exempt | 4,299<br><sub>3,642–4,944</sub> | 5,502<br><sub>4,646–6,016</sub> | 23.5<br><sub>19.4–27.8</sub> | 16.7<br><sub>15.6–17.6</sub> | 159<br><sub>127–186</sub> | 22<br><sub>6–44</sub> | 366<br><sub>326–418</sub> | 1,331<br><sub>1,200–1,465</sub> | 8,114<br><sub>1,366–15,524</sub> | 423<br><sub>357–532</sub> | 4<br><sub>0–8</sub> | 619<br><sub>542–686</sub> |
| cloud 20 · both, exempt | 6,416<br><sub>5,256–8,155</sub> | 4,676<br><sub>4,404–5,292</sub> | 30.0<br><sub>26.3–33.4</sub> | 11.5<br><sub>7.2–14.4</sub> | 231<br><sub>176–304</sub> | 22<br><sub>6–44</sub> | 655<br><sub>424–1,026</sub> | 2,050<br><sub>1,575–3,152</sub> | 3,311<br><sub>2,218–4,953</sub> | 680<br><sub>472–1,124</sub> | 4<br><sub>0–9</sub> | 580<br><sub>421–655</sub> |
| cloud 60 · off | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| cloud 60 · decay, final | 894<br><sub>421–1,600</sub> | 1,723<br><sub>957–2,400</sub> | 58.6<br><sub>53.4–62.2</sub> | 12.7<br><sub>10.7–15.7</sub> | 31<br><sub>24–43</sub> | 22<br><sub>6–44</sub> | 71<br><sub>43–96</sub> | 350<br><sub>124–434</sub> | 1,221<br><sub>198–2,155</sub> | 72<br><sub>58–94</sub> | 2<br><sub>0–4</sub> | 548<br><sub>421–616</sub> |
| cloud 60 · decay, restored exempt | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| cloud 60 · both, exempt | 2,808<br><sub>1,762–4,692</sub> | 2,132<br><sub>1,656–2,785</sub> | 71.7<br><sub>65.3–82.6</sub> | 2.6<br><sub>2.0–3.9</sub> | 58<br><sub>39–88</sub> | 22<br><sub>6–44</sub> | 105<br><sub>58–201</sub> | 455<br><sub>162–887</sub> | 515<br><sub>316–756</sub> | 113<br><sub>73–210</sub> | 3<br><sub>0–6</sub> | 550<br><sub>368–637</sub> |
| cloud 200 · off | 301<br><sub>3–1,009</sub> | 301<br><sub>3–1,009</sub> | 228.4<br><sub>139.8–278.1</sub> | 2.0 | 8<br><sub>2–18</sub> | 22<br><sub>6–44</sub> | 34<br><sub>14–68</sub> | 140<br><sub>25–315</sub> | 165<br><sub>39–356</sub> | 33<br><sub>15–58</sub> | 0 | 0 |
| cloud 200 · decay, final | 254<br><sub>3–871</sub> | 447<br><sub>11–1,129</sub> | 226.5<br><sub>128.7–278.1</sub> | 2.0 | 8<br><sub>2–17</sub> | 22<br><sub>6–44</sub> | 33<br><sub>12–67</sub> | 138<br><sub>25–315</sub> | 114<br><sub>39–240</sub> | 29<br><sub>14–54</sub> | 2<br><sub>0–6</sub> | 516<br><sub>320–593</sub> |
| cloud 200 · decay, restored exempt | 279<br><sub>11–871</sub> | 444<br><sub>11–1,129</sub> | 226.5<br><sub>128.7–278.1</sub> | 2.0 | 8<br><sub>2–17</sub> | 22<br><sub>6–44</sub> | 33<br><sub>13–67</sub> | 138<br><sub>25–315</sub> | 121<br><sub>39–241</sub> | 29<br><sub>15–54</sub> | 2<br><sub>0–6</sub> | 515<br><sub>320–594</sub> |
| cloud 200 · both, exempt | 677<br><sub>66–2,464</sub> | 496<br><sub>16–1,356</sub> | 226.8<br><sub>128.7–278.6</sub> | 2.0 | 10<br><sub>2–25</sub> | 22<br><sub>6–44</sub> | 37<br><sub>14–86</sub> | 156<br><sub>25–340</sub> | 93<br><sub>38–178</sub> | 33<br><sub>15–68</sub> | 2<br><sub>0–6</sub> | 513<br><sub>310–592</sub> |

### Against off, at the same cloud cap

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| cloud 0 · decay, final | -15 % | +2 % | – | -24 % | -40 % |
| cloud 0 · decay, restored exempt | -36 % | -24 % | – | -18 % | -58 % |
| cloud 0 · both, exempt | -20 % | -37 % | – | +32 % | -74 % |
| cloud 20 · decay, final | -30 % | +38 % | -27 % | -41 % | -65 % |
| cloud 20 · decay, restored exempt | -21 % | +1 % | -38 % | -35 % | -74 % |
| cloud 20 · both, exempt | +18 % | -14 % | -20 % | +17 % | -89 % |
| cloud 60 · decay, final | -47 % | +2 % | -4 % | -18 % | -76 % |
| cloud 60 · decay, restored exempt | -24 % | -1 % | -4 % | -13 % | -78 % |
| cloud 60 · both, exempt | +67 % | +26 % | +17 % | +21 % | -90 % |
| cloud 200 · decay, final | -16 % | +49 % | -1 % | -3 % | -31 % |
| cloud 200 · decay, restored exempt | -7 % | +47 % | -1 % | -3 % | -27 % |
| cloud 200 · both, exempt | +125 % | +65 % | -1 % | +11 % | -43 % |

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

Axes: **cloud cap** (4); **intent** (4). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
