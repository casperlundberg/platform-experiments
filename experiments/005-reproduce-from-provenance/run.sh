#!/usr/bin/env bash
#
# Can a run be reproduced from nothing but what it recorded about itself?
#
# See README.md for what this is asking and why.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/harness.sh"

# The original is built from each repository's last commit, in clean worktrees,
# so its provenance names commits that exist. Building from the working copies
# would record whatever is uncommitted there, and the right answer for that is
# a refusal — which is the second half of this experiment, not the first.
harness::log "Building both services from their last commits"
for repo in autoscaler simlab-api; do
  git -C "$PLATFORM_DIR/$repo" worktree add -q --detach "$WORK/src/$repo" HEAD
done
experiment::cleanup() {
  harness::cleanup
  for repo in autoscaler simlab-api; do git -C "$PLATFORM_DIR/$repo" worktree prune 2>/dev/null || true; done
}
trap experiment::cleanup EXIT
(cd "$WORK/src/autoscaler" && make build >/dev/null && cp bin/autoscaler "$WORK/autoscaler")
(cd "$WORK/src/simlab-api" && make build >/dev/null && cp bin/simlab-api "$WORK/simlab-api")
harness::ok "autoscaler $(git -C "$WORK/src/autoscaler" rev-parse --short HEAD), simlab-api $(git -C "$WORK/src/simlab-api" rev-parse --short HEAD)"

harness::postgres
harness::start_autoscaler
harness::start_simlab

harness::log "Recording a run that exercises everything a run records"
curl -sf "$API/api/mines" -H 'Content-Type: application/json' -d '{
  "id":"storhall","name":"Storhall","sensors":40,"background_rate_per_hour":60}' >/dev/null
# A burst with a stated main shock, pick error and a workforce: every dial a
# replay has to carry, so a dial the provenance forgot shows up as a difference.
curl -sf "$API/api/scenarios" -H 'Content-Type: application/json' -d '{
  "id":"burst","mine_id":"storhall","name":"Burst to reproduce",
  "duration_seconds":3600,"job_seconds":20,"seed":20260917,"pick_jitter_seconds":0.003,
  "priority_mix":{"100":1,"50":1,"25":3},
  "workforce":{"people":6,"crewed_vehicles":3,"autonomous_vehicles":2},
  "bursts":[{"at_seconds":600,"magnitude":30,"aftershock_decay_seconds":900,"main_magnitude":3.1}]}' >/dev/null

# record NAME COMPRESSION [EXTRA JSON FIELDS]
record() {
  curl -sf "$API/api/runs" -H 'Content-Type: application/json' -d "{
    \"name\": \"$1\", \"mode\": \"simulation\", \"scenario_id\": \"burst\",
    \"decision_interval_seconds\": 15, \"time_compression\": $2,
    \"settings\": {\"local_executor_cap\": 12, \"cloud_executor_cap\": 30, \"cloud_coldstart_seconds\": 120}
    ${3:+, $3}}" \
    | harness::json 'd["id"]'
}
# Intent that moves work both ways, a change planned for a later cycle, and a
# change made by hand while the run is in flight — slow enough to be caught in
# flight. The hand edit lands at whatever cycle it lands at; that cycle is part
# of what the run recorded, and replaying it is the point.
original=$(record "Original" 600 '"intent": {"mode": "both", "burst_exempt": ["restored"]},
  "intent_schedule": [{"cycle": 40, "settings": {"lookahead_seconds": 60}}]')
# Straight away: the run is in flight from the moment it is created, and at
# this pace it stays so for several seconds.
curl -sf -X PATCH "$API/api/runs/$original/intent" -H 'Content-Type: application/json' \
  -d '{"mode": "decay", "restore": false}' >/dev/null \
  || harness::bad "intent could not be changed while the run was in flight"
harness::expect "the original run completed" "$(harness::run_to_completion "$original")" "completed"
# The hand edit may land before the first cycle, in which case the intent the
# run was created with never took effect and is not recorded as having done so.
sources=$(curl -sf "$API/api/runs/$original/intent" | harness::json '",".join(sorted({c["source"] for c in d["changes"]} - {"initial"}))')
harness::expect "the original recorded its planned and its hand-made intent change" "$sources" "operator,schedule"

# The scenario is changed after the run, as a person tidying up would. A
# reproduction that read the scenario rather than the provenance would now
# replay different work.
curl -sf -X PUT "$API/api/scenarios/burst" -H 'Content-Type: application/json' -d '{
  "id":"burst","mine_id":"storhall","name":"Edited afterwards",
  "duration_seconds":1800,"job_seconds":35,"seed":1,
  "priority_mix":{"100":1},"bursts":[]}' >/dev/null
harness::ok "the scenario was edited after the run"

harness::log "Reproducing it from its provenance alone"
if SOURCE_URL="$API" SOURCE_TOKEN="" "$EXPERIMENTS_DIR/lib/reproduce.sh" "$original" > "$WORK/reproduce.log" 2>&1; then
  harness::ok "the run was rebuilt at its commits and replayed identically"
else
  harness::bad "the run did not reproduce"
fi
grep -E "SAME|DIFFERS|✗" "$WORK/reproduce.log" | while read -r line; do harness::note "$line"; done

# A comparison that could not fail would prove nothing. One value changed in a
# copy of the original has to be found, and named.
harness::log "The comparison notices a single changed value"
python3 "$EXPERIMENTS_DIR/lib/results.py" fetch "$API" "" "$original" "$WORK/original.json" >/dev/null
python3 -c '
import json, sys
results = json.load(open(sys.argv[1]))
results["cycles"][len(results["cycles"]) // 2]["plan_cloud"] += 1
json.dump(results, open(sys.argv[2], "w"))' "$WORK/original.json" "$WORK/tampered.json"
if found=$(python3 "$EXPERIMENTS_DIR/lib/results.py" compare "$WORK/original.json" "$WORK/tampered.json"); then
  harness::bad "a changed plan went unnoticed"
elif grep -qE "DIFFERS cycles: first at cycles\[[0-9]+\]\.plan_cloud" <<< "$found"; then
  harness::ok "a single changed plan is found and named"
else
  harness::bad "a changed plan was noticed, but not where it was: $found"
fi

harness::log "A run from a build with uncommitted changes is refused, not reproduced"
harness::stop_autoscaler
kill "$SIMLAB_PID" 2>/dev/null || true
wait "$SIMLAB_PID" 2>/dev/null || true
echo "// an uncommitted change" > "$WORK/src/simlab-api/internal/uncommitted.go"
(cd "$WORK/src/simlab-api" && make build >/dev/null && cp bin/simlab-api "$WORK/simlab-api")
harness::start_autoscaler
harness::start_simlab
dirty=$(record "From a modified build" 100000)
harness::expect "the run from the modified build completed" "$(harness::run_to_completion "$dirty")" "completed"

if SOURCE_URL="$API" SOURCE_TOKEN="" "$EXPERIMENTS_DIR/lib/reproduce.sh" "$dirty" > "$WORK/refuse.log" 2>&1; then
  harness::bad "a run from a modified build was reproduced as if its commit were the code"
elif grep -q "changes its commit does not contain" "$WORK/refuse.log"; then
  harness::ok "refused, naming the modified build"
else
  harness::bad "refused, but not for the right reason"
  tail -5 "$WORK/refuse.log" | while read -r line; do harness::note "$line"; done
fi

harness::finish
