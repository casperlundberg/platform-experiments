#!/usr/bin/env bash
#
# Runs a sweep and writes its report.
#
#   lib/sweep.sh sweeps/intent-modes.json
#   make sweep S=intent-modes
#
# Both services are built from clean checkouts of each repository's HEAD, not
# from the working tree, so every number in a report is tied to a commit and a
# report can say truthfully which code produced it. Uncommitted changes are not
# in a sweep; commit them first. SWEEP_PARALLEL runs that many at once (4).
#
# Runs on its own ports, so it can run beside an experiment or a dev stack.
set -euo pipefail

SWEEP="${1:?usage: sweep.sh SWEEP.json}"
SWEEP="$(cd "$(dirname "$SWEEP")" && pwd)/$(basename "$SWEEP")"

export AUTOSCALER_PORT="${SWEEP_AUTOSCALER_PORT:-18690}"
export SIMLAB_PORT="${SWEEP_SIMLAB_PORT:-18691}"
export PG_PORT="${SWEEP_PG_PORT:-15469}"
export PG_CONTAINER="${SWEEP_PG_CONTAINER:-platform-sweep-pg}"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=harness.sh
source "$here/harness.sh"

sweep::cleanup() {
  harness::cleanup
  for repo in "$PLATFORM_DIR/autoscaler" "$PLATFORM_DIR/simlab-api"; do
    git -C "$repo" worktree prune 2>/dev/null || true
  done
}
trap sweep::cleanup EXIT

harness::log "Building both services from their committed HEAD"
checkout() { # repo
  local repo="$PLATFORM_DIR/$1" tree="$WORK/src/$1" commit
  commit=$(git -C "$repo" rev-parse HEAD)
  if [[ -n "$(git -C "$repo" status --porcelain --untracked-files=no)" ]]; then
    harness::note "$1 has uncommitted changes; they are not in this sweep" >&2
  fi
  git -C "$repo" worktree add -q --detach "$tree" "$commit" >&2
  (cd "$tree" && make build >&2)
  echo "$tree"
}
AUTOSCALER_DIR="$(checkout autoscaler)"
SIMLAB_DIR="$(checkout simlab-api)"
cp "$AUTOSCALER_DIR/bin/autoscaler" "$WORK/autoscaler"
cp "$SIMLAB_DIR/bin/simlab-api" "$WORK/simlab-api"
harness::ok "built"

harness::postgres
harness::start_autoscaler
harness::start_simlab
harness::ok "autoscaler on :$AUTOSCALER_PORT, simlab-api on :$SIMLAB_PORT"

harness::log "Running $(basename "$SWEEP" .json)"
python3 "$here/sweep.py" run "$API" "$SWEEP" "$EXPERIMENTS_DIR/reports" "${SWEEP_PARALLEL:-4}"
