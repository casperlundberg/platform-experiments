#!/usr/bin/env bash
#
# When no executor count can avoid a breach, does the controller ask for what
# the queue needs, or for everything it is allowed?
#
# See README.md for what this is asking and why.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/harness.sh"

harness::start

# Caps wide enough that "ask for everything" would be unmistakable, and
# coldstarts an operator would recognise. The whole point is that 220 and 3 are
# not easily confused.
LOCAL_CAP=20
CLOUD_CAP=200
CEILING=$((LOCAL_CAP + CLOUD_CAP))

harness::log "Registering a cold target with realistic coldstarts"

harness::as -X POST "$AUTOSCALER_API/v1/targets" -d "{
  \"target\": {\"id\": \"storhall\", \"name\": \"Storhall\", \"kind\": \"simulation\",
             \"mode\": \"driven\",
             \"config\": {\"local_coldstart_seconds\": \"120\",
                        \"cloud_coldstart_seconds\": \"300\"}},
  \"settings\": {\"local_executor_cap\": $LOCAL_CAP, \"cloud_executor_cap\": $CLOUD_CAP,
               \"min_local_executors\": 0,
               \"local_coldstart_seconds\": 120, \"cloud_coldstart_seconds\": 300,
               \"horizon_seconds\": 600, \"simulation_step_seconds\": 10,
               \"deadline_seconds_by_priority\": {\"100\": 60},
               \"default_deadline_seconds\": 3600,
               \"scale_up_cooldown_seconds\": 0, \"max_scale_up_step\": 1000,
               \"safety_factor\": 1.15}
}" >/dev/null
harness::ok "target registered with a 2m local and 5m cloud coldstart"

# cycle runs one decision against a supplied queue and a stated fleet, and
# leaves the whole result in $WORK/cycle.json for the checks that follow.
#
# The fleet is never asserted, only observed: the simulation adapter reports
# what it is holding and ages it, so whether capacity is ready or still
# starting is a consequence of what earlier cycles asked for. That is the point
# — the difference between those two is the entire subject here, and stating it
# directly would be assuming the answer.
cycle() {
  local depth=$1 age=$2 arrivals=$3 deadline=$4
  harness::as -X PATCH "$AUTOSCALER_API/v1/targets/storhall/settings" \
    -d "{\"deadline_seconds_by_priority\": {\"100\": $deadline}}" >/dev/null
  harness::as -X POST "$AUTOSCALER_API/v1/targets/storhall/cycle" -d "{
    \"workload\": {\"executor_throughput_per_second\": 1,
                 \"queues\": {\"100\": {\"depth\": $depth,
                                     \"oldest_job_age_seconds\": $age,
                                     \"arrival_rate_per_second\": $arrivals}}}
  }" > "$WORK/cycle.json"
}

plan()    { harness::json "d[\"decision\"][\"plan\"][\"$1\"]" < "$WORK/cycle.json"; }
reason()  { harness::json 'd["decision"]["reason"]' < "$WORK/cycle.json"; }
breach()  { harness::json 'str(d["decision"]["projection"].get("breach_expected", False)).lower()' < "$WORK/cycle.json"; }

# ------------------------------------------- a cold pool against a tight deadline
#
# P100 is 55s into a 60s deadline and nothing is running. The local tier is two
# minutes away, so no executor count avoids this breach. What it asks for is
# the question.

harness::log "A cold pool, 55s into a 60s deadline: nothing can start in time"

cycle 20 55 0.1 60

TOTAL=$(( $(plan local_executors) + $(plan cloud_executors) ))
harness::note "plan: $(plan local_executors) local + $(plan cloud_executors) cloud"

if (( TOTAL > 0 && TOTAL < CEILING / 4 )); then
  harness::ok "asked for $TOTAL executors, not the $CEILING its caps allow"
else
  harness::bad "asked for $TOTAL executors against a ceiling of $CEILING"
  harness::note "a breach that no capacity can avoid is not a reason to buy all of it"
fi

# The reasoning is the only place an operator can see that this was not
# under-provisioning. A modest count beside a breach looks like a mistake
# unless the decision says otherwise.
REASON=$(reason)
harness::note "reason: $REASON"

if [[ "$REASON" == *"no executor count avoids it"* ]]; then
  harness::ok "the reasoning says the breach was unavoidable"
else
  harness::bad "the reasoning does not say the breach was unavoidable"
fi

if [[ "$REASON" == *"coldstart"* ]]; then
  harness::ok "and it names coldstart as the reason"
else
  harness::bad "and it does not name coldstart"
fi

harness::expect "the projection still reports the breach" "$(breach)" "true"

# ------------------------------------------- the same queue, room to act in
#
# Move the deadline past the local coldstart and capacity can arrive in time,
# so this must read as an ordinary requirement again.

harness::log "The same queue with a deadline beyond the coldstart"

cycle 20 55 0.1 600

REASON=$(reason)
harness::note "reason: $REASON"

if [[ "$REASON" != *"no executor count avoids it"* ]]; then
  harness::ok "with room before the deadline it is an ordinary requirement again"
else
  harness::bad "still reported as unavoidable with ten minutes of slack"
fi

# And it must not have reached for the cloud. Local is not at its cap, so there
# is no proven overflow, and cloud is overflow or it is nothing.
harness::expect "and it stayed on the local tier" "$(plan cloud_executors)" "0"

# ------------------------------------------- a genuine overload
#
# Coldstart must not have swallowed the case the ceiling exists for: when
# arrivals outrun both caps serving from the first instant, capacity really is
# the binding constraint.

harness::log "A genuine overload: 500 jobs a second against a ceiling of $CEILING"

cycle 5000 50 500 60

TOTAL=$(( $(plan local_executors) + $(plan cloud_executors) ))
harness::expect "a genuine overload still runs flat out at both caps" "$TOTAL" "$CEILING"
harness::note "reason: $(reason)"

# ------------------------------------------- capacity that is starting is not throughput
#
# The defect in one comparison. An engine that folds pending capacity into the
# count it simulates cannot tell a fleet that is working from an identical
# fleet that is still pulling an image — and the second is what every cycle
# during a ramp actually looks like.
#
# This gets its own target. Doing it on the one above would inherit the
# overload's fleet and the scale-down step limit that follows it, and a check
# whose setup is three sections of history is a check nobody can read.

harness::log "A second target, so the fleet has a history of exactly one cycle"

harness::as -X POST "$AUTOSCALER_API/v1/targets" -d "{
  \"target\": {\"id\": \"ramping\", \"name\": \"Ramping\", \"kind\": \"simulation\",
             \"mode\": \"driven\",
             \"config\": {\"local_coldstart_seconds\": \"120\",
                        \"cloud_coldstart_seconds\": \"300\"}},
  \"settings\": {\"local_executor_cap\": $LOCAL_CAP, \"cloud_executor_cap\": $CLOUD_CAP,
               \"min_local_executors\": 0,
               \"local_coldstart_seconds\": 120, \"cloud_coldstart_seconds\": 300,
               \"horizon_seconds\": 1800, \"simulation_step_seconds\": 10,
               \"deadline_seconds_by_priority\": {\"100\": 900},
               \"default_deadline_seconds\": 3600,
               \"scale_up_cooldown_seconds\": 0, \"max_scale_up_step\": 1000,
               \"safety_factor\": 1.0}
}" >/dev/null
harness::ok "registered, cold, with a deadline that leaves room to act"

ramp_cycle() {
  harness::as -X POST "$AUTOSCALER_API/v1/targets/ramping/cycle" -d '{
    "workload": {"executor_throughput_per_second": 1,
                 "queues": {"100": {"depth": 300, "oldest_job_age_seconds": 40,
                                    "arrival_rate_per_second": 1}}}
  }' > "$WORK/cycle.json"
}

# One cycle from cold: nothing is running, so the engine asks for capacity.
ramp_cycle
FIRST=$(( $(plan local_executors) + $(plan cloud_executors) ))
harness::note "from cold  : asked for $FIRST — $(reason)"

if (( FIRST > 0 )); then
  harness::ok "a cold pool asked for capacity"
else
  harness::bad "a cold pool asked for nothing, so there is no ramp to observe"
fi

# The same observation again. The capacity requested above has been created but
# cannot have finished a two-minute coldstart in the time this took, so the
# adapter now reports it as pending — and the decision has to say so.
ramp_cycle
SECOND_REASON=$(reason)
harness::note "one cycle on: $SECOND_REASON"

if [[ "$SECOND_REASON" == *"still starting"* ]]; then
  harness::ok "capacity that cannot work yet is reported as starting, not as throughput"
else
  harness::bad "the decision does not mention capacity that cannot work yet"
  harness::note "an engine that counts a pending executor as throughput cannot say this,"
  harness::note "and will report no breach for a queue that nothing is serving"
fi

# And the count it mentions is the pending one, not a total that hides it.
if [[ "$SECOND_REASON" == *"($FIRST still starting)"* ]]; then
  harness::ok "and it says how much: all $FIRST of them"
else
  harness::bad "it does not say that all $FIRST requested executors are still starting"
fi

harness::finish
