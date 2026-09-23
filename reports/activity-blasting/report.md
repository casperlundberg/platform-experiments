# When the mine blasts

> A worked mine's seismicity follows its blasting: does when it blasts — at night as LKAB fires, in the day, spread through the night, or once — change what decay is worth to the decisions the mine has to make?

48 runs: 12 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-23T05:33:18+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.15+42e0e8a (`42e0e8a89901`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.8+a680c09 (`a680c09b5de1`).

Regenerate with:

```bash
make -C platform-experiments sweep S=activity-blasting
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `ebe6410726497fa3…`.

## Reading

The first sweep over a mine that is actually worked. Until now the day's
events were spread evenly along every production tunnel around the clock; here
they come from where mining puts them — half from around the four faces being
worked, a fifth background, and **three tenths from the blasts and the
sequences that decay after them** (modified Omori, p = 1, over twelve hours).
The day's total rate is unchanged at 91 events an hour, so this sweep varies
*when* the mine's seismicity happens, not how much of it there is. Crews are
cleared from the production areas 30 minutes before the first blast and re-enter
three hours after the last.

Four schedules, each 24 h × 4 seeds: **night, four blasts** (01:15–01:45 every
ten minutes, as LKAB fires at Kiruna), **day, four blasts** (13:00–13:30),
**through the night** (01:00–05:00, nine blasts half an hour apart) and **one a
day** (a single round at 01:15 carrying the whole day's blast share).

**The schedule decides whether there is a queue problem at all.**

| Schedule | Breaches, intent off | with decay | p95 time-to-locate, off |
|---|---:|---:|---:|
| night, four blasts | 33 | 514 | 125 s |
| day, four blasts | 51 | 566 | 128 s |
| through the night | 36 | 607 | 149 s |
| one a day | 2,186 | **1,470** | 210 s |

Spreading the round over four or nine blasts spreads the aftershock sequences
with it, and the fleet keeps up: a few dozen breaches a day, and decay costs
breaches exactly as it does on the calibrated quiet day — deferring harmless
work past its deadline to buy 5–19 % less cloud. Fire the whole round at once
and the same daily total arrives in one peak: 2,186 breaches. That is the first
schedule in any sweep where **decay reduces breaches on a calibrated workday**
(−33 %), and the oracle −65 %, because there is finally contention for it to
resolve. Blast scheduling is therefore a platform-capacity decision as much as a
ventilation one.

**What the decisions see.** Any location almost always arrives in time (91–94 %
of turn-back decisions), and neither the schedule nor the intent moves that
much. The measure that separates them is the **warning** — the first location
whose own zone, widened by the 50 m allowance for location error, reaches the
unit:

| Turn-back warned, in time | off | decay | oracle |
|---|---:|---:|---:|
| night, four blasts | 70 % | 76 % | 89 % |
| day, four blasts | 72 % | 75 % | 87 % |
| through the night | 74 % | 72 % | 88 % |
| one a day | **65 %** | **75 %** | 86 % |

The single round is both the worst day to be warned on (65 %) and the day decay
helps most (+9 pp, median warning latency 63 s → 52 s). Way-out warned moves
85 → 89 → 96 % and reroute warned 54 → 62 → 69 % on the same day. On the three
spread schedules decay adds 3–6 pp, and on *through the night* it adds nothing
at all (74 → 72 %) — there is no congestion, so reordering can only move work
about.

**When the mine blasts also decides who is exposed.** The schedules produce
different numbers of events that catch somebody inside a moderate zone, though
every day has the same 2,160 events:

| Schedule | Exposing events a day | Turn-back decisions | Way-out decisions |
|---|---:|---:|---:|
| through the night | **65** | 146 | 231 |
| night, four blasts | 88 | 176 | 298 |
| one a day | 96 | 212 | 307 |
| day, four blasts | **104** | 184 | 336 |

Blasting through the night keeps the production areas cleared across the whole
window and the busiest part of every sequence, and exposes a third fewer events
than blasting in the middle of the day shift — where the sequences decay with
crews back at the faces. This is a result about the mine, not about the
platform: it holds with intent off, and the platform can only make the best of
whichever schedule the mine keeps.

**At what price.** The oracle's cost is visible in the tail: it decays 2,045
events a day against decay's 1,610, and the p95 time-to-locate over *all* events
goes from 80–130 s to 1.6–2.2 h. Deferred harmless work is genuinely deferred;
what the run buys with it is the exposing events' p95 falling from 116 s to
52 s.

**Caveats.** Four seeds, one mine, one workforce, 4 faces worked and the
balanced mix throughout (`activity-shape` varies those). Clear and re-entry are
fixed at 30 min and 3 h; re-entry protocols in the surveyed mines run 2–12 h, and
case 7 will sweep them. Blast timing is exact and known; the application is not
yet told about it. A decision is scored on whether its information arrived, not
on what the mine then did.

## Results

| Arm | Breaches | Cloud h | Turn-back: decisions | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 s | Way-out: decisions | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Reroute: unwinnable | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| night, four blasts · off | 33<br><sub>7–62</sub> | 61.0<br><sub>56.0–65.6</sub> | 176<br><sub>126–260</sub> | 0.94<br><sub>0.89–0.97</sub> | 0.70<br><sub>0.64–0.73</sub> | 36<br><sub>35–37</sub> | 298<br><sub>272–325</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.88<br><sub>0.87–0.89</sub> | 0.76<br><sub>0.70–0.84</sub> | 0.57<br><sub>0.48–0.65</sub> | 37<br><sub>10–68</sub> | 0.94<br><sub>0.90–0.96</sub> |
| night, four blasts · decay | 514<br><sub>345–719</sub> | 57.9<br><sub>47.0–65.2</sub> | 176<br><sub>126–260</sub> | 0.93<br><sub>0.90–0.96</sub> | 0.76<br><sub>0.70–0.80</sub> | 33<br><sub>31–34</sub> | 298<br><sub>272–325</sub> | 0.98<br><sub>0.97–0.99</sub> | 0.92<br><sub>0.89–0.95</sub> | 0.76<br><sub>0.69–0.84</sub> | 0.61<br><sub>0.56–0.65</sub> | 37<br><sub>10–68</sub> | 0.93<br><sub>0.91–0.96</sub> |
| night, four blasts · decay, oracle | 678<br><sub>471–774</sub> | 46.5<br><sub>40.3–52.3</sub> | 176<br><sub>126–260</sub> | 0.93<br><sub>0.90–0.94</sub> | 0.89<br><sub>0.86–0.90</sub> | 31<br><sub>30–33</sub> | 298<br><sub>272–325</sub> | 0.98<br><sub>0.97–0.99</sub> | 0.98<br><sub>0.96–0.99</sub> | 0.74<br><sub>0.67–0.84</sub> | 0.69<br><sub>0.59–0.79</sub> | 37<br><sub>10–68</sub> | 0.94<br><sub>0.91–0.96</sub> |
| day, four blasts · off | 51<br><sub>7–115</sub> | 63.3<br><sub>59.6–68.3</sub> | 184<br><sub>101–267</sub> | 0.91<br><sub>0.88–0.95</sub> | 0.72<br><sub>0.66–0.76</sub> | 35<br><sub>30–37</sub> | 336<br><sub>286–394</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.88<br><sub>0.86–0.91</sub> | 0.75<br><sub>0.69–0.83</sub> | 0.58<br><sub>0.50–0.67</sub> | 44<br><sub>19–74</sub> | 0.93<br><sub>0.89–0.96</sub> |
| day, four blasts · decay | 566<br><sub>470–640</sub> | 57.8<br><sub>53.9–62.4</sub> | 184<br><sub>101–267</sub> | 0.92<br><sub>0.88–0.95</sub> | 0.75<br><sub>0.73–0.78</sub> | 32<br><sub>30–34</sub> | 336<br><sub>286–394</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.91<br><sub>0.88–0.94</sub> | 0.75<br><sub>0.69–0.83</sub> | 0.61<br><sub>0.56–0.68</sub> | 44<br><sub>19–74</sub> | 0.93<br><sub>0.89–0.96</sub> |
| day, four blasts · decay, oracle | 684<br><sub>480–831</sub> | 47.5<br><sub>44.8–50.5</sub> | 184<br><sub>101–267</sub> | 0.92<br><sub>0.89–0.95</sub> | 0.87<br><sub>0.85–0.89</sub> | 29<br><sub>27–31</sub> | 336<br><sub>286–394</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.97<br><sub>0.95–0.99</sub> | 0.75<br><sub>0.69–0.83</sub> | 0.70<br><sub>0.65–0.78</sub> | 44<br><sub>19–74</sub> | 0.94<br><sub>0.91–0.96</sub> |
| through the night · off | 36<br><sub>12–85</sub> | 63.1<br><sub>59.0–68.6</sub> | 146<br><sub>92–190</sub> | 0.91<br><sub>0.90–0.92</sub> | 0.73<br><sub>0.66–0.83</sub> | 35<br><sub>31–40</sub> | 231<br><sub>175–287</sub> | 0.97<br><sub>0.95–1.00</sub> | 0.94<br><sub>0.92–0.97</sub> | 0.79<br><sub>0.73–0.88</sub> | 0.63<br><sub>0.55–0.73</sub> | 25<br><sub>7–37</sub> | 0.90<br><sub>0.89–0.92</sub> |
| through the night · decay | 607<br><sub>371–779</sub> | 51.3<br><sub>43.4–55.5</sub> | 146<br><sub>92–190</sub> | 0.92<br><sub>0.91–0.93</sub> | 0.72<br><sub>0.69–0.78</sub> | 35<br><sub>30–39</sub> | 231<br><sub>175–287</sub> | 0.97<br><sub>0.96–1.00</sub> | 0.91<br><sub>0.86–0.94</sub> | 0.80<br><sub>0.74–0.87</sub> | 0.62<br><sub>0.57–0.67</sub> | 25<br><sub>7–37</sub> | 0.91<br><sub>0.89–0.95</sub> |
| through the night · decay, oracle | 699<br><sub>523–845</sub> | 40.8<br><sub>37.4–44.4</sub> | 146<br><sub>92–190</sub> | 0.92<br><sub>0.91–0.93</sub> | 0.88<br><sub>0.86–0.90</sub> | 31<br><sub>30–33</sub> | 231<br><sub>175–287</sub> | 0.97<br><sub>0.96–1.00</sub> | 0.97<br><sub>0.95–1.00</sub> | 0.79<br><sub>0.74–0.85</sub> | 0.71<br><sub>0.68–0.75</sub> | 25<br><sub>7–37</sub> | 0.92<br><sub>0.90–0.95</sub> |
| one a day · off | 2,186<br><sub>1,707–2,906</sub> | 59.3<br><sub>54.3–63.6</sub> | 212<br><sub>125–256</sub> | 0.91<br><sub>0.87–0.96</sub> | 0.65<br><sub>0.59–0.73</sub> | 37<br><sub>36–37</sub> | 307<br><sub>267–328</sub> | 0.96<br><sub>0.94–0.98</sub> | 0.85<br><sub>0.81–0.90</sub> | 0.76<br><sub>0.71–0.86</sub> | 0.54<br><sub>0.48–0.64</sub> | 44<br><sub>14–55</sub> | 0.91<br><sub>0.86–0.95</sub> |
| one a day · decay | 1,470<br><sub>991–2,306</sub> | 55.5<br><sub>47.1–59.5</sub> | 212<br><sub>125–256</sub> | 0.92<br><sub>0.90–0.94</sub> | 0.75<br><sub>0.70–0.79</sub> | 34<br><sub>32–36</sub> | 307<br><sub>267–328</sub> | 0.96<br><sub>0.94–0.98</sub> | 0.89<br><sub>0.86–0.93</sub> | 0.77<br><sub>0.70–0.86</sub> | 0.62<br><sub>0.56–0.73</sub> | 44<br><sub>14–55</sub> | 0.93<br><sub>0.89–0.95</sub> |
| one a day · decay, oracle | 774<br><sub>555–1,080</sub> | 45.9<br><sub>41.4–49.0</sub> | 212<br><sub>125–256</sub> | 0.92<br><sub>0.92–0.93</sub> | 0.86<br><sub>0.85–0.88</sub> | 29<br><sub>28–31</sub> | 307<br><sub>267–328</sub> | 0.97<br><sub>0.95–0.98</sub> | 0.96<br><sub>0.95–0.98</sub> | 0.76<br><sub>0.69–0.85</sub> | 0.69<br><sub>0.61–0.78</sub> | 44<br><sub>14–55</sub> | 0.94<br><sub>0.91–0.95</sub> |

### Against off, at the same blasting

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| night, four blasts · decay | +1444 % | -5 % | -0 % | +8 % | -7 % | +0 % | +4 % | +0 % | +7 % | -1 % |
| night, four blasts · decay, oracle | +1938 % | -24 % | -0 % | +26 % | -12 % | +1 % | +11 % | -2 % | +21 % | -0 % |
| day, four blasts · decay | +1009 % | -9 % | +1 % | +5 % | -9 % | +0 % | +3 % | +0 % | +5 % | +0 % |
| day, four blasts · decay, oracle | +1241 % | -25 % | +1 % | +22 % | -16 % | +1 % | +10 % | +0 % | +21 % | +1 % |
| through the night · decay | +1599 % | -19 % | +1 % | -2 % | -1 % | +0 % | -3 % | +0 % | -2 % | +1 % |
| through the night · decay, oracle | +1855 % | -35 % | +1 % | +20 % | -10 % | +0 % | +3 % | -1 % | +13 % | +1 % |
| one a day · decay | -33 % | -6 % | +1 % | +14 % | -7 % | -0 % | +4 % | +2 % | +15 % | +3 % |
| one a day · decay, oracle | -65 % | -23 % | +1 % | +32 % | -20 % | +0 % | +12 % | +0 % | +28 % | +4 % |

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

Axes: **blasting** (4); **intent** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
    "description": "A day. Job mix and duration follow the operational catalogue: 22.2 % associate (priority 100), 51.0 % locate (50) and 26.7 % pick (0), and a weighted mean execution time of 28 s.",
    "activity": {}
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

<sub>Tables rendered by platform-experiments `a680c09b5de1`.</sub>
