## Reading

Autoscaler 2.0 gives capacity back one scale-down window after it was last
wanted, per tier, and keeps each cloud executor for a minimum lifetime. The
reference arm is what 2.0 ships: local window 15 minutes, cloud window 5, cloud
lifetime 10. Each other arm changes one of the three, with local capacity just
short of the average day (12) and with plenty of it (24).

**The local window must never be zero, and longer is better.** Local capacity
is hardware the mine already owns.

| Breaches against the 15-minute window | local window 0 | local window 60 min |
|---|---:|---:|
| workday, local 12 | +2,069 % (16 → 352) | −26 % |
| workday, local 24 | 14 → 6,524 | −35 % |
| rock burst, local 12 / 24 | +71 % / +190 % | −4 % / −0 % |
| earthquake, local 12 / 24 | +29 % / +76 % | −11 % / −11 % |

With no window, local capacity follows each cycle's requirement down to what
the deadlines need at that moment. On a workday with 24 local executors that
turned 14 breaches into 6,524, and the 95th-percentile wait into a whole day.
An hour's window instead costs 1–17 % more local executor-hours and nothing
billed, and cuts breaches by up to 35 %.

**A longer cloud window buys shorter waits more than fewer breaches.**

| 30-minute cloud window against 5 | Cloud h | Breaches | Wait p95 |
|---|---:|---:|---:|
| workday, local 12 | +118 % | −20 % (16 → 13) | −93 % |
| rock burst, local 12 | +66 % | −5 % | −95 % |
| earthquake, local 12 | +24 % | −13 % | −64 % |
| rock burst, local 24 | +70 % | 0 % | −89 % |
| earthquake, local 24 | +32 % | −10 % | −70 % |

Held longer, cloud executors serve work that still had hours left on its
deadline, so the 95th-percentile wait falls by an order of magnitude while
breaches move 0–20 %. Sixty minutes goes further on both counts: 37–173 %
more cloud time with local 12, for 6–20 % fewer breaches. A cloud window of 0
saves up to 8 % of cloud time for up to 11 % more breaches. The minimum
lifetime is the smaller dial: with local 12, none saves 2–18 % of cloud time
for 3–5 % more breaches, and 30 minutes costs 9–72 % more for 4–20 % fewer.

**For the default:** measured against deadlines, which is what the autoscaler
is for, a 5-minute cloud window is the cheaper choice on every day, and the
breaches it gives up are small — at most 3 a workday and 13 % under the
earthquake. A 30-minute window is a runtime choice for an expected aftershock
sequence, where it takes 10–13 % off the breaches for 24–32 % more cloud
time. The local window is the opposite case: it costs nothing billed, and an
hour did as well as 15 minutes or better on every day.

**Caveats.** Four seeds, one mine, intent off. Local executor-hours are
treated as free; on an edge cluster shared with other applications they are
not.
