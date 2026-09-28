#!/bin/bash
# Evaluates 5 canonical benchmark routes covering all 5 Bench2Drive advanced driving skills:
# 1. Merging: Route 23687 (HighwayExit)
# 2. Emergency Brake: Route 14194 (PedestrianCrossing)
# 3. Overtaking: Route 2513 (ConstructionObstacle)
# 4. Give Way: Route 2790 (InvadingTurn)
# 5. Traffic Sign Compliance: Route 3144 (VanillaSignalizedTurnEncounterRedLight)
#
# Compares Baseline Z-AI Alpamayo vs. Stage 2 Trained Pilot (checkpoint-600)
#
# Usage:
#   bash scripts/common/eval_batch_5canonical.sh            # Run Stage 2 & compare against Baseline
#   bash scripts/common/eval_batch_5canonical.sh --both     # Run both Baseline and Stage 2 sequentially
#   bash scripts/common/eval_batch_5canonical.sh --base     # Run Baseline only
#   bash scripts/common/eval_batch_5canonical.sh --stage2   # Run Stage 2 only

set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "src/lead/routes/benchmark_routes/bench2drive/23687.xml"
    "src/lead/routes/benchmark_routes/bench2drive/14194.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2513.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2790.xml"
    "src/lead/routes/benchmark_routes/bench2drive/3144.xml"
)

MODE="compare" # default: run stage2 and compare with baseline
for arg in "$@"; do
    case "$arg" in
        --both)   MODE="both" ;;
        --base)   MODE="base" ;;
        --stage2) MODE="stage2" ;;
    esac
done

STAGE2_MODEL_PATH="/home/aimslab/checkpoints/checkpoint-600"
BASE_MODEL_PATH="z-lab/Alpamayo-1.5-10B"

run_suite() {
    local tag="$1"
    local model_path="$2"
    local desc="$3"
    
    echo ""
    echo "=========================================================="
    echo "Starting Batch Evaluation for: $desc (tag=$tag)"
    echo "=========================================================="
    
    for route in "${ROUTES[@]}"; do
        route_id=$(basename "$route" .xml)
        echo ""
        echo "----------------------------------------------------------"
        echo "[$tag] Starting Route: $route_id ($route)"
        echo "----------------------------------------------------------"
        
        mkdir -p "outputs/local_evaluation/${tag}_${route_id}"
        log_file="outputs/local_evaluation/${tag}_${route_id}/eval.log"
        
        # Kill any active server when switching models to ensure fresh weights load
        rm -f "/tmp/alpamayo_flashdrive.sock"
        pkill -f "flashdrive_server.py" 2>/dev/null || true
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        sleep 2
        
        MODEL_TAG="$tag" MODEL_PATH="$model_path" bash scripts/common/eval_alpamayo_b2d.sh "$route" > "$log_file" 2>&1 || {
            echo "[$tag] Route $route_id completed with return code $?."
        }
        
        echo "[$tag] Finished Route: $route_id"
        
        ckpt_path="outputs/local_evaluation/${tag}_${route_id}/checkpoint_endpoint.json"
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
    print(f"  [{sys.argv[3]}] Route {sys.argv[2]}: Completion = {score_route:.1f}%, Score = {score_composed:.1f}, Status = {status}")
except Exception as e:
    print(f"  [{sys.argv[3]}] Error parsing checkpoint: {e}")
' "$ckpt_path" "$route_id" "$tag"
        fi
        
        pkill -9 -f "CarlaUE4" 2>/dev/null || true
        sleep 2
    done
}

if [ "$MODE" = "base" ] || [ "$MODE" = "both" ]; then
    run_suite "base" "$BASE_MODEL_PATH" "Baseline (z-lab/Alpamayo-1.5-10B)"
fi

if [ "$MODE" = "stage2" ] || [ "$MODE" = "both" ] || [ "$MODE" = "compare" ]; then
    run_suite "stage2" "$STAGE2_MODEL_PATH" "Trained Pilot (Stage 2 checkpoint-600)"
fi

echo ""
echo "=========================================================="
echo "5 Canonical Abilities A/B Comparison: Base vs. Stage 2"
echo "=========================================================="

python3 -c '
import json, os

routes = ["23687", "14194", "2513", "2790", "3144"]
categories = {
    "23687": ("Merging", "Highway Exit"),
    "14194": ("Emergency Brake", "Pedestrian Crossing"),
    "2513":  ("Overtaking", "Construction Obstacle"),
    "2790":  ("Give Way", "Invading Turn"),
    "3144":  ("Traffic Signs", "Signalized Red Light Turn")
}

def get_stats(prefix, r):
    paths = [
        f"outputs/local_evaluation/{prefix}_{r}/checkpoint_endpoint.json",
        f"outputs/local_evaluation/alpamayo_{r}/checkpoint_endpoint.json" if prefix == "base" else None
    ]
    for p in paths:
        if p and os.path.exists(p):
            try:
                with open(p) as f:
                    rec = json.load(f)["_checkpoint"]["global_record"]
                return rec.get("scores_mean", {}).get("score_route", 0.0), rec.get("scores_mean", {}).get("score_composed", 0.0), rec.get("status", "Unknown")
            except Exception:
                pass
    return None, None, "Not run"

h_route, h_cat, h_sc = "Route", "Ability Category", "Scenario Type"
h_b_pct, h_s2_pct = "Base %", "Stg2 %"
h_b_sc, h_s2_sc = "Base DS", "Stg2 DS"
h_diff = "Δ Score"

sep = "_" * 115
dash = "-"

print(sep)
print(f"| {h_route:<7} | {h_cat:<17} | {h_sc:<28} | {h_b_pct:<8} | {h_s2_pct:<8} | {h_b_sc:<8} | {h_s2_sc:<8} | {h_diff:<8} |")
print(f"|{dash*9}|{dash*19}|{dash*30}|{dash*10}|{dash*10}|{dash*10}|{dash*10}|{dash*10}|")

for r in routes:
    cat, name = categories[r]
    b_pct, b_sc, b_st = get_stats("base", r)
    s2_pct, s2_sc, s2_st = get_stats("stage2", r)
    
    b_pct_str = f"{b_pct:>6.1f} %" if b_pct is not None else "Pending"
    s2_pct_str = f"{s2_pct:>6.1f} %" if s2_pct is not None else "Pending"
    b_sc_str = f"{b_sc:>8.1f}" if b_sc is not None else "Pending"
    s2_sc_str = f"{s2_sc:>8.1f}" if s2_sc is not None else "Pending"
    
    if b_sc is not None and s2_sc is not None:
        diff = s2_sc - b_sc
        diff_str = f"{diff:>+8.1f}"
    else:
        diff_str = "    --  "
        
    print(f"| {r:<7} | {cat:<17} | {name:<28} | {b_pct_str:<8} | {s2_pct_str:<8} | {b_sc_str:<8} | {s2_sc_str:<8} | {diff_str:<8} |")

print(sep)
'
