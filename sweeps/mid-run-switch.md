## Reading

**Intent's effect is almost entirely in the burst.** Switching decay on at the
burst gives the same result as decay throughout; switching it off at the burst
gives the same result as no intent. Before the burst there is little queue to
reorder.

Switching to both decay and promotion at the burst costs what promotion costs
throughout (breaches +66 %, cloud +17 %), and dropping promotion again thirty
minutes after the burst recovers only part of it (+55 %, +8 %): the promoted work
is already late and already dispatched.

Every change here is a schedule. The same changes made by hand through the API
while a run is in flight are recorded with the cycle they took effect from and
replay identically — experiment 005 checks exactly that.
