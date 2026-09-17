#!/usr/bin/env bash
#
# Reproduces a recorded run from its provenance, and checks the replay matches.
#
#   lib/reproduce.sh RUN_ID            a run on the deployed platform
#   make reproduce RUN=RUN_ID          the same
#   SOURCE_URL=http://127.0.0.1:8081 SOURCE_TOKEN= lib/reproduce.sh RUN_ID
#
# Nothing about the run is taken from anywhere but the run itself:
#
#   1. read its provenance, and refuse if it names a build that cannot be
#      rebuilt — no commit, or changes the commit does not contain
#   2. check out both services at the recorded commits, in clean worktrees,
#      and build them
#   3. start them against a fresh database
#   4. recreate the recorded mine and scenario, and replay the run under the
#      recorded effective settings
#   5. compare every metric, cycle, seismic event and track with the original
#
# It exits zero only if the replay is identical. A difference is reported at
# the first field where the two runs part ways.
#
# Runs on its own ports, so it can run beside an experiment or a dev stack.
set -euo pipefail

RUN_ID="${1:?usage: reproduce.sh RUN_ID}"

export AUTOSCALER_PORT="${REPRODUCE_AUTOSCALER_PORT:-18590}"
export SIMLAB_PORT="${REPRODUCE_SIMLAB_PORT:-18591}"
export PG_PORT="${REPRODUCE_PG_PORT:-15459}"
export PG_CONTAINER="${REPRODUCE_PG_CONTAINER:-platform-reproduce-pg}"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=harness.sh
source "$here/harness.sh"
results="$here/results.py"

# The worktrees live under $WORK, which the harness removes; pruning afterwards
# is what tells each repository they are gone.
reproduce::cleanup() {
  harness::cleanup
  for repo in "$PLATFORM_DIR/autoscaler" "$PLATFORM_DIR/simlab-api"; do
    git -C "$repo" worktree prune 2>/dev/null || true
  done
}
trap reproduce::cleanup EXIT

if [[ -z "${SOURCE_URL:-}" ]]; then
  eval "$("$PLATFORM_DIR/platform-deploy/scripts/simlab-env.sh")"
  SOURCE_URL="$SIMLAB_URL"
  SOURCE_TOKEN="$SIMLAB_TOKEN"
fi
SOURCE_TOKEN="${SOURCE_TOKEN:-}"

harness::log "Reading run $RUN_ID from $SOURCE_URL"
python3 "$results" fetch "$SOURCE_URL" "$SOURCE_TOKEN" "$RUN_ID" "$WORK/original.json"
python3 -c 'import json,sys; json.dump(json.load(open(sys.argv[1]))["detail"], open(sys.argv[2], "w"))' \
  "$WORK/original.json" "$WORK/detail.json"
eval "$(python3 "$results" plan "$WORK/detail.json")"

if [[ -n "$REASONS" ]]; then
  harness::bad "run $RUN_ID cannot be reproduced from its provenance"
  harness::note "because $REASONS"
  harness::finish
fi
harness::ok "recorded by simlab-api ${SIMLAB_VERSION:-unversioned} ($SIMLAB_COMMIT)"
harness::ok "and autoscaler ${AUTOSCALER_VERSION:-unversioned} ($AUTOSCALER_COMMIT)"

here_platform="$(go env GOOS)/$(go env GOARCH)"
if [[ -n "$RECORDED_PLATFORM" && "$RECORDED_PLATFORM" != "$here_platform" ]]; then
  harness::note "recorded on $RECORDED_PLATFORM and replayed on $here_platform: floating point may round"
  harness::note "differently, so a difference found here may be the architecture rather than the code"
fi

harness::log "Rebuilding both services at the recorded commits"
# The Go toolchain is part of the environment a result came from: the same
# source compiled by another Go can round differently. GOTOOLCHAIN has the go
# command fetch and use exactly the recorded one.
checkout() { # repo commit go-version
  local repo="$PLATFORM_DIR/$1" commit=$2 toolchain=${3:-local} tree="$WORK/src/$1"
  if ! git -C "$repo" cat-file -e "${commit}^{commit}" 2>/dev/null; then
    git -C "$repo" fetch -q origin
  fi
  git -C "$repo" worktree add -q --detach "$tree" "$commit" >&2
  (cd "$tree" && GOTOOLCHAIN="$toolchain" make build >&2)
  echo "$tree"
}
AUTOSCALER_DIR="$(checkout autoscaler "$AUTOSCALER_COMMIT" "$AUTOSCALER_GO")"
SIMLAB_DIR="$(checkout simlab-api "$SIMLAB_COMMIT" "$SIMLAB_GO")"
cp "$AUTOSCALER_DIR/bin/autoscaler" "$WORK/autoscaler"
cp "$SIMLAB_DIR/bin/simlab-api" "$WORK/simlab-api"
harness::ok "built from clean checkouts of both commits, with ${AUTOSCALER_GO:-the local Go} and ${SIMLAB_GO:-the local Go}"

harness::log "Starting them against a fresh database"
harness::postgres
harness::start_autoscaler
harness::start_simlab
harness::ok "autoscaler on :$AUTOSCALER_PORT, simlab-api on :$SIMLAB_PORT"

harness::log "Replaying from the recorded mine, scenario and settings"
python3 - "$WORK/original.json" "$WORK" <<'PY'
import json, sys
original = json.load(open(sys.argv[1]))
detail, record = original["detail"], original.get("intent")
p, run = detail["provenance"], detail["run"]
json.dump(p["mine"], open(f"{sys.argv[2]}/mine.json", "w"))
json.dump(p["scenario"], open(f"{sys.argv[2]}/scenario.json", "w"))
body = {
    "name": f"Reproduction of {run['id']}",
    "mode": "simulation",
    "scenario_id": p["scenario"]["id"],
    "decision_interval_seconds": run["decision_interval_seconds"],
    # Pacing only: how fast simulated time passes in real time changes nothing
    # a run records.
    "time_compression": 1000000,
    "settings": p["settings"],
    # A run from before intent reordered nothing, and a run created now
    # without saying so would decay.
    "intent": (p.get("intent") or {}).get("settings") or {"mode": "off"},
}
# Every change after the settings the run was created with — version 1 — is
# replayed at the cycle it took effect from and with the version it had. Not
# simply every change after the first recorded: an edit made before the first
# cycle is the first recorded, and version 1 never took effect at all.
changes = [c for c in (record or {}).get("changes", []) if c["version"] > 1]
if changes:
    body["intent_schedule"] = [
        {"cycle": c["cycle"], "settings": c["settings"], "version": c["version"], "source": c["source"]}
        for c in changes
    ]
json.dump(body, open(f"{sys.argv[2]}/run.json", "w"))
PY
curl -sf "$API/api/mines" -H 'Content-Type: application/json' --data-binary @"$WORK/mine.json" >/dev/null
curl -sf "$API/api/scenarios" -H 'Content-Type: application/json' --data-binary @"$WORK/scenario.json" >/dev/null
replay=$(curl -sf "$API/api/runs" -H 'Content-Type: application/json' --data-binary @"$WORK/run.json" \
  | harness::json 'd["id"]')
status=$(harness::run_to_completion "$replay" 3600)
harness::expect "the replay completed" "$status" "completed"

python3 "$results" fetch "$API" "" "$replay" "$WORK/replay.json"
rebuilt=$(python3 -c '
import json,sys
p = json.load(open(sys.argv[1]))["detail"]["provenance"]
s, a = p["simlab_api"], p["autoscaler"]
print(s["commit"], a["commit"], s["modified"] or a["modified"], s["go_version"], a["go_version"])' \
  "$WORK/replay.json")
harness::expect "the replay was produced by the recorded commits and toolchains, unmodified" \
  "$rebuilt" "$SIMLAB_COMMIT $AUTOSCALER_COMMIT False $SIMLAB_GO $AUTOSCALER_GO"

harness::log "Comparing the replay with the original"
if comparison=$(python3 "$results" compare "$WORK/original.json" "$WORK/replay.json"); then
  while read -r line; do harness::note "$line"; done <<< "$comparison"
  harness::ok "run $RUN_ID reproduced exactly"
else
  while read -r line; do harness::note "$line"; done <<< "$comparison"
  harness::bad "run $RUN_ID did not reproduce"
fi

harness::finish
