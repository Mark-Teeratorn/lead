#!/bin/bash
# Revision-round-1 GPU suite, part 4 (docs/ANALYSIS_ADDENDUM.md section 11, motion-history swap test).
#
# Waits for part 3 (run_revision_suite3.sh) to finish, then runs with the history-swap agent
# (alpamayo_bridge_agent_histswap.py) on the eight replicate routes, one pass each:
#   1. Matrix-Flooded-6400  -> model_matrix_flooded_6400_histswap   (route 2534 first, as the agent check)
#   2. Matrix-Golden-6400   -> model_matrix_golden_6400_histswap
#
# Same rules as parts 1 to 3: no relaunch of a scored route, partial outputs moved aside, model identity
# checked before every route, live audit log, per-route provenance. No extraction or other heavy job here.
set -u
cd /home/aimslab/lead

SUITE_LOG="outputs/revision_suite4_progress.log"
AUDIT_LOG="outputs/revision_suite4_audit.log"
SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
# Anchored so that only the real server process matches, never a shell whose command line mentions it.
SERVER_PAT="^/home/aimslab/flashdrive/.venv/bin/python -u /home/aimslab/flashdrive/scripts/flashdrive_server.py"
PART3_PID="${PART3_PID:-1824157}"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"
ROUTE_TIMEOUT_S=9000        # 2.5 h hard limit per route (a 4,000-tick route takes about 65 min)
MAX_ATTEMPTS=3              # launches per route; only routes with no score are relaunched

FLOODED_DIR="/home/aimslab/checkpoints/action_experts/extracted_matrix_flooded_6400"
GOLDEN_DIR="/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
FGBAL_DIR="${FGBAL_DIR:-/mnt/disk2/checkpoints/action_experts/extracted_matrix_fgbalanced_6400}"
FGBAL_EXPORT_DIR="${FGBAL_EXPORT_DIR:-/mnt/disk2/fgbalanced_unpacked/Alpamayo-1.5-10B-Matrix-FloodedGroups-Balanced-6400-A15}"
LEAD_PYTHON="/home/aimslab/lead/.venv/bin/python"
AGENT_DEFAULT="src/lead/evaluation/agents/alpamayo/alpamayo_bridge_agent.py"
AGENT_HISTSWAP="src/lead/evaluation/agents/alpamayo/alpamayo_bridge_agent_histswap.py"

CANONICAL_44="2534 1852 2204 2513 1825 3561 3086 17752 2201 3540 1790 3436 2286 23687 23901 23695 2790 2283 23771 2084 28087 2115 2082 2127 1773 2664 3248 1711 1956 14194 17563 3936 28099 2050 2709 26458 2390 2416 14842 3144 3464 2144 2164 3364"
REPLICATE_8="2534 3561 1790 23695 28087 2664 17563 26458"   # every 5th canonical route from index 0

# Optional: limit to the first N jobs / a smoke run. SUITE_ONLY="tag1,tag2" restricts the phases.
SUITE_ONLY="${SUITE_ONLY:-}"
ROUTES_OVERRIDE="${ROUTES_OVERRIDE:-}"

audit() { echo "$(date '+%Y-%m-%d %H:%M:%S') | $*" | tee -a "$AUDIT_LOG" >> "$SUITE_LOG"; }
say()   { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$SUITE_LOG"; }

sha_of() { sha256sum "$1" | cut -d' ' -f1; }

server_serves() {   # $1 = model dir
    [ -S "$SOCK_PATH" ] || return 1
    if [ "$1" = "BASE" ]; then
        # Base = server started without --model-path (default z-lab/Alpamayo-1.5-10B, no fine-tuned expert)
        pgrep -f "$SERVER_PAT" > /dev/null || return 1
        pgrep -af "$SERVER_PAT" | grep -q -- "--model-path" && return 1
    else
        pgrep -af "$SERVER_PAT" | grep -q -- "--model-path $1 " || return 1
    fi
    python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

ensure_server() {   # $1 = model dir
    local model_dir="$1"
    if server_serves "$model_dir"; then return 0; fi
    audit "- | server | (re)starting model server for $model_dir"
    pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "$SERVER_PAT" 2>/dev/null || true
    rm -f "$SOCK_PATH"
    sleep 5
    local model_arg=""
    [ "$model_dir" != "BASE" ] && model_arg="--model-path $model_dir"
    # The environment prefix must sit directly on the server command (it was on the `local` line before 13 Nov 23:30,
    # which left the server without these variables; fixed before this suite started any job).
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTORCH_ALLOC_CONF=expandable_segments:True \
    setsid nohup $FLASHDRIVE_PYTHON -u /home/aimslab/flashdrive/scripts/flashdrive_server.py \
        $model_arg --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_revision4.log 2>&1 &
    for i in $(seq 1 900); do
        if server_serves "$model_dir"; then
            audit "- | server | ready, pid $(pgrep -f "$SERVER_PAT" | head -1), model $model_dir"
            return 0
        fi
        sleep 1
    done
    audit "- | server | FAILED to start for $model_dir"
    return 1
}

route_scored() {    # $1 = tag, $2 = route id
    local f="outputs/local_evaluation/${1}_${2}/checkpoint_endpoint.json"
    [ -f "$f" ] && grep -q '"scores_mean"' "$f" 2>/dev/null
}

run_job() {         # $1 tag, $2 model dir, $3 agent file, $4 routes, $5 checkpoint sha
    local tag="$1" model_dir="$2" agent="$3" routes="$4" ckpt_sha="$5"
    if [ -n "$SUITE_ONLY" ] && ! echo ",$SUITE_ONLY," | grep -q ",$tag,"; then return 0; fi
    [ -n "$ROUTES_OVERRIDE" ] && routes="$ROUTES_OVERRIDE"
    local agent_sha; agent_sha=$(sha_of "$agent")
    audit "- | job start | tag=$tag model=$model_dir ckpt_sha=$ckpt_sha agent=$agent agent_sha=$agent_sha"
    local n=0 total; total=$(echo $routes | wc -w)
    for rid in $routes; do
        n=$((n+1))
        local out_dir="outputs/local_evaluation/${tag}_${rid}"
        if route_scored "$tag" "$rid"; then
            say "[$tag $n/$total] route $rid already scored, skipping"
            continue
        fi
        local attempt=0
        while [ $attempt -lt $MAX_ATTEMPTS ]; do
            attempt=$((attempt+1))
            if ! ensure_server "$model_dir"; then
                audit "$rid | abort | tag=$tag attempt=$attempt model server unavailable"
                sleep 30; continue
            fi
            # move any unscored partial output aside (never delete)
            if [ -d "$out_dir" ] && [ -n "$(ls -A "$out_dir" 2>/dev/null | grep -v '^aborted_')" ]; then
                local aside="$out_dir/aborted_$(date +%Y%m%d_%H%M%S)"
                mkdir -p "$aside"
                find "$out_dir" -maxdepth 1 -type f -exec mv {} "$aside/" \;
                audit "$rid | partial moved | tag=$tag -> $aside"
            fi
            pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
            pkill -9 -f "CarlaUE4" 2>/dev/null || true
            sleep 3
            local srv_pid; srv_pid=$(pgrep -f "$SERVER_PAT" | head -1)
            audit "$rid | launch | tag=$tag attempt=$attempt server_pid=$srv_pid"
            local t0; t0=$(date '+%Y-%m-%dT%H:%M:%S')
            local model_path_env="$model_dir"
            [ "$model_dir" = "BASE" ] && model_path_env=""
            MODEL_TAG="$tag" MODEL_PATH="$model_path_env" AGENT_FILE="$agent" \
                timeout --signal=TERM --kill-after=60 $ROUTE_TIMEOUT_S \
                bash scripts/common/eval_alpamayo_b2d.sh "src/lead/routes/benchmark_routes/bench2drive/${rid}.xml" >> "$SUITE_LOG" 2>&1
            local rc=$?
            local t1; t1=$(date '+%Y-%m-%dT%H:%M:%S')
            if route_scored "$tag" "$rid"; then
                python3 - "$out_dir" "$tag" "$rid" "$model_dir" "$ckpt_sha" "$agent" "$agent_sha" "$attempt" "$t0" "$t1" "$srv_pid" <<'PY'
import json, sys, hashlib, subprocess
out_dir, tag, rid, model_dir, ckpt_sha, agent, agent_sha, attempt, t0, t1, srv_pid = sys.argv[1:12]
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()
harness = {k: sha(p) for k, p in {
    'scenario_manager': '3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/scenarios/scenario_manager.py',
    'leaderboard_evaluator': '3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/leaderboard_evaluator.py',
    'route_scenario': '3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/scenarios/route_scenario.py',
    'launcher': 'scripts/common/eval_alpamayo_b2d.sh'}.items()}
rec = json.load(open(out_dir + '/checkpoint_endpoint.json'))['_checkpoint']['records'][0]
prov = dict(tag=tag, route_id=rid, model_dir=model_dir, checkpoint_sha256=ckpt_sha, agent_file=agent,
            agent_sha256=agent_sha, harness_sha256=harness, attempt=int(attempt), started=t0, finished=t1,
            server_pid=srv_pid, git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
            status=rec['status'], duration_game=rec['meta']['duration_game'])
json.dump(prov, open(out_dir + '/run_provenance.json', 'w'), indent=1)
PY
                local status; status=$(python3 -c "import json;print(json.load(open('$out_dir/checkpoint_endpoint.json'))['_checkpoint']['records'][0]['status'])" 2>/dev/null)
                audit "$rid | result | tag=$tag attempt=$attempt exit=$rc status=$status"
                break
            else
                audit "$rid | no score | tag=$tag attempt=$attempt exit=$rc (will relaunch if attempts remain)"
                sleep 20
            fi
        done
        if ! route_scored "$tag" "$rid"; then
            audit "$rid | GAVE UP | tag=$tag after $MAX_ATTEMPTS attempts with no score"
        fi
    done
    audit "- | job end | tag=$tag"
}

# wait for part 3
while kill -0 "$PART3_PID" 2>/dev/null; do sleep 60; done

audit "- | suite4 start | git_head=$(git rev-parse HEAD) pid=$$"
FLOODED_SHA=$(sha_of "$FLOODED_DIR/action_expert.safetensors")
GOLDEN_SHA=$(sha_of "$GOLDEN_DIR/action_expert.safetensors")

# Agent check: the first route runs alone. It is that route's run and is not repeated.
run_job model_matrix_flooded_6400_histswap "$FLOODED_DIR" "$AGENT_HISTSWAP" "2534" "$FLOODED_SHA"
if [ -z "$SUITE_ONLY" ] && [ -z "$ROUTES_OVERRIDE" ]; then
    check=$(python3 - <<'PY'
import json
p = 'outputs/local_evaluation/model_matrix_flooded_6400_histswap_2534/predicted_trajectories.jsonl'
try:
    rows = [json.loads(l) for l in open(p) if l.strip()]
    kinds = [r.get('hist_kind') for r in rows]
    ok = len(rows) > 100 and all(k in ('true', 'moving', 'stationary') for k in kinds) \
        and all(r.get('controller_variant') == 'histswap' for r in rows) and sum(k != 'true' for k in kinds) >= 10
    print('ok' if ok else 'bad', len(rows), {k: kinds.count(k) for k in set(kinds)})
except Exception as e:
    print('bad', repr(e))
PY
)
    audit "2534 | agent check | $check"
    case "$check" in ok*) ;; *) audit "- | suite4 abort | history-swap log check failed"; pkill -9 -f "CarlaUE4" 2>/dev/null || true; exit 1 ;; esac
fi
run_job model_matrix_flooded_6400_histswap "$FLOODED_DIR" "$AGENT_HISTSWAP" "$REPLICATE_8" "$FLOODED_SHA"
run_job model_matrix_golden_6400_histswap  "$GOLDEN_DIR"  "$AGENT_HISTSWAP" "$REPLICATE_8" "$GOLDEN_SHA"

pkill -9 -f "CarlaUE4" 2>/dev/null || true
audit "- | suite4 end | all jobs processed"
