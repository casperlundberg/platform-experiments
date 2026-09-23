# How much the assumptions decide

> Two numbers in every use-case result are assumptions: how long after an event its zone still matters, and how long before the moment it matters a unit has to be told. Does what decay is worth to a decision survive changing them?

24 runs: 6 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-23T07:16:06+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.21+f7cc25b (`f7cc25b27a94`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.16+b45fc5e (`b45fc5ea0dbc`).

Regenerate with:

```bash
make -C platform-experiments sweep S=use-case-assumptions
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `5ccc1816080dfd40…`.

## Reading

Every use-case number in these reports rests on two assumptions, stated as such
since the cases were written and never varied: **the window** — how long after
an event its zone still matters to someone about to enter it — and **the
reaction time** — how long before that moment a unit has to be told, to act.
Scoring is post-hoc over what a run stored, so all nine combinations of three
windows and three reaction times are read from the same six arms: no extra
runs, and no arm scored under an assumption the others were not.

All nine are the strict measure — a **warning**, a location whose own zone,
widened by the 50 m allowance, actually reaches the unit.

**The assumptions move the level by twenty points.** On the workday, with
intent off:

| Window \ reaction | 15 s | 30 s | 120 s |
|---|---:|---:|---:|
| 10 min | 58.5 % | 56.5 % | 44.6 % |
| 30 min | 71.1 % | **70.3 %** | 65.1 % |
| 60 min | 77.6 % | 77.1 % | 74.0 % |

(30 min and 30 s are the defaults every other report uses.) A longer window
both raises the share and adds decisions — 292 at ten minutes, 735 at thirty,
1,276 at sixty — because the ones it adds are units entering later, with more
slack. A two-minute reaction costs 3 to 12 points, most at the short window,
where it is a fifth of the whole window.

**They do not move the conclusion.** What decay is worth, in points of
warned-in-time over intent off, across all nine:

| | workday | earthquake |
|---|---|---|
| decay − off | **+5.0 to +8.9** | +2.7 to +5.9 |
| oracle − off | +15.5 to +25.4 | +21.6 to +27.5 |
| decay's share of the oracle's gain | **30–35 %** | 10–21 % |

Nothing changes sign, the ordering off < decay < oracle holds in every cell,
and decay's share of what perfect knowledge would be worth is close to constant
— a third on the workday, a fifth or less under the earthquake. That is the
same finding the first use-case sweep reported at one setting of the
assumptions, and it survives varying them by a factor of six in window and
eight in reaction.

**Where the assumptions do bite is the absolute claim.** "Seven decisions in
ten have a warning in time" is a statement about a 30-minute window and a
30-second reaction, and it would be 45 % or 78 % under other defensible
choices. Any absolute share quoted from these sweeps has to carry both numbers
with it; the differences between arms do not.

**Caveats.** Four seeds, one mine, two days. The window and the reaction are
swept together here but the 50 m allowance is not — it is intent's own, and the
closure map is where it is varied.

## Results

| Arm | Breaches | 10 min, 15 s: decisions | 10 min, 15 s: in time | 10 min, 30 s: in time | 10 min, 120 s: in time | 30 min, 15 s: in time | 30 min, 30 s: in time | 30 min, 120 s: in time | 60 min, 15 s: in time | 60 min, 30 s: in time | 60 min, 120 s: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · off | 16<br><sub>9–30</sub> | 292<br><sub>277–320</sub> | 0.58<br><sub>0.53–0.61</sub> | 0.56<br><sub>0.51–0.60</sub> | 0.45<br><sub>0.41–0.49</sub> | 0.71<br><sub>0.66–0.74</sub> | 0.70<br><sub>0.65–0.74</sub> | 0.65<br><sub>0.61–0.69</sub> | 0.78<br><sub>0.70–0.83</sub> | 0.77<br><sub>0.70–0.83</sub> | 0.74<br><sub>0.67–0.79</sub> |
| workday · decay | 1,435<br><sub>1,263–1,555</sub> | 292<br><sub>277–320</sub> | 0.67<br><sub>0.66–0.71</sub> | 0.65<br><sub>0.63–0.70</sub> | 0.52<br><sub>0.48–0.60</sub> | 0.78<br><sub>0.76–0.81</sub> | 0.77<br><sub>0.74–0.80</sub> | 0.72<br><sub>0.68–0.76</sub> | 0.83<br><sub>0.80–0.85</sub> | 0.82<br><sub>0.80–0.85</sub> | 0.79<br><sub>0.76–0.82</sub> |
| workday · decay, oracle | 2,588<br><sub>2,214–2,949</sub> | 292<br><sub>277–320</sub> | 0.84<br><sub>0.80–0.86</sub> | 0.81<br><sub>0.77–0.84</sub> | 0.63<br><sub>0.60–0.66</sub> | 0.92<br><sub>0.90–0.94</sub> | 0.91<br><sub>0.89–0.93</sub> | 0.83<br><sub>0.81–0.85</sub> | 0.95<br><sub>0.94–0.96</sub> | 0.94<br><sub>0.93–0.96</sub> | 0.90<br><sub>0.87–0.91</sub> |
| earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 417<br><sub>325–583</sub> | 0.52<br><sub>0.49–0.57</sub> | 0.50<br><sub>0.47–0.55</sub> | 0.40<br><sub>0.36–0.45</sub> | 0.59<br><sub>0.56–0.64</sub> | 0.58<br><sub>0.55–0.64</sub> | 0.54<br><sub>0.51–0.60</sub> | 0.62<br><sub>0.59–0.66</sub> | 0.62<br><sub>0.59–0.66</sub> | 0.59<br><sub>0.56–0.63</sub> |
| earthquake · decay | 20,010<br><sub>18,350–21,917</sub> | 417<br><sub>325–583</sub> | 0.55<br><sub>0.52–0.61</sub> | 0.53<br><sub>0.49–0.59</sub> | 0.44<br><sub>0.41–0.50</sub> | 0.64<br><sub>0.61–0.70</sub> | 0.64<br><sub>0.60–0.70</sub> | 0.60<br><sub>0.56–0.66</sub> | 0.68<br><sub>0.66–0.72</sub> | 0.67<br><sub>0.65–0.72</sub> | 0.65<br><sub>0.63–0.70</sub> |
| earthquake · decay, oracle | 12,716<br><sub>11,188–14,371</sub> | 417<br><sub>325–583</sub> | 0.79<br><sub>0.72–0.85</sub> | 0.76<br><sub>0.69–0.82</sub> | 0.62<br><sub>0.57–0.68</sub> | 0.87<br><sub>0.80–0.92</sub> | 0.85<br><sub>0.79–0.91</sub> | 0.79<br><sub>0.74–0.85</sub> | 0.89<br><sub>0.84–0.94</sub> | 0.89<br><sub>0.84–0.93</sub> | 0.85<br><sub>0.81–0.89</sub> |

### Against off, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | 10 min, 15 s: in time | 10 min, 30 s: in time | 10 min, 120 s: in time | 30 min, 15 s: in time | 30 min, 30 s: in time | 30 min, 120 s: in time | 60 min, 15 s: in time | 60 min, 30 s: in time | 60 min, 120 s: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · decay | +15 % | +15 % | +16 % | +10 % | +10 % | +10 % | +7 % | +7 % | +7 % |
| workday · decay, oracle | +43 % | +43 % | +41 % | +30 % | +30 % | +28 % | +23 % | +23 % | +21 % |
| earthquake · decay | +5 % | +6 % | +8 % | +9 % | +9 % | +10 % | +9 % | +9 % | +10 % |
| earthquake · decay, oracle | +51 % | +51 % | +54 % | +46 % | +47 % | +46 % | +44 % | +44 % | +43 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **10 min, 15 s: decisions**: how many the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 15, "window_seconds": 600}`, the rest default) a run gave.
- **10 min, 15 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 15, "window_seconds": 600}`, the rest default) whose information arrived no later than the decision closed.
- **10 min, 30 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 30, "window_seconds": 600}`, the rest default) whose information arrived no later than the decision closed.
- **10 min, 120 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 120, "window_seconds": 600}`, the rest default) whose information arrived no later than the decision closed.
- **30 min, 15 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 15, "window_seconds": 1800}`, the rest default) whose information arrived no later than the decision closed.
- **30 min, 30 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 30, "window_seconds": 1800}`, the rest default) whose information arrived no later than the decision closed.
- **30 min, 120 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 120, "window_seconds": 1800}`, the rest default) whose information arrived no later than the decision closed.
- **60 min, 15 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 15, "window_seconds": 3600}`, the rest default) whose information arrived no later than the decision closed.
- **60 min, 30 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 30, "window_seconds": 3600}`, the rest default) whose information arrived no later than the decision closed.
- **60 min, 120 s: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning", "reaction_seconds": 120, "window_seconds": 3600}`, the rest default) whose information arrived no later than the decision closed.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **day** (2); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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

<sub>Tables rendered by platform-experiments `b45fc5ea0dbc`.</sub>
