# Future experiments

Experiments worth running once the platform can do what they need, kept here so
the idea and its reasoning survive until then. Each says what it asks, what has
to exist first, what to measure, and what a "no" would look like — the test an
idea has to pass before it becomes an experiment (see the README, "Writing one").

When one is built it moves to `experiments/NNN-name/` or `sweeps/NAME.json`,
and its entry here is replaced by a pointer.

## The seismic application layer acting on risk zones

Today intent only reorders processing work. People and vehicles follow tracks
computed before the run and react to nothing, so nothing measures what a
faster location is *for*: getting someone out of harm's way sooner, keeping a
machine out of a collapse, or putting a crew back to work in a quiet heading.
These cases close that loop.

### What they all need first

- **A way to change an entity's remaining track mid-run.** Tracks are
  precomputed waypoints (`simlab-api/internal/domain/entity.go`). A command —
  stop, turn around, leave by this route — must replan from the entity's
  current position along the tunnels, deterministically and recorded with the
  cycle it took effect, so `make reproduce` still replays a run exactly.
- **A definition of the zone to keep out of.** Intent's zones today are how far
  an event's ground motion reached when it happened. A zone to *avoid
  afterwards* is a re-entry question — the risk is further events near the
  hypocentre — and needs its own radius and duration from the literature
  (re-entry protocols, aftershock decay) before it is modelled, not a guess.
- **Scoring against the truth.** Each decision is made from estimates; each
  outcome is judged against where events really were, which the simulator
  already keeps separately.

The tunnel network and a deterministic shortest-path search already exist
(`simlab-api/internal/mineplan/graph.go`).

### Case 1 — a vehicle heading into a zone before it is known

A vehicle drives towards the area of an event whose location is not yet
estimated. As soon as the hypocentre estimate declares the zone, the vehicle
gets a turn-around signal and turns back.

- **The question:** how far into the zone does the vehicle get, and how much
  does ordering the processing queue change that?
- **Measure:** time from event to signal; the vehicle's deepest penetration
  into the true zone, and time spent inside it; under no intent, intent from
  estimates, and the oracle.
- **A "no" looks like:** the signal arriving at the same point on the vehicle's
  path whatever the ordering — the location being fast enough, or slow enough,
  that the queue does not matter.
- **Why it matters:** it turns seconds to first location into metres of
  exposure avoided — the measure an operator cares about, and the one the
  sweeps so far could not produce.

### Case 2 — several imperfect hypocentres

**Built.** `simlab-api`'s closure map (`POST /api/runs/{id}/closure`,
`usecase.Closure`) draws the ground the mine would keep people out of from the
locations it had, as a union over events, and measures it against the ground
its events really made dangerous: metre-seconds of tunnel missed, metre-seconds
closed that nothing endangered, how much of the mine is shut, and how long
after each event the map covered all of it. Swept over pick error and over how
much extra a cautious mine closes in `sweeps/closure-map.json`.

What is left of the entry: **a per-location allowance.** The zones a run
records are widened by one fixed 50 m, and the pick-jitter sweep found a fixed
allowance fails once pick error grows. A location carries its own RMS residual
and pick count, so an allowance from those is a change to how `internal/workload`
records zones — and the closure map is the measure that would show whether it
is worth making.

### Case 3 — the safest way out

A vehicle is already inside a high-risk zone when the estimate arrives. A
planner routes it out avoiding the estimated hypocentre at all cost, against
the shortest way out.

- **The question:** does a hazard-aware route lower the exposure the vehicle
  actually receives, given that it plans from an estimate that may be wrong?
- **Measure:** predicted and true peak ground motion along the route, exposure
  integrated over the time spent in the zone, and time to leave it — for the
  shortest route, a route maximising distance from the estimated hypocentre,
  and one minimising hazard integrated along the path with the location's
  uncertainty folded in.
- **A "no" looks like:** the safest-by-estimate route exposing the vehicle
  *more* under the truth than the shortest one, because the detour runs past
  where the event really was.
- **Builds on:** the tunnel graph's Dijkstra search, with a hazard weight on
  each edge instead of its length.

### Case 4 — evacuation along given escape routes

Raised 2026-09-21. After a large event, every person and vehicle is ordered out
along an assigned escape route — to a refuge chamber, the ramp or the shaft —
and follows it. The routes are planned from what the mine knows at the moment
of the order and revised as better locations and further events arrive.

- **The question:** how quickly and how safely does the whole workforce get out,
  and how much does the processing order behind the hazard picture change
  that — does intent's ordering get the locations that shape the routes done
  first?
- **Needs first:** the replanning above, for every entity at once; refuge
  points and exits in the mine plan (`simlab-api/internal/mineplan` has the
  shaft, ramp and drives, not refuges); and a rule for when a route is revised
  — every new location, or only one that closes part of the route in use.
  Vehicles and people sharing a drift may need its capacity modelled, or every
  route will look faster than it is.
- **Measure:** time until the last unit is safe; each unit's exposure along its
  route, predicted and true; how often a route was revised, and how many units
  were sent through a zone that a later location showed to be dangerous; under
  no intent, intent from estimates, and the oracle.
- **A "no" looks like:** evacuation time and exposure the same whatever the
  processing order, because the order goes out on the first location and later
  ones never change a route.
- **Relates to:** case 3, which is one unit already inside a zone; this is every
  unit at once, where routes compete for the same drifts and an escape route
  planned around one estimate may run past the next event.

### The baseline these cases are measured against

Raised 2026-09-21. Most of these cases compare against **no dynamic
reordering**, not against a naive queue: a static priority that is already
calibrated to the mine — a congested drive, an active heading or a refuge route
starts at a higher priority than an empty stope. Beating a strawman proves
nothing; the claim worth making is that dynamic fusion of positions and
seismicity beats the best static assignment a mine planner could set in advance.
Each case should state its static baseline explicitly, pin it in the sweep
definition, and keep the oracle (decisions from the true hypocentres) as the
ceiling.

### Case 5 — wait, or take another path

A vehicle has a planned path; seismicity is active near part of it. Decide
whether it proceeds, waits until activity along the path has decayed, or
takes another route — before it reaches the zone rather than inside it (case 1
is the late version, case 3 the one already inside).

- **Measure:** exposure-seconds avoided against the delay added (waiting time,
  longer route); how often the decision flips as later locations arrive.
- **Baseline:** follow the plan unless a fixed exclusion zone covers it.
- **Needs:** activity along a path over time — an aftershock-decay estimate per
  area — not just the latest event.

### Case 6 — where rock is likely to have loosened, and sending a scaler

Seismic events shake loose rock from the back and walls of drifts. Mark the
drifts whose shaking passed a threshold since they were last scaled, rank them
by who and what will use them next, and dispatch a scaling rig (or a machine to
clear fallen rock) in that order.

- **Measure:** time from event to scaled drift, weighted by traffic about to use
  it; drifts entered by people before being scaled.
- **Baseline:** scale on a fixed schedule, or after inspection reports.
- **Evidence to fuse:** ThingWave's instrumented rock bolts report strain and
  breakage where the seismic system sees shaking — two independent signals of
  the same damage.
- **The threshold is per drift, not one number** (checked 2026-09-21). The
  Canadian Rockburst Support Handbook (Kaiser et al. 1996, §8.2.4, Eqn 8.5a)
  gives the ppv that triggers a seismically induced fall from the back:
  ppv_T = g / (2πf) · (m_d · SF_s − 1), with SF_s the block's static strength
  factor before the event (≥ 1), m_d the dynamic strength multiplier (1.1–1.4
  for steel) and f the dominant frequency (10–30 Hz is critical for typical
  drifts; 20–30 Hz fits Hedley's 1992 ppv–ppa data, §8.2.1). At 25 Hz and
  m_d 1.2, a marginal block (SF_s 1.0) falls at about 0.013 m/s and a sound one
  (SF_s 2.0) at about 0.09 m/s — the moderate-to-high band the hazard levels
  already use. So: a seeded SF_s per drift segment, lower where the ground is
  highly jointed (Table 3.1 expects shaking-induced falls in ground below peak
  strength only if it is highly jointed). That a shaken segment's SF_s drops
  until it is scaled is an assumption to state and sweep, not a finding.
  Minor damage is a skin under 0.25 m (< 7 kN/m², Table 2.1) that standard
  support retains — what a scaler clears. Bauer and Calder's (1978)
  blast-damage limits (no fracturing of intact rock below 0.254 m/s, minor
  slabbing to 0.635 m/s) are widely cited, but only seen in secondary sources.

### Case 7 — re-entry after a blast, by robot first

After a development blast the heading is closed while gas clears and the rock
settles, usually for a fixed time. Faster processing of the blast's own
seismicity and its aftershocks gives an evidence-based re-entry time, and an
estimate of how the new walls are behaving, so robots can go in to support
them before anyone does — and nobody goes in while blast gases remain.

- **Measure:** re-entry time against the fixed one, with the risk taken on
  each (events after re-entry within reach of the heading); time until the
  first robot can start ground support.
- **Baseline:** the mine's fixed re-entry period after blasting.
- **Needs:** the blast plan (where and when), which also tells the system which
  events are blasts rather than natural seismicity; gas readings for the
  ventilation side. Wall capability prediction is a research question of its
  own and should be scoped carefully.

### Case 8 — shortest safe route to a refuge chamber

After a major event, route everyone to the nearest refuge chamber — sealed,
with air and supplies for a stay — by the shortest path the current hazard
picture allows, and get that picture faster than a baseline would.

- **Measure:** time until every person is in a chamber or out; exposure along
  the way; chamber capacity respected.
- **Baseline:** each person's pre-assigned chamber and route.
- **Relates to:** case 4, of which this is the version with shelters rather
  than exits, and capacity per shelter.
- **The escape budget** (checked 2026-09-21). Western Australia's refuge
  chamber guideline (Department of Mines and Petroleum 2013, §5.2) sizes the
  farthest a worker should be from a refuge by what they can walk at a
  moderate pace on half a self-rescuer's nominal duration: with 30-minute
  units, no more than 750 m — 50 m a minute, 0.83 m/s, and "considerably
  reduced" by gradient, ladderways, heat and smoke. So a 15-minute walking
  budget as a parameter, at a pace a little under the simulator's 1 m/s, and
  chambers that hold their occupants for 36 hours. The guideline is written
  for fire and gas; the same chambers are where people go after a large event.
  Case 4 uses the same budget to the nearest exit.

### Case 9 — silent sensors and tags

Chosen 2026-09-21. Geophones, ThingWave tags and the mesh network's nodes stop
reporting for two very different reasons: an event damaged them, or they
failed on their own. Where and when a device went silent, set against the
events located around it, tells the two apart — damage near a hypocentre right
after it, a maintenance ticket anywhere else.

- **The question:** can the fused picture flag damage faster and more reliably
  than a heartbeat timeout, and keep locating well when geophones drop out?
- **Measure:** time from event to a damage flag per silent device; false damage
  flags (silence unrelated to any event); location quality and time to locate
  when the solver stops expecting picks from silent geophones, against waiting
  for them.
- **Baseline:** a fixed heartbeat timeout per device, blind to seismicity.
- **Needs:** device heartbeats from both stacks (tags and nodes through
  Arrowhead, geophones through BEMIS); devices in the simulator that fail —
  seeded, and more likely the harder they were shaken, which the ground-motion
  scaling law intent already uses can give at each device's position; and a
  background failure rate for the silences that are nobody's fault.
- **A "no" looks like:** devices failing for other reasons far more often than
  from shaking, so silence near an event says little more than a timeout does.
- **How devices are lost** (checked 2026-09-21). No fragility curve for in-mine
  devices against shaking turned up. What the sources support: geophones clip
  at ground displacements above a few millimetres, so a nearby large event
  costs picks before it costs devices (IMS, on geophones and accelerometers);
  and a device fixed to the rock goes when the rock does — at moderate damage
  many holding elements fail, at major damage the drift may be closed
  (Kaiser et al. 1996, §2.4). So a device is lost when its drift segment has a
  fall of moderate or major severity (case 6's relation), a geophone clips
  within reach of a large event, and anything can fail at the background rate.
  This is an assumption built from those sources, and should be swept.

### Case 10 — protecting machines as well as people

Chosen 2026-09-21. Intent already counts autonomous vehicles among the
protected, exactly like people. Machines differ: they are expensive, their
routes are planned, and stopping or rerouting one costs production, where a
person's protection is not traded against anything.

- **The question:** what does protecting the fleet by its value buy, in machine
  exposure avoided, against production lost — without weakening anyone's
  protection?
- **Measure:** machine exposure weighted by value; people's exposure (must not
  rise); machine-hours stopped or rerouted; the processing and cloud cost of
  the extra work kept at high priority.
- **Baseline:** today's default — every protected entity treated alike — and,
  as a second reference, machines not protected at all.
- **Needs:** protection levels and weights per class of entity, people strictest;
  a production model saying what a stopped loader or drill costs; the same
  mid-run rerouting as cases 1, 3 and 5.
- **A "no" looks like:** the value-weighted rule converging on protecting
  everything alike, because the machines are always near the people.

### Case 11 — scheduling around seismicity

Chosen 2026-09-21. After a blast or a large event a mine waits — for a fixed
period, often mine-wide — before the next blast or before crews go back into a
heading. A forecast of activity per area, fitted to the events the system has
located, could release quiet areas sooner and hold active ones longer.

- **The question:** does a per-area forecast of seismic activity time blasts and
  crew entry better than a fixed mine-wide wait, in both production and risk?
- **Measure:** heading idle time; events after entry within reach of the crews
  sent in; blasts per shift; how often the forecast released an area that then
  produced an event above the threshold.
- **Baseline:** the mine's fixed wait after blasting, or after an event above a
  magnitude, applied everywhere.
- **Needs:** a schedule of blasts and crew assignments in the simulator; a
  forecast per area from located events only (an aftershock-decay fit), never
  from the simulator's true process, which the workload generator already
  models; case 7's blast plan. The same forecast serves the local-capacity
  follow-up below — readiness for the burst an area is likely to produce.
- **A "no" looks like:** forecasts too uncertain at the scale of one heading to
  release anything sooner than the fixed wait, safely.

### Sources checked for wave B

- Kaiser, P.K., McCreath, D.R. and Tannant, D.D. (1996). *Canadian Rockburst
  Support Handbook*. Geomechanics Research Centre, Laurentian University.
  <https://www.geo-kaiser.ca/www.geo-kaiser.ca/wp-content/uploads/Publications/CRBSHB%201996%20Kaiser%20et%20al.pdf>
- Department of Mines and Petroleum (2013). *Refuge chambers in underground
  mines — guideline*. Resources Safety, Western Australia.
  <https://www.worksafe.wa.gov.au/system/files/documents/2025-02/MSH_G_RefugeChambersUGmines.pdf>
- Institute of Mine Seismology, *Seismic sensors: geophones and
  accelerometers*. <https://www.imseismology.org/sensors/>

### Considered, not taken up

Proposed 2026-09-21 and left aside for now: blasts as calibration shots for
location error; machine noise on geophones, deprioritised by vehicle position;
the order in which to search for missing people after an event; teleoperation
sharing the edge with seismic processing.

## Graduated decay, as the mine learns more

Raised 2026-09-21. Intent today is binary per event: an event is `unknown`,
`kept`, `decayed` or `promoted` (`simlab-api/internal/intent/planner.go`), and a
decayed event's unfinished work drops in one move to `decay_to` (−1) — the same
level whether the event's zone misses everyone by 5 m or by 500 m, and whether
its location came from four picks or twenty. The judgement is taken from the
first location, and a better one from later picks is not used until the event
is finished (`docs/intent.md`, "Limits worth stating"). The plan was a
step-wise decay that lowers work further as knowledge accumulates.

- **The question:** does lowering work in steps — by margin to the nearest
  protected path, by the location's uncertainty, and again as each better
  location arrives — keep decay's benefit while missing fewer exposing events
  than one drop to the floor?
- **Needs first:** re-judging an event on every improved location, not only the
  first; several decay levels, each with its own deadline in the autoscaler's
  SLA; a rule mapping margin and confidence to a level.
- **Sweep:** the levels decayed work goes to; how often events are re-judged;
  and a record of *why* each event was or was not decayed — including the
  events that could have been decayed and were not (unknown for too long, or
  kept by an allowance wider than the location needed).
- **A "no" looks like:** graduated decay converging on the single drop, because
  the first location is already good enough that later ones rarely change a
  judgement.

## Local capacity from a forecast, not a timer

Raised 2026-09-21. On-premise hardware is already paid for, so idle local
executors cost nothing but a warm executor answers a burst without a
coldstart. Today the local tier shrinks one scale-down window after it was last
needed (a fixed, configurable time). A forecast of the arrival rate — the
daily cycle the calibrated day shows, the aftershock decay after a large event
— could instead keep enough local capacity warm for the burst that is likely,
and let the timer handle only what the forecast does not expect.

- **The question:** does a forecast-driven local floor cut breaches at the start
  of a burst, and cloud bought during it, for the same local executor-hours?
- **Needs first:** a forecast the autoscaler can consult (in the workload it is
  sent, or learned from the arrival history it sees), and a local floor derived
  from it, both configurable so they can be swept.
- **A "no" looks like:** the forecast's warm floor never being the binding
  constraint, because bursts arrive faster than any forecast of this workload
  anticipates them.
