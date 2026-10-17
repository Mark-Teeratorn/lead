#!/bin/bash
# Auto-watchdog for Test 2: monitors Route 1773 and automatically relaunches if CARLA crashes or hangs.
cd /home/aimslab/lead

ROUTE_XML="src/lead/routes/benchmark_routes/bench2drive/1773.xml"
CKPT_FILE="outputs/local_evaluation/model_v4_test2_1773_1773/checkpoint_endpoint.json"
LOG_FILE="outputs/test2_lookahead_1773.log"

check_success() {
    [ -f "$CKPT_FILE" ] && python3 -c "
import json
with open('$CKPT_FILE') as f: d = json.load(f)
recs = d.get('_checkpoint', {}).get('records', [])
if recs and 'scores' in recs[0]:
    exit(0)
exit(1)
" 2>/dev/null
}

echo "[watchdog] Auto-watchdog started for Route 1773 Test 2..."

while true; do
    sleep 30
    
    # Check if run finished successfully
    if check_success; then
        echo "[watchdog] Route 1773 completed successfully!"
        break
    fi
    
    # Check if evaluator is still actively running
    if ! pgrep -f "leaderboard_evaluator.py" > /dev/null; then
        echo "[watchdog] Detected process stopped without completion. Auto-relaunching Route 1773..."
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
        sleep 3
        
        MODEL_TAG="model_v4_test2_1773" \
        MODEL_PATH="/home/aimslab/checkpoints/action_experts/model_v4" \
        nohup bash scripts/common/eval_alpamayo_b2d.sh "$ROUTE_XML" >> "$LOG_FILE" 2>&1 &
        echo "[watchdog] Relaunched with PID $!"
    fi
done
