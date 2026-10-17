#!/bin/bash
# ==============================================================================
# Bench2Drive 44 Canonical Scenarios Evaluation - checkpoint-20050 Final Run
# ==============================================================================
# Model: checkpoint-20050 (Curated 6,400 Large)
# Controller: Zero-Lag Steering (alpha_steer = 1.0) + Standstill Breakout Torque
# Tag: model_v4_final
# ==============================================================================

set -e
cd /home/aimslab/lead

LOG_FILE="outputs/full_44_eval_progress.log"
mkdir -p outputs/local_evaluation
touch "$LOG_FILE"

echo "================================================================================" | tee -a "$LOG_FILE"
echo "Starting Full 44 Canonical Scenarios Evaluation for checkpoint-20050" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"

# Verify FlashDrive Model Server is responsive
server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

if ! server_is_alive; then
    echo "[Runner] Model server socket not active. Launching FlashDrive Server..." | tee -a "$LOG_FILE"
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
    
    echo "[Runner] Waiting for server to initialize..." | tee -a "$LOG_FILE"
    for i in $(seq 1 600); do
        if server_is_alive; then
            echo "[Runner] Model Server ready!" | tee -a "$LOG_FILE"
            break
        fi
        sleep 1
    done
fi

# 44 Canonical Bench2Drive Scenarios
SCENARIOS=(
    "Accident:2534"
    "AccidentTwoWays:1852"
    "BlockedIntersection:2204"
    "ConstructionObstacle:2513"
    "ConstructionObstacleTwoWays:1825"
    "ControlLoss:3561"
    "CrossingBicycleFlow:3086"
    "DynamicObjectCrossing:17752"
    "EnterActorFlow:2201"
    "HardBreakRoute:3540"
    "HazardAtSideLane:1790"
    "HazardAtSideLaneTwoWays:3436"
    "HighwayCutIn:2286"
    "HighwayExit:23687"
    "InterurbanActorFlow:23901"
    "InterurbanAdvancedActorFlow:23695"
    "InvadingTurn:2790"
    "MergerIntoSlowTraffic:2283"
    "MergerIntoSlowTrafficV2:23771"
    "NonSignalizedJunctionLeftTurn:2084"
    "NonSignalizedJunctionLeftTurnEnterFlow:28087"
    "NonSignalizedJunctionRightTurn:2115"
    "OppositeVehicleRunningRedLight:2082"
    "OppositeVehicleTakingPriority:2127"
    "ParkedObstacle:1773"
    "ParkedObstacleTwoWays:2664"
    "ParkingCrossingPedestrian:3248"
    "ParkingCutIn:1711"
    "ParkingExit:1956"
    "PedestrianCrossing:14194"
    "SequentialLaneChange:17563"
    "SignalizedJunctionLeftTurn:3936"
    "SignalizedJunctionLeftTurnEnterFlow:28099"
    "SignalizedJunctionRightTurn:2050"
    "StaticCutIn:2709"
    "T_Junction:26458"
    "VanillaNonSignalizedTurn:2390"
    "VanillaNonSignalizedTurnEncounterStopsign:2416"
    "VanillaSignalizedTurnEncounterGreenLight:14842"
    "VanillaSignalizedTurnEncounterRedLight:3144"
    "VehicleOpensDoorTwoWays:3464"
    "VehicleTurningRoute:2144"
    "VehicleTurningRoutePedestrian:2164"
    "YieldToEmergencyVehicle:3364"
)

TOTAL=${#SCENARIOS[@]}

for idx in "${!SCENARIOS[@]}"; do
    ENTRY="${SCENARIOS[$idx]}"
    SC_NAME="${ENTRY%%:*}"
    ROUTE_ID="${ENTRY##*:}"
    CURRENT=$((idx + 1))
    
    CKPT_FILE="outputs/local_evaluation/model_v4_final_${ROUTE_ID}/checkpoint_endpoint.json"
    
    # Check if already completed
    if [ -f "$CKPT_FILE" ] && grep -q '"scores_mean"' "$CKPT_FILE" 2>/dev/null; then
        echo "[$CURRENT/$TOTAL] Route $ROUTE_ID ($SC_NAME) already completed. Skipping." | tee -a "$LOG_FILE"
        continue
    fi
    
    echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"
    echo "[$CURRENT/$TOTAL] Starting Route $ROUTE_ID ($SC_NAME)..." | tee -a "$LOG_FILE"
    echo "--------------------------------------------------------------------------------" | tee -a "$LOG_FILE"
    
    # Ensure CARLA is clean
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
    sleep 2
    
    ROUTE_XML="src/lead/routes/benchmark_routes/bench2drive/${ROUTE_ID}.xml"
    
    MODEL_TAG="model_v4_final" \
    MODEL_PATH="/home/aimslab/checkpoints/action_experts/model_v4" \
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
    col = len(r.get('infractions', {}).get('collisions_vehicle', []))
    status = r.get('status', 'Unknown')
    print(f'>>> RESULT [$CURRENT/$TOTAL] Route $ROUTE_ID ($SC_NAME): DS={ds:6.2f} | RC={rc:5.1f}% | Col={col} | Status: {status}')
except Exception as e:
    print(f'>>> RESULT [$CURRENT/$TOTAL] Route $ROUTE_ID ($SC_NAME): Error parsing results ({e})')
" | tee -a "$LOG_FILE"

    sleep 2
done

echo "================================================================================" | tee -a "$LOG_FILE"
echo "Evaluation Finished at $(date)!" | tee -a "$LOG_FILE"
echo "================================================================================" | tee -a "$LOG_FILE"

# Final Scorecard Computation
python3 -c "
import glob, json, re

results = {}
for p in sorted(glob.glob('outputs/local_evaluation/model_v4_final_*/checkpoint_endpoint.json')):
    m = re.search(r'model_v4_final_(\d+)/checkpoint_endpoint\.json', p)
    if m:
        try:
            with open(p) as f: d = json.load(f)
            r = d['_checkpoint']['records'][0]
            results[m.group(1)] = {
                'ds': r['scores']['score_composed'],
                'rc': r['scores']['score_route'],
                'col': len(r.get('infractions', {}).get('collisions_vehicle', [])),
                'status': r.get('status', 'Unknown')
            }
        except Exception:
            pass

n = len(results)
if n > 0:
    mean_ds = sum(r['ds'] for r in results.values()) / n
    mean_rc = sum(r['rc'] for r in results.values()) / n
    succ = sum(1 for r in results.values() if r['status'] == 'Completed')
    total_col = sum(r['col'] for r in results.values())
    print(f'FINAL SCORECARD (checkpoint-20050):')
    print(f'Routes Evaluated: {n}/44')
    print(f'Mean Driving Score (DS): {mean_ds:.2f}')
    print(f'Mean Route Completion:   {mean_rc:.2f}%')
    print(f'Success Rate (SR):       {succ}/{n} ({succ/n*100:.1f}%)')
    print(f'Total Vehicle Collisions: {total_col}')
" | tee -a "$LOG_FILE"
