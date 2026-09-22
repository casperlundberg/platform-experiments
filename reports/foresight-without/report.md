# Decay when the mine knows only where people are

> How much of what decay did came from knowing where people would walk? The same days on simlab-api 4.0.0-dev, where a person is protected along every tunnel they could reach, against foresight-with.

36 runs: 9 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-22T08:20:12+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.7+6d90568 (`6d90568aab21`), built from clean checkouts of those commits, measured by platform-experiments 1.0.1-dev.1+3979e30 (`3979e30064e7`).

Regenerate with:

```bash
make -C platform-experiments sweep S=foresight-without
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `aa0ad84533cf484a…`.

## Reading

The same three calibrated days, seeds and autoscaler (2.0.0) as
[`foresight-with`](../foresight-with/report.md); the one difference is
simlab-api 4.0.0-dev, where the mine's own view protects a person along every
stretch of tunnel they could walk to over the lookahead (300 s at 1 m/s),
instead of along the route the simulator will walk them. Intent off and the
oracle arm come out byte for byte as they did on 3.0.0 — the change touches only
what the mine knows — so every difference below is the foresight.

**Without foresight, decay relaxes a little less, and keeps most of what it
bought.** Decay against no intent on the same day, with foresight → without:

| | Locate exposing | Process exposing | Breaches |
|---|---:|---:|---:|
| workday | −20 % → −17 % | −53 % → −57 % | +10,483 % → +8,731 % |
| rock burst | −23 % → −20 % | −82 % → −78 % | +7 % → +2 % |
| earthquake | −56 % → −50 % | −81 % → −66 % | −20 % → −20 % |

Knowing only where people are, the mine protects every way they could go, so
fewer events are decayed: 16 % fewer on the workday (1,885 → 1,578 a day), 7 %
under the rock burst, 2 % under the earthquake. Less relaxed work frees less
capacity for the events that matter, and that costs most where contention is
highest: under the earthquake, exposing events finish 77 % later than with
foresight (11,522 → 20,399 s) and are first located 15 % later (172 → 197 s).
Even so, decay without foresight still halves the time to locate them against no
intent, and finishes them in a third of the time.

**On a quiet day, less decay costs less.** Decay's known price on a day the
fleet keeps up with (see `scenario-shapes`) is breaches; relaxing fewer events
takes 17 % off it (1,720 → 1,435 a day).

**Misses barely move.** Exposing events decayed at some point, per day: 10.5 →
8.3 on the workday, 12.8 → 11.3 under the rock burst, 16.5 → 17.0 under the
earthquake. They come from estimates of where events are, not of where people
go.

**For the reports before simlab-api 4.0.0:** every one that protects people
credited the mine with this foresight. Under the earthquake it overstated how
much sooner decay finishes exposing events (81 % against 66 %), and slightly how
much sooner it locates them (56 % against 50 %); the breaches it saved were not
overstated.

**Caveats.** Four seeds; one mine and the default workforce (8 people, 4 crewed
and 3 autonomous vehicles); vehicles' routes are known in both reports, so only
people's foresight is measured. This report names platform-experiments
1.0.1-dev.1, for the reason given in `foresight-with`.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · off | 16<br><sub>9–30</sub> | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 59<br><sub>54–70</sub> | 46<br><sub>42–52</sub> | 140<br><sub>126–178</sub> | 2,218<br><sub>1,269–4,024</sub> | 48<br><sub>47–50</sub> | 0 | 0 |
| workday · decay | 1,435<br><sub>1,263–1,555</sub> | 3,797<br><sub>3,551–4,133</sub> | 45.0<br><sub>40.9–47.7</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 59<br><sub>54–70</sub> | 38<br><sub>36–42</sub> | 81<br><sub>59–107</sub> | 962<br><sub>485–1,745</sub> | 41<br><sub>40–42</sub> | 8<br><sub>4–12</sub> | 1,578<br><sub>1,548–1,599</sub> |
| workday · decay, oracle | 2,588<br><sub>2,214–2,949</sub> | 12,314<br><sub>11,815–13,138</sub> | 36.1<br><sub>31.5–38.0</sub> | 24.3<br><sub>24.0–24.6</sub> | 0 | 59<br><sub>54–70</sub> | 32<br><sub>31–34</sub> | 58<br><sub>52–70</sub> | 118<br><sub>113–127</sub> | 703<br><sub>558–823</sub> | 0 | 2,052<br><sub>2,021–2,091</sub> |
| rock burst · off | 6,338<br><sub>5,881–6,780</sub> | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 68<br><sub>57–76</sub> | 83<br><sub>61–105</sub> | 418<br><sub>151–686</sub> | 26,090<br><sub>20,947–32,281</sub> | 132<br><sub>125–145</sub> | 0 | 0 |
| rock burst · decay | 6,465<br><sub>6,053–7,040</sub> | 9,859<br><sub>9,767–9,949</sub> | 122.5<br><sub>118.1–129.8</sub> | 40.0<br><sub>32.8–44.8</sub> | 130<br><sub>124–138</sub> | 68<br><sub>57–76</sub> | 66<br><sub>52–80</sub> | 281<br><sub>110–644</sub> | 5,691<br><sub>2,717–8,110</sub> | 90<br><sub>85–100</sub> | 11<br><sub>5–15</sub> | 2,544<br><sub>2,445–2,623</sub> |
| rock burst · decay, oracle | 4,818<br><sub>4,489–5,375</sub> | 17,542<br><sub>17,133–17,891</sub> | 103.2<br><sub>97.5–106.1</sub> | 43.5<br><sub>40.4–48.2</sub> | 50<br><sub>42–58</sub> | 68<br><sub>57–76</sub> | 38<br><sub>35–41</sub> | 81<br><sub>70–112</sub> | 152<br><sub>130–167</sub> | 3,692<br><sub>3,179–4,210</sub> | 0 | 2,880<br><sub>2,830–2,920</sub> |
| earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 122<br><sub>97–151</sub> | 394<br><sub>153–545</sub> | 2,496<br><sub>730–3,254</sub> | 59,325<br><sub>56,268–64,092</sub> | 441<br><sub>399–485</sub> | 0 | 0 |
| earthquake · decay | 20,010<br><sub>18,350–21,917</sub> | 24,382<br><sub>22,395–26,077</sub> | 355.1<br><sub>343.5–382.8</sub> | 48.0<br><sub>47.7–48.2</sub> | 582<br><sub>498–759</sub> | 122<br><sub>97–151</sub> | 197<br><sub>53–330</sub> | 1,293<br><sub>176–2,025</sub> | 20,399<br><sub>7,883–38,395</sub> | 205<br><sub>151–277</sub> | 17<br><sub>9–25</sub> | 4,754<br><sub>4,691–4,838</sub> |
| earthquake · decay, oracle | 12,716<br><sub>11,188–14,371</sub> | 29,938<br><sub>28,160–31,601</sub> | 310.8<br><sub>301.9–322.2</sub> | 48.2<br><sub>48.1–48.3</sub> | 226<br><sub>156–264</sub> | 122<br><sub>97–151</sub> | 34<br><sub>30–42</sub> | 67<br><sub>44–123</sub> | 295<br><sub>160–567</sub> | 8,512<br><sub>7,876–9,467</sub> | 0 | 5,032<br><sub>4,979–5,138</sub> |

### Against off, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| workday · decay | +8731 % | +23268 % | -15 % | -17 % | -57 % |
| workday · decay, oracle | +15823 % | +75680 % | -32 % | -31 % | -95 % |
| rock burst · decay | +2 % | +56 % | -8 % | -20 % | -78 % |
| rock burst · decay, oracle | -24 % | +177 % | -23 % | -54 % | -99 % |
| earthquake · decay | -20 % | -2 % | -1 % | -50 % | -66 % |
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
