#!/bin/bash
# Evaluates the remaining 4 benchmark routes sequentially
set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "src/lead/routes/benchmark_routes/bench2drive/23687.xml"
    "src/lead/routes/benchmark_routes/bench2drive/14194.xml"
    "src/lead/routes/benchmark_routes/bench2drive/10857.xml"
    "src/lead/routes/benchmark_routes/bench2drive/11381.xml"
)

echo "=========================================================="
echo "Starting Batch Evaluation of 4 Routes"
echo "=========================================================="

for route in "${ROUTES[@]}"; do
    route_id=$(basename "$route" .xml)
    echo ""
    echo "----------------------------------------------------------"
    echo "[Batch Evaluator] Starting Route: $route_id ($route)"
    echo "----------------------------------------------------------"
    
    mkdir -p "outputs/local_evaluation/alpamayo_${route_id}"
    log_file="outputs/local_evaluation/alpamayo_${route_id}/eval.log"
    
    # Run route evaluation redirecting output to log file to avoid terminal pty buffer deadlocks
    bash scripts/common/eval_alpamayo_b2d.sh "$route" > "$log_file" 2>&1 || {
        echo "[Batch Evaluator] Route $route_id completed with return code $?."
    }
    
    echo "[Batch Evaluator] Finished Route: $route_id"
    
    # Print status of this route
    ckpt_path="outputs/local_evaluation/alpamayo_${route_id}/checkpoint_endpoint.json"
    if [ -f "$ckpt_path" ]; then
        python3 -c '
import json, sys
try:
    with open(sys.argv[1]) as f:
        data = json.load(f)
    rec = data.get("_checkpoint", {}).get("global_record", {})
    score_route = rec.get("scores_mean", {}).get("score_route", 0.0)
    score_composed = rec.get("scores_mean", {}).get("score_composed", 0.0)
    status = rec.get("status", "Unknown")
    print(f"  [Result] Route {sys.argv[2]}: Completion = {score_route:.1f}%, Score = {score_composed:.1f}, Status = {status}")
except Exception as e:
    print(f"  [Result] Error parsing checkpoint: {e}")
' "$ckpt_path" "$route_id"
    else
        echo "  [Result] Checkpoint not generated for route $route_id"
    fi
    
    # Clean up CARLA to guarantee fresh simulator state for the next route
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 3
done

echo ""
echo "=========================================================="
echo "Batch Evaluation Complete! Summarizing results..."
echo "=========================================================="

python3 -c '
import json, os

routes = ["3936", "23687", "14194", "10857", "11381"]
names = {
    "3936": "Signalized Left Turn",
    "23687": "Highway Exit",
    "14194": "Pedestrian Crossing",
    "10857": "Vehicle Turning Route Pedestrian",
    "11381": "Vehicle Turning Route Pedestrian"
}

print(f"{chr(95)*85}")
print(f"| {\"Route\":<7} | {\"Scenario Type\":<32} | {\"Route %\":<8} | {\"Score\":<8} | {\"Status\":<15} |")
print(f"|{chr(45)*9}|{chr(45)*34}|{chr(45)*10}|{chr(45)*10}|{chr(45)*17}|")

for r in routes:
    ckpt_path = f"outputs/local_evaluation/alpamayo_{r}/checkpoint_endpoint.json"
    if os.path.exists(ckpt_path):
        try:
            with open(ckpt_path) as f:
                data = json.load(f)
            rec = data["_checkpoint"]["global_record"]
            score_route = rec.get("scores_mean", {}).get("score_route", 0.0)
            score_composed = rec.get("scores_mean", {}).get("score_composed", 0.0)
            status = rec.get("status", "Unknown")
            print(f"| {r:<7} | {names.get(r, \"Unknown\"):<32} | {score_route:>6.1f} % | {score_composed:>8.1f} | {status:<15} |")
        except Exception as e:
            print(f"| {r:<7} | {names.get(r, \"Unknown\"):<32} | Error reading checkpoint: {e} |")
    else:
        print(f"| {r:<7} | {names.get(r, \"Unknown\"):<32} | {\"Pending\":<8} | {\"Pending\":<8} | {\"Not run yet\":<15} |")

print(f"{chr(95)*85}")
'
