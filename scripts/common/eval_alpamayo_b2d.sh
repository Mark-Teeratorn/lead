#!/bin/bash
# Evaluates Alpamayo 1.5 (via FlashDrive Client-Server Bridge) on Bench2Drive / Fail2Drive
set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

_lead_output_dir_root=$(dotenv LEAD_OUTPUT_DIR_ROOT 2>/dev/null || echo "outputs")

# Parse arguments flexibly: supports route.xml, --gui, and --dummy in any order
_gui=0
_dummy_flag=""
_routes=""

for arg in "$@"; do
    case "$arg" in
        --gui)
            _gui=1
            ;;
        --dummy)
            _dummy_flag="--dummy"
            ;;
        *.xml)
            _routes="$arg"
            ;;
        *)
            if [ -z "$_routes" ]; then
                _routes="$arg"
            fi
            ;;
    esac
done

if [ -z "$_routes" ]; then
    _routes="src/lead/routes/benchmark_routes/bench2drive/23687.xml"
fi

if [ "$_gui" = "1" ] || [ "${CARLA_GUI:-0}" = "1" ]; then
    export CARLA_GUI=1
    export DISPLAY="${DISPLAY:-:1}"
    _uid=$(id -u)
    if [ -z "$XAUTHORITY" ] && [ -f "/run/user/$_uid/gdm/Xauthority" ]; then
        export XAUTHORITY="/run/user/$_uid/gdm/Xauthority"
    fi
fi

export BENCHMARK_ROUTE_ID=$(basename "$_routes" .xml)
_evaluation_output_dir="$_lead_output_dir_root/local_evaluation/alpamayo_$BENCHMARK_ROUTE_ID/"

# Python environment paths
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"
LEAD_PYTHON="/home/aimslab/lead/.venv/bin/python"
CARLA_API="/home/aimslab/lead/3rd_party/CARLA/fail2drive_0915/PythonAPI/carla"
CARLA_0915_EGG="$CARLA_API/dist/carla-0.9.15-py3.10-linux-x86_64.egg"

export PYTHONPATH="$CARLA_0915_EGG:$CARLA_API:src:3rd_party/leaderboard/bench2drive/leaderboard:3rd_party/leaderboard/bench2drive/scenario_runner:$PYTHONPATH"
export SCENARIO_RUNNER_ROOT="3rd_party/leaderboard/bench2drive/scenario_runner"
export IS_BENCH2DRIVE=1
export SAVE_PATH="$_evaluation_output_dir/"
export PYTHONUNBUFFERED=1
export CARLA_QUALITY_LEVEL="${CARLA_QUALITY_LEVEL:-Low}"
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

mkdir -p "$_evaluation_output_dir"
rm -f "$_evaluation_output_dir/checkpoint_endpoint.json" "$_evaluation_output_dir/predicted_trajectories.jsonl"

# 1. Start FlashDrive Model Server (Python 3.12)
SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
SERVER_PID=""

cleanup() {
    echo "[eval_alpamayo] Cleaning up services..."
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        rm -f "$SOCK_PATH"
    fi
    if [ -n "$CARLA_PID" ]; then
        kill $CARLA_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(1); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

if server_is_alive; then
    echo "[eval_alpamayo] Detected active Model Server on $SOCK_PATH. Reusing it."
else
    rm -f "$SOCK_PATH"
    
    # If CARLA is running, temporarily stop it so the 10B model has full 24GB VRAM headroom during load
    if ss -tulpn | grep -q ":2000 "; then
        echo "[eval_alpamayo] Stopping existing CARLA to free VRAM for Alpamayo 10B model loading..."
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        sleep 2
    fi

    echo "[eval_alpamayo] Starting FlashDrive Model Server (Python 3.12)..."
    DUMMY_ARG=""
    if [ "$_dummy_flag" = "--dummy" ]; then
        DUMMY_ARG="--dummy"
    fi

    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PYTORCH_ALLOC_CONF=expandable_segments:True \
    $FLASHDRIVE_PYTHON /home/aimslab/flashdrive/scripts/flashdrive_server.py $DUMMY_ARG --socket-path "$SOCK_PATH" &
    SERVER_PID=$!

    # Wait for server socket to be active (10B model + W4A8 quantization + DFlash takes ~3-5 mins)
    echo "[eval_alpamayo] Waiting for Model Server socket to initialize (takes ~3-5 mins)..."
    for i in $(seq 1 600); do
        if [ -S "$SOCK_PATH" ]; then
            echo -e "\n[eval_alpamayo] Model Server is ready."
            break
        fi
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo -e "\n[eval_alpamayo] Error: Model Server process died unexpectedly."
            break
        fi
        if [ $((i % 10)) -eq 0 ]; then
            echo -n "."
        fi
        sleep 1
    done

    if [ ! -S "$SOCK_PATH" ]; then
        echo "[eval_alpamayo] Error: Model Server failed to start within timeout."
        exit 1
    fi
fi

# 2. Start CARLA 0.9.15 if not already running on port 2000
CARLA_PID=""
CARLA_EXTRA_FLAGS=""
if [ "${CARLA_GUI:-0}" = "1" ]; then
    CARLA_EXTRA_FLAGS="--gui"
fi

# If CARLA is running headless but GUI was requested, restart it with GUI
if ss -tulpn | grep -q ":2000 "; then
    if [ "${CARLA_GUI:-0}" = "1" ] && pgrep -f "CarlaUE4.*-RenderOffScreen" >/dev/null; then
        echo "[eval_alpamayo] Detected CARLA running headless. Restarting in GUI mode..."
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        sleep 2
    fi
fi

if ! ss -tulpn | grep -q ":2000 "; then
    if [ "${CARLA_GUI:-0}" = "1" ]; then
        echo "[eval_alpamayo] Starting CARLA 0.9.15 server with GUI (Quality: $CARLA_QUALITY_LEVEL, Display: $DISPLAY)..."
    else
        echo "[eval_alpamayo] Starting CARLA 0.9.15 server in headless mode (Quality: $CARLA_QUALITY_LEVEL)..."
    fi
    ./scripts/cli/start_carla --fail2drive $CARLA_EXTRA_FLAGS 2000 2001 &
    CARLA_PID=$!
    echo "[eval_alpamayo] Waiting for CARLA to listen on port 2000..."
    for i in $(seq 1 60); do
        if ss -tulpn | grep -q ":2000 "; then
            echo "[eval_alpamayo] CARLA 0.9.15 is ready on port 2000."
            break
        fi
        sleep 1
    done
fi

if ! ss -tulpn | grep -q ":2000 "; then
    echo "[eval_alpamayo] Error: CARLA failed to start on port 2000."
    exit 1
fi

# 3. Launch Bench2Drive Leaderboard Evaluator
echo "[eval_alpamayo] Launching Leaderboard Evaluator on route $_routes..."
$LEAD_PYTHON 3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/leaderboard_evaluator.py \
    --routes="$_routes" \
    --track=SENSORS \
    --checkpoint="$_evaluation_output_dir/checkpoint_endpoint.json" \
    --agent=src/lead/evaluation/agents/alpamayo/alpamayo_bridge_agent.py \
    --debug=0 \
    --record=None \
    --port=2000 \
    --traffic-manager-port=8000 \
    --timeout=60 \
    --traffic-manager-seed=0 \
    --repetitions=1

echo "[eval_alpamayo] Evaluation finished successfully."
