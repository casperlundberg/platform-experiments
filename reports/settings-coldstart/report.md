# How long capacity takes to arrive

> What does a slower coldstart cost on each kind of day — an on-premise executor that starts in no time or in five minutes, a cloud executor that starts in one minute or in ten?

108 runs: 27 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-21T16:29:54+00:00 by autoscaler 2.0.0-dev.3+1bbd547 (`1bbd5472a9db`) and simlab-api 3.0.0 (`1dcaed0addff`), built from clean checkouts of those commits, measured by platform-experiments 1.0.0-dev.22+024b6e7 (`024b6e7d5aa2`).

Regenerate with:

```bash
make -C platform-experiments sweep S=settings-coldstart
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `a414d40dbafad7f7…`.

## Reading

Coldstart here is a fact of the platform, not a dial: it sets both what the
autoscaler assumes and how long the simulated fleet actually takes, so each arm
is a different platform — an on-premise executor that starts at once, in a
minute or in five; a cloud executor in one, three or ten minutes.

**How fast the cloud starts decides whether it can help at all.**

| Breaches against local 1 min, cloud 3 min | cloud 1 min | cloud 10 min |
|---|---:|---:|
| workday | −14 % | +2,958 % (16 → 497) |
| rock burst | −10 % | +16 % |
| earthquake | −6 % | +8 % |

The top level's deadline is 60 seconds and the next is 5 minutes, so cloud
capacity that takes 10 minutes to start can rescue neither. On the workday the
engine saw 257 decisions where no capacity within both caps avoided a breach, up
from none. The cloud time bought barely changed (+1–9 %); what changed is how
much of it arrived in time to count. A one-minute cloud also cut the
95th-percentile wait by 35–44 % on the workday and rock burst.

**On-premise coldstart matters at the edges of the day.** Local executors that
start at once took the workday from 16 breaches to 4 — the floor the other
sweeps share is the day's own cold start — and five minutes more than doubled
it (39); under the bursts either way moved breaches by 3 % or less.

**For a mine:** measure the coldstart of the platform the cloud tier runs on,
and weigh it against the shortest deadline that tier is meant to rescue. A
container platform that starts in a minute is worth more here than a larger cap
on one that takes ten.

**Caveats.** Four seeds, one mine, intent off. The autoscaler's assumed
coldstart and the fleet's real one are the same value in every arm; a mismatch
between them — an autoscaler told 3 minutes on a platform that takes 10 — was
not swept.

## Results

| Arm | Breaches | Cloud h | Local h | Drained h | Overloads | Wait p95 s | Locate all, mean s | Locate all, p95 s | Locate exposing, mean s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · local 0 s · cloud 1 min | 4<br><sub>1–7</sub> | 56.5<br><sub>51.0–59.3</sub> | 277.7<br><sub>276.8–278.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 2,557<br><sub>1,004–5,091</sub> | 44<br><sub>43–46</sub> | 116<br><sub>113–120</sub> | 42<br><sub>38–47</sub> |
| workday · local 0 s · cloud 3 min | 4<br><sub>2–7</sub> | 52.6<br><sub>50.3–57.0</sub> | 277.7<br><sub>276.8–278.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,640<br><sub>2,264–8,038</sub> | 48<br><sub>47–50</sub> | 134<br><sub>133–136</sub> | 46<br><sub>42–51</sub> |
| workday · local 0 s · cloud 10 min | 498<br><sub>200–837</sub> | 57.5<br><sub>36.4–67.7</sub> | 277.9<br><sub>276.8–278.9</sub> | 24.0<br><sub>24.0–24.1</sub> | 258<br><sub>197–319</sub> | 3,139<br><sub>979–8,712</sub> | 57<br><sub>56–58</sub> | 183<br><sub>171–197</sub> | 58<br><sub>54–65</sub> |
| workday · local 1 min · cloud 1 min | 14<br><sub>7–24</sub> | 57.5<br><sub>51.3–62.1</sub> | 277.3<br><sub>276.5–278.1</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 2,560<br><sub>1,006–5,092</sub> | 44<br><sub>44–46</sub> | 117<br><sub>115–119</sub> | 42<br><sub>38–48</sub> |
| workday · local 1 min · cloud 3 min | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local 1 min · cloud 10 min | 497<br><sub>207–840</sub> | 57.6<br><sub>36.4–67.6</sub> | 277.6<br><sub>276.5–278.9</sub> | 24.0<br><sub>24.0–24.1</sub> | 257<br><sub>195–316</sub> | 3,158<br><sub>976–8,786</sub> | 57<br><sub>56–58</sub> | 185<br><sub>172–197</sub> | 58<br><sub>54–63</sub> |
| workday · local 5 min · cloud 1 min | 20<br><sub>9–34</sub> | 60.8<br><sub>55.6–63.0</sub> | 274.1<br><sub>273.1–274.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 2,576<br><sub>1,011–5,132</sub> | 45<br><sub>44–46</sub> | 121<br><sub>117–125</sub> | 42<br><sub>38–48</sub> |
| workday · local 5 min · cloud 3 min | 39<br><sub>37–44</sub> | 59.3<br><sub>57.4–61.4</sub> | 274.1<br><sub>273.1–274.7</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,412<br><sub>2,284–8,130</sub> | 49<br><sub>48–51</sub> | 145<br><sub>140–149</sub> | 46<br><sub>42–53</sub> |
| workday · local 5 min · cloud 10 min | 614<br><sub>361–900</sub> | 58.9<br><sub>37.0–70.0</sub> | 275.2<br><sub>273.4–278.1</sub> | 24.1<br><sub>24.0–24.3</sub> | 279<br><sub>219–332</sub> | 3,348<br><sub>1,007–9,462</sub> | 60<br><sub>59–60</sub> | 196<br><sub>182–208</sub> | 58<br><sub>54–64</sub> |
| rock burst · local 0 s · cloud 1 min | 5,724<br><sub>5,391–6,087</sub> | 139.3<br><sub>132.1–148.3</sub> | 301.7<br><sub>300.8–303.0</sub> | 43.5<br><sub>41.2–45.8</sub> | 188<br><sub>178–200</sub> | 26,394<br><sub>25,175–28,387</sub> | 115<br><sub>109–126</sub> | 860<br><sub>795–962</sub> | 73<br><sub>53–94</sub> |
| rock burst · local 0 s · cloud 3 min | 6,330<br><sub>5,834–6,843</sub> | 133.2<br><sub>125.8–145.4</sub> | 307.6<br><sub>306.3–309.6</sub> | 47.7<br><sub>46.8–48.1</sub> | 200<br><sub>189–210</sub> | 40,227<br><sub>29,248–48,367</sub> | 132<br><sub>124–144</sub> | 977<br><sub>904–1,079</sub> | 82<br><sub>61–104</sub> |
| rock burst · local 0 s · cloud 10 min | 7,368<br><sub>6,656–7,869</sub> | 139.1<br><sub>128.5–149.5</sub> | 298.6<br><sub>296.1–301.1</sub> | 40.4<br><sub>36.4–44.8</sub> | 533<br><sub>481–584</sub> | 23,163<br><sub>19,586–27,769</sub> | 184<br><sub>146–215</sub> | 1,313<br><sub>1,035–1,510</sub> | 112<br><sub>82–141</sub> |
| rock burst · local 1 min · cloud 1 min | 5,731<br><sub>5,403–6,095</sub> | 139.8<br><sub>132.3–148.4</sub> | 301.5<br><sub>300.6–303.0</sub> | 43.7<br><sub>41.3–46.0</sub> | 188<br><sub>178–200</sub> | 26,533<br><sub>25,233–28,415</sub> | 116<br><sub>109–126</sub> | 860<br><sub>795–962</sub> | 73<br><sub>53–94</sub> |
| rock burst · local 1 min · cloud 3 min | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 307.2<br><sub>305.9–309.3</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 40,625<br><sub>29,145–48,307</sub> | 132<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–105</sub> |
| rock burst · local 1 min · cloud 10 min | 7,373<br><sub>6,658–7,877</sub> | 139.3<br><sub>128.6–150.0</sub> | 298.3<br><sub>295.8–300.8</sub> | 40.5<br><sub>36.4–45.2</sub> | 534<br><sub>481–588</sub> | 23,236<br><sub>19,491–28,041</sub> | 184<br><sub>145–215</sub> | 1,311<br><sub>1,030–1,510</sub> | 112<br><sub>81–141</sub> |
| rock burst · local 5 min · cloud 1 min | 5,732<br><sub>5,408–6,095</sub> | 143.0<br><sub>135.7–152.5</sub> | 299.3<br><sub>298.2–301.9</sub> | 44.0<br><sub>41.5–46.5</sub> | 188<br><sub>178–200</sub> | 26,826<br><sub>25,249–28,589</sub> | 116<br><sub>110–126</sub> | 860<br><sub>795–962</sub> | 73<br><sub>53–94</sub> |
| rock burst · local 5 min · cloud 3 min | 6,385<br><sub>5,927–6,920</sub> | 138.2<br><sub>129.3–150.7</sub> | 305.1<br><sub>303.8–308.1</sub> | 47.6<br><sub>46.2–48.1</sub> | 200<br><sub>189–210</sub> | 41,328<br><sub>28,761–49,312</sub> | 133<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 84<br><sub>61–105</sub> |
| rock burst · local 5 min · cloud 10 min | 7,433<br><sub>6,588–7,981</sub> | 142.1<br><sub>131.9–153.5</sub> | 295.6<br><sub>292.1–298.0</sub> | 40.1<br><sub>34.4–43.9</sub> | 552<br><sub>502–594</sub> | 22,680<br><sub>17,408–27,076</sub> | 183<br><sub>138–216</sub> | 1,293<br><sub>955–1,510</sub> | 114<br><sub>83–144</sub> |
| earthquake · local 0 s · cloud 1 min | 23,192<br><sub>21,888–24,007</sub> | 359.7<br><sub>349.2–374.0</sub> | 391.3<br><sub>387.2–396.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 722<br><sub>686–748</sub> | 86,368<br><sub>86,354–86,382</sub> | 416<br><sub>374–457</sub> | 2,882<br><sub>2,687–2,977</sub> | 370<br><sub>140–521</sub> |
| earthquake · local 0 s · cloud 3 min | 24,596<br><sub>22,684–25,920</sub> | 355.5<br><sub>347.5–367.1</sub> | 394.4<br><sub>388.1–401.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,382<br><sub>86,358–86,398</sub> | 441<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 0 s · cloud 10 min | 26,620<br><sub>24,769–28,782</sub> | 359.0<br><sub>349.8–376.1</sub> | 389.1<br><sub>385.0–395.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 1,202<br><sub>1,127–1,258</sub> | 86,389<br><sub>86,382–86,404</sub> | 479<br><sub>419–560</sub> | 3,130<br><sub>2,864–3,519</sub> | 429<br><sub>167–639</sub> |
| earthquake · local 1 min · cloud 1 min | 23,364<br><sub>22,018–24,320</sub> | 364.1<br><sub>352.6–377.6</sub> | 387.4<br><sub>384.2–392.8</sub> | 48.2<br><sub>48.1–48.3</sub> | 722<br><sub>686–748</sub> | 86,363<br><sub>86,346–86,371</sub> | 416<br><sub>374–457</sub> | 2,882<br><sub>2,687–2,977</sub> | 370<br><sub>140–521</sub> |
| earthquake · local 1 min · cloud 3 min | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 393.0<br><sub>387.2–398.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,391<br><sub>86,361–86,410</sub> | 441<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 1 min · cloud 10 min | 27,016<br><sub>25,076–29,018</sub> | 359.1<br><sub>350.7–375.4</sub> | 389.0<br><sub>384.5–394.0</sub> | 48.2<br><sub>48.1–48.3</sub> | 1,200<br><sub>1,123–1,258</sub> | 86,397<br><sub>86,384–86,421</sub> | 482<br><sub>419–560</sub> | 3,146<br><sub>2,864–3,519</sub> | 434<br><sub>167–639</sub> |
| earthquake · local 5 min · cloud 1 min | 23,868<br><sub>22,656–24,799</sub> | 379.2<br><sub>368.9–393.6</sub> | 372.6<br><sub>368.7–377.3</sub> | 48.3<br><sub>48.2–48.5</sub> | 722<br><sub>686–748</sub> | 86,354<br><sub>86,329–86,386</sub> | 417<br><sub>374–457</sub> | 2,882<br><sub>2,687–2,977</sub> | 370<br><sub>140–521</sub> |
| earthquake · local 5 min · cloud 3 min | 25,785<br><sub>24,056–26,929</sub> | 369.5<br><sub>361.9–383.0</sub> | 382.2<br><sub>376.3–387.2</sub> | 48.3<br><sub>48.1–48.5</sub> | 734<br><sub>698–761</sub> | 86,445<br><sub>86,404–86,478</sub> | 442<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 5 min · cloud 10 min | 28,335<br><sub>26,724–30,277</sub> | 364.8<br><sub>355.6–384.1</sub> | 384.1<br><sub>380.9–389.8</sub> | 48.2<br><sub>48.2–48.3</sub> | 1,213<br><sub>1,122–1,277</sub> | 86,482<br><sub>86,441–86,551</sub> | 479<br><sub>420–560</sub> | 3,127<br><sub>2,864–3,519</sub> | 429<br><sub>167–638</sub> |

### Against local 1 min · cloud 3 min, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Local h | Wait p95 | Locate all, mean | Locate exposing, mean |
|---|---:|---:|---:|---:|---:|---:|
| workday · local 0 s · cloud 1 min | -78 % | +7 % | +0 % | -44 % | -8 % | -9 % |
| workday · local 0 s · cloud 3 min | -72 % | -1 % | +0 % | +1 % | -1 % | -1 % |
| workday · local 0 s · cloud 10 min | +2968 % | +9 % | +0 % | -32 % | +19 % | +25 % |
| workday · local 1 min · cloud 1 min | -14 % | +9 % | -0 % | -44 % | -8 % | -9 % |
| workday · local 1 min · cloud 10 min | +2958 % | +9 % | +0 % | -31 % | +19 % | +25 % |
| workday · local 5 min · cloud 1 min | +25 % | +15 % | -1 % | -44 % | -6 % | -8 % |
| workday · local 5 min · cloud 3 min | +140 % | +12 % | -1 % | -4 % | +2 % | -0 % |
| workday · local 5 min · cloud 10 min | +3675 % | +11 % | -1 % | -27 % | +23 % | +26 % |
| rock burst · local 0 s · cloud 1 min | -10 % | +4 % | -2 % | -35 % | -13 % | -12 % |
| rock burst · local 0 s · cloud 3 min | -0 % | -0 % | +0 % | -1 % | -0 % | -0 % |
| rock burst · local 0 s · cloud 10 min | +16 % | +4 % | -3 % | -43 % | +39 % | +36 % |
| rock burst · local 1 min · cloud 1 min | -10 % | +5 % | -2 % | -35 % | -13 % | -12 % |
| rock burst · local 1 min · cloud 10 min | +16 % | +4 % | -3 % | -43 % | +39 % | +36 % |
| rock burst · local 5 min · cloud 1 min | -10 % | +7 % | -3 % | -34 % | -13 % | -11 % |
| rock burst · local 5 min · cloud 3 min | +1 % | +3 % | -1 % | +2 % | +0 % | +2 % |
| rock burst · local 5 min · cloud 10 min | +17 % | +6 % | -4 % | -44 % | +38 % | +38 % |
| earthquake · local 0 s · cloud 1 min | -7 % | +1 % | -0 % | -0 % | -6 % | -6 % |
| earthquake · local 0 s · cloud 3 min | -2 % | -0 % | +0 % | -0 % | -0 % | -0 % |
| earthquake · local 0 s · cloud 10 min | +7 % | +1 % | -1 % | -0 % | +8 % | +9 % |
| earthquake · local 1 min · cloud 1 min | -6 % | +2 % | -1 % | -0 % | -6 % | -6 % |
| earthquake · local 1 min · cloud 10 min | +8 % | +1 % | -1 % | +0 % | +9 % | +10 % |
| earthquake · local 5 min · cloud 1 min | -4 % | +6 % | -5 % | -0 % | -6 % | -6 % |
| earthquake · local 5 min · cloud 3 min | +3 % | +4 % | -3 % | +0 % | +0 % | -0 % |
| earthquake · local 5 min · cloud 10 min | +13 % | +2 % | -2 % | +0 % | +8 % | +9 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Local h**: on-premise executor-hours of ready capacity — hardware the mine already owns, so these hours are not billed.
- **Drained h**: simulated hours until the queue was empty.
- **Overloads**: decisions where no capacity within both caps avoided a predicted breach, so the autoscaler ran flat out.
- **Wait p95 s**: the 95th percentile of the seconds a job waited in the queue before an executor took it.
- **Locate all, mean s**: seconds from an event to its first location, over every event.
- **Locate all, p95 s**: the 95th percentile of the seconds from an event to its first location.
- **Locate exposing**: seconds from an event that truly exposed someone to at least moderate ground motion (judged by the simulator from the truth) to its first location.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **day** (3); **local coldstart** (3); **cloud coldstart** (3). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
    "mode": "off",
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

<sub>Tables rendered by platform-experiments `024b6e7d5aa2`.</sub>
