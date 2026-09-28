#!/bin/bash
# Evaluates 5 stress-test (hardest) benchmark routes covering all 5 Bench2Drive advanced driving skills:
# 1. Merging: Route 2283 (MergerIntoSlowTraffic - forced merge into dense non-yielding traffic)
# 2. Emergency Brake: Route 2082 (OppositeVehicleRunningRedLight - high-speed red light runner)
# 3. Overtaking: Route 1825 (ConstructionObstacleTwoWays - entering oncoming lane to overtake)
# 4. Give Way: Route 2790 (InvadingTurn - oncoming vehicle encroaches ego lane mid-turn)
# 5. Traffic Sign Compliance: Route 2204 (BlockedIntersection - green light gridlock / don't block the box)
# All routes are in Town12 for optimal CARLA stability and simulation speed.

set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "src/lead/routes/benchmark_routes/bench2drive/2283.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2082.xml"
    "src/lead/routes/benchmark_routes/bench2drive/1825.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2790.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2204.xml"
)

echo "=========================================================="
echo "Starting Evaluation of 5 Stress-Test (Hardest) Routes"
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
echo "Stress-Test Evaluation Complete! Summarizing results..."
echo "=========================================================="

python3 -c '
import json, os

routes = ["2283", "2082", "1825", "2790", "2204"]
categories = {
    "2283": ("Merging", "Merger Into Slow Traffic"),
    "2082": ("Emergency Brake", "Red Light Runner"),
    "1825": ("Overtaking", "Two-Way Construction Obstacle"),
    "2790": ("Give Way", "Invading Turn"),
    "2204": ("Traffic Signs", "Blocked Intersection Gridlock")
}

h_route = "Route"
h_cat = "Ability Category"
h_sc = "Scenario Type"
h_pct = "Route %"
h_score = "Score"
h_status = "Status"
sep = "_" * 98
dash = "-"

print(sep)
print(f"| {h_route:<7} | {h_cat:<18} | {h_sc:<31} | {h_pct:<8} | {h_score:<8} | {h_status:<10} |")
print(f"|{dash*9}|{dash*20}|{dash*33}|{dash*10}|{dash*10}|{dash*12}|")

for r in routes:
    cat, name = categories.get(r, ("Unknown", "Unknown"))
    ckpt_path = f"outputs/local_evaluation/alpamayo_{r}/checkpoint_endpoint.json"
    if os.path.exists(ckpt_path):
        try:
            with open(ckpt_path) as f:
                data = json.load(f)
            rec = data["_checkpoint"]["global_record"]
            score_route = rec.get("scores_mean", {}).get("score_route", 0.0)
            score_composed = rec.get("scores_mean", {}).get("score_composed", 0.0)
            status = rec.get("status", "Unknown")
            print(f"| {r:<7} | {cat:<18} | {name:<31} | {score_route:>6.1f} % | {score_composed:>8.1f} | {status:<10} |")
        except Exception as e:
            print(f"| {r:<7} | {cat:<18} | {name:<31} | Error: {e} |")
    else:
        pending = "Pending"
        not_run = "Not run"
        print(f"| {r:<7} | {cat:<18} | {name:<31} | {pending:<8} | {pending:<8} | {not_run:<10} |")

print(sep)
'
