#!/bin/bash
# ==============================================================================
# Bench2Drive 44 Canonical Scenarios Evaluation - Watchdog Supervisor (Matrix-Flooded-6400)
# ==============================================================================
# Monitors run_full_44_matrix_flooded_6400.sh continuously:
# 1. Detects premature crashes, killed processes, or early exits.
# 2. Detects simulation freezes (no log activity for > 15 minutes).
# 3. Automatically recovers the model server and relaunches the runner.
# 4. Exits cleanly when all 44 routes have verified completed checkpoints.
# ==============================================================================

cd /home/aimslab/lead

WATCHDOG_LOG="outputs/watchdog_supervisor_matrix_flooded_6400.log"
PROGRESS_LOG="outputs/full_44_matrix_flooded_6400_progress.log"
SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"
MODEL_DIR="/home/aimslab/checkpoints/action_experts/extracted_matrix_flooded_6400"

touch "$WATCHDOG_LOG"
echo "================================================================================" | tee -a "$WATCHDOG_LOG"
echo "[Watchdog] Supervisor started at $(date). Target: All 44 routes (Matrix-Flooded-6400)" | tee -a "$WATCHDOG_LOG"
echo "================================================================================" | tee -a "$WATCHDOG_LOG"

count_completed() {
    python3 -c "
import glob, json
count = 0
for p in glob.glob('outputs/local_evaluation/model_matrix_flooded_6400_*/checkpoint_endpoint.json'):
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
    [ -S "$SOCK_PATH" ] && \
    ps aux | grep -v grep | grep "flashdrive_server.py" | grep -q "extracted_matrix_flooded_6400" && \
    python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

ensure_server() {
    if ! server_is_alive; then
        echo "[Watchdog] Model Server down. Restarting FlashDrive Server with Matrix-Flooded-6400..." | tee -a "$WATCHDOG_LOG"
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
            --model-path "$MODEL_DIR" \
            --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_flooded6400.log 2>&1 &
        
        for i in $(seq 1 600); do
            if server_is_alive; then
                echo "[Watchdog] FlashDrive Model Server recovered successfully." | tee -a "$WATCHDOG_LOG"
                break
            fi
            sleep 1
        done
    fi
}

start_runner() {
    echo "[Watchdog] Launching run_full_44_matrix_flooded_6400.sh in background..." | tee -a "$WATCHDOG_LOG"
    ensure_server
    bash scripts/common/run_full_44_matrix_flooded_6400.sh >> "$PROGRESS_LOG" 2>&1 &
    RUNNER_PID=$!
    echo "[Watchdog] Runner started with PID $RUNNER_PID at $(date)." | tee -a "$WATCHDOG_LOG"
}

# Initial launch
ensure_server
start_runner

STUCK_THRESHOLD_SEC=900 # 15 minutes of zero log growth

while true; do
    sleep 30
    
    COMPLETED=$(count_completed)
    echo "[Watchdog Check $(date +%H:%M:%S)] Completed routes: $COMPLETED / 44" | tee -a "$WATCHDOG_LOG"
    
    if [ "$COMPLETED" -ge 44 ]; then
        echo "================================================================================" | tee -a "$WATCHDOG_LOG"
        echo "[Watchdog SUCCESS] All 44 routes have completed checkpoints for Matrix-Flooded-6400!" | tee -a "$WATCHDOG_LOG"
        echo "Finished at $(date)." | tee -a "$WATCHDOG_LOG"
        echo "================================================================================" | tee -a "$WATCHDOG_LOG"
        break
    fi
    
    # 1. Check if runner process is alive
    if ! ps aux | grep -v grep | grep -q "run_full_44_matrix_flooded_6400.sh"; then
        echo "[Watchdog ALERT] Runner script died unexpectedly! Restarting..." | tee -a "$WATCHDOG_LOG"
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
        sleep 3
        start_runner
        continue
    fi
    
    # 2. Check for frozen simulation (log inactivity)
    if [ -f "$PROGRESS_LOG" ]; then
        LAST_MOD=$(stat -c %Y "$PROGRESS_LOG" 2>/dev/null || stat -f %m "$PROGRESS_LOG" 2>/dev/null)
        NOW=$(date +%s)
        DIFF=$((NOW - LAST_MOD))
        
        if [ "$DIFF" -gt "$STUCK_THRESHOLD_SEC" ]; then
            echo "[Watchdog ALERT] Simulation stuck for $DIFF seconds (> $STUCK_THRESHOLD_SEC s). Killing and recovering..." | tee -a "$WATCHDOG_LOG"
            pkill -9 -f "run_full_44_matrix_flooded_6400.sh" 2>/dev/null || true
            pkill -9 -f "CarlaUE4" 2>/dev/null || true
            pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
            pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
            rm -f "$SOCK_PATH"
            sleep 5
            start_runner
            continue
        fi
    fi
done
