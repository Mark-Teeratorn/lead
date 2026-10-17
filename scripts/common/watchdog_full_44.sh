#!/bin/bash
# ==============================================================================
# Bench2Drive 44 Canonical Scenarios Evaluation - Watchdog Supervisor
# ==============================================================================
# Monitors run_full_44_eval.sh continuously:
# 1. Detects premature crashes, killed processes, or early exits.
# 2. Detects simulation freezes (no log activity for > 15 minutes).
# 3. Automatically recovers the model server and relaunches the runner.
# 4. Exits cleanly when all 44 routes have verified completed checkpoints.
# ==============================================================================

cd /home/aimslab/lead

WATCHDOG_LOG="outputs/watchdog_supervisor.log"
PROGRESS_LOG="outputs/full_44_eval_progress.log"
SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"

touch "$WATCHDOG_LOG"
echo "================================================================================" | tee -a "$WATCHDOG_LOG"
echo "[Watchdog] Supervisor started at $(date). Target: All 44 routes" | tee -a "$WATCHDOG_LOG"
echo "================================================================================" | tee -a "$WATCHDOG_LOG"

count_completed() {
    python3 -c "
import glob, json
count = 0
for p in glob.glob('outputs/local_evaluation/model_v4_final_*/checkpoint_endpoint.json'):
    try:
        with open(p) as f: d = json.load(f)
        if 'scores_mean' in d.get('_checkpoint', {}).get('global_record', {}):
            count += 1
    except Exception:
        pass
print(count)
" 2>/dev/null || echo "0"
}

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

ensure_server() {
    if ! server_is_alive; then
        echo "[Watchdog] Model Server down. Restarting FlashDrive Server..." | tee -a "$WATCHDOG_LOG"
        rm -f "$SOCK_PATH"
        pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        sleep 2

        HF_HUB_OFFLINE=1 \
        TRANSFORMERS_OFFLINE=1 \
        PYTHONUNBUFFERED=1 \
        PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
        PYTORCH_ALLOC_CONF=expandable_segments:True \
        $FLASHDRIVE_PYTHON -u /home/aimslab/flashdrive/scripts/flashdrive_server.py \
            --model-path /home/aimslab/checkpoints/action_experts/model_v4 \
            --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_eval44.log 2>&1 &
        
        for i in $(seq 1 600); do
            if server_is_alive; then
                echo "[Watchdog] Model Server recovered successfully." | tee -a "$WATCHDOG_LOG"
                break
            fi
            sleep 1
        done
    fi
}

relaunch_eval() {
    local done_count="$1"
    echo "[Watchdog] Alert at $(date): Evaluation not running or hung. ($done_count/44 completed)" | tee -a "$WATCHDOG_LOG"
    echo "[Watchdog] Cleaning stuck processes and relaunching..." | tee -a "$WATCHDOG_LOG"

    pkill -9 -f "run_full_44_eval.sh" 2>/dev/null || true
    pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 3

    ensure_server

    nohup bash scripts/common/run_full_44_eval.sh >> outputs/full_44_eval.log 2>&1 &
    local new_pid=$!
    echo "[Watchdog] Relaunched run_full_44_eval.sh with PID $new_pid" | tee -a "$WATCHDOG_LOG"
}

while true; do
    sleep 30

    DONE_COUNT=$(count_completed)

    if [ "$DONE_COUNT" -ge 44 ]; then
        echo "================================================================================" | tee -a "$WATCHDOG_LOG"
        echo "[Watchdog] SUCCESS! All 44 routes have completed evaluation at $(date)." | tee -a "$WATCHDOG_LOG"
        echo "================================================================================" | tee -a "$WATCHDOG_LOG"
        break
    fi

    RUNNER_RUNNING=0
    if pgrep -f "run_full_44_eval.sh" > /dev/null; then
        RUNNER_RUNNING=1
    fi

    # Check for stagnation / hang (no progress log change for > 15 minutes = 900s)
    HUNG=0
    if [ -f "$PROGRESS_LOG" ]; then
        now=$(date +%s)
        last_mod=$(stat -c %Y "$PROGRESS_LOG" 2>/dev/null || echo "$now")
        diff_sec=$((now - last_mod))
        if [ "$diff_sec" -gt 900 ]; then
            HUNG=1
            echo "[Watchdog] Detected log stagnation for ${diff_sec}s (> 900s limit)." | tee -a "$WATCHDOG_LOG"
        fi
    fi

    # If runner is not active or hung, restart
    if [ "$RUNNER_RUNNING" -eq 0 ] || [ "$HUNG" -eq 1 ]; then
        relaunch_eval "$DONE_COUNT"
        # Give it grace period to initialize
        sleep 45
    fi
done
