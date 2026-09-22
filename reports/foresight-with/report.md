# Decay when the mine knows where people will walk

> What does decay do when the mine is credited with each person's route over the lookahead, as simlab-api did before 4.0.0?

36 runs: 9 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-22T08:08:20+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 3.0.0 (`1dcaed0addff`), built from clean checkouts of those commits, measured by platform-experiments 1.0.1-dev.1+3979e30 (`3979e30064e7`).

Regenerate with:

```bash
make -C platform-experiments sweep S=foresight-with
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `53c7a8affefa1b32…`.

## Reading

The reference for [`foresight-without`](../foresight-without/report.md): the
three calibrated days on simlab-api 3.0.0, whose planner protected a person
along the route the simulator would walk them over the lookahead — a foresight
no mine has — and autoscaler 2.0.0. Its reading is there, next to the numbers
it is compared with.

**Caveat.** This report names platform-experiments 1.0.1-dev.1: it began before
the 1.1.0 section of the changelog existed, so its label says patch where the
changelog says minor. No number depends on that label.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · off | 16<br><sub>9–30</sub> | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 59<br><sub>54–70</sub> | 46<br><sub>42–52</sub> | 140<br><sub>126–178</sub> | 2,218<br><sub>1,269–4,024</sub> | 48<br><sub>47–50</sub> | 0 | 0 |
| workday · decay | 1,720<br><sub>1,284–1,912</sub> | 4,442<br><sub>3,958–4,899</sub> | 44.0<br><sub>40.3–46.1</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 59<br><sub>54–70</sub> | 37<br><sub>35–40</sub> | 76<br><sub>58–99</sub> | 1,042<br><sub>474–1,676</sub> | 40<br><sub>39–40</sub> | 10<br><sub>4–15</sub> | 1,884<br><sub>1,810–1,920</sub> |
| workday · decay, oracle | 2,588<br><sub>2,214–2,949</sub> | 12,314<br><sub>11,815–13,138</sub> | 36.1<br><sub>31.5–38.0</sub> | 24.3<br><sub>24.0–24.6</sub> | 0 | 59<br><sub>54–70</sub> | 32<br><sub>31–34</sub> | 58<br><sub>52–70</sub> | 118<br><sub>113–127</sub> | 703<br><sub>558–823</sub> | 0 | 2,052<br><sub>2,021–2,091</sub> |
| rock burst · off | 6,338<br><sub>5,881–6,780</sub> | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 68<br><sub>57–76</sub> | 83<br><sub>61–105</sub> | 418<br><sub>151–686</sub> | 26,090<br><sub>20,947–32,281</sub> | 132<br><sub>125–145</sub> | 0 | 0 |
| rock burst · decay | 6,810<br><sub>6,131–7,489</sub> | 10,400<br><sub>10,295–10,518</sub> | 121.6<br><sub>119.3–122.7</sub> | 38.5<br><sub>31.6–45.8</sub> | 130<br><sub>117–151</sub> | 68<br><sub>57–76</sub> | 64<br><sub>51–77</sub> | 275<br><sub>111–644</sub> | 4,640<br><sub>3,669–5,368</sub> | 86<br><sub>80–91</sub> | 13<br><sub>8–17</sub> | 2,747<br><sub>2,724–2,772</sub> |
| rock burst · decay, oracle | 4,818<br><sub>4,489–5,375</sub> | 17,542<br><sub>17,133–17,891</sub> | 103.2<br><sub>97.5–106.1</sub> | 43.5<br><sub>40.4–48.2</sub> | 50<br><sub>42–58</sub> | 68<br><sub>57–76</sub> | 38<br><sub>35–41</sub> | 81<br><sub>70–112</sub> | 152<br><sub>130–167</sub> | 3,692<br><sub>3,179–4,210</sub> | 0 | 2,880<br><sub>2,830–2,920</sub> |
| earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 122<br><sub>97–151</sub> | 394<br><sub>153–545</sub> | 2,496<br><sub>730–3,254</sub> | 59,325<br><sub>56,268–64,092</sub> | 441<br><sub>399–485</sub> | 0 | 0 |
| earthquake · decay | 20,038<br><sub>17,848–22,443</sub> | 24,838<br><sub>22,254–26,747</sub> | 363.7<br><sub>344.0–387.4</sub> | 47.0<br><sub>43.6–48.2</sub> | 537<br><sub>421–678</sub> | 122<br><sub>97–151</sub> | 172<br><sub>47–310</sub> | 1,127<br><sub>165–1,920</sub> | 11,522<br><sub>5,371–21,503</sub> | 168<br><sub>118–250</sub> | 16<br><sub>12–22</sub> | 4,849<br><sub>4,793–4,929</sub> |
| earthquake · decay, oracle | 12,716<br><sub>11,188–14,371</sub> | 29,938<br><sub>28,160–31,601</sub> | 310.8<br><sub>301.9–322.2</sub> | 48.2<br><sub>48.1–48.3</sub> | 226<br><sub>156–264</sub> | 122<br><sub>97–151</sub> | 34<br><sub>30–42</sub> | 67<br><sub>44–123</sub> | 295<br><sub>160–567</sub> | 8,512<br><sub>7,876–9,467</sub> | 0 | 5,032<br><sub>4,979–5,138</sub> |

### Against off, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| workday · decay | +10483 % | +27232 % | -17 % | -20 % | -53 % |
| workday · decay, oracle | +15823 % | +75680 % | -32 % | -31 % | -95 % |
| rock burst · decay | +7 % | +64 % | -9 % | -23 % | -82 % |
| rock burst · decay, oracle | -24 % | +177 % | -23 % | -54 % | -99 % |
| earthquake · decay | -20 % | -1 % | +2 % | -56 % | -81 % |
| earthquake · decay, oracle | -49 % | +20 % | -13 % | -91 % | -100 % |

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

Axes: **day** (3); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
    "decision_interval_seconds": 15,
    "horizon_seconds": 900,
    "simulation_step_seconds": 15,
    "deadline_seconds_by_priority": {
      "400": 30,
      "100": 60,
      "50": 300,
      "25": 43200,
      "0": 86400
    },
    "default_deadline_seconds": 86400,
    "local_executor_cap": 12,
    "cloud_executor_cap": 60,
    "min_local_executors": 1,
    "local_coldstart_seconds": 60,
    "cloud_coldstart_seconds": 180,
    "scale_up_cooldown_seconds": 0,
    "max_scale_up_step": 50,
    "local_scale_down_window_seconds": 900,
    "cloud_scale_down_window_seconds": 300,
    "cloud_min_lifetime_seconds": 600,
    "safety_factor": 1.15,
    "dry_run": false
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
    "decay_to": -1,
    "promote_to": 400,
    "deadline_from": "arrival",
    "restore": true,
    "burst_exempt": [
      "restored"
    ]
  },
  "run": {
    "decision_interval_seconds": 15
  }
}
```

Per-seed figures, with every measured column, are in [`runs.csv`](runs.csv).

<sub>Tables rendered by platform-experiments `675e96958016`.</sub>
