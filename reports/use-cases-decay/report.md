# Decay against the decisions it is for

> Does decay get the information a mine's tactical decisions need to them in time — turning a unit back before it enters an event's zone, leading one out of it, rerouting before the last junction — more often than no intent, and how close does it come to the oracle?

36 runs: 9 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-22T09:00:20+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.10+25e3eb8 (`25e3eb87c28a`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.5+231d8d1 (`231d8d18d5c9`).

Regenerate with:

```bash
make -C platform-experiments sweep S=use-cases-decay
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `16d27f23f5f82ff7…`.

## Reading

The first time decay is measured against the decisions it is for rather than
against the queue. The three calibrated days on autoscaler 2.0.0 and
simlab-api 4.0.0-dev, where the mine knows where people are but not where they
will walk; each run scored for every decision of three kinds over an event's
true moderate zone: **turn-back** (a unit about to enter the zone must be told
before it does), **way-out** (one inside it must be told before it would have
left anyway) and **reroute** (one heading in must be told before the last
junction on the way). Each is scored twice: waiting on the event's **first
location**, and on a **warning** — the first location whose own zone, widened by
the 50 m allowance for location error, reaches the unit. The window (30 min
after the event) and the reaction time (30 s) are assumptions. The world is the
same in every arm: 735 turn-back decisions on the workday, 769 under the rock
burst and 1,140 under the earthquake, per day.

**Any location usually arrives in time, even with no intent.** The median first
location comes 36–38 s after the event, and a unit reaches a zone minutes later.

| Share in time: off → decay → oracle | turn-back | way-out | reroute |
|---|---:|---:|---:|
| workday | 93 → 94 → 95 % | 68 → 70 → 70 % | 83 → 84 → 83 % |
| rock burst | 92 → 94 → 95 % | 73 → 74 → 76 % | 83 → 84 → 84 % |
| earthquake | 85 → 89 → 94 % | 73 → 77 → 86 % | 76 → 80 → 83 % |

Decay helps where contention makes the tail late: under the earthquake it gets
four more turn-back decisions in a hundred their location in time, five more
reroutes and four more ways out. The oracle's ceiling is the same ordering
told the truth; it doubles those gains. Way-out stays lowest because a unit
already inside a zone often leaves within a minute, and reroute cannot rise
above what the tunnels allow: 13 % of reroute decisions come after the unit's
last junction and cannot be won by any processing.

**A location good enough to warn is much rarer in time, and there decay does
more.**

| Share in time, warned: off → decay → oracle | turn-back | way-out | reroute |
|---|---:|---:|---:|
| workday | 70 → 77 → 91 % | 58 → 61 → 68 % | 63 → 68 → 78 % |
| rock burst | 67 → 72 → 90 % | 60 → 63 → 74 % | 60 → 64 → 77 % |
| earthquake | 58 → 64 → 85 % | 62 → 67 → 83 % | 52 → 57 → 74 % |

A first location from four or five picks is often too far out for its zone to
reach the unit, and the warning waits for the final location — which is where
ordering matters: decay adds five to seven decisions in a hundred on every day,
and the oracle twenty more. **The gap between decay and the oracle is the
finding.** With locations good enough to act on as the measure, decay from the
mine's own estimates recovers about a quarter to a third of what perfect
knowledge of which events matter would (turn-back under the earthquake: 58 →
64 % against 85 %). What stands between is knowing sooner which events those
are, and how accurately they are located — not how fast processing is.

**Machines** (turn-back for the autonomous fleet only, use case 10) follow the
same pattern: 82 → 87 → 93 % under the earthquake.

**At what price.** The same arms' breaches and cloud time are the decay
findings already reported: on the quiet workday decay costs breaches (16 →
1,435 a day) for 15 % less cloud; under the earthquake it cuts breaches by a
fifth for the same cloud. The decisions it serves improve on every day.

**Caveats.** Four seeds, one mine, one workforce. The zone is the true moderate
zone; the window and reaction time are unswept assumptions, and the warning's
allowance is intent's own 50 m. A decision is scored on whether its information
arrived, not on what the mine then did — units follow their tracks whatever is
decided (the closed loop is still to come). Every unit's position is known
exactly; detection does not yet depend on distance or magnitude.

## Results

| Arm | Breaches | Cloud h | Turn-back: decisions | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 s | Way-out: decisions | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Reroute: unwinnable | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · off | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 735<br><sub>696–753</sub> | 0.93<br><sub>0.92–0.95</sub> | 0.70<br><sub>0.65–0.74</sub> | 37<br><sub>35–38</sub> | 78<br><sub>62–104</sub> | 0.68<br><sub>0.61–0.76</sub> | 0.58<br><sub>0.48–0.70</sub> | 0.83<br><sub>0.82–0.85</sub> | 0.63<br><sub>0.58–0.67</sub> | 98<br><sub>84–114</sub> | 0.93<br><sub>0.89–0.97</sub> |
| workday · decay | 1,435<br><sub>1,263–1,555</sub> | 45.0<br><sub>40.9–47.7</sub> | 735<br><sub>696–753</sub> | 0.94<br><sub>0.93–0.95</sub> | 0.77<br><sub>0.74–0.80</sub> | 35<br><sub>34–35</sub> | 78<br><sub>62–104</sub> | 0.70<br><sub>0.61–0.77</sub> | 0.61<br><sub>0.53–0.76</sub> | 0.84<br><sub>0.82–0.86</sub> | 0.68<br><sub>0.65–0.72</sub> | 98<br><sub>84–114</sub> | 0.93<br><sub>0.89–0.97</sub> |
| workday · decay, oracle | 2,588<br><sub>2,214–2,949</sub> | 36.1<br><sub>31.5–38.0</sub> | 735<br><sub>696–753</sub> | 0.95<br><sub>0.93–0.96</sub> | 0.91<br><sub>0.89–0.93</sub> | 31<br><sub>29–32</sub> | 78<br><sub>62–104</sub> | 0.70<br><sub>0.61–0.77</sub> | 0.68<br><sub>0.61–0.76</sub> | 0.83<br><sub>0.81–0.85</sub> | 0.78<br><sub>0.76–0.80</sub> | 98<br><sub>84–114</sub> | 0.94<br><sub>0.89–0.98</sub> |
| rock burst · off | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 769<br><sub>685–810</sub> | 0.92<br><sub>0.91–0.94</sub> | 0.67<br><sub>0.66–0.67</sub> | 36<br><sub>35–38</sub> | 98<br><sub>79–116</sub> | 0.73<br><sub>0.65–0.82</sub> | 0.60<br><sub>0.52–0.68</sub> | 0.83<br><sub>0.81–0.84</sub> | 0.60<br><sub>0.59–0.62</sub> | 100<br><sub>88–118</sub> | 0.92<br><sub>0.90–0.94</sub> |
| rock burst · decay | 6,465<br><sub>6,053–7,040</sub> | 122.5<br><sub>118.1–129.8</sub> | 769<br><sub>685–810</sub> | 0.94<br><sub>0.92–0.95</sub> | 0.72<br><sub>0.68–0.77</sub> | 35<br><sub>34–36</sub> | 98<br><sub>79–116</sub> | 0.74<br><sub>0.63–0.83</sub> | 0.63<br><sub>0.56–0.71</sub> | 0.84<br><sub>0.82–0.86</sub> | 0.64<br><sub>0.61–0.68</sub> | 100<br><sub>88–118</sub> | 0.94<br><sub>0.92–0.96</sub> |
| rock burst · decay, oracle | 4,818<br><sub>4,489–5,375</sub> | 103.2<br><sub>97.5–106.1</sub> | 769<br><sub>685–810</sub> | 0.95<br><sub>0.94–0.96</sub> | 0.90<br><sub>0.87–0.92</sub> | 30<br><sub>30–31</sub> | 98<br><sub>79–116</sub> | 0.75<br><sub>0.69–0.83</sub> | 0.74<br><sub>0.66–0.82</sub> | 0.83<br><sub>0.83–0.84</sub> | 0.77<br><sub>0.75–0.80</sub> | 100<br><sub>88–118</sub> | 0.94<br><sub>0.92–0.96</sub> |
| earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 1,140<br><sub>914–1,608</sub> | 0.85<br><sub>0.80–0.89</sub> | 0.58<br><sub>0.55–0.64</sub> | 38<br><sub>37–39</sub> | 217<br><sub>171–263</sub> | 0.73<br><sub>0.65–0.78</sub> | 0.62<br><sub>0.55–0.67</sub> | 0.76<br><sub>0.73–0.81</sub> | 0.52<br><sub>0.49–0.57</sub> | 139<br><sub>102–198</sub> | 0.82<br><sub>0.77–0.90</sub> |
| earthquake · decay | 20,010<br><sub>18,350–21,917</sub> | 355.1<br><sub>343.5–382.8</sub> | 1,140<br><sub>914–1,608</sub> | 0.89<br><sub>0.83–0.92</sub> | 0.64<br><sub>0.60–0.70</sub> | 35<br><sub>34–37</sub> | 217<br><sub>171–263</sub> | 0.77<br><sub>0.71–0.82</sub> | 0.67<br><sub>0.61–0.73</sub> | 0.80<br><sub>0.77–0.84</sub> | 0.57<br><sub>0.52–0.63</sub> | 139<br><sub>102–198</sub> | 0.87<br><sub>0.80–0.92</sub> |
| earthquake · decay, oracle | 12,716<br><sub>11,188–14,371</sub> | 310.8<br><sub>301.9–322.2</sub> | 1,140<br><sub>914–1,608</sub> | 0.94<br><sub>0.92–0.96</sub> | 0.85<br><sub>0.79–0.91</sub> | 28<br><sub>27–29</sub> | 217<br><sub>171–263</sub> | 0.86<br><sub>0.83–0.87</sub> | 0.83<br><sub>0.81–0.86</sub> | 0.83<br><sub>0.78–0.86</sub> | 0.74<br><sub>0.67–0.79</sub> | 139<br><sub>102–198</sub> | 0.93<br><sub>0.89–0.95</sub> |

### Against off, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · decay | +8731 % | -15 % | +1 % | +10 % | -4 % | +2 % | +5 % | +1 % | +9 % | +0 % |
| workday · decay, oracle | +15823 % | -32 % | +1 % | +30 % | -16 % | +3 % | +19 % | -0 % | +24 % | +1 % |
| rock burst · decay | +2 % | -8 % | +2 % | +8 % | -4 % | +1 % | +6 % | +2 % | +7 % | +1 % |
| rock burst · decay, oracle | -24 % | -23 % | +2 % | +35 % | -17 % | +4 % | +23 % | +1 % | +29 % | +1 % |
| earthquake · decay | -20 % | -1 % | +5 % | +9 % | -6 % | +6 % | +7 % | +5 % | +10 % | +6 % |
| earthquake · decay, oracle | -49 % | -13 % | +11 % | +47 % | -25 % | +17 % | +33 % | +9 % | +43 % | +14 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Turn-back: decisions**: how many the `turn-back` decisions (parameters `{}`, the rest default) a run gave.
- **Turn-back: in time**: the share of the `turn-back` decisions (parameters `{}`, the rest default) whose information arrived no later than the decision closed.
- **Turn-back warned: in time**: the share of the `turn-back` decisions (parameters `{"need": "warning"}`, the rest default) whose information arrived no later than the decision closed.
- **Turn-back: latency p50 s**: the median seconds from the event to the information, over the `turn-back` decisions (parameters `{}`, the rest default) that had it.
- **Way-out: decisions**: how many the `way-out` decisions (parameters `{}`, the rest default) a run gave.
- **Way-out: in time**: the share of the `way-out` decisions (parameters `{}`, the rest default) whose information arrived no later than the decision closed.
- **Way-out warned: in time**: the share of the `way-out` decisions (parameters `{"need": "warning"}`, the rest default) whose information arrived no later than the decision closed.
- **Reroute: in time**: the share of the `reroute` decisions (parameters `{}`, the rest default) whose information arrived no later than the decision closed.
- **Reroute warned: in time**: the share of the `reroute` decisions (parameters `{"need": "warning"}`, the rest default) whose information arrived no later than the decision closed.
- **Reroute: unwinnable**: the `reroute` decisions (parameters `{}`, the rest default) that closed no later than they opened.
- **Machines: in time**: the share of the `turn-back` decisions (parameters `{"kinds": ["autonomous-vehicle"]}`, the rest default) whose information arrived no later than the decision closed.
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

<sub>Tables rendered by platform-experiments `231d8d18d5c9`.</sub>
