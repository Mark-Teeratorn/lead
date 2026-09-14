#!/bin/bash
# Collects expert driving data for the given routes (paths relative to
# src/lead/routes/data_routes/), booting a fresh CARLA server per attempt. Only
# its own server is ever killed: other jobs on the host run their own. CARLA is
# flaky, so a route only counts as failed once every attempt fails.
# Run from the repo root with the lead environment and scripts/cli on PATH.
set -eu

# Port-block locks live under /tmp so every runner account sees them and
# parallel jobs never collide.
mkdir -p /tmp/lead_ports && chmod 1777 /tmp/lead_ports 2>/dev/null || true

CARLA_PID=""
SAMPLER_PID=""
# The kernel counts OOM kills per cgroup, and this counter is readable without
# root (dmesg is not). It covers every process of this job, CARLA included.
oom_events="/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)/memory.events"
trap '[ -n "$CARLA_PID" ] && kill -9 -- "-$CARLA_PID" 2>/dev/null; [ -n "$SAMPLER_PID" ] && kill "$SAMPLER_PID" 2>/dev/null' EXIT

max_attempts=3
failed=()
for route in "$@"; do
  scenario_type=$(basename "$(dirname "$route")")
  passed=false
  for attempt in $(seq 1 "$max_attempts"); do
    echo "::group::$route (attempt $attempt/$max_attempts)"
    # Reserve a fresh port block per attempt: a hung server that survived the
    # group kill would otherwise hold the old ports and sink every retry.
    # CARLA takes the block's first three ports (rpc, streaming, secondary
    # server) and the traffic manager sits at 50. The blocks stay below the
    # ephemeral range (32768 and up), so no outgoing connection can sit on one
    # of them, and a block counts as taken while a socket in any state still
    # uses one of its ports.
    exec 9<&-
    while :; do
      CARLA_PORT=$((20000 + 100 * (RANDOM % 128)))
      touch "/tmp/lead_ports/$CARLA_PORT.lock" 2>/dev/null || true
      exec 9<"/tmp/lead_ports/$CARLA_PORT.lock"
      flock -n 9 || continue
      ss -tan | grep -qE ":($CARLA_PORT|$((CARLA_PORT + 1))|$((CARLA_PORT + 2))|$((CARLA_PORT + 50))) " || break
    done
    TM_PORT=$((CARLA_PORT + 50))
    # setsid makes $CARLA_PID a process-group id, so the group kill in
    # clean_carla reaches the engine process CarlaUE4.sh spawns.
    setsid start_carla "$CARLA_PORT" > carla_server.log 2>&1 &
    CARLA_PID=$!
    # Ready means the server answers RPC calls and has a world, not just a
    # listening port. Each probe waits up to five seconds for an answer.
    for _ in $(seq 1 30); do
      test_carla_connection "$CARLA_PORT" && break
      sleep 1
    done
    if test_carla_connection "$CARLA_PORT"; then
      # A retry starts from a clean log: the writer only adds files, so the
      # frames of a crashed attempt would stay beside the new ones.
      if [ "$attempt" -gt 1 ]; then
        rm -rf "${PY123D_DATA_ROOT:?}"/logs/*/"$scenario_type"
      fi
      # Debug level 2 makes the leaderboard rewrite live_results.txt every
      # tick, so a hung route can be diagnosed from its last known state.
      rm -f live_results.txt
      # Sample host and GPU memory every second: the peaks tell whether a route
      # died of memory. Both counters cover the whole host, so other jobs on
      # it are included.
      : > memory_samples.txt
      (
        while :; do
          gpu_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -n 1)
          ram_used=$(free -m | awk '/^Mem:/ {print $3}')
          echo "$gpu_used $ram_used" >> memory_samples.txt
          sleep 1
        done
      ) &
      SAMPLER_PID=$!
      oom_kills_before=$(awk '/^oom_kill /{n=$2} END{print n+0}' "$oom_events" 2>/dev/null || echo 0)
      # The deadline bounds a hung expert; timeout signals the whole process group.
      timeout -k 30 40m python -u -m lead --expert \
          --routes="src/lead/routes/data_routes/$route" \
          --port="$CARLA_PORT" \
          --traffic-manager-port="$TM_PORT" \
          --debug=2 && passed=true
      kill "$SAMPLER_PID" 2>/dev/null || true
      SAMPLER_PID=""
      oom_kills_after=$(awk '/^oom_kill /{n=$2} END{print n+0}' "$oom_events" 2>/dev/null || echo 0)
      echo "OOM kills during attempt: $((oom_kills_after - oom_kills_before))"
      awk 'BEGIN {gpu = 0; ram = 0} {if ($1 > gpu) gpu = $1; if ($2 > ram) ram = $2} END {printf "Peak memory: GPU %d MiB, RAM %d MiB (%d samples)\n", gpu, ram, NR}' memory_samples.txt
    else
      echo "CARLA on port $CARLA_PORT never answered"
    fi
    if ! $passed; then
      # The server log is truncated per attempt and cleaned with the workspace,
      # so a crash or hang is only diagnosable if it is shown here.
      echo "--- carla_server.log (last 100 lines) ---"
      tail -n 100 carla_server.log
      echo "--- live_results.txt ---"
      cat live_results.txt 2>/dev/null || echo "(never written)"
      echo "--- sockets on the block's ports ---"
      ss -tanp | grep -E ":($CARLA_PORT|$((CARLA_PORT + 1))|$((CARLA_PORT + 2))|$TM_PORT) " || true
      echo "--- GPU memory ---"
      nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader || true
    fi
    echo "::endgroup::"

    clean_carla "$CARLA_PID"
    wait "$CARLA_PID" 2>/dev/null || true
    CARLA_PID=""
    if $passed; then
      break
    fi
    echo "$route failed attempt $attempt/$max_attempts"
  done
  if ! $passed; then
    failed+=("$route")
  fi
done

if [ "${#failed[@]}" -gt 0 ]; then
  echo "::error::Failing routes: ${failed[*]}"
  exit 1
fi
echo "All $# routes collected."
