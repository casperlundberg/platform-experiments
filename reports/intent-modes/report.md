# Intent modes, estimate against oracle

> What does each intent mode do to SLA breaches, cloud cost and how soon events that endanger people are located — from the mine's own estimates, and from the truth?

114 runs: 19 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:45:28+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=intent-modes
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `34c56cf60a78139e…`.

## Reading

**Decay helps; promotion from the mine's own estimates does not, yet.** Against
no intent, on the default capacity (12 on-premise, 60 cloud):

- **Decay with restored work exempt** — the default — cuts breaches by a quarter
  (1,687 → 1,281) with no more cloud time (61.1 → 58.5 h), locates events that
  truly exposed someone 13 % sooner (87 → 76 s) and finishes their picks four
  times sooner (5,025 → 1,113 s). The SLA as submitted is unchanged (−1 %): the
  work decayed was work that could wait.
- **Decay with every restore counted** is the same ordering bought at +41 % cloud
  time (85.9 h). Restored work comes back already late, each restore is a breach
  no capacity avoids, and the autoscaler runs flat out. This is why restored work
  is exempt by default.
- **Decay made final** has the fewest breaches of any estimate arm (894) at the
  same cloud time. It is not the default because it stops protecting anyone who
  arrives after the lookahead, and nothing measured here — exposure is judged at
  the moment an event happens — can see that cost.
- **Promotion** under estimates costs more cloud time (+17 to +46 %) and, unless
  the deadline restarts on a change, far more breaches (+47 to +111 %); and the
  first location of an exposing event comes later, not sooner (+12 to +34 %): promotion can only act once an event is located, so it
  cannot speed the location that decides it, and the promoted work — already past
  a 30-second deadline — takes capacity from everything else. What it buys is the
  final location of exposing events, six to fourteen times sooner.

**Knowledge is worth a great deal.** The oracle arms, deciding from where events
really were, locate exposing events up to 56 % sooner (38 s) and cut breaches by
up to 95 %. The gap between the estimate and oracle arms is what better locations
could still win.

**Misses.** Across six seeds, 129 events truly exposed someone to at least
moderate ground motion (only 2 to high). Estimate arms decayed 2–3 of them per
seed on average at some point; the oracle none. Counting where people were when
an event happened (simlab-api 2.0.0) took the oracle's misses from three to five
per seed to none.

**Caveats.** Six seeds, with 6 to 44 exposing events each; per-seed ranges in the
table are wide. One scenario shape (a two-hour window with one large burst).
Exposure is judged at the instant an event happens, so the value of restoring
work for someone who arrives later is not measured.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off · estimate | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| decay · estimate | 1,182<br><sub>543–1,673</sub> | 1,576<br><sub>912–2,003</sub> | 85.9<br><sub>72.6–94.9</sub> | 2.1<br><sub>2.0–2.2</sub> | 53<br><sub>39–73</sub> | 22<br><sub>6–44</sub> | 73<br><sub>44–98</sub> | 339<br><sub>61–434</sub> | 445<br><sub>273–749</sub> | 73<br><sub>56–91</sub> | 2<br><sub>0–5</sub> | 561<br><sub>409–653</sub> |
| decay · truth | 198<br><sub>39–359</sub> | 1,304<br><sub>943–1,755</sub> | 71.8<br><sub>51.5–88.3</sub> | 2.1<br><sub>2.0–2.4</sub> | 30<br><sub>18–50</sub> | 22<br><sub>6–44</sub> | 38<br><sub>20–49</sub> | 164<br><sub>46–255</sub> | 172<br><sub>53–399</sub> | 268<br><sub>174–413</sub> | 0 | 648<br><sub>576–691</sub> |
| decay, final · estimate | 894<br><sub>421–1,600</sub> | 1,723<br><sub>957–2,400</sub> | 58.6<br><sub>53.4–62.2</sub> | 12.7<br><sub>10.7–15.7</sub> | 31<br><sub>24–43</sub> | 22<br><sub>6–44</sub> | 71<br><sub>43–96</sub> | 350<br><sub>124–434</sub> | 1,221<br><sub>198–2,155</sub> | 72<br><sub>58–94</sub> | 2<br><sub>0–4</sub> | 548<br><sub>421–616</sub> |
| decay, final · truth | 90<br><sub>0–503</sub> | 2,261<br><sub>1,497–3,097</sub> | 40.1<br><sub>35.1–61.1</sub> | 15.4<br><sub>10.8–19.5</sub> | 15<br><sub>8–23</sub> | 22<br><sub>6–44</sub> | 54<br><sub>25–90</sub> | 214<br><sub>46–310</sub> | 158<br><sub>66–353</sub> | 1,742<br><sub>1,028–2,543</sub> | 0 | 640<br><sub>549–688</sub> |
| decay, restored exempt · estimate | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| decay, restored exempt · truth | 460<br><sub>162–861</sub> | 1,994<br><sub>1,542–2,283</sub> | 40.2<br><sub>35.3–61.1</sub> | 9.8<br><sub>5.1–13.1</sub> | 17<br><sub>12–24</sub> | 22<br><sub>6–44</sub> | 57<br><sub>30–93</sub> | 224<br><sub>46–355</sub> | 211<br><sub>96–478</sub> | 1,080<br><sub>415–1,617</sub> | 0 | 651<br><sub>586–693</sub> |
| decay, clock restarts · estimate | 911<br><sub>470–1,605</sub> | 1,685<br><sub>968–2,217</sub> | 62.5<br><sub>53.6–70.4</sub> | 8.7<br><sub>3.0–15.0</sub> | 33<br><sub>26–46</sub> | 22<br><sub>6–44</sub> | 76<br><sub>46–98</sub> | 350<br><sub>124–434</sub> | 1,345<br><sub>338–2,194</sub> | 74<br><sub>60–95</sub> | 2<br><sub>0–5</sub> | 568<br><sub>422–655</sub> |
| decay, clock restarts · truth | 123<br><sub>1–662</sub> | 2,142<br><sub>1,528–2,951</sub> | 46.9<br><sub>36.0–67.1</sub> | 8.5<br><sub>3.1–17.9</sub> | 17<br><sub>10–27</sub> | 22<br><sub>6–44</sub> | 56<br><sub>29–93</sub> | 216<br><sub>46–325</sub> | 201<br><sub>90–426</sub> | 1,065<br><sub>508–1,838</sub> | 0 | 648<br><sub>575–693</sub> |
| promote · estimate | 3,316<br><sub>2,068–5,350</sub> | 2,118<br><sub>1,530–2,737</sub> | 89.2<br><sub>83.3–99.9</sub> | 2.0 | 90<br><sub>64–122</sub> | 22<br><sub>6–44</sub> | 108<br><sub>75–206</sub> | 518<br><sub>360–932</sub> | 615<br><sub>401–835</sub> | 136<br><sub>91–227</sub> | 0 | 0 |
| promote · truth | 1,730<br><sub>1,011–2,167</sub> | 1,716<br><sub>998–2,167</sub> | 73.7<br><sub>56.8–88.9</sub> | 4.9<br><sub>2.0–12.4</sub> | 53<br><sub>43–66</sub> | 22<br><sub>6–44</sub> | 84<br><sub>69–108</sub> | 369<br><sub>192–464</sub> | 1,918<br><sub>818–4,760</sub> | 105<br><sub>77–146</sub> | 0 | 0 |
| promote, exempt · estimate | 3,552<br><sub>2,492–5,709</sub> | 2,178<br><sub>1,647–2,781</sub> | 74.4<br><sub>62.6–86.2</sub> | 2.2<br><sub>2.0–2.5</sub> | 80<br><sub>64–102</sub> | 22<br><sub>6–44</sub> | 116<br><sub>82–211</sub> | 525<br><sub>372–917</sub> | 777<br><sub>564–1,008</sub> | 143<br><sub>105–236</sub> | 0 | 0 |
| promote, exempt · truth | 1,734<br><sub>1,011–2,167</sub> | 1,716<br><sub>998–2,167</sub> | 61.1<br><sub>56.6–64.8</sub> | 9.8<br><sub>7.8–12.4</sub> | 52<br><sub>41–65</sub> | 22<br><sub>6–44</sub> | 86<br><sub>69–110</sub> | 369<br><sub>192–464</sub> | 4,096<br><sub>1,735–6,830</sub> | 129<br><sub>80–188</sub> | 0 | 0 |
| both · estimate | 2,482<br><sub>1,231–4,344</sub> | 1,981<br><sub>1,386–2,706</sub> | 87.9<br><sub>83.1–94.4</sub> | 2.0 | 79<br><sub>51–114</sub> | 22<br><sub>6–44</sub> | 97<br><sub>47–194</sub> | 440<br><sub>132–869</sub> | 361<br><sub>246–507</sub> | 106<br><sub>64–204</sub> | 3<br><sub>0–7</sub> | 546<br><sub>366–629</sub> |
| both · truth | 207<br><sub>39–368</sub> | 1,318<br><sub>949–1,763</sub> | 71.8<br><sub>51.3–88.3</sub> | 2.1<br><sub>2.0–2.3</sub> | 30<br><sub>18–47</sub> | 22<br><sub>6–44</sub> | 38<br><sub>20–48</sub> | 161<br><sub>46–255</sub> | 163<br><sub>53–367</sub> | 272<br><sub>175–413</sub> | 0 | 648<br><sub>574–691</sub> |
| both, exempt · estimate | 2,808<br><sub>1,762–4,692</sub> | 2,132<br><sub>1,656–2,785</sub> | 71.7<br><sub>65.3–82.6</sub> | 2.6<br><sub>2.0–3.9</sub> | 58<br><sub>39–88</sub> | 22<br><sub>6–44</sub> | 105<br><sub>58–201</sub> | 455<br><sub>162–887</sub> | 515<br><sub>316–756</sub> | 113<br><sub>73–210</sub> | 3<br><sub>0–6</sub> | 550<br><sub>368–637</sub> |
| both, exempt · truth | 475<br><sub>191–891</sub> | 2,024<br><sub>1,546–2,451</sub> | 40.1<br><sub>35.1–61.1</sub> | 9.8<br><sub>5.1–15.2</sub> | 18<br><sub>12–25</sub> | 22<br><sub>6–44</sub> | 58<br><sub>29–94</sub> | 206<br><sub>46–279</sub> | 201<br><sub>95–439</sub> | 1,105<br><sub>444–1,958</sub> | 0 | 650<br><sub>580–693</sub> |
| both, clock restarts · estimate | 1,606<br><sub>1,165–2,174</sub> | 2,119<br><sub>1,609–2,775</sub> | 77.1<br><sub>68.0–84.9</sub> | 2.1<br><sub>2.0–2.7</sub> | 57<br><sub>40–88</sub> | 22<br><sub>6–44</sub> | 102<br><sub>50–198</sub> | 449<br><sub>147–872</sub> | 488<br><sub>334–717</sub> | 109<br><sub>72–207</sub> | 3<br><sub>0–6</sub> | 546<br><sub>364–634</sub> |
| both, clock restarts · truth | 120<br><sub>3–608</sub> | 2,153<br><sub>1,551–2,951</sub> | 47.4<br><sub>36.0–69.3</sub> | 8.1<br><sub>2.5–17.9</sub> | 17<br><sub>10–25</sub> | 22<br><sub>6–44</sub> | 58<br><sub>29–94</sub> | 201<br><sub>46–268</sub> | 191<br><sub>90–397</sub> | 1,032<br><sub>305–1,838</sub> | 0 | 648<br><sub>573–693</sub> |

### Against off · estimate

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| decay · estimate | -30 % | -7 % | +41 % | -16 % | -91 % |
| decay · truth | -88 % | -23 % | +18 % | -56 % | -97 % |
| decay, final · estimate | -47 % | +2 % | -4 % | -18 % | -76 % |
| decay, final · truth | -95 % | +34 % | -34 % | -37 % | -97 % |
| decay, restored exempt · estimate | -24 % | -1 % | -4 % | -13 % | -78 % |
| decay, restored exempt · truth | -73 % | +18 % | -34 % | -34 % | -96 % |
| decay, clock restarts · estimate | -46 % | -0 % | +2 % | -13 % | -73 % |
| decay, clock restarts · truth | -93 % | +27 % | -23 % | -35 % | -96 % |
| promote · estimate | +97 % | +26 % | +46 % | +25 % | -88 % |
| promote · truth | +3 % | +2 % | +21 % | -4 % | -62 % |
| promote, exempt · estimate | +111 % | +29 % | +22 % | +34 % | -85 % |
| promote, exempt · truth | +3 % | +2 % | +0 % | -1 % | -18 % |
| both · estimate | +47 % | +17 % | +44 % | +12 % | -93 % |
| both · truth | -88 % | -22 % | +18 % | -56 % | -97 % |
| both, exempt · estimate | +67 % | +26 % | +17 % | +21 % | -90 % |
| both, exempt · truth | -72 % | +20 % | -34 % | -33 % | -96 % |
| both, clock restarts · estimate | -5 % | +26 % | +26 % | +18 % | -90 % |
| both, clock restarts · truth | -93 % | +28 % | -22 % | -33 % | -96 % |

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

Axes: **intent** (10); **knowledge** (2). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
