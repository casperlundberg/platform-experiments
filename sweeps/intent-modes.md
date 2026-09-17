## Reading

**Decay helps; promotion from the mine's own estimates does not, yet.** Against
no intent, on the default capacity (12 on-premise, 60 cloud):

- **Decay with restored work exempt** — the default — cuts breaches by a quarter
  (1,687 → 1,281) with no more cloud time (61.1 → 58.5 h), locates events that
  truly exposed someone 13 % sooner (87 → 76 s) and finishes their picks four
  times sooner (5,025 → 1,113 s). The SLA as submitted is unchanged (−1 %): the
  work decayed was work that could wait.
- **Decay with every restore counted** is the same ordering bought at +41 % cloud
  time (85.9 h). Restored work comes back already late, each restore is a breach
  no capacity avoids, and the autoscaler runs flat out. This is why restored work
  is exempt by default.
- **Decay made final** has the fewest breaches of any estimate arm (894) at the
  same cloud time. It is not the default because it stops protecting anyone who
  arrives after the lookahead, and nothing measured here — exposure is judged at
  the moment an event happens — can see that cost.
- **Promotion** under estimates costs more cloud time (+17 to +46 %) and, unless
  the deadline restarts on a change, far more breaches (+47 to +111 %); and the
  first location of an exposing event comes later, not sooner (+12 to +34 %): promotion can only act once an event is located, so it
  cannot speed the location that decides it, and the promoted work — already past
  a 30-second deadline — takes capacity from everything else. What it buys is the
  final location of exposing events, six to fourteen times sooner.

**Knowledge is worth a great deal.** The oracle arms, deciding from where events
really were, locate exposing events up to 56 % sooner (38 s) and cut breaches by
up to 95 %. The gap between the estimate and oracle arms is what better locations
could still win.

**Misses.** Across six seeds, 129 events truly exposed someone to at least
moderate ground motion (only 2 to high). Estimate arms decayed 2–3 of them per
seed on average at some point; the oracle none. Counting where people were when
an event happened (simlab-api 2.0.0) took the oracle's misses from three to five
per seed to none.

**Caveats.** Six seeds, with 6 to 44 exposing events each; per-seed ranges in the
table are wide. One scenario shape (a two-hour window with one large burst).
Exposure is judged at the instant an event happens, so the value of restoring
work for someone who arrives later is not measured.
