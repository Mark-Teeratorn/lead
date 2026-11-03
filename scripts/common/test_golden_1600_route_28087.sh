#!/bin/bash
# ==============================================================================
# Re-test Route 28087 for Alpamayo-1.5-10B-Matrix-Golden-1600-A15
# Scenario: NonSignalizedJunctionLeftTurnEnterFlow (Route 28087)
# Controller: Clean Baseline Controller (VehiclePIDController)
# ==============================================================================

set -e
cd /home/aimslab/lead

LOG_FILE="outputs/test_golden_1600_route_28087.log"
mkdir -p outputs/local_evaluation
rm -f "$LOG_FILE"
touch "$LOG_FILE"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "Starting Route 28087 Re-test: Alpamayo-1.5-10B-Matrix-Golden-1600-A15" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"
MODEL_DIR="/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

if server_is_alive; then
    echo "[Setup] Active FlashDrive Server detected on $SOCK_PATH. Reusing existing server!" | tee -a "$LOG_FILE"
else
    echo "[Setup] Ensuring clean environment..." | tee -a "$LOG_FILE"
    rm -f "$SOCK_PATH"
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
    sleep 2

    echo "[Setup] Launching FlashDrive Server with Matrix-Golden-1600..." | tee -a "$LOG_FILE"
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PYTORCH_ALLOC_CONF=expandable_segments:True \
    $FLASHDRIVE_PYTHON -u /home/aimslab/flashdrive/scripts/flashdrive_server.py \
        --model-path "$MODEL_DIR" \
        --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_golden_retest.log 2>&1 &

    echo "[Setup] Waiting for model server to initialize..." | tee -a "$LOG_FILE"
    for i in $(seq 1 300); do
        if server_is_alive; then
            echo "[Setup] Model Server ready!" | tee -a "$LOG_FILE"
            break
        fi
        sleep 1
    done

    if ! server_is_alive; then
        echo "[Error] FlashDrive server failed to start within timeout." | tee -a "$LOG_FILE"
        exit 1
    fi
fi

ROUTE_XML="src/lead/routes/benchmark_routes/bench2drive/28087.xml"
MODEL_TAG="model_matrix_golden_1600_retest"

echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"
echo "Executing Evaluation: Route 28087 (NonSignalizedJunctionLeftTurnEnterFlow)..." | tee -a "$LOG_FILE"
echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"

MODEL_TAG="$MODEL_TAG" \
MODEL_PATH="$MODEL_DIR" \
bash scripts/common/eval_alpamayo_b2d.sh "$ROUTE_XML" >> "$LOG_FILE" 2>&1 || {
    echo "Evaluation exited with status $?." | tee -a "$LOG_FILE"
}

CKPT_FILE="outputs/local_evaluation/${MODEL_TAG}_28087/checkpoint_endpoint.json"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "RESULT EVALUATION FOR ROUTE 28087" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

python3 -c "
import json
try:
    with open('$CKPT_FILE') as f:
        d = json.load(f)
    r = d['_checkpoint']['records'][0]
    ds = r['scores']['score_composed']
    rc = r['scores']['score_route']
    inf = r.get('infractions', {})
    crashes = len(inf.get('collisions_layout', [])) + len(inf.get('collisions_vehicle', [])) + len(inf.get('collisions_pedestrian', []))
    status = r.get('status', 'Unknown')
    print(f'>>> RESULT Route 28087 (Golden 1600 Retest): DS={ds:6.2f} | RC={rc:5.1f}% | Crashes={crashes} | Status: {status}')
except Exception as e:
    print(f'Error reading result file: {e}')
" | tee -a "$LOG_FILE"

echo "Finished at $(date)" | tee -a "$LOG_FILE"
