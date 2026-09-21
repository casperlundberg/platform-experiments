#!/usr/bin/env bash
#
# Is cloud bought only when the queue needs it, and given back when it does not?
#
# See README.md for what this is asking and why.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/harness.sh"

harness::start

harness::log "A quiet half hour, a rock burst, and a quiet hour after it"

curl -sf "$API/api/mines" -H 'Content-Type: application/json' -d '{
  "id":"storhall","name":"Storhall","sensors":30,"background_rate_per_hour":90}' >/dev/null
# No long-deadline level and a short tail: the queue empties after the burst
# and stays empty, which is the stretch in which cloud must be given back.
# Work with a twelve-hour deadline would sit in the queue for hours, and so
# would the question of whether anything still wanted cloud.
curl -sf "$API/api/scenarios" -H 'Content-Type: application/json' -d '{
  "id":"late-burst","mine_id":"storhall","name":"Quiet start, a burst, quiet after",
  "duration_seconds":7200,"job_seconds":20,"seed":20260921,
  "priority_mix":{"100":1,"50":1},
  "bursts":[{"at_seconds":1800,"magnitude":45,"aftershock_decay_seconds":600}]}' >/dev/null
harness::ok "mine and scenario registered"

# Background work needs about ten executors; twice that on-premise means the
# local tier alone plainly serves it once the burst is over, so any cloud still
# held then is held by the window or a lifetime, never by the queue.
RUN=$(curl -sf "$API/api/runs" -H 'Content-Type: application/json' -d '{
  "name":"Cloud bought and given back","mode":"simulation","scenario_id":"late-burst",
  "decision_interval_seconds":15,"time_compression":100000,
  "settings":{"local_executor_cap":24,"cloud_executor_cap":60,
              "local_coldstart_seconds":60,"cloud_coldstart_seconds":180}}' | harness::json 'd["id"]')
status=$(harness::run_to_completion "$RUN")
harness::expect "the run completed" "$status" "completed"

harness::log "Reading the cloud bill from every cycle"

# One python pass over the recorded cycles and the settings the run used,
# printing one "name|value" line per measure for the checks below.
MEASURES=$(python3 - "$API" "$RUN" <<'PY'
import json, sys, urllib.request

api, run = sys.argv[1], sys.argv[2]
cycles, cursor = [], 0
while True:
    page = json.load(urllib.request.urlopen(f"{api}/api/runs/{run}/cycles?from={cursor}&limit=20000"))
    if not page["cycles"]:
        break
    cycles += page["cycles"]
    if page["next"] <= cursor:
        break
    cursor = page["next"]
settings = json.load(urllib.request.urlopen(f"{api}/api/runs/{run}"))["provenance"]["settings"]

interval, burst, cap, local_cap, job_seconds = 15, 1800, 60, 24, 20
before = [c for c in cycles if c["sequence"] * interval < burst]
during = [c for c in cycles if burst <= c["sequence"] * interval < burst + 1800]

# After the burst: from thirty minutes after it began, three times its
# aftershock decay, when arrivals are back to background that the local tier
# serves alone. Cloud used from then is cloud nothing needed, and the most the
# rules allow is the whole cap held for the longer of the scale-down window and
# the minimum lifetime. (A per-cycle bound would need the engine's requirement
# on every cycle, which a recorded run does not carry; release_test.go in the
# autoscaler holds the rule itself, cycle by cycle.)
after = [c for c in cycles if c["sequence"] * interval >= burst + 1800]

window = settings.get("cloud_scale_down_window_seconds", 0)
lifetime = settings.get("cloud_min_lifetime_seconds", 0)
budget = cap * max(window, lifetime) / 3600
print(f"quiet_cloud_hours|{sum(c['cloud_ready'] for c in before) * interval / 3600:.1f}")
print(f"quiet_peak_plan|{max(c['plan_cloud'] for c in before)}")
print(f"burst_peak_plan|{max(c['plan_cloud'] for c in during)}")
print(f"after_cloud_hours|{sum(c['cloud_ready'] for c in after) * interval / 3600:.1f}")
print(f"after_budget|{budget:.1f}")
print(f"after_minutes|{len(after) * interval // 60}")
print(f"cloud_cap|{cap}")
PY
)
measure() { grep "^$1|" <<<"$MEASURES" | cut -d'|' -f2; }

quiet_hours=$(measure quiet_cloud_hours)
quiet_peak=$(measure quiet_peak_plan)
burst_peak=$(measure burst_peak_plan)
after_hours=$(measure after_cloud_hours)
budget=$(measure after_budget)
after_minutes=$(measure after_minutes)
cap=$(measure cloud_cap)

if python3 -c "import sys; sys.exit(0 if float('$quiet_hours') < 1 else 1)" && [[ "$quiet_peak" -lt "$cap" ]]; then
  harness::ok "a quiet start bought $quiet_hours cloud executor-hours, planning at most $quiet_peak cloud executors"
else
  harness::bad "a quiet start bought $quiet_hours cloud executor-hours and planned $quiet_peak of $cap cloud executors"
fi

if [[ "$burst_peak" -eq "$cap" ]]; then
  harness::ok "the burst still reached the cloud cap of $cap"
else
  harness::bad "the burst planned at most $burst_peak of $cap cloud executors: the checks above passed by not bursting"
fi

if [[ "$after_minutes" -lt 30 ]]; then
  harness::bad "the run ended $after_minutes minutes after the burst was over, too soon to show a release"
elif python3 -c "import sys; sys.exit(0 if float('$after_hours') <= float('$budget') else 1)"; then
  harness::ok "in the $after_minutes minutes after the burst, $after_hours cloud executor-hours (the rules allow at most $budget)"
else
  harness::bad "in the $after_minutes minutes after the burst, $after_hours cloud executor-hours, over the $budget the window and lifetime allow"
fi

harness::finish
