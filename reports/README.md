# Reports

What the sweeps found. Each report names the builds that produced it, the
command that regenerates it, and a digest of its per-run results; at the same
commits every number comes out the same. `sweeps/NAME.md` is the reading and
`sweeps/NAME.json` the definition.

All eight were produced on 2026-09-17 by **autoscaler 1.1.0** (`14f2ca0`) and
**simlab-api 2.0.0** (`ddaa206`), built from clean checkouts, measured by
platform-experiments `152bad5` — 540 runs of one two-hour scenario with one
large rock burst, on six seeds, against 12 on-premise and (unless varied) 60
cloud executors.

| Report | Question | What it found |
|---|---|---|
| [intent-modes](intent-modes/report.md) | What does each intent mode do, from estimates and from the truth? | Decay with restored work exempt: breaches −24 %, cloud −4 %, exposing events located 13 % and finished 78 % sooner. Counting restores costs +41 % cloud. Promotion from estimates costs cloud and first locations. The oracle locates exposing events up to 56 % sooner. |
| [cloud-caps](cloud-caps/report.md) | Does intent's value depend on the cloud budget? | Most valuable when capacity is scarce: with 20 cloud executors decay also cuts cloud time by a quarter to two-fifths and locates exposing events 35–41 % sooner. With 200 it hardly matters. |
| [lookahead-uncertainty](lookahead-uncertainty/report.md) | How far ahead to protect, and how much to allow for location error? | The allowance is the dial: ±0 m relaxes most and misses a quarter to two-fifths of exposing events, ±150 m misses almost none and relaxes almost nothing, ±50 m misses two or three a seed. Lookahead barely moves the cost. |
| [pick-jitter](pick-jitter/report.md) | How good must locations be? | Breaches falling with pick error is not success: at 20 ms nearly half of exposing events are decayed at some point, at 50 ms two-thirds. A fixed allowance is not enough; it should follow each location's uncertainty. |
| [pre-location](pre-location/report.md) | Does acting before a location help? | Not with 30 sensors: the first sensors to trigger say too little to decay anything, and promotion from them raises breaches nearly sixfold. |
| [mid-run-switch](mid-run-switch/report.md) | What does changing intent mid-run do? | Intent's effect is in the burst: on at the burst equals on throughout, off at the burst equals never. Promotion's cost persists after it is switched off. |
| [promotion](promotion/report.md) | Can promotion keep its benefit without its cost? | Not as tested. Restarting the deadline removes its extra breaches but not its cloud time; very-high ground motion never occurs at these magnitudes; promoting less high changes little. |
| [workforce](workforce/report.md) | How does crew size change intent's value? | More people protect more of the mine: decay saves fewer breaches (−28 % → −17 %) and misses about one exposing event in ten. |

## Threads worth pulling

- An allowance for location error taken from each location's own uncertainty,
  rather than one number (pick-jitter).
- Promotion that raises only the next picks an event needs, rather than all its
  remaining work (promotion).
- A measure of the value of restoring decayed work for someone who arrives after
  an event, which exposure judged at the moment of the event cannot see
  (intent-modes).
- More scenario shapes than one burst in two hours, and more exposing events at
  high ground motion: two in 129 here.
