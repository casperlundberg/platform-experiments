# How much of the mine is being worked

> Where the events are decides how much decay can relax: does the number of faces worked at once, and how much of the day's seismicity comes from blasting rather than from the working faces, change what decay is worth?

72 runs: 18 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-23T05:46:36+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.15+42e0e8a (`42e0e8a89901`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.8+a680c09 (`a680c09b5de1`).

Regenerate with:

```bash
make -C platform-experiments sweep S=activity-shape
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `a82fd2229ac3296f…`.

## Reading

The same worked mine, with the two things about *how* it is worked that the
activity model exposes: how many faces are worked at once (2, 4 or 8, rotating
each 12-hour shift), and where the day's seismicity comes from — **mostly
blasting** (0.6 blast / 0.3 work / 0.1 background), **balanced** (0.3 / 0.5 /
0.2) or **mostly working** (0.1 / 0.7 / 0.2). The night schedule (four blasts,
01:15–01:45) and the 91 events an hour are the same in all eighteen arms, so
again only *where and when* the day's events fall changes.

**The mix is the load.** A blast's events are drawn from an Omori sequence, so
the more of the day comes from blasting, the more of it arrives in the hour
after 01:15:

| Mix | Breaches, off | with decay | Cloud h, off | with decay |
|---|---:|---:|---:|---:|
| mostly blasting | 1,774 | **1,246–1,338** | 89.2 | 90.5–92.5 |
| balanced | 33 | 514–637 | 61.0 | 56.0–57.9 |
| mostly working | 15 | 358–426 | 46.1 | 38.2–38.4 |

Same 2,160 events, same fleet, a factor of 118 in breaches and twice the cloud.
This is the second place a calibrated workday congests at all — and, as with a
single blast a day, it is where decay **earns**: 25–30 % fewer breaches, for
cloud within 4 % of the baseline. Where the day is spread (mostly working) decay
does what it has always done on a quiet day: costs breaches on harmless work,
and takes 17 % off the cloud bill.

**Decay is worth most to the decisions in exactly the same place.** Warned
shares (the first location whose zone, widened by the 50 m allowance, reaches
the unit), off → decay:

| Mix | Turn-back warned | Way-out warned | Reroute warned |
|---|---|---|---|
| mostly blasting | 60–63 % → **70–74 %** | 73–78 % → 84–87 % | 49–53 % → 56–63 % |
| balanced | 70–71 % → 76 % | 84–88 % → 87–92 % | 55–57 % → 57–61 % |
| mostly working | 70–76 % → 76–77 % | 89–93 % → 89–93 % | 57–63 % → 62–64 % |

A blast-dominated mine is the hardest one to be warned in (turn-back warned as
low as 60 %) and the one where reordering recovers most (+10 to +12 points,
median warning latency 66 s → 43 s at two faces). In a mine whose seismicity
follows its work rather than its rounds, warnings already arrive and decay adds
1–6 points. **Decay's value tracks how peaked the day is, not how many events it
has.**

**Faces worked change who is in the way, not the queue.** With intent off, every
arm at a given mix records *identical* breaches and cloud hours across 2, 4 and
8 faces — the load depends on when events happen, and the number of faces moves
only where. What it moves is exposure:

| Faces worked (mostly blasting) | Exposing events | Turn-back decisions | Way-out decisions |
|---|---:|---:|---:|
| 2 | 81 | 275 | **467** |
| 4 | 71 | 175 | 248 |
| 8 | 68 | 216 | **153** |

Concentrating the whole crew into two faces puts three times as many people
inside the zone of an event that has already happened as spreading them over
eight — the same seismicity, the same people, three times the ways out to find.
Spreading work also raises the baseline warned share (60 % → 63 % at two versus
eight faces) simply because fewer decisions compete for the same processing.
Decay's gain is roughly constant across the three (+10 to +12 points), so it
neither depends on nor substitutes for how work is laid out.

**Caveats.** Four seeds, one mine, one workforce, one blast schedule
(`activity-blasting` varies that). The "mostly blasting" mix is deliberately
extreme — 60 % of a day's events from four rounds — and is a stress case, not a
measurement of any mine. Every unit's position is known exactly and detection
does not depend on distance or magnitude, so these are upper bounds on what the
warnings could be. Decisions are scored on whether their information arrived,
not on what the mine then did.

## Results

| Arm | Breaches | Cloud h | Turn-back: decisions | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 s | Way-out: decisions | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Reroute: unwinnable | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 faces · mostly blasting · off | 1,774<br><sub>98–3,156</sub> | 89.2<br><sub>84.1–93.0</sub> | 275<br><sub>81–465</sub> | 0.92<br><sub>0.90–0.95</sub> | 0.60<br><sub>0.54–0.65</sub> | 37<br><sub>35–39</sub> | 467<br><sub>429–501</sub> | 0.97<br><sub>0.94–1.00</sub> | 0.76<br><sub>0.69–0.83</sub> | 0.73<br><sub>0.65–0.89</sub> | 0.49<br><sub>0.41–0.62</sub> | 78<br><sub>8–150</sub> | 0.90<br><sub>0.87–0.97</sub> |
| 2 faces · mostly blasting · decay | 1,246<br><sub>816–1,697</sub> | 92.5<br><sub>88.4–97.5</sub> | 275<br><sub>81–465</sub> | 0.92<br><sub>0.90–0.95</sub> | 0.70<br><sub>0.66–0.77</sub> | 35<br><sub>31–38</sub> | 467<br><sub>429–501</sub> | 0.97<br><sub>0.94–1.00</sub> | 0.86<br><sub>0.83–0.89</sub> | 0.74<br><sub>0.66–0.90</sub> | 0.56<br><sub>0.45–0.70</sub> | 78<br><sub>8–150</sub> | 0.92<br><sub>0.90–0.97</sub> |
| 2 faces · balanced · off | 33<br><sub>7–62</sub> | 61.0<br><sub>56.0–65.6</sub> | 257<br><sub>121–364</sub> | 0.95<br><sub>0.94–0.97</sub> | 0.70<br><sub>0.68–0.75</sub> | 35<br><sub>31–38</sub> | 541<br><sub>402–631</sub> | 0.98<br><sub>0.96–1.00</sub> | 0.88<br><sub>0.83–0.91</sub> | 0.73<br><sub>0.65–0.86</sub> | 0.54<br><sub>0.48–0.66</sub> | 66<br><sub>5–112</sub> | 0.95<br><sub>0.94–0.96</sub> |
| 2 faces · balanced · decay | 570<br><sub>474–685</sub> | 56.2<br><sub>45.9–63.4</sub> | 257<br><sub>121–364</sub> | 0.95<br><sub>0.94–0.97</sub> | 0.76<br><sub>0.72–0.80</sub> | 33<br><sub>31–37</sub> | 541<br><sub>402–631</sub> | 0.98<br><sub>0.97–1.00</sub> | 0.90<br><sub>0.84–0.94</sub> | 0.73<br><sub>0.65–0.86</sub> | 0.57<br><sub>0.50–0.66</sub> | 66<br><sub>5–112</sub> | 0.95<br><sub>0.94–0.96</sub> |
| 2 faces · mostly working · off | 15<br><sub>7–23</sub> | 46.1<br><sub>40.3–49.4</sub> | 289<br><sub>105–440</sub> | 0.94<br><sub>0.91–0.98</sub> | 0.70<br><sub>0.64–0.75</sub> | 37<br><sub>33–38</sub> | 687<br><sub>620–757</sub> | 0.98<br><sub>0.95–1.00</sub> | 0.93<br><sub>0.88–0.99</sub> | 0.78<br><sub>0.65–0.94</sub> | 0.57<br><sub>0.49–0.64</sub> | 72<br><sub>5–141</sub> | 0.94<br><sub>0.90–0.98</sub> |
| 2 faces · mostly working · decay | 358<br><sub>141–561</sub> | 38.4<br><sub>32.7–41.7</sub> | 289<br><sub>105–440</sub> | 0.94<br><sub>0.91–0.97</sub> | 0.76<br><sub>0.63–0.86</sub> | 36<br><sub>34–37</sub> | 687<br><sub>620–757</sub> | 0.98<br><sub>0.96–1.00</sub> | 0.92<br><sub>0.84–0.98</sub> | 0.78<br><sub>0.65–0.94</sub> | 0.63<br><sub>0.46–0.78</sub> | 72<br><sub>5–141</sub> | 0.94<br><sub>0.90–0.98</sub> |
| 4 faces · mostly blasting · off | 1,774<br><sub>98–3,156</sub> | 89.2<br><sub>84.1–93.0</sub> | 174<br><sub>115–283</sub> | 0.93<br><sub>0.91–0.95</sub> | 0.61<br><sub>0.59–0.65</sub> | 37<br><sub>35–39</sub> | 248<br><sub>222–275</sub> | 0.97<br><sub>0.92–0.99</sub> | 0.78<br><sub>0.69–0.83</sub> | 0.77<br><sub>0.71–0.88</sub> | 0.51<br><sub>0.42–0.57</sub> | 38<br><sub>10–72</sub> | 0.91<br><sub>0.88–0.94</sub> |
| 4 faces · mostly blasting · decay | 1,338<br><sub>1,170–1,531</sub> | 90.5<br><sub>84.2–97.9</sub> | 174<br><sub>115–283</sub> | 0.93<br><sub>0.92–0.95</sub> | 0.73<br><sub>0.67–0.77</sub> | 36<br><sub>33–38</sub> | 248<br><sub>222–275</sub> | 0.97<br><sub>0.92–0.99</sub> | 0.87<br><sub>0.82–0.92</sub> | 0.77<br><sub>0.72–0.90</sub> | 0.61<br><sub>0.53–0.73</sub> | 38<br><sub>10–72</sub> | 0.92<br><sub>0.90–0.94</sub> |
| 4 faces · balanced · off | 33<br><sub>7–62</sub> | 61.0<br><sub>56.0–65.6</sub> | 176<br><sub>126–260</sub> | 0.94<br><sub>0.89–0.97</sub> | 0.70<br><sub>0.64–0.73</sub> | 36<br><sub>35–37</sub> | 298<br><sub>272–325</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.88<br><sub>0.87–0.89</sub> | 0.76<br><sub>0.70–0.84</sub> | 0.57<br><sub>0.48–0.65</sub> | 37<br><sub>10–68</sub> | 0.94<br><sub>0.90–0.96</sub> |
| 4 faces · balanced · decay | 514<br><sub>345–719</sub> | 57.9<br><sub>47.0–65.2</sub> | 176<br><sub>126–260</sub> | 0.93<br><sub>0.90–0.96</sub> | 0.76<br><sub>0.70–0.80</sub> | 33<br><sub>31–34</sub> | 298<br><sub>272–325</sub> | 0.98<br><sub>0.97–0.99</sub> | 0.92<br><sub>0.89–0.95</sub> | 0.76<br><sub>0.69–0.84</sub> | 0.61<br><sub>0.56–0.65</sub> | 37<br><sub>10–68</sub> | 0.93<br><sub>0.91–0.96</sub> |
| 4 faces · mostly working · off | 15<br><sub>7–23</sub> | 46.1<br><sub>40.3–49.4</sub> | 205<br><sub>118–331</sub> | 0.93<br><sub>0.91–0.97</sub> | 0.74<br><sub>0.69–0.78</sub> | 37<br><sub>36–38</sub> | 374<br><sub>349–426</sub> | 0.97<br><sub>0.95–0.99</sub> | 0.93<br><sub>0.88–0.99</sub> | 0.80<br><sub>0.71–0.89</sub> | 0.62<br><sub>0.54–0.67</sub> | 42<br><sub>8–91</sub> | 0.94<br><sub>0.90–0.97</sub> |
| 4 faces · mostly working · decay | 396<br><sub>169–575</sub> | 38.2<br><sub>32.5–42.1</sub> | 205<br><sub>118–331</sub> | 0.94<br><sub>0.91–0.97</sub> | 0.76<br><sub>0.72–0.81</sub> | 36<br><sub>34–36</sub> | 374<br><sub>349–426</sub> | 0.97<br><sub>0.96–0.99</sub> | 0.93<br><sub>0.89–0.98</sub> | 0.80<br><sub>0.71–0.89</sub> | 0.62<br><sub>0.55–0.69</sub> | 42<br><sub>8–91</sub> | 0.94<br><sub>0.90–0.97</sub> |
| 8 faces · mostly blasting · off | 1,774<br><sub>98–3,156</sub> | 89.2<br><sub>84.1–93.0</sub> | 216<br><sub>127–262</sub> | 0.91<br><sub>0.88–0.94</sub> | 0.63<br><sub>0.60–0.70</sub> | 37<br><sub>35–39</sub> | 153<br><sub>126–175</sub> | 0.94<br><sub>0.90–0.97</sub> | 0.73<br><sub>0.68–0.78</sub> | 0.78<br><sub>0.71–0.85</sub> | 0.53<br><sub>0.48–0.60</sub> | 40<br><sub>14–60</sub> | 0.91<br><sub>0.89–0.92</sub> |
| 8 faces · mostly blasting · decay | 1,336<br><sub>1,112–1,548</sub> | 90.9<br><sub>84.3–97.8</sub> | 216<br><sub>127–262</sub> | 0.92<br><sub>0.89–0.94</sub> | 0.74<br><sub>0.69–0.79</sub> | 35<br><sub>32–38</sub> | 153<br><sub>126–175</sub> | 0.94<br><sub>0.90–0.97</sub> | 0.84<br><sub>0.83–0.86</sub> | 0.79<br><sub>0.71–0.87</sub> | 0.63<br><sub>0.58–0.68</sub> | 40<br><sub>14–60</sub> | 0.91<br><sub>0.89–0.93</sub> |
| 8 faces · balanced · off | 33<br><sub>7–62</sub> | 61.0<br><sub>56.0–65.6</sub> | 236<br><sub>145–276</sub> | 0.92<br><sub>0.90–0.93</sub> | 0.71<br><sub>0.69–0.75</sub> | 35<br><sub>33–38</sub> | 178<br><sub>128–213</sub> | 0.95<br><sub>0.93–0.98</sub> | 0.84<br><sub>0.79–0.87</sub> | 0.74<br><sub>0.67–0.79</sub> | 0.57<br><sub>0.54–0.59</sub> | 53<br><sub>21–82</sub> | 0.94<br><sub>0.92–0.96</sub> |
| 8 faces · balanced · decay | 637<br><sub>521–835</sub> | 56.0<br><sub>52.7–58.6</sub> | 236<br><sub>145–276</sub> | 0.92<br><sub>0.89–0.94</sub> | 0.76<br><sub>0.72–0.79</sub> | 33<br><sub>31–35</sub> | 178<br><sub>128–213</sub> | 0.95<br><sub>0.94–0.97</sub> | 0.87<br><sub>0.80–0.91</sub> | 0.75<br><sub>0.67–0.80</sub> | 0.60<br><sub>0.57–0.66</sub> | 53<br><sub>21–82</sub> | 0.94<br><sub>0.92–0.97</sub> |
| 8 faces · mostly working · off | 15<br><sub>7–23</sub> | 46.1<br><sub>40.3–49.4</sub> | 263<br><sub>145–312</sub> | 0.93<br><sub>0.92–0.95</sub> | 0.76<br><sub>0.69–0.81</sub> | 37<br><sub>35–38</sub> | 215<br><sub>201–234</sub> | 0.93<br><sub>0.91–0.96</sub> | 0.89<br><sub>0.88–0.91</sub> | 0.77<br><sub>0.72–0.82</sub> | 0.63<br><sub>0.59–0.67</sub> | 54<br><sub>27–76</sub> | 0.94<br><sub>0.92–0.96</sub> |
| 8 faces · mostly working · decay | 426<br><sub>210–615</sub> | 38.4<br><sub>33.0–42.3</sub> | 263<br><sub>145–312</sub> | 0.94<br><sub>0.93–0.95</sub> | 0.77<br><sub>0.74–0.80</sub> | 35<br><sub>34–37</sub> | 215<br><sub>201–234</sub> | 0.93<br><sub>0.91–0.96</sub> | 0.89<br><sub>0.88–0.91</sub> | 0.78<br><sub>0.73–0.83</sub> | 0.64<br><sub>0.58–0.71</sub> | 54<br><sub>27–76</sub> | 0.95<br><sub>0.94–0.96</sub> |

### Against off, at the same areas and mix

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Turn-back: in time | Turn-back warned: in time | Turn-back: latency p50 | Way-out: in time | Way-out warned: in time | Reroute: in time | Reroute warned: in time | Machines: in time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 faces · mostly blasting · decay | -30 % | +4 % | +0 % | +17 % | -6 % | +0 % | +12 % | +0 % | +15 % | +2 % |
| 2 faces · balanced · decay | +1615 % | -8 % | -0 % | +8 % | -7 % | +0 % | +2 % | -0 % | +5 % | -0 % |
| 2 faces · mostly working · decay | +2324 % | -17 % | +0 % | +8 % | -2 % | +0 % | -1 % | +0 % | +11 % | -0 % |
| 4 faces · mostly blasting · decay | -25 % | +1 % | +1 % | +20 % | -4 % | +0 % | +11 % | +0 % | +20 % | +1 % |
| 4 faces · balanced · decay | +1444 % | -5 % | -0 % | +8 % | -7 % | +0 % | +4 % | +0 % | +7 % | -1 % |
| 4 faces · mostly working · decay | +2586 % | -17 % | +0 % | +3 % | -4 % | +0 % | +0 % | +0 % | +0 % | +1 % |
| 8 faces · mostly blasting · decay | -25 % | +2 % | +1 % | +17 % | -6 % | +0 % | +15 % | +1 % | +18 % | +1 % |
| 8 faces · balanced · decay | +1816 % | -8 % | +0 % | +7 % | -6 % | +0 % | +3 % | +0 % | +7 % | +0 % |
| 8 faces · mostly working · decay | +2788 % | -17 % | +1 % | +1 % | -4 % | +0 % | +0 % | +1 % | +2 % | +1 % |

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

Axes: **areas** (3); **mix** (3); **intent** (2). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
