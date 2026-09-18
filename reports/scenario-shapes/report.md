# A workday, a rock burst and an earthquake

> Does intent still pay on a normal day's workload, and on a day with a medium earthquake rather than a single rock burst?

48 runs: 12 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-18T05:44:54+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.1 (`b47790adfee0`), built from clean checkouts of those commits, measured by platform-experiments `3eb4eaf9f448`.

Regenerate with:

```bash
make -C platform-experiments sweep S=scenario-shapes
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `706af6b688c8ac4a…`.

## Reading

Three days on one mine fitted to an operational catalogue
([`docs/calibration.md`](../docs/calibration.md)): a normal workday of about
40,000 jobs, the same day with a rock burst (55,000), and the same day with a
medium earthquake — a Nuttli 4 main shock and a six-hour aftershock tail
(93,000). Each is a 24-hour day with 59 to 123 events that truly exposed
someone, against 6 to 44 in the two-hour scenario the earlier sweeps used.

**Intent's value follows contention, and on a quiet day it is a cost.**

| | Breaches vs no intent | Cloud h | Locate exposing |
|---|---:|---:|---:|
| workday | **+2,281 %** (49 → 1,161) | −3 % | −20 % |
| rock burst | −8 % (6,164 → 5,669) | −16 % | −22 % |
| earthquake | −27 % (20,661 → 15,054) | −1 % | −57 % |

On the workday the fleet keeps up on its own — 49 breaches in a day — and
anything intent relaxes is work that would have been served on time. It shows
up as a hundredfold rise in breaches off a tiny base, and as 4,800 jobs past the
deadline they arrived with. Under the earthquake the same settings cut breaches
by a quarter and more than halve the wait for a location on events that exposed
someone, at no extra cloud time. The mid-run-switch sweep already showed intent
can be switched on at the burst and off after; these numbers say when it is
worth doing.

**Decayed work needs a level of its own.** The arms differ only in `decay_to`:
0, which this job mix also submits a quarter of its work at, against −1, below
everything.

| Finish exposing events | no intent | decay to 0 | decay to its own level |
|---|---:|---:|---:|
| workday | 1,566 s | 2,151 s | **760 s** |
| rock burst | 6,421 s | 9,047 s | **1,767 s** |
| earthquake | 49,439 s | 46,657 s | **7,154 s** |

Decaying into a level that carries submitted work puts relaxed work in front of
the low-priority picks of the very events intent kept, and those events then
finish *later* than with no intent at all. Below the floor they finish five to
seven times sooner, for the same breaches and slightly less cloud time. This is
why simlab-api 3.0.0 decays to −1 by default; the arms here are pinned to the
old and new values, so both are on the record.

**The earlier sweeps are not wrong, but they were lucky.** Their mix submitted
nothing below priority 25, so decaying to 0 was already below everything, and
the collision could not appear. A job mix from a real pipeline found it in its
first run.

**Promotion** still buys the fastest finish for exposing events on every shape
and still costs breaches and cloud time, except under the earthquake where its
first locations are also better than no intent (−44 %).

**Caveats.** Four seeds. One mine, one workforce, one array. The earthquake is a
main shock of Nuttli 4 with aftershocks capped 1.5 below it, which is the first
scenario here where very high ground motion occurs at all — and it reaches only
one or two events per day, so promotion at that level is still barely tested.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · off | 49<br><sub>39–58</sub> | 49<br><sub>39–58</sub> | 160.4<br><sub>124.8–195.3</sub> | 25.2<br><sub>24.0–28.3</sub> | 8<br><sub>4–12</sub> | 59<br><sub>54–70</sub> | 48<br><sub>47–49</sub> | 159<br><sub>143–193</sub> | 1,567<br><sub>522–4,285</sub> | 51<br><sub>49–52</sub> | 0 | 0 |
| workday · decay, restored exempt | 1,160<br><sub>849–1,651</sub> | 4,782<br><sub>4,562–5,040</sub> | 155.3<br><sub>128.3–180.7</sub> | 24.5<br><sub>24.0–26.1</sub> | 7<br><sub>5–9</sub> | 59<br><sub>54–70</sub> | 39<br><sub>37–41</sub> | 97<br><sub>75–122</sub> | 2,151<br><sub>1,120–4,521</sub> | 41<br><sub>40–42</sub> | 10<br><sub>4–12</sub> | 2,004<br><sub>1,956–2,058</sub> |
| workday · decay to its own level | 1,650<br><sub>1,193–2,060</sub> | 5,034<br><sub>4,578–5,641</sub> | 141.2<br><sub>94.4–161.3</sub> | 24.4<br><sub>24.0–25.4</sub> | 6<br><sub>4–8</sub> | 59<br><sub>54–70</sub> | 40<br><sub>37–44</sub> | 106<br><sub>75–159</sub> | 760<br><sub>462–1,029</sub> | 41<br><sub>40–43</sub> | 11<br><sub>9–13</sub> | 1,867<br><sub>1,814–1,904</sub> |
| workday · both, exempt | 2,144<br><sub>1,795–2,818</sub> | 3,862<br><sub>3,550–4,289</sub> | 270.1<br><sub>229.6–303.1</sub> | 24.0 | 16<br><sub>11–29</sub> | 59<br><sub>54–70</sub> | 38<br><sub>31–41</sub> | 93<br><sub>69–122</sub> | 518<br><sub>346–828</sub> | 40<br><sub>39–41</sub> | 9<br><sub>8–11</sub> | 1,882<br><sub>1,837–1,901</sub> |
| rock burst · off | 6,164<br><sub>5,764–6,592</sub> | 6,164<br><sub>5,764–6,592</sub> | 258.3<br><sub>245.9–287.8</sub> | 24.0<br><sub>24.0–24.1</sub> | 206<br><sub>196–219</sub> | 68<br><sub>57–76</sub> | 83<br><sub>58–108</sub> | 433<br><sub>164–701</sub> | 6,421<br><sub>3,846–10,283</sub> | 134<br><sub>126–144</sub> | 0 | 0 |
| rock burst · decay, restored exempt | 5,669<br><sub>5,284–6,455</sub> | 10,140<br><sub>9,761–10,479</sub> | 216.6<br><sub>186.1–275.6</sub> | 30.5<br><sub>24.0–37.9</sub> | 114<br><sub>105–121</sub> | 68<br><sub>57–76</sub> | 64<br><sub>50–81</sub> | 281<br><sub>100–674</sub> | 9,048<br><sub>7,052–12,655</sub> | 85<br><sub>79–92</sub> | 12<br><sub>9–15</sub> | 2,824<br><sub>2,791–2,856</sub> |
| rock burst · decay to its own level | 5,778<br><sub>5,664–6,025</sub> | 10,171<br><sub>9,919–10,430</sub> | 216.9<br><sub>196.7–254.1</sub> | 26.5<br><sub>24.0–30.3</sub> | 118<br><sub>111–126</sub> | 68<br><sub>57–76</sub> | 63<br><sub>50–77</sub> | 270<br><sub>100–614</sub> | 1,766<br><sub>833–2,588</sub> | 84<br><sub>78–92</sub> | 12<br><sub>11–17</sub> | 2,694<br><sub>2,643–2,720</sub> |
| rock burst · both, exempt | 7,112<br><sub>6,348–7,840</sub> | 9,226<br><sub>8,891–9,742</sub> | 340.7<br><sub>291.3–409.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 144<br><sub>135–151</sub> | 68<br><sub>57–76</sub> | 64<br><sub>43–81</sub> | 268<br><sub>75–644</sub> | 1,256<br><sub>919–1,642</sub> | 86<br><sub>80–98</sub> | 10<br><sub>8–12</sub> | 2,696<br><sub>2,685–2,712</sub> |
| earthquake · off | 20,661<br><sub>19,545–21,464</sub> | 20,661<br><sub>19,545–21,464</sub> | 523.5<br><sub>498.6–537.6</sub> | 44.6<br><sub>41.5–48.0</sub> | 766<br><sub>722–799</sub> | 122<br><sub>97–151</sub> | 393<br><sub>154–547</sub> | 2,503<br><sub>730–3,284</sub> | 49,439<br><sub>45,905–55,546</sub> | 438<br><sub>397–475</sub> | 0 | 0 |
| earthquake · decay, restored exempt | 15,054<br><sub>12,059–19,208</sub> | 21,578<br><sub>19,834–24,666</sub> | 516.3<br><sub>505.8–526.2</sub> | 46.2<br><sub>45.4–46.9</sub> | 463<br><sub>397–602</sub> | 122<br><sub>97–151</sub> | 170<br><sub>46–306</sub> | 1,128<br><sub>166–1,920</sub> | 46,657<br><sub>36,115–53,262</sub> | 171<br><sub>112–249</sub> | 17<br><sub>8–24</sub> | 4,885<br><sub>4,818–4,939</sub> |
| earthquake · decay to its own level | 15,271<br><sub>12,491–19,037</sub> | 21,402<br><sub>19,608–24,520</sub> | 520.4<br><sub>506.7–534.7</sub> | 42.7<br><sub>39.0–46.5</sub> | 471<br><sub>410–599</sub> | 122<br><sub>97–151</sub> | 171<br><sub>46–308</sub> | 1,132<br><sub>150–1,935</sub> | 7,154<br><sub>2,394–15,080</sub> | 166<br><sub>113–250</sub> | 16<br><sub>7–21</sub> | 4,818<br><sub>4,752–4,919</sub> |
| earthquake · both, exempt | 23,210<br><sub>18,730–29,527</sub> | 22,790<br><sub>21,583–25,789</sub> | 566.2<br><sub>557.1–580.7</sub> | 24.2<br><sub>24.0–24.6</sub> | 585<br><sub>475–787</sub> | 122<br><sub>97–151</sub> | 220<br><sub>58–430</sub> | 1,366<br><sub>179–2,572</sub> | 8,071<br><sub>7,602–8,432</sub> | 217<br><sub>134–367</sub> | 17<br><sub>10–26</sub> | 4,740<br><sub>4,674–4,779</sub> |

### Against off, at the same shape

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| workday · decay, restored exempt | +2281 % | +9710 % | -3 % | -20 % | +37 % |
| workday · decay to its own level | +3284 % | +10226 % | -12 % | -17 % | -51 % |
| workday · both, exempt | +4297 % | +7822 % | +68 % | -21 % | -67 % |
| rock burst · decay, restored exempt | -8 % | +65 % | -16 % | -22 % | +41 % |
| rock burst · decay to its own level | -6 % | +65 % | -16 % | -23 % | -72 % |
| rock burst · both, exempt | +15 % | +50 % | +32 % | -23 % | -80 % |
| earthquake · decay, restored exempt | -27 % | +4 % | -1 % | -57 % | -6 % |
| earthquake · decay to its own level | -26 % | +4 % | -1 % | -57 % | -86 % |
| earthquake · both, exempt | +12 % | +10 % | +8 % | -44 % | -84 % |

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

Axes: **shape** (3); **intent** (4). Each arm's own intent, settings and scenario changes are in `sweep.json`.

```json
{
  "mine": {
    "id": "workday",
    "name": "Workday mine",
    "sensors": 30,
    "background_rate_per_hour": 91,
    "description": "Calibrated to an operational seismic-processing catalogue: 30 sensors and 91 events an hour give about 1,680 pick jobs an hour, against the 1,644 an hour that catalogue averages on a typical day."
  },
  "scenario": {
    "duration_seconds": 86400,
    "job_seconds": 28,
    "pick_jitter_seconds": 0.005,
    "priority_mix": {
      "100": 22.2,
      "50": 51.0,
      "0": 26.7
    },
    "description": "A day. Job mix and duration follow the operational catalogue: 22.2 % associate (priority 100), 51.0 % locate (50) and 26.7 % pick (0), and a weighted mean execution time of 28 s."
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

<sub>Tables rendered by platform-experiments `3eb4eaf9f448`.</sub>
