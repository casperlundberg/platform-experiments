#!/usr/bin/env bash
#
# Does a completed run account for every job it admitted?
#
# See README.md for what this is asking and why.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/harness.sh"

harness::start

harness::log "Defining a workload that forces the fleet up and down"

curl -sf "$API/api/mines" -H 'Content-Type: application/json' -d '{
  "id":"storhall","name":"Storhall","sensors":30,"background_rate_per_hour":90}' >/dev/null

# Bursts are the point. A flat workload never makes the controller scale down
# while long jobs are still running, which is the state that loses work.
curl -sf "$API/api/scenarios" -H 'Content-Type: application/json' -d '{
  "id":"burst-train","mine_id":"storhall","name":"Repeated bursts",
  "duration_seconds":7200,"job_seconds":45,"seed":20260912,
  "priority_mix":{"100":1,"50":1,"25":2},
  "bursts":[{"at_seconds":900,"magnitude":40,"aftershock_decay_seconds":600},
            {"at_seconds":3600,"magnitude":50,"aftershock_decay_seconds":900},
            {"at_seconds":5400,"magnitude":30,"aftershock_decay_seconds":600}]}' >/dev/null
harness::ok "mine and scenario registered"

# Caps that are tight enough that the controller has to keep moving, rather
# than parking at the ceiling and staying there.
run_one() {
  local name=$1 settings=$2
  curl -sf "$API/api/runs" -H 'Content-Type: application/json' -d "{
    \"name\": \"$name\", \"mode\": \"simulation\", \"scenario_id\": \"burst-train\",
    \"decision_interval_seconds\": 15, \"time_compression\": 100000,
    \"settings\": $settings}" | harness::json 'd["id"]'
}

harness::log "Replaying it under three policies"

declare -A RUNS
RUNS[tight]=$(run_one "Tight caps" '{"local_executor_cap": 6, "cloud_executor_cap": 6, "local_scale_down_window_seconds": 0, "cloud_scale_down_window_seconds": 0}')
RUNS[generous]=$(run_one "Generous caps" '{"local_executor_cap": 40, "cloud_executor_cap": 80}')
RUNS[local-only]=$(run_one "On-premise only" '{"local_executor_cap": 20, "cloud_executor_cap": 0}')

for label in tight generous local-only; do
  id=${RUNS[$label]}
  status=$(harness::run_to_completion "$id")
  if [[ "$status" != "completed" ]]; then
    harness::bad "run '$label' ended as $status"
    continue
  fi

  read -r submitted completed breaches < <(
    curl -sf "$API/api/runs/$id/metrics" | harness::json \
      '"%d %d %d" % (d["jobs_submitted"], d["jobs_completed"], d["sla_breaches"])')

  harness::expect "run '$label' completed every job it admitted ($submitted)" \
    "$completed" "$submitted"

  # A breach is a job that waited too long. A job that was never served cannot
  # have breached, so breaches above the job count means something is being
  # counted that is not a job.
  if [[ "$breaches" -gt "$submitted" ]]; then
    harness::bad "run '$label' recorded $breaches breaches over $submitted jobs"
  else
    harness::ok "run '$label' recorded $breaches breaches over $submitted jobs"
  fi
done

# ------------------------------------------------------- the seed still holds
#
# Two runs of the same scenario must admit exactly the same jobs, or a
# comparison between policies is measuring the workload rather than the policy.

harness::log "Checking the seed still fixes the workload"

A=$(curl -sf "$API/api/runs/${RUNS[tight]}/metrics" | harness::json 'd["jobs_submitted"]')
B=$(curl -sf "$API/api/runs/${RUNS[generous]}/metrics" | harness::json 'd["jobs_submitted"]')
C=$(curl -sf "$API/api/runs/${RUNS[local-only]}/metrics" | harness::json 'd["jobs_submitted"]')
harness::expect "all three runs replayed the identical workload" "$A|$B|$C" "$A|$A|$A"

harness::finish
