# How much notice a decision needs

> Scripted encounters give a unit a stated notice of high ground motion ahead of it. How much notice does the processing need for the decision to be made in time, and how much of that does ordering the queue by intent buy?

48 runs: 12 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-23T06:57:36+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.21+f7cc25b (`f7cc25b27a94`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.14+0d2630f (`0d2630fea455`).

Regenerate with:

```bash
make -C platform-experiments sweep S=encounter-lead
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `97cca34fd9e60cb1…`.

## Reading

The first sweep that sets the deadline instead of observing it. Forty
encounters are scripted into each calibrated day: an event of Nuttli 2.5
placed a zone's radius ahead of where a unit's own track is taking it, timed so
that unit reaches the edge of the high-ground-motion zone exactly the stated
notice after the event happens. Each is scored for the unit it was scripted
for and no other. Everything else is the workday as before — and the day's own
735 turn-back decisions are scored beside them, unchanged across every arm,
which is the control.

**A decision needs about two minutes of notice. Below that, nothing the
platform does matters.**

| Notice | Budget after a 30 s reaction | In time: off → decay → oracle |
|---|---:|---|
| 30 s | ~0 s | 0 → 0 → 0 % |
| 60 s | 30 s | 31 → 31 → **48 %** |
| 120 s | 90 s | 90 → **97** → 99 % |
| 300 s | 270 s | 100 → 100 → 100 % |

At 30 s the reaction time eats the whole notice and every one of the 40
decisions is lost however fast the queue runs — the median first location comes
30–39 s after the event, and the decision has already closed. At 300 s every
decision is won by every arm. **The platform's ordering only decides anything
in between**, and that window is narrow: one to five minutes of notice.

**Where in that window ordering pays is not where knowing pays.** At 60 s,
decay is worth nothing at all (31 % either way) while the oracle — the same
ordering told which events matter — is worth 17 points. At 120 s decay is worth
7 points and the oracle 9. The reason is in the latencies: the median first
location moves 37.9 → 37.2 s under decay, but 30.0 s under the oracle. Decay
reorders by what it can infer; when the budget is 30 s, inferring wrongly costs
the whole decision.

**A warning is much harder than a location, at every notice.** Scored on a
location whose own zone, widened by the 50 m allowance, actually reaches the
unit:

| Notice | Warned in time: off → decay → oracle |
|---|---|
| 60 s | 20 → 18 → 28 % |
| 120 s | 62 → 70 → **84 %** |
| 300 s | 73 → 84 → **98 %** |

Even with five minutes' notice, a mine reading its own estimates warns the unit
in time three times in four; the same processing told the truth warns it
essentially always. That gap — 25 points at 300 s, 22 at 120 s — is the cost of
imperfect hypocentres, not of slow processing, and it is the same gap the
closure map measures in ground.

**Rerouting needs far more notice than turning back.** A unit can wait or take
another path only until the last junction before the zone, which it passes long
before it reaches the zone itself:

| Notice | Reroute in time | Decisions that could not be won |
|---|---:|---:|
| 30 s | 0 % | 40 of 40 |
| 60 s | 0 % | 34 of 40 |
| 120 s | 30–36 % | 21 of 40 |
| 300 s | **73–74 %** | 9.5 of 40 |

At two minutes' notice half the reroute decisions are already unwinnable — the
unit is past its last junction when the event happens. This is a property of
the tunnels, not of the platform: no processing speed recovers them, and the
only remedy is to know sooner, which means predicting rather than reacting.

**The control held.** The day's own 735 turn-back decisions score 93.4–94.4 %
in time in every arm, moving only with intent (93.4 off → 93.8 decay → 94.4
oracle) and not at all with the notice axis — as they should, since scripting
an encounter does not touch them. **And the cost is the usual one**: 14–16
breaches a day with intent off against about 1,480 under decay and 2,730 under
the oracle, on a day with capacity to spare.

**Caveats.** Four seeds, one mine, one magnitude (2.5, whose high zone reaches
about 140 m). The reaction time is fixed at 30 s and the window at 30 min; both
are assumptions, swept separately. The scripted unit follows its track whatever
is decided — the closed loop is still to come — so "in time" means the
information arrived, not that anybody acted on it.

## Results

| Arm | Breaches | Cloud h | Encounter: decisions | Encounter: in time | Encounter: latency p50 s | Encounter: slack p50 s | Encounter warned: in time | Encounter reroute: in time | Encounter reroute: unwinnable | The day's own: decisions | The day's own: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 s · off | 14<br><sub>9–26</sub> | 55.6<br><sub>52.3–60.2</sub> | 40 | 0.00 | 39<br><sub>37–42</sub> | – | 0.00 | 0.00 | 40 | 735<br><sub>696–753</sub> | 0.93<br><sub>0.92–0.95</sub> |
| 30 s · decay | 1,477<br><sub>1,248–1,607</sub> | 47.5<br><sub>43.2–49.9</sub> | 40 | 0.00 | 36<br><sub>33–39</sub> | – | 0.00 | 0.00 | 40 | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |
| 30 s · decay, oracle | 2,719<br><sub>2,430–3,065</sub> | 38.2<br><sub>33.5–40.5</sub> | 40 | 0.00 | 31<br><sub>29–32</sub> | – | 0.00 | 0.00 | 40 | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |
| 60 s · off | 15<br><sub>10–28</sub> | 56.4<br><sub>53.4–62.1</sub> | 40 | 0.31<br><sub>0.17–0.45</sub> | 38<br><sub>31–43</sub> | 7<br><sub>5–9</sub> | 0.20<br><sub>0.10–0.28</sub> | 0.00 | 34 | 735<br><sub>696–753</sub> | 0.93<br><sub>0.92–0.95</sub> |
| 60 s · decay | 1,486<br><sub>1,333–1,581</sub> | 47.3<br><sub>43.2–49.8</sub> | 40 | 0.31<br><sub>0.20–0.40</sub> | 37<br><sub>35–39</sub> | 6<br><sub>4–8</sub> | 0.18<br><sub>0.12–0.23</sub> | 0.00 | 34 | 735<br><sub>696–753</sub> | 0.94<br><sub>0.92–0.95</sub> |
| 60 s · decay, oracle | 2,732<br><sub>2,453–3,037</sub> | 38.4<br><sub>34.1–40.4</sub> | 40 | 0.48<br><sub>0.38–0.55</sub> | 30<br><sub>27–33</sub> | 7<br><sub>6–9</sub> | 0.28<br><sub>0.17–0.38</sub> | 0.01<br><sub>0.00–0.03</sub> | 34 | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.96</sub> |
| 120 s · off | 16<br><sub>7–33</sub> | 56.3<br><sub>53.6–61.8</sub> | 40 | 0.90<br><sub>0.85–0.93</sub> | 35<br><sub>32–38</sub> | 56<br><sub>53–61</sub> | 0.62<br><sub>0.55–0.70</sub> | 0.30<br><sub>0.28–0.33</sub> | 21<br><sub>20–24</sub> | 735<br><sub>696–753</sub> | 0.93<br><sub>0.92–0.95</sub> |
| 120 s · decay | 1,449<br><sub>1,214–1,596</sub> | 47.5<br><sub>43.3–50.1</sub> | 40 | 0.97<br><sub>0.93–1.00</sub> | 34<br><sub>29–36</sub> | 56<br><sub>54–61</sub> | 0.70<br><sub>0.62–0.80</sub> | 0.32<br><sub>0.30–0.35</sub> | 21<br><sub>20–24</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |
| 120 s · decay, oracle | 2,720<br><sub>2,380–3,021</sub> | 38.4<br><sub>34.1–40.3</sub> | 40 | 0.99<br><sub>0.97–1.00</sub> | 31<br><sub>29–34</sub> | 59<br><sub>56–60</sub> | 0.84<br><sub>0.78–0.90</sub> | 0.36<br><sub>0.33–0.45</sub> | 21<br><sub>20–24</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |
| 300 s · off | 14<br><sub>5–30</sub> | 56.0<br><sub>52.8–59.4</sub> | 40 | 1.00 | 38<br><sub>36–39</sub> | 232<br><sub>230–234</sub> | 0.72<br><sub>0.62–0.80</sub> | 0.73<br><sub>0.65–0.82</sub> | 10<br><sub>6–12</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.92–0.95</sub> |
| 300 s · decay | 1,502<br><sub>1,268–1,641</sub> | 47.1<br><sub>42.9–49.6</sub> | 40 | 1.00 | 35<br><sub>31–38</sub> | 234<br><sub>232–237</sub> | 0.84<br><sub>0.78–0.90</sub> | 0.74<br><sub>0.68–0.85</sub> | 10<br><sub>6–12</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |
| 300 s · decay, oracle | 2,734<br><sub>2,415–3,027</sub> | 38.3<br><sub>33.8–40.4</sub> | 40 | 1.00 | 30<br><sub>27–34</sub> | 240<br><sub>235–242</sub> | 0.97<br><sub>0.95–1.00</sub> | 0.74<br><sub>0.68–0.85</sub> | 10<br><sub>6–12</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> |

### Against off, at the same notice

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Encounter: in time | Encounter warned: in time | Encounter: latency p50 | Encounter reroute: in time | The day's own: in time |
|---|---:|---:|---:|---:|---:|---:|
| 30 s · decay | +10088 % | – | – | -8 % | – | +0 % |
| 30 s · decay, oracle | +18650 % | – | – | -22 % | – | +1 % |
| 60 s · decay | +9978 % | +0 % | -9 % | -2 % | – | +0 % |
| 60 s · decay, oracle | +18422 % | +54 % | +41 % | -21 % | – | +1 % |
| 120 s · decay | +8955 % | +8 % | +13 % | -3 % | +6 % | +1 % |
| 120 s · decay, oracle | +16898 % | +10 % | +35 % | -11 % | +21 % | +1 % |
| 300 s · decay | +10257 % | +0 % | +16 % | -7 % | +2 % | +0 % |
| 300 s · decay, oracle | +18753 % | +0 % | +34 % | -21 % | +2 % | +1 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Encounter: decisions**: how many the `turn-back` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) a run gave.
- **Encounter: in time**: the share of the `turn-back` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) whose information arrived no later than the decision closed.
- **Encounter: latency p50 s**: the median seconds from the event to the information, over the `turn-back` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) that had it.
- **Encounter: slack p50 s**: the median seconds to spare, over the `turn-back` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) that had it in time.
- **Encounter warned: in time**: the share of the `turn-back` decisions (parameters `{"activity": "encounter", "level": "high", "need": "warning"}`, the rest default) whose information arrived no later than the decision closed.
- **Encounter reroute: in time**: the share of the `reroute` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) whose information arrived no later than the decision closed.
- **Encounter reroute: unwinnable**: the `reroute` decisions (parameters `{"activity": "encounter", "level": "high"}`, the rest default) that closed no later than they opened.
- **The day's own: decisions**: how many the `turn-back` decisions (parameters `{}`, the rest default) a run gave.
- **The day's own: in time**: the share of the `turn-back` decisions (parameters `{}`, the rest default) whose information arrived no later than the decision closed.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **notice** (4); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
    "description": "A day. Job mix and duration follow the operational catalogue: 22.2 % associate (priority 100), 51.0 % locate (50) and 26.7 % pick (0), and a weighted mean execution time of 28 s. Forty encounters are scripted into it: events placed where a unit is about to be, each giving that unit the stated notice of high ground motion.",
    "encounters": {
      "count": 40,
      "magnitude": 2.5,
      "level": "high"
    }
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

<sub>Tables rendered by platform-experiments `0d2630fea455`.</sub>
