## Reading

**Intent matters most when capacity is scarce, and stops mattering when it is
not.** Compared with no intent at the same cloud cap:

- **No cloud at all:** decay with restored work exempt cuts breaches by 36 % and
  its SLA as submitted by 24 %, locates exposing events 18 % sooner and finishes
  them 58 % sooner. The queue is hours deep, and ordering is the only lever left.
- **20 cloud executors:** decay also cuts cloud time by a third (37.6 → 23.5 h
  with restored work exempt, 27.7 h made final): with less urgent work waiting, the
  autoscaler buys less. Exposing events are located 35–41 % sooner. Decay made final
  lets the SLA as submitted slide 38 % — decayed work that is never restored waits
  for hours.
- **60 (the default):** as in the intent-modes sweep — a quarter to a half fewer
  breaches, no more cloud time, exposing events located 13–18 % sooner.
- **200:** capacity absorbs almost everything and every run drains in two hours.
  Decay still trims breaches (−7 to −16 %) but the SLA as submitted rises by half
  — on counts small enough (301 → 445 breaches over six seeds) that decaying a few
  hundred jobs shows. Exposing events are located within a few seconds of each
  other whatever the intent.

**Both, exempt** finishes exposing events fastest at every cap but the largest
(−74 to −90 %), but
locates them later and breaches more once there is enough capacity for the
promoted work to crowd out the rest.

**Caveat.** Exemption lets restored work be late without buying cloud; with no
cloud to buy it changes what counts as late for the autoscaler's projection but
not the fleet, which is why the arms still differ at cap 0.
