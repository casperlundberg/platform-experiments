# How far ahead to protect, and how much to allow for location error

> How do the lookahead along planned routes and the allowance for location error trade misses (endangering events decayed) against how much work is relaxed?

78 runs: 13 arms × 6 seeds (101, 202, 303, 404, 505, 606). Produced 2026-09-17T17:48:55+00:00 by autoscaler 1.1.0 (`14f2ca0f570b`) and simlab-api 2.0.0 (`ddaa2061fe52`), built from clean checkouts of those commits, measured by platform-experiments `152bad5951de`.

Regenerate with:

```bash
make -C platform-experiments sweep S=lookahead-uncertainty
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `0cfd432d5ea07e44…`.

## Reading

**The allowance for location error is the dial; the lookahead barely moves the
cost.** With decay and restored work exempt:

| Allowance | Breaches vs no intent | Exposing events decayed, of 21.5 per seed |
|---|---:|---:|
| ±0 m | −47 % | 5.7–8.5 |
| ±50 m | −25 % | 2.3–3.3 |
| ±150 m | −4 % | 0.8–1.0 |

An allowance of zero relaxes the most and decays a quarter to two-fifths of the
events that truly exposed someone. ±150 m protects nearly all of them and relaxes almost
nothing. ±50 m — the re-entry practice figure, and the default — keeps most of
the benefit and decays two or three a seed.

**Lookahead** changes breaches and cloud time by at most a few percent. It reduces
misses where the allowance leaves room for them (±0 m: 8.5 at no lookahead, 5.7
at fifteen minutes) and, at ±50 m, lowers how many events are decayed at all
(620 → 495) without buying fewer breaches. Five minutes is not obviously wrong,
and fifteen is not obviously better.

**Caveat.** A fixed allowance is blind to how good a given location is; see the
pick-jitter sweep, where it stops being enough.

## Results

| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events | Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s | Exposing decayed | Events decayed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off · lookahead 300s · ±50 m | 1,687<br><sub>950–2,119</sub> | 1,687<br><sub>950–2,119</sub> | 61.1<br><sub>56.6–64.8</sub> | 10.2<br><sub>8.1–12.5</sub> | 52<br><sub>40–65</sub> | 22<br><sub>6–44</sub> | 87<br><sub>69–110</sub> | 367<br><sub>177–467</sub> | 5,025<br><sub>3,141–6,838</sub> | 131<br><sub>79–199</sub> | 0 | 0 |
| decay, restored exempt · lookahead 0s · ±0 m | 890<br><sub>432–1,287</sub> | 1,624<br><sub>1,053–1,961</sub> | 58.5<br><sub>52.9–62.4</sub> | 8.8<br><sub>7.1–11.7</sub> | 28<br><sub>20–35</sub> | 22<br><sub>6–44</sub> | 69<br><sub>33–98</sub> | 337<br><sub>79–418</sub> | 2,035<br><sub>199–4,265</sub> | 68<br><sub>55–81</sub> | 8<br><sub>1–21</sub> | 670<br><sub>654–708</sub> |
| decay, restored exempt · lookahead 0s · ±50 m | 1,256<br><sub>660–1,757</sub> | 1,662<br><sub>1,019–2,081</sub> | 58.5<br><sub>52.9–62.2</sub> | 6.1<br><sub>3.6–9.1</sub> | 31<br><sub>24–40</sub> | 22<br><sub>6–44</sub> | 73<br><sub>49–98</sub> | 349<br><sub>139–418</sub> | 979<br><sub>310–1,550</sub> | 73<br><sub>59–93</sub> | 3<br><sub>0–8</sub> | 620<br><sub>551–693</sub> |
| decay, restored exempt · lookahead 0s · ±150 m | 1,614<br><sub>955–2,054</sub> | 1,708<br><sub>1,038–2,183</sub> | 59.1<br><sub>53.6–62.3</sub> | 7.0<br><sub>5.2–9.2</sub> | 40<br><sub>29–51</sub> | 22<br><sub>6–44</sub> | 81<br><sub>62–110</sub> | 360<br><sub>169–452</sub> | 1,873<br><sub>936–2,960</sub> | 96<br><sub>69–124</sub> | 1<br><sub>0–2</sub> | 419<br><sub>231–575</sub> |
| decay, restored exempt · lookahead 120s · ±0 m | 898<br><sub>439–1,288</sub> | 1,629<br><sub>1,058–1,976</sub> | 58.5<br><sub>52.9–62.4</sub> | 10.4<br><sub>8.3–13.3</sub> | 28<br><sub>20–35</sub> | 22<br><sub>6–44</sub> | 69<br><sub>33–98</sub> | 337<br><sub>79–418</sub> | 2,660<br><sub>1,446–6,140</sub> | 69<br><sub>56–84</sub> | 8<br><sub>1–21</sub> | 664<br><sub>647–699</sub> |
| decay, restored exempt · lookahead 120s · ±50 m | 1,265<br><sub>695–1,764</sub> | 1,663<br><sub>1,028–2,089</sub> | 58.6<br><sub>53.2–62.2</sub> | 7.0<br><sub>5.6–9.4</sub> | 32<br><sub>25–42</sub> | 22<br><sub>6–44</sub> | 73<br><sub>48–98</sub> | 347<br><sub>109–434</sub> | 990<br><sub>322–1,370</sub> | 74<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 600<br><sub>512–672</sub> |
| decay, restored exempt · lookahead 120s · ±150 m | 1,620<br><sub>955–2,054</sub> | 1,706<br><sub>1,040–2,170</sub> | 59.4<br><sub>53.8–62.4</sub> | 7.2<br><sub>5.3–9.4</sub> | 42<br><sub>34–52</sub> | 22<br><sub>6–44</sub> | 84<br><sub>68–112</sub> | 357<br><sub>147–452</sub> | 2,271<br><sub>922–4,852</sub> | 102<br><sub>76–148</sub> | 1<br><sub>0–2</sub> | 397<br><sub>209–561</sub> |
| decay, restored exempt · lookahead 300s · ±0 m | 884<br><sub>439–1,255</sub> | 1,616<br><sub>1,054–1,963</sub> | 58.5<br><sub>52.9–62.2</sub> | 10.1<br><sub>8.3–13.2</sub> | 28<br><sub>20–35</sub> | 22<br><sub>6–44</sub> | 69<br><sub>32–95</sub> | 337<br><sub>79–418</sub> | 2,304<br><sub>188–5,972</sub> | 69<br><sub>55–85</sub> | 8<br><sub>0–21</sub> | 648<br><sub>602–684</sub> |
| decay, restored exempt · lookahead 300s · ±50 m | 1,280<br><sub>651–1,790</sub> | 1,664<br><sub>966–2,106</sub> | 58.5<br><sub>53.0–62.2</sub> | 7.6<br><sub>5.5–11.0</sub> | 34<br><sub>25–43</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 350<br><sub>124–434</sub> | 1,113<br><sub>365–1,861</sub> | 77<br><sub>60–96</sub> | 2<br><sub>0–4</sub> | 572<br><sub>433–657</sub> |
| decay, restored exempt · lookahead 300s · ±150 m | 1,636<br><sub>899–2,060</sub> | 1,720<br><sub>990–2,147</sub> | 59.7<br><sub>53.8–62.8</sub> | 7.6<br><sub>6.0–10.7</sub> | 46<br><sub>36–57</sub> | 22<br><sub>6–44</sub> | 84<br><sub>69–110</sub> | 358<br><sub>154–452</sub> | 2,248<br><sub>1,018–3,475</sub> | 104<br><sub>75–141</sub> | 1<br><sub>0–2</sub> | 371<br><sub>172–533</sub> |
| decay, restored exempt · lookahead 900s · ±0 m | 885<br><sub>393–1,247</sub> | 1,621<br><sub>995–1,959</sub> | 58.5<br><sub>52.9–62.2</sub> | 10.7<br><sub>8.4–13.1</sub> | 30<br><sub>22–36</sub> | 22<br><sub>6–44</sub> | 70<br><sub>36–98</sub> | 342<br><sub>109–418</sub> | 1,412<br><sub>231–3,232</sub> | 71<br><sub>56–86</sub> | 6<br><sub>0–17</sub> | 598<br><sub>500–642</sub> |
| decay, restored exempt · lookahead 900s · ±50 m | 1,313<br><sub>635–1,789</sub> | 1,687<br><sub>949–2,091</sub> | 58.8<br><sub>53.6–62.2</sub> | 7.0<br><sub>5.4–11.4</sub> | 39<br><sub>28–50</sub> | 22<br><sub>6–44</sub> | 75<br><sub>50–98</sub> | 347<br><sub>124–434</sub> | 1,545<br><sub>592–2,163</sub> | 83<br><sub>66–98</sub> | 3<br><sub>0–5</sub> | 495<br><sub>314–582</sub> |
| decay, restored exempt · lookahead 900s · ±150 m | 1,651<br><sub>894–2,115</sub> | 1,732<br><sub>984–2,155</sub> | 60.3<br><sub>55.5–64.3</sub> | 7.2<br><sub>6.4–10.1</sub> | 48<br><sub>36–63</sub> | 22<br><sub>6–44</sub> | 83<br><sub>69–103</sub> | 355<br><sub>154–452</sub> | 2,211<br><sub>1,188–2,837</sub> | 106<br><sub>75–136</sub> | 1<br><sub>0–2</sub> | 275<br><sub>139–441</sub> |

### Against off · lookahead 300s · ±50 m

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |
|---|---:|---:|---:|---:|---:|
| decay, restored exempt · lookahead 0s · ±0 m | -47 % | -4 % | -4 % | -20 % | -60 % |
| decay, restored exempt · lookahead 0s · ±50 m | -26 % | -1 % | -4 % | -16 % | -81 % |
| decay, restored exempt · lookahead 0s · ±150 m | -4 % | +1 % | -3 % | -7 % | -63 % |
| decay, restored exempt · lookahead 120s · ±0 m | -47 % | -3 % | -4 % | -20 % | -47 % |
| decay, restored exempt · lookahead 120s · ±50 m | -25 % | -1 % | -4 % | -16 % | -80 % |
| decay, restored exempt · lookahead 120s · ±150 m | -4 % | +1 % | -3 % | -3 % | -55 % |
| decay, restored exempt · lookahead 300s · ±0 m | -48 % | -4 % | -4 % | -20 % | -54 % |
| decay, restored exempt · lookahead 300s · ±50 m | -24 % | -1 % | -4 % | -13 % | -78 % |
| decay, restored exempt · lookahead 300s · ±150 m | -3 % | +2 % | -2 % | -3 % | -55 % |
| decay, restored exempt · lookahead 900s · ±0 m | -48 % | -4 % | -4 % | -19 % | -72 % |
| decay, restored exempt · lookahead 900s · ±50 m | -22 % | +0 % | -4 % | -13 % | -69 % |
| decay, restored exempt · lookahead 900s · ±150 m | -2 % | +3 % | -1 % | -4 % | -56 % |

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

Axes: **intent** (2); **lookahead** (4); **uncertainty** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
