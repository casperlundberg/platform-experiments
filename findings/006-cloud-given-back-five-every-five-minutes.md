# Cloud was given back five executors every five minutes

**Found by:** the report that "cloud keeps resources despite not needed
anymore, downscaling after cloud burst seems to be failing", confirmed by
driving the engine through a burst and a quiet hour with its default settings.
**Repository:** `autoscaler` · `internal/policy/engine.go`, `internal/config`
**Severity:** results-corrupting for every cloud-hour figure recorded on 1.x;
a direct cost on any real cloud tier.

## What happened

Two hysteresis rules, each reasonable alone, compounded:

- `MaxScaleDownStep = 5`: a tier comes down at most five executors a cycle.
- `ScaleDownCooldown = 5m`, measured from the **last scale-down**: after one,
  no other may follow for five minutes.

Together: five executors every five minutes, one a minute. With the engine
saying from the first quiet cycle that four executors were enough:

| Cloud held after the burst | Time to give it all back | Idle cloud executor-hours |
|---|---|---|
| 60 | 65 min | 37.5 |
| 200 | 3 h 25 min | 358 |

And `CloudSince`, the clock for the cloud minimum lifetime, restarted for the
whole tier whenever it grew at all, so two executors added late in an
aftershock renewed the lifetime of every executor bought before them. The two
tiers also shared one scale-down clock, so shrinking the local tier held back
the cloud one.

## Why it mattered

The recorded run behind finding 005 dripped its 200 cloud executors back at
five per five minutes for its whole length with the queue empty. The cloud-caps
report's 228 cloud-hours in two hours at a cap of 200 is mostly this. Every
cloud-hour figure in the 1.x reports includes it, and — with finding 005 — the
two-hour shape's breach counts were helped by capacity still dripping back from
the start of the run when the burst arrived.

## Why nothing caught it

The engine tests set `ScaleDownCooldown = 0` and `MaxScaleDownStep = 100`, so
they could work plans out by hand. That was reasonable for testing the
requirement, and it meant the default hysteresis was never exercised as a
whole. Each rule had its own test, and each test passed; no test ran the
engine through a burst and a quiet hour and asked when the cloud was gone.

## The fix (autoscaler 2.0.0)

Chosen with the platform's owner, per tier:

- A tier comes down to the most its requirement asked for within its
  **scale-down window**, in one move: `cloud_scale_down_window_seconds`
  (default 300) and `local_scale_down_window_seconds` (default 900; local is
  already paid for and a warm executor answers the next burst). Both are
  settings so they can be swept. `scale_down_cooldown_seconds` and
  `max_scale_down_step` are gone and refused by name.
- Each cloud executor keeps its minimum lifetime from its own request.
- The tiers keep separate memories.

## What it changes

On the two-hour burst, six seeds, no intent: 1.1.0 used 61.1 cloud-hours for
1,687 breaches; 2.0 uses 25.0 at a 5-minute cloud window and 49.5 at 30
minutes, with breaches of 4,149 and 2,396, and the queue drains in 2.1 hours
instead of 10.2 at the longer window. The higher breach count is not the
release rule's alone: 1.1.0 met the burst at minute 30 with 25–30 cloud
executors left over from its start-up spike (finding 005), so part of its
advantage on this shape is capacity bought for nothing that happened to still
be there. The calibrated days, where the burst comes eight hours in, are the
fair comparison (four seeds, exploratory builds of 2026-09-21, 1.1.0 against
2.0 at two cloud windows):

| Day, intent | 1.1.0 breaches / cloud h | 2.0, 30-min window | 2.0, 5-min window |
|---|---:|---:|---:|
| workday, none | 49 / 160 | 13 / 115 | 16 / 53 |
| workday, decay | 1,650 / 141 | 70 / 105 | 1,720 / 44 |
| rock burst, none | 6,164 / 258 | 6,038 / 222 | 6,338 / 134 |
| rock burst, decay | 5,778 / 217 | 3,904 / 199 | 6,810 / 122 |
| earthquake, none | 20,661 / 524 | 21,604 / 441 | 24,974 / 357 |
| earthquake, decay | 15,271 / 520 | 13,633 / 426 | 20,038 / 364 |

At a 30-minute cloud window 2.0 matches or beats 1.1.0 on breaches everywhere
but the earthquake without intent (+5 %), for 8–35 % less cloud, and mean waits
fall sharply (rock burst without intent: 1,841 s to 360 s). A 5-minute window
buys a much smaller bill with more breaches under a burst. The window is the
dial between the two, which is why it is a setting; a sweep on released builds
should choose its default.

## Guarded by

- `autoscaler/internal/policy/release_test.go`: the regression with default
  settings (`TestAfterABurstTheCloudGoesInMinutesNotAnHour`), one window and
  in one move, a lull inside the window, local's longer window, local never
  delaying cloud, per-executor lifetimes, an aftershock tail, and the property
  `TestHeldCapacityIsExactlyWhatTheWindowsAndLifetimesJustify`. Each was
  confirmed by reintroducing the behaviour it guards against: the drip, the
  tier-wide lifetime, one window for both tiers.
- [Experiment 006](../experiments/006-cloud-bought-and-given-back), check
  three: after the burst, no more cloud than the window and lifetime allow
  (1.1.0: 12.6 executor-hours against 10.0).

## The general lesson

Two limits on the same motion multiply. A step limit per cycle and a cooldown
per step are each a brake; together they are a rate, and nobody chose that
rate. Test hysteresis the way it runs — all of it, at its defaults, over time —
not one rule at a time with the others switched off.
