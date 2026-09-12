#!/usr/bin/env bash
#
# Does the settings compare-and-swap hold when several editors race, while the
# target is being cycled?
#
# See README.md for what this is asking and why.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/harness.sh"

harness::start

harness::log "Registering a target to tune"

harness::as -X POST "$AUTOSCALER_API/v1/targets" -d '{
  "target": {"id": "contended", "name": "Contended", "kind": "simulation",
             "mode": "driven", "config": {"local_coldstart_seconds": "0"}},
  "settings": {"local_executor_cap": 10, "cloud_executor_cap": 10}
}' >/dev/null
harness::ok "target registered at version 1"

# ------------------------------------------------- racing writers, one version
#
# Every writer reads the same version and writes against it. Exactly one can
# win: the rest edited a version that is no longer current, which is the whole
# point of sending expected_version.

harness::log "Twenty editors racing on one version"

VERSION=$(harness::as "$AUTOSCALER_API/v1/targets/contended/settings" | harness::json 'd["version"]')

# Note: wait on these PIDs specifically, never a bare `wait` — the harness
# runs the two services as background jobs of this same shell, and a bare wait
# would sit on them until the experiment was killed.
RACERS=()
for i in $(seq 1 20); do
  (
    code=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH \
      -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
      "$AUTOSCALER_API/v1/targets/contended/settings?expected_version=$VERSION" \
      -d "{\"local_executor_cap\": $((20 + i))}")
    echo "$code" > "$WORK/race-$i.code"
  ) &
  RACERS+=($!)
done
for pid in "${RACERS[@]}"; do wait "$pid"; done

CODES=$(cat "$WORK"/race-*.code)
ACCEPTED=$(printf '%s\n' "$CODES" | grep -c '^200$' || true)
CONFLICTED=$(printf '%s\n' "$CODES" | grep -c '^409$' || true)
OTHER=$(printf '%s\n' "$CODES" | grep -vc '^200$\|^409$' || true)

harness::expect "exactly one writer won" "$ACCEPTED" "1"
harness::expect "the other nineteen were refused as stale" "$CONFLICTED" "19"
harness::expect "nobody got an unexpected status" "$OTHER" "0"

AFTER=$(harness::as "$AUTOSCALER_API/v1/targets/contended/settings" | harness::json 'd["version"]')
harness::expect "the version advanced exactly once" "$AFTER" "$((VERSION + 1))"

# ------------------------------------------------------- no torn document
#
# A reader must never see half of one edit and half of another. Each writer
# below sets a pair of fields that must stay consistent with each other, and a
# reader checks the pair on every read.

harness::log "Writers changing a pair of fields while a reader watches"

# Establish the invariant before anyone observes it. Without this the reader
# starts against whatever the previous section left behind, and reports a
# perfectly consistent document as torn — which is a flaw in the experiment,
# not a finding about the service.
harness::as -X PATCH "$AUTOSCALER_API/v1/targets/contended/settings" \
  -d '{"local_executor_cap": 10, "min_local_executors": 1}' >/dev/null

(
  for i in $(seq 1 40); do
    n=$(( (i % 5 + 1) * 10 ))
    curl -s -o /dev/null -X PATCH \
      -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
      "$AUTOSCALER_API/v1/targets/contended/settings" \
      -d "{\"local_executor_cap\": $n, \"min_local_executors\": $((n / 10))}"
  done
) &
WRITER=$!

TORN=0
READS=0
while kill -0 "$WRITER" 2>/dev/null && [[ "$READS" -lt 5000 ]]; do
  pair=$(harness::as "$AUTOSCALER_API/v1/targets/contended/settings" | harness::json \
    '"%d %d" % (d["settings"]["local_executor_cap"], d["settings"]["min_local_executors"])' || echo "0 0")
  cap=${pair% *}; floor=${pair#* }
  READS=$((READS + 1))
  # The writers always set the floor to a tenth of the cap. Any other pairing
  # is a document assembled from two different versions.
  if [[ "$floor" -ne $((cap / 10)) ]]; then
    TORN=$((TORN + 1))
    harness::note "torn read: cap=$cap floor=$floor"
  fi
done
wait "$WRITER"

harness::expect "no reader ever saw a half-applied edit (over $READS reads)" "$TORN" "0"

# ------------------------------------------------- a rejected write changes nothing

harness::log "A rejected write must leave the running settings alone"

BEFORE=$(harness::as "$AUTOSCALER_API/v1/targets/contended/settings" | harness::json 'd["version"]')
BAD=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$AUTOSCALER_API/v1/targets/contended/settings" \
  -d '{"local_executor_cap": 5, "min_local_executors": 99}')
harness::expect "a floor above the ceiling is refused" "$BAD" "400"

STILL=$(harness::as "$AUTOSCALER_API/v1/targets/contended/settings" | harness::json 'd["version"]')
harness::expect "the version did not move" "$STILL" "$BEFORE"

harness::finish
