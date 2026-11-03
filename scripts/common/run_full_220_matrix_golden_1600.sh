#!/bin/bash
# ==============================================================================
# Bench2Drive Full 220 Routes Evaluation - Matrix-Golden-1600 Run
# ==============================================================================
# Model: Alpamayo-1.5-10B-Matrix-Golden-1600-A15 (Curated 1,600 Small)
# Controller: Clean Baseline Controller (VehiclePIDController)
# Tag: model_matrix_golden_1600
# Total Routes: 220 (44 canonical already completed, 176 remaining)
# ==============================================================================

set -e
cd /home/aimslab/lead

LOG_FILE="outputs/full_220_matrix_golden_1600_progress.log"
mkdir -p outputs/local_evaluation
touch "$LOG_FILE"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "Starting Full 220 Evaluation: Alpamayo-1.5-10B-Matrix-Golden-1600-A15" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"
MODEL_DIR="/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

if ! server_is_alive; then
    echo "[Runner] Launching FlashDrive Server with Matrix-Golden-1600..." | tee -a "$LOG_FILE"
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
        --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_golden1600.log 2>&1 &
    
    echo "[Runner] Waiting for server to initialize..." | tee -a "$LOG_FILE"
    for i in $(seq 1 600); do
        if server_is_alive; then
            echo "[Runner] Model Server ready!" | tee -a "$LOG_FILE"
            break
        fi
        sleep 1
    done
fi

# Load all 220 routes from bench2drive220.xml
ROUTES_TO_RUN=()
while IFS= read -r rid; do
    [ -n "$rid" ] && ROUTES_TO_RUN+=("$rid")
done < <(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('/home/aimslab/Bench2Drive/leaderboard/data/bench2drive220.xml')
for r in tree.getroot().findall('route'):
    print(r.get('id'))
")

TOTAL=${#ROUTES_TO_RUN[@]}
echo "[Runner] Total benchmark routes registered: $TOTAL" | tee -a "$LOG_FILE"

for idx in "${!ROUTES_TO_RUN[@]}"; do
    ROUTE_ID="${ROUTES_TO_RUN[$idx]}"
    CURRENT=$((idx + 1))
    
    CKPT_FILE="outputs/local_evaluation/model_matrix_golden_1600_${ROUTE_ID}/checkpoint_endpoint.json"
    
    # Check if already completed and valid
    if [ -f "$CKPT_FILE" ] && grep -q '"score_composed"' "$CKPT_FILE" 2>/dev/null; then
        echo "[$CURRENT/$TOTAL] Route $ROUTE_ID already completed. Skipping." | tee -a "$LOG_FILE"
        continue
    fi
    
    echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"
    echo "[$CURRENT/$TOTAL] Starting Route $ROUTE_ID..." | tee -a "$LOG_FILE"
    echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"
    
    # Ensure CARLA is clean
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
    sleep 2
    
    ROUTE_XML="src/lead/routes/benchmark_routes/bench2drive/${ROUTE_ID}.xml"
    
    MODEL_TAG="model_matrix_golden_1600" \
    MODEL_PATH="$MODEL_DIR" \
    bash scripts/common/eval_alpamayo_b2d.sh "$ROUTE_XML" >> "$LOG_FILE" 2>&1 || {
        echo "[$CURRENT/$TOTAL] Route $ROUTE_ID finished with non-zero exit code. Checking logs..." | tee -a "$LOG_FILE"
    }
    
    # Read and report result
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
    print(f'>>> RESULT [$CURRENT/$TOTAL] Route $ROUTE_ID: DS={ds:6.2f} | RC={rc:5.1f}% | Crashes={crashes} | Status: {status}')
except Exception as e:
    print(f'>>> RESULT [$CURRENT/$TOTAL] Route $ROUTE_ID: Error parsing results ({e})')
" | tee -a "$LOG_FILE"

    sleep 2
done

echo "================================================================================" | tee -a "$LOG_FILE"
echo "Evaluation Finished at $(date)!" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"
