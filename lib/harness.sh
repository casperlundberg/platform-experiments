#!/usr/bin/env bash
#
# Shared harness for the experiments in this repository.
#
# Every experiment needs the same thing: real binaries, a real Postgres, and
# the two services talking to each other. This builds and starts them, and
# tears everything down on exit however the experiment ends.
#
# Source it, do not execute it:
#
#   source "$(dirname "${BASH_SOURCE[0]}")/../../lib/harness.sh"
#   harness::start
#   ... the experiment ...
#
# The services are started with distinct default ports so an experiment can run
# while platform-deploy's verify.sh or a development stack is up.

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPERIMENTS_DIR="$(cd "$HARNESS_DIR/.." && pwd)"
PLATFORM_DIR="$(cd "$EXPERIMENTS_DIR/.." && pwd)"

AUTOSCALER_DIR="${AUTOSCALER_DIR:-$PLATFORM_DIR/autoscaler}"
SIMLAB_DIR="${SIMLAB_DIR:-$PLATFORM_DIR/simlab-api}"

AUTOSCALER_PORT="${AUTOSCALER_PORT:-18290}"
SIMLAB_PORT="${SIMLAB_PORT:-18291}"
PG_PORT="${PG_PORT:-15434}"
PG_CONTAINER="${PG_CONTAINER:-platform-experiments-pg}"

TOKEN="experiment-$RANDOM"
API="http://127.0.0.1:$SIMLAB_PORT"
AUTOSCALER_API="http://127.0.0.1:$AUTOSCALER_PORT"

WORK="$(mktemp -d)"
OWN_POSTGRES=0
FAILURES=0

# ------------------------------------------------------------------ output

harness::log()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
harness::ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
harness::bad()  { printf '  \033[31m✗\033[0m %s\n' "$*"; FAILURES=$((FAILURES + 1)); }
harness::note() { printf '      %s\n' "$*"; }

# harness::expect <description> <actual> <expected>
harness::expect() {
  local what=$1 actual=$2 expected=$3
  if [[ "$actual" == "$expected" ]]; then
    harness::ok "$what"
  else
    harness::bad "$what"
    harness::note "got      : $actual"
    harness::note "expected : $expected"
  fi
}

# harness::finish is the experiment's exit status: non-zero if anything failed.
harness::finish() {
  if [[ "$FAILURES" -gt 0 ]]; then
    printf '\n\033[31m%d check(s) failed.\033[0m\n' "$FAILURES"
    exit 1
  fi
  printf '\n\033[32mAll checks passed.\033[0m\n'
}

# ----------------------------------------------------------------- lifecycle

harness::cleanup() {
  [[ -n "${SIMLAB_PID:-}" ]] && kill "$SIMLAB_PID" 2>/dev/null || true
  [[ -n "${AUTOSCALER_PID:-}" ]] && kill "$AUTOSCALER_PID" 2>/dev/null || true
  [[ "$OWN_POSTGRES" == "1" ]] && docker rm -f "$PG_CONTAINER" >/dev/null 2>&1 || true
  rm -rf "$WORK"
}
trap harness::cleanup EXIT

harness::wait_for() {
  local url=$1 name=$2
  for _ in $(seq 1 160); do
    curl -sf "$url" >/dev/null 2>&1 && return 0
    sleep 0.25
  done
  echo "--- $name log ---"; cat "$WORK/$name.log" 2>/dev/null || true
  echo "$name never became healthy at $url" >&2
  exit 1
}

harness::postgres() {
  if [[ -n "${POSTGRES_URL:-}" ]]; then
    return
  fi
  docker rm -f "$PG_CONTAINER" >/dev/null 2>&1 || true
  docker run -d --name "$PG_CONTAINER" \
    -e POSTGRES_PASSWORD=simlab -e POSTGRES_USER=simlab -e POSTGRES_DB=experiments \
    -p "$PG_PORT:5432" postgres:16-alpine >/dev/null
  OWN_POSTGRES=1
  POSTGRES_URL="postgres://simlab:simlab@127.0.0.1:$PG_PORT/experiments?sslmode=disable"
  for _ in $(seq 1 160); do
    docker exec "$PG_CONTAINER" pg_isready -U simlab >/dev/null 2>&1 && break
    sleep 0.5
  done
}

harness::build() {
  for dir in "$AUTOSCALER_DIR" "$SIMLAB_DIR"; do
    [[ -d "$dir" ]] || {
      echo "$dir is not there. These experiments expect the service repositories" >&2
      echo "checked out beside this one; set AUTOSCALER_DIR and SIMLAB_DIR otherwise." >&2
      exit 1
    }
  done
  (cd "$AUTOSCALER_DIR" && go build -o "$WORK/autoscaler" ./cmd/autoscaler)
  (cd "$SIMLAB_DIR" && go build -o "$WORK/simlab-api" ./cmd/simlab-api)
}

# harness::start_autoscaler keeps its state in $WORK/targets.json, so an
# experiment can stop and restart it and see what survived.
harness::start_autoscaler() {
  AUTOSCALER_ADDRESS=":$AUTOSCALER_PORT" \
  AUTOSCALER_API_TOKEN="$TOKEN" \
  AUTOSCALER_STATE_FILE="$WORK/targets.json" \
  AUTOSCALER_TICK="${AUTOSCALER_TICK:-1s}" \
    "$WORK/autoscaler" >> "$WORK/autoscaler.log" 2>&1 &
  AUTOSCALER_PID=$!
  harness::wait_for "$AUTOSCALER_API/healthz" autoscaler
}

harness::stop_autoscaler() {
  [[ -n "${AUTOSCALER_PID:-}" ]] || return 0
  kill "$AUTOSCALER_PID" 2>/dev/null || true
  wait "$AUTOSCALER_PID" 2>/dev/null || true
  AUTOSCALER_PID=""
}

harness::start_simlab() {
  SIMLAB_ADDRESS=":$SIMLAB_PORT" \
  SIMLAB_DATABASE_URL="$POSTGRES_URL" \
  SIMLAB_AUTOSCALER_URL="$AUTOSCALER_API" \
  SIMLAB_AUTOSCALER_TOKEN="$TOKEN" \
    "$WORK/simlab-api" >> "$WORK/simlab-api.log" 2>&1 &
  SIMLAB_PID=$!
  harness::wait_for "$API/healthz" simlab-api
}

# harness::start brings the whole stack up.
harness::start() {
  harness::log "Starting the platform"
  harness::postgres
  harness::build
  harness::start_autoscaler
  harness::start_simlab
  harness::ok "autoscaler on :$AUTOSCALER_PORT, simlab-api on :$SIMLAB_PORT"
}

# harness::as authenticates a call to the autoscaler directly.
harness::as() {
  curl -sf -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' "$@"
}

# harness::json runs a python expression over a JSON document on stdin.
harness::json() {
  python3 -c "import sys,json; d=json.load(sys.stdin); print($1)"
}

# harness::run_to_completion polls a run until it leaves the running states.
harness::run_to_completion() {
  local id=$1 limit=${2:-600}
  for _ in $(seq 1 "$limit"); do
    local status
    status=$(curl -sf "$API/api/runs/$id" | harness::json 'd["run"]["status"]')
    case "$status" in
      completed|failed|cancelled) echo "$status"; return 0 ;;
    esac
    sleep 0.5
  done
  echo "timeout"
}

# A warning worth keeping here rather than rediscovering: the two services run
# as background jobs of the shell that sourced this file, so an experiment must
# never use a bare `wait`. It would sit on the services and hang until killed.
# Collect the PIDs you care about and wait on those.
