#!/bin/bash
# Evaluates a checkpoint on the given Bench2Drive routes (ids under
# src/lead/routes/benchmark_routes/bench2drive/), booting a fresh CARLA server
# per route and checking each route's result files. Run from the repo root
# with the lead environment and scripts/cli on PATH.
#
# Usage: evaluate_checkpoint.sh <checkpoint_dir> <route_id...>
set -eu

checkpoint_dir=$1
shift

# Up to three jobs share one box, each with CARLA and video encoders beside the
# model; a thread per core in every torch process would only thrash.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export NUMBA_NUM_THREADS=1 NUMBA_THREADING_LAYER=workqueue

# Exercise every visualization code path; the outputs are discarded. Every
# fifth frame is enough for that and keeps the encoders light.
export LEAD_CONFIG="\
evaluation.produce_frame_frequency=5 \
evaluation.produce_demo_image=true \
evaluation.produce_demo_video=true \
evaluation.produce_debug_image=true \
evaluation.produce_debug_video=true \
evaluation.produce_input_image=true \
evaluation.produce_input_video=true \
evaluation.produce_grid_image=true \
evaluation.produce_grid_video=true"
checkpoint_name="$(basename "$(dirname "$checkpoint_dir")")/$(basename "$checkpoint_dir")"
output_root="${RUNNER_TEMP:-/tmp}/checkpoint_evaluation/$checkpoint_name"

# Port-block locks live under /tmp so every runner account sees them and
# parallel jobs never collide.
mkdir -p /tmp/lead_ports && chmod 1777 /tmp/lead_ports 2>/dev/null || true

CARLA_PID=""
SAMPLER_PID=""
# The kernel counts OOM kills per cgroup, and this counter is readable without
# root (dmesg is not). It covers every process of this job, CARLA included.
oom_events="/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)/memory.events"
trap '[ -n "$CARLA_PID" ] && kill -9 -- "-$CARLA_PID" 2>/dev/null; [ -n "$SAMPLER_PID" ] && kill "$SAMPLER_PID" 2>/dev/null' EXIT

# CARLA is flaky: it can crash or stop answering mid-route for reasons unrelated
# to the checkpoint. A route only counts as failed once every attempt fails,
# each on a freshly booted server.
max_attempts=3
failed=()
for route_id in "$@"; do
  passed=false
  for attempt in $(seq 1 "$max_attempts"); do
    evaluated=false
    echo "::group::$checkpoint_name route $route_id (attempt $attempt/$max_attempts)"
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
    # setsid makes $CARLA_PID a process-group id; clean_carla's group kill
    # must reach the engine process CarlaUE4.sh spawns.
    setsid start_carla "$CARLA_PORT" > carla_server.log 2>&1 &
    CARLA_PID=$!
    # Ready means the server answers RPC calls and has a world, not just a
    # listening port. Each probe waits up to five seconds for an answer.
    for _ in $(seq 1 30); do
      test_carla_connection "$CARLA_PORT" && break
      sleep 1
    done
    if test_carla_connection "$CARLA_PORT"; then
      route_output="$output_root/$route_id"
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
      # The deadline bounds a hung evaluator (e.g. CARLA stops answering and the
      # leaderboard process never exits); timeout signals the whole process group.
      # The evaluator wipes a stale output dir itself, so a retry starts clean.
      timeout -k 30 30m python -u -m lead --checkpoint "$checkpoint_dir" \
          --routes="src/lead/routes/benchmark_routes/bench2drive/$route_id.xml" \
          --bench2drive \
          --port="$CARLA_PORT" \
          --traffic-manager-port="$TM_PORT" \
          --output-dir="$route_output" \
          --debug=2 && evaluated=true
      kill "$SAMPLER_PID" 2>/dev/null || true
      SAMPLER_PID=""
      oom_kills_after=$(awk '/^oom_kill /{n=$2} END{print n+0}' "$oom_events" 2>/dev/null || echo 0)
      echo "OOM kills during attempt: $((oom_kills_after - oom_kills_before))"
      awk 'BEGIN {gpu = 0; ram = 0} {if ($1 > gpu) gpu = $1; if ($2 > ram) ram = $2} END {printf "Peak memory: GPU %d MiB, RAM %d MiB (%d samples)\n", gpu, ram, NR}' memory_samples.txt
      if $evaluated; then
        # The threshold below 100 absorbs simulation nondeterminism.
        python - "$route_output" <<'EOF' && passed=true
import json
import sys

route_output = sys.argv[1]
record = json.load(open(f"{route_output}/checkpoint_endpoint.json"))
record = record["_checkpoint"]["global_record"]
status = record["status"]
score = record["scores_mean"]["score_composed"]
print(f"status {status} | driving score {score}")
assert status == "Completed", f"route did not complete: {status}"
assert score >= 80.0, f"driving score {score} below 80"
EOF
      fi
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
    fi
    echo "::endgroup::"

    clean_carla "$CARLA_PID"
    wait "$CARLA_PID" 2>/dev/null || true
    CARLA_PID=""
    if $passed; then
      break
    fi
    echo "route $route_id failed attempt $attempt/$max_attempts"
  done
  if ! $passed; then
    failed+=("$route_id")
  fi
done

if [ "${#failed[@]}" -gt 0 ]; then
  echo "::error::Failing evaluation routes: ${failed[*]}"
  exit 1
fi
echo "All $# evaluation routes passed."
