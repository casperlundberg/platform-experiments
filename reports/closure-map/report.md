# The map drawn from imperfect hypocentres

> Does the ground the mine closes, drawn from the locations it has, cover the ground its events really made dangerous — and what does closing more of the mine buy, as picks get noisier?

48 runs: 12 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-23T06:33:29+00:00 by autoscaler 2.0.0 (`009707439727`) and simlab-api 4.0.0-dev.16+64820a3 (`64820a35ea64`), built from clean checkouts of those commits, measured by platform-experiments 1.1.0-dev.9+d97c2e0 (`d97c2e006c8f`).

Regenerate with:

```bash
make -C platform-experiments sweep S=closure-map
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `d698d55ff6baaf4f…`.

## Reading

Use case 2, asked of the calibrated days. Not "was this decision made in time"
but "**is the picture right**": take every location the mine had at a moment,
draw each one's zone, and compare the closed ground with the ground the events
really made dangerous. Measured over the tunnels in metre-seconds — so many
metres of drift shut for so many seconds — with each event's ground dangerous,
and its zone closed, for 30 minutes. Four maps are drawn of every run, which
costs nothing: at moderate and at high ground motion, each as the run's own
locations drew it (the mine's 50 m allowance) and again with 150 m more.

**Location error decides whether the map covers the ground. Processing does
not.** On the workday, at the moderate level, as drawn:

| Pick error | Dangerous ground closed | Of what was closed, needlessly | Mine shut, on average |
|---|---:|---:|---:|
| 5 ms | 89 % | 64 % | 25 % |
| 20 ms | 62 % | 69 % | 20 % |
| 50 ms | **37 %** | 75 % | 15 % |

Tripling the pick error halves what the map covers, and the mine is shut *less*
— it closes the wrong ground, not more ground. This is the pick-jitter
sweep's finding in the terms an operator would use: a fixed allowance stops
describing the hazard once picks get noisy, and what it then closes is mostly
somewhere else.

**Even at its best the map is mostly needless closure.** At 5 ms — the
calibrated day, the array as installed — a quarter of the mine is shut on
average and 64 % of that closure was never over dangerous ground. The mine's
own 50 m allowance is what buys the 89 %.

**Covering everything means closing everything.** With 150 m more allowance:

| | Dangerous ground closed | Mine shut, on average |
|---|---:|---:|
| moderate, as drawn | 89 % | 25 % |
| moderate, +150 m | 99 % | **85 %** |
| high, as drawn | 69 % | 5 % |
| high, +150 m | 98 % | **69 %** |

There is no allowance that both covers the hazard and leaves a mine to work in.
The way out of that trade is a better location, not a wider circle — which is
what a per-location allowance (the residual each estimate already carries) is
for, and the reason it is the open item on case 2.

**Decay improves both sides of the map.** Unlike its effect on breaches, where
it buys cloud at the cost of harmless work missing deadlines, ordering the
queue by intent makes the picture strictly better — it covers more and closes
less needlessly, because the events that endanger someone are located sooner:

| Moderate, off → decay | Ground covered | Needless closure | Events never covered whole |
|---|---|---|---|
| workday, 5 ms | 89 → **92 %** | 64 → 63 % | 99 → 69 |
| workday, 20 ms | 62 → **69 %** | 69 → 64 % | 415 → 378 |
| workday, 50 ms | 37 → **41 %** | 75 → 71 % | 664 → 630 |
| earthquake, 5 ms | 86 → **88 %** | 44 → 44 % | 134 → 99 |
| earthquake, 50 ms | 63 → **67 %** | 51 → 49 % | 546 → 490 |

**A busy day's map is better, not worse.** Case 2 was written expecting the
opposite — that overlapping zones would hide an estimate badly out behind one
that is right. They do hide it, and that *helps*: on the earthquake day half of
all events have their dangerous ground already closed **at the moment they
happen** (median time to a complete map: 0 s, against 34 s on the workday),
because a neighbour's zone is already over it. Coverage at 50 ms pick error is
63 % on the earthquake day against 37 % on the quiet one, and needless closure
is 51 % against 75 %. Where events cluster, the union is forgiving.

**How long the map takes to be right.** Median 34 s on the workday at 5 ms, but
the 95th percentile is 806–923 s, and 1,400–1,600 s once pick error grows. A
map that is right for half the events within a minute is wrong at its edges for
a quarter of an hour.

**The high level, where the decisions matter most, is barely covered at all on
a quiet day**: 69 % at 5 ms, 19 % at 20 ms, 8 % at 50 ms — a zone tens of
metres across cannot survive a location tens of metres out, and 99.6 % of what
is closed at that level was never dangerous. On the earthquake day, where big
events make big high zones, it holds up: 81 → 75 → 58 % across the same pick
errors. **The quiet day's high-level figures come from a handful of events**
(per-seed coverage ranges from 0.0 to 0.22 at 50 ms), which is exactly why
scripted encounters exist.

**Caveats.** Four seeds, one mine. The map assumes the mine closes exactly the
zones its locations drew, for 30 minutes, and re-opens: no re-entry protocol
(case 7), no operator judgement. "Needless" means the true zone never reached
that ground, which is not the same as safe — aftershocks are not counted
against it. The allowance in the recorded zones is intent's own 50 m; a
per-location allowance is not yet built.

## Results

| Arm | Breaches | Moderate: ground covered | Moderate: closed needlessly | Moderate: mine closed | Moderate: complete p95 s | Moderate: never complete | Moderate wide: ground covered | Moderate wide: mine closed | High: ground covered | High: closed needlessly | High: mine closed | High: complete p95 s | High wide: ground covered | High wide: mine closed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| jitter 5 ms · workday · off | 16<br><sub>9–30</sub> | 0.890<br><sub>0.875–0.908</sub> | 0.641<br><sub>0.606–0.673</sub> | 0.248<br><sub>0.231–0.272</sub> | 923<br><sub>671–1,114</sub> | 99<br><sub>68–113</sub> | 0.994<br><sub>0.992–0.996</sub> | 0.845<br><sub>0.838–0.851</sub> | 0.685<br><sub>0.620–0.734</sub> | 0.996<br><sub>0.995–0.997</sub> | 0.050<br><sub>0.049–0.050</sub> | 783<br><sub>353–1,057</sub> | 0.976<br><sub>0.948–0.998</sub> | 0.694<br><sub>0.689–0.701</sub> |
| jitter 5 ms · workday · decay | 1,435<br><sub>1,263–1,555</sub> | 0.917<br><sub>0.900–0.933</sub> | 0.628<br><sub>0.589–0.661</sub> | 0.247<br><sub>0.233–0.272</sub> | 806<br><sub>775–834</sub> | 69<br><sub>61–79</sub> | 0.996<br><sub>0.995–0.997</sub> | 0.844<br><sub>0.839–0.853</sub> | 0.866<br><sub>0.797–0.951</sub> | 0.996<br><sub>0.995–0.996</sub> | 0.052<br><sub>0.051–0.053</sub> | 670<br><sub>389–1,132</sub> | 0.985<br><sub>0.954–0.998</sub> | 0.691<br><sub>0.687–0.694</sub> |
| jitter 5 ms · earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 0.856<br><sub>0.810–0.924</sub> | 0.443<br><sub>0.429–0.456</sub> | 0.323<br><sub>0.304–0.353</sub> | 374<br><sub>319–420</sub> | 134<br><sub>114–156</sub> | 0.989<br><sub>0.986–0.995</sub> | 0.849<br><sub>0.831–0.875</sub> | 0.805<br><sub>0.631–0.978</sub> | 0.833<br><sub>0.797–0.885</sub> | 0.067<br><sub>0.061–0.069</sub> | 559<br><sub>342–764</sub> | 0.960<br><sub>0.882–0.998</sub> | 0.692<br><sub>0.675–0.719</sub> |
| jitter 5 ms · earthquake · decay | 20,010<br><sub>18,350–21,917</sub> | 0.881<br><sub>0.848–0.941</sub> | 0.442<br><sub>0.432–0.457</sub> | 0.332<br><sub>0.317–0.360</sub> | 328<br><sub>255–389</sub> | 99<br><sub>75–124</sub> | 0.992<br><sub>0.986–0.996</sub> | 0.855<br><sub>0.836–0.882</sub> | 0.802<br><sub>0.617–0.980</sub> | 0.840<br><sub>0.804–0.889</sub> | 0.070<br><sub>0.063–0.074</sub> | 469<br><sub>237–780</sub> | 0.960<br><sub>0.878–0.998</sub> | 0.701<br><sub>0.684–0.723</sub> |
| jitter 20 ms · workday · off | 16<br><sub>9–30</sub> | 0.621<br><sub>0.605–0.640</sub> | 0.686<br><sub>0.651–0.719</sub> | 0.198<br><sub>0.186–0.216</sub> | 1,512<br><sub>1,452–1,625</sub> | 415<br><sub>394–445</sub> | 0.982<br><sub>0.980–0.985</sub> | 0.821<br><sub>0.813–0.832</sub> | 0.185<br><sub>0.133–0.242</sub> | 0.998<br><sub>0.997–0.999</sub> | 0.028<br><sub>0.027–0.028</sub> | 658<br><sub>353–1,087</sub> | 0.900<br><sub>0.841–0.951</sub> | 0.650<br><sub>0.646–0.654</sub> |
| jitter 20 ms · workday · decay | 908<br><sub>747–1,097</sub> | 0.686<br><sub>0.669–0.708</sub> | 0.643<br><sub>0.605–0.680</sub> | 0.193<br><sub>0.180–0.217</sub> | 1,416<br><sub>1,340–1,528</sub> | 378<br><sub>353–397</sub> | 0.984<br><sub>0.980–0.987</sub> | 0.813<br><sub>0.803–0.823</sub> | 0.282<br><sub>0.132–0.363</sub> | 0.997<br><sub>0.996–0.999</sub> | 0.026<br><sub>0.026–0.027</sub> | 888<br><sub>430–1,207</sub> | 0.953<br><sub>0.939–0.965</sub> | 0.639<br><sub>0.637–0.642</sub> |
| jitter 20 ms · earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 0.761<br><sub>0.719–0.819</sub> | 0.463<br><sub>0.451–0.484</sub> | 0.298<br><sub>0.279–0.328</sub> | 950<br><sub>894–988</sub> | 370<br><sub>352–392</sub> | 0.985<br><sub>0.980–0.990</sub> | 0.832<br><sub>0.814–0.866</sub> | 0.751<br><sub>0.568–0.967</sub> | 0.801<br><sub>0.747–0.854</sub> | 0.052<br><sub>0.044–0.058</sub> | 840<br><sub>476–1,282</sub> | 0.961<br><sub>0.894–0.994</sub> | 0.665<br><sub>0.647–0.690</sub> |
| jitter 20 ms · earthquake · decay | 19,860<br><sub>17,461–22,409</sub> | 0.800<br><sub>0.765–0.839</sub> | 0.455<br><sub>0.426–0.480</sub> | 0.309<br><sub>0.288–0.338</sub> | 994<br><sub>894–1,118</sub> | 329<br><sub>299–363</sub> | 0.987<br><sub>0.983–0.993</sub> | 0.838<br><sub>0.820–0.875</sub> | 0.711<br><sub>0.429–0.965</sub> | 0.819<br><sub>0.761–0.892</sub> | 0.054<br><sub>0.044–0.059</sub> | 1,151<br><sub>929–1,354</sub> | 0.957<br><sub>0.888–0.997</sub> | 0.672<br><sub>0.652–0.706</sub> |
| jitter 50 ms · workday · off | 16<br><sub>9–30</sub> | 0.371<br><sub>0.328–0.417</sub> | 0.753<br><sub>0.717–0.797</sub> | 0.151<br><sub>0.137–0.178</sub> | 1,612<br><sub>1,562–1,677</sub> | 664<br><sub>648–680</sub> | 0.914<br><sub>0.908–0.926</sub> | 0.755<br><sub>0.741–0.773</sub> | 0.075<br><sub>0.000–0.225</sub> | 0.999<br><sub>0.997–1.000</sub> | 0.018<br><sub>0.018–0.019</sub> | 788<br><sub>0–1,576</sub> | 0.786<br><sub>0.684–0.908</sub> | 0.553<br><sub>0.545–0.561</sub> |
| jitter 50 ms · workday · decay | 672<br><sub>537–730</sub> | 0.414<br><sub>0.358–0.473</sub> | 0.712<br><sub>0.669–0.766</sub> | 0.145<br><sub>0.132–0.172</sub> | 1,627<br><sub>1,598–1,664</sub> | 630<br><sub>577–660</sub> | 0.919<br><sub>0.912–0.932</sub> | 0.736<br><sub>0.726–0.755</sub> | 0.037<br><sub>0.000–0.090</sub> | 0.999<br><sub>0.999–1.000</sub> | 0.016<br><sub>0.015–0.016</sub> | 593<br><sub>75–1,576</sub> | 0.862<br><sub>0.809–0.971</sub> | 0.530<br><sub>0.523–0.540</sub> |
| jitter 50 ms · earthquake · off | 24,974<br><sub>23,046–26,284</sub> | 0.629<br><sub>0.573–0.694</sub> | 0.514<br><sub>0.508–0.524</sub> | 0.272<br><sub>0.250–0.301</sub> | 1,206<br><sub>1,041–1,420</sub> | 546<br><sub>524–601</sub> | 0.962<br><sub>0.952–0.972</sub> | 0.805<br><sub>0.786–0.849</sub> | 0.579<br><sub>0.463–0.783</sub> | 0.795<br><sub>0.733–0.837</sub> | 0.039<br><sub>0.037–0.042</sub> | 979<br><sub>0–1,687</sub> | 0.940<br><sub>0.871–0.989</sub> | 0.615<br><sub>0.600–0.649</sub> |
| jitter 50 ms · earthquake · decay | 18,920<br><sub>18,166–20,431</sub> | 0.668<br><sub>0.628–0.691</sub> | 0.493<br><sub>0.469–0.511</sub> | 0.277<br><sub>0.258–0.310</sub> | 1,183<br><sub>1,030–1,360</sub> | 490<br><sub>445–522</sub> | 0.970<br><sub>0.954–0.976</sub> | 0.802<br><sub>0.780–0.849</sub> | 0.576<br><sub>0.451–0.777</sub> | 0.803<br><sub>0.745–0.837</sub> | 0.040<br><sub>0.038–0.044</sub> | 1,039<br><sub>98–1,700</sub> | 0.941<br><sub>0.868–0.989</sub> | 0.614<br><sub>0.593–0.652</sub> |

### Against off, at the same jitter and day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Moderate: ground covered | Moderate: closed needlessly | Moderate: complete p95 | High: ground covered | High: closed needlessly | High: complete p95 |
|---|---:|---:|---:|---:|---:|---:|
| jitter 5 ms · workday · decay | +3 % | -2 % | -13 % | +26 % | -0 % | -14 % |
| jitter 5 ms · earthquake · decay | +3 % | -0 % | -12 % | -0 % | +1 % | -16 % |
| jitter 20 ms · workday · decay | +10 % | -6 % | -6 % | +53 % | -0 % | +35 % |
| jitter 20 ms · earthquake · decay | +5 % | -2 % | +5 % | -5 % | +2 % | +37 % |
| jitter 50 ms · workday · decay | +12 % | -5 % | +1 % | -51 % | +0 % | +5 % |
| jitter 50 ms · earthquake · decay | +6 % | -4 % | -2 % | -1 % | +1 % | +6 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **Moderate: ground covered**: the share of the tunnel the events truly made dangerous, in metre-seconds, that the closure map drawn from the run's locations (parameters `{}`, the rest default) closed.
- **Moderate: closed needlessly**: the share of what the closure map drawn from the run's locations (parameters `{}`, the rest default) closed that nothing endangered.
- **Moderate: mine closed**: the share of the mine's tunnel the closure map drawn from the run's locations (parameters `{}`, the rest default) shuts, averaged over the run.
- **Moderate: complete p95 s**: the same at the 95th percentile.
- **Moderate: never complete**: events the closure map drawn from the run's locations (parameters `{}`, the rest default) never covered whole, within their window.
- **Moderate wide: ground covered**: the share of the tunnel the events truly made dangerous, in metre-seconds, that the closure map drawn from the run's locations (parameters `{"extra_allowance_meters": 150}`, the rest default) closed.
- **Moderate wide: mine closed**: the share of the mine's tunnel the closure map drawn from the run's locations (parameters `{"extra_allowance_meters": 150}`, the rest default) shuts, averaged over the run.
- **High: ground covered**: the share of the tunnel the events truly made dangerous, in metre-seconds, that the closure map drawn from the run's locations (parameters `{"level": "high"}`, the rest default) closed.
- **High: closed needlessly**: the share of what the closure map drawn from the run's locations (parameters `{"level": "high"}`, the rest default) closed that nothing endangered.
- **High: mine closed**: the share of the mine's tunnel the closure map drawn from the run's locations (parameters `{"level": "high"}`, the rest default) shuts, averaged over the run.
- **High: complete p95 s**: the same at the 95th percentile.
- **High wide: ground covered**: the share of the tunnel the events truly made dangerous, in metre-seconds, that the closure map drawn from the run's locations (parameters `{"extra_allowance_meters": 150, "level": "high"}`, the rest default) closed.
- **High wide: mine closed**: the share of the mine's tunnel the closure map drawn from the run's locations (parameters `{"extra_allowance_meters": 150, "level": "high"}`, the rest default) shuts, averaged over the run.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **jitter** (3); **day** (2); **intent** (2). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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

<sub>Tables rendered by platform-experiments `90cdbc469030`.</sub>
