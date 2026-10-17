#!/bin/bash
# Evaluates checkpoint-20050 with optimized controller on all faulty / low DS routes
set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "1956"   # ParkingExit (1.85 DS -> test roll-out guard)
    "1773"   # ParkedObstacle (7.78 DS -> test lateral evasion lookahead)
    "1825"   # ConstructionObstacleTwoWays (19.11 DS)
    "14842"  # SignalizedTurnGreenLight (20.20 DS)
    "2513"   # ConstructionObstacle (21.60 DS)
    "1790"   # HazardAtSideLane (21.60 DS)
    "17563"  # SequentialLaneChange (21.60 DS)
    "2709"   # StaticCutIn (21.60 DS)
    "3936"   # SignalizedJunctionLeftTurn (24.86 DS)
    "2416"   # NonSignalizedTurnStopsign (28.28 DS)
    "2534"   # Accident (29.46 DS)
    "3561"   # ControlLoss (32.51 DS)
    "3436"   # HazardAtSideLaneTwoWays (32.74 DS)
    "2050"   # SignalizedJunctionRightTurn (33.40 DS)
    "2144"   # VehicleTurningRoute (33.72 DS)
    "1852"   # AccidentTwoWays (36.00 DS)
    "2664"   # ParkedObstacleTwoWays (36.00 DS)
    "3364"   # YieldToEmergencyVehicle (36.00 DS)
    "23695"  # InterurbanAdvancedActorFlow (36.00 DS)
)

SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"

cleanup_all() {
    echo "[eval_faulty] Cleaning up..."
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        rm -f "$SOCK_PATH"
    fi
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
}
trap cleanup_all EXIT INT TERM

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(1); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

if server_is_alive; then
    echo "[eval_faulty] Detected active Model Server on $SOCK_PATH. Reusing it."
    SERVER_PID=""
else
    rm -f "$SOCK_PATH"
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 2

    echo "[eval_faulty] Starting persistent FlashDrive Model Server for checkpoint-20050..."
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PYTORCH_ALLOC_CONF=expandable_segments:True \
    $FLASHDRIVE_PYTHON -u /home/aimslab/flashdrive/scripts/flashdrive_server.py \
        --model-path /home/aimslab/checkpoints/action_experts/model_v4 \
        --socket-path "$SOCK_PATH" > /tmp/flashdrive_server_persistent.log 2>&1 &
    SERVER_PID=$!

    echo "[eval_faulty] Waiting for Model Server socket to initialize..."
    for i in $(seq 1 600); do
        if [ -S "$SOCK_PATH" ]; then
            echo -e "\n[eval_faulty] Model Server is ready."
            break
        fi
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo -e "\n[eval_faulty] Error: Model Server died unexpectedly."
            cat /tmp/flashdrive_server_persistent.log | tail -n 20
            exit 1
        fi
        sleep 1
    done
fi

mkdir -p outputs/ctrl_opt_eval

for idx in "${!ROUTES[@]}"; do
    route_id="${ROUTES[$idx]}"
    echo "================================================================================"
    echo "[eval_faulty] ($((idx+1))/${#ROUTES[@]}) Testing Route $route_id with Controller Optimization"
    echo "================================================================================"

    # Run evaluation on route
    MODEL_TAG="model_v4_ctrl_opt" \
    MODEL_PATH="/home/aimslab/checkpoints/action_experts/model_v4" \
    bash scripts/common/eval_alpamayo_b2d.sh "src/lead/routes/benchmark_routes/bench2drive/${route_id}.xml" || {
        echo "[eval_faulty] Warning: Route $route_id failed or exited with error. Continuing..."
    }

    # Print immediate score comparison if result exists
    new_res="outputs/local_evaluation/model_v4_ctrl_opt_${route_id}/checkpoint_endpoint.json"
    old_res="outputs/local_evaluation/model_v4_${route_id}/checkpoint_endpoint.json"
    if [ -f "$new_res" ]; then
        python3 -c "
import json
try:
    with open('$new_res') as f: d_new = json.load(f)
    r_new = d_new['_checkpoint']['records'][0]
    ds_new = r_new['scores']['score_composed']
    rc_new = r_new['scores']['score_route']
    col_new = len(r_new['infractions'].get('collisions_vehicle', []))

    ds_old, rc_old, col_old = 'N/A', 'N/A', 'N/A'
    if '$old_res':
        try:
            with open('$old_res') as f: d_old = json.load(f)
            r_old = d_old['_checkpoint']['records'][0]
            ds_old = f\"{r_old['scores']['score_composed']:.2f}\"
            rc_old = f\"{r_old['scores']['score_route']:.1f}%\"
            col_old = len(r_old['infractions'].get('collisions_vehicle', []))
        except: pass

    print(f'>>> Route $route_id RESULT: Old DS={ds_old} (RC={rc_old}, Col={col_old}) -> New DS={ds_new:.2f} (RC={rc_new:.1f}%, Col={col_new})')
except Exception as e:
    print(f'Error reading result: {e}')
"
    fi
    sleep 3
done

echo "================================================================================"
echo "[eval_faulty] All faulty routes evaluation completed!"
echo "================================================================================"
