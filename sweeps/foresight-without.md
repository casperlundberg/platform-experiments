## Reading

The same three calibrated days, seeds and autoscaler (2.0.0) as
[`foresight-with`](../foresight-with/report.md); the one difference is
simlab-api 4.0.0-dev, where the mine's own view protects a person along every
stretch of tunnel they could walk to over the lookahead (300 s at 1 m/s),
instead of along the route the simulator will walk them. Intent off and the
oracle arm come out byte for byte as they did on 3.0.0 — the change touches only
what the mine knows — so every difference below is the foresight.

**Without foresight, decay relaxes a little less, and keeps most of what it
bought.** Decay against no intent on the same day, with foresight → without:

| | Locate exposing | Process exposing | Breaches |
|---|---:|---:|---:|
| workday | −20 % → −17 % | −53 % → −57 % | +10,483 % → +8,731 % |
| rock burst | −23 % → −20 % | −82 % → −78 % | +7 % → +2 % |
| earthquake | −56 % → −50 % | −81 % → −66 % | −20 % → −20 % |

Knowing only where people are, the mine protects every way they could go, so
fewer events are decayed: 16 % fewer on the workday (1,885 → 1,578 a day), 7 %
under the rock burst, 2 % under the earthquake. Less relaxed work frees less
capacity for the events that matter, and that costs most where contention is
highest: under the earthquake, exposing events finish 77 % later than with
foresight (11,522 → 20,399 s) and are first located 15 % later (172 → 197 s).
Even so, decay without foresight still halves the time to locate them against no
intent, and finishes them in a third of the time.

**On a quiet day, less decay costs less.** Decay's known price on a day the
fleet keeps up with (see `scenario-shapes`) is breaches; relaxing fewer events
takes 17 % off it (1,720 → 1,435 a day).

**Misses barely move.** Exposing events decayed at some point, per day: 10.5 →
8.3 on the workday, 12.8 → 11.3 under the rock burst, 16.5 → 17.0 under the
earthquake. They come from estimates of where events are, not of where people
go.

**For the reports before simlab-api 4.0.0:** every one that protects people
credited the mine with this foresight. Under the earthquake it overstated how
much sooner decay finishes exposing events (81 % against 66 %), and slightly how
much sooner it locates them (56 % against 50 %); the breaches it saved were not
overstated.

**Caveats.** Four seeds; one mine and the default workforce (8 people, 4 crewed
and 3 autonomous vehicles); vehicles' routes are known in both reports, so only
people's foresight is measured. This report names platform-experiments
1.0.1-dev.1, for the reason given in `foresight-with`.
