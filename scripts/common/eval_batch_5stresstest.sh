#!/bin/bash
# Evaluates 5 stress-test (hardest) benchmark routes covering all 5 Bench2Drive advanced driving skills:
# 1. Merging: Route 2283 (MergerIntoSlowTraffic - forced merge into dense non-yielding traffic)
# 2. Emergency Brake: Route 2082 (OppositeVehicleRunningRedLight - high-speed red light runner)
# 3. Overtaking: Route 1825 (ConstructionObstacleTwoWays - entering oncoming lane to overtake)
# 4. Give Way: Route 2790 (InvadingTurn - oncoming vehicle encroaches ego lane mid-turn)
# 5. Traffic Sign Compliance: Route 2204 (BlockedIntersection - green light gridlock / don't block the box)
#
# Compares Baseline Z-AI Alpamayo vs. Stage 2 Trained Pilot (checkpoint-600)
#
# Usage:
#   bash scripts/common/eval_batch_5stresstest.sh            # Run Stage 2 & compare against Baseline
#   bash scripts/common/eval_batch_5stresstest.sh --both     # Run both Baseline and Stage 2 sequentially
#   bash scripts/common/eval_batch_5stresstest.sh --base     # Run Baseline only
#   bash scripts/common/eval_batch_5stresstest.sh --stage2   # Run Stage 2 only

set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "src/lead/routes/benchmark_routes/bench2drive/2283.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2082.xml"
    "src/lead/routes/benchmark_routes/bench2drive/1825.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2790.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2204.xml"
)

MODE="both" # default: run both base and stage2 together in order
FORCE=0
PAIRWISE=0

for arg in "$@"; do
    case "$arg" in
        --both)       MODE="both" ;;
        --base)       MODE="base" ;;
        --stage2)     MODE="stage2" ;;
        --pairwise|--interleaved) PAIRWISE=1 ;;
        --force)      FORCE=1 ;;
        --help|-h)
            echo "Usage: $0 [--both] [--base] [--stage2] [--pairwise] [--force]"
            echo "  --both       : Run Baseline then Stage 2 across all routes (default)"
            echo "  --base       : Run Baseline only"
            echo "  --stage2     : Run Stage 2 only"
            echo "  --pairwise   : Run Base then Stage 2 route-by-route"
            echo "  --force      : Re-evaluate routes even if completed results already exist"
            exit 0
            ;;
    esac
done

STAGE2_MODEL_PATH="/home/aimslab/checkpoints/action_experts/checkpoint-600"
BASE_MODEL_PATH="z-lab/Alpamayo-1.5-10B"

run_single_route() {
    local tag="$1"
    local model_path="$2"
    local route="$3"
    local route_id=$(basename "$route" .xml)

    mkdir -p "outputs/local_evaluation/${tag}_${route_id}"
    local log_file="outputs/local_evaluation/${tag}_${route_id}/eval.log"
    local ckpt_path="outputs/local_evaluation/${tag}_${route_id}/checkpoint_endpoint.json"
    local alt_ckpt="outputs/local_evaluation/alpamayo_${route_id}/checkpoint_endpoint.json"

    if [ "$FORCE" -eq 0 ]; then
        if [ -f "$ckpt_path" ]; then
            echo "[$tag] Existing completed run found for route $route_id ($ckpt_path). Skipping (use --force to re-run)."
            return 0
        elif [ "$tag" = "base" ] && [ -f "$alt_ckpt" ]; then
            echo "[$tag] Existing completed baseline run found for route $route_id ($alt_ckpt). Skipping (use --force to re-run)."
            return 0
        fi
    fi

    echo ""
    echo "----------------------------------------------------------"
    echo "[$tag] Starting Route: $route_id ($route)"
    echo "----------------------------------------------------------"

    # Kill any active server when switching routes/models to ensure fresh weights load
    rm -f "/tmp/alpamayo_flashdrive.sock"
    pkill -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 2

    MODEL_TAG="$tag" MODEL_PATH="$model_path" bash scripts/common/eval_alpamayo_b2d.sh "$route" > "$log_file" 2>&1 || {
        echo "[$tag] Route $route_id completed with return code $?."
    }

    echo "[$tag] Finished Route: $route_id"

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
}

if [ "$PAIRWISE" -eq 1 ]; then
    echo "=========================================================="
    echo "Starting Pairwise Route-by-Route Evaluation (Base then Stage 2)"
    echo "=========================================================="
    for route in "${ROUTES[@]}"; do
        run_single_route "base" "$BASE_MODEL_PATH" "$route"
        run_single_route "stage2" "$STAGE2_MODEL_PATH" "$route"
    done
else
    if [ "$MODE" = "base" ] || [ "$MODE" = "both" ]; then
        echo ""
        echo "=========================================================="
        echo "Starting Batch Evaluation for: Baseline (z-lab/Alpamayo-1.5-10B) (tag=base)"
        echo "=========================================================="
        for route in "${ROUTES[@]}"; do
            run_single_route "base" "$BASE_MODEL_PATH" "$route"
        done
    fi

    if [ "$MODE" = "stage2" ] || [ "$MODE" = "both" ]; then
        echo ""
        echo "=========================================================="
        echo "Starting Batch Evaluation for: Trained Pilot (Stage 2 checkpoint-600) (tag=stage2)"
        echo "=========================================================="
        for route in "${ROUTES[@]}"; do
            run_single_route "stage2" "$STAGE2_MODEL_PATH" "$route"
        done
    fi
fi

echo ""
echo "=========================================================="
echo "5 Stress-Test Abilities A/B Comparison: Base vs. Stage 2"
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
                if rec and "scores_mean" in rec and rec["scores_mean"]:
                    return rec.get("scores_mean", {}).get("score_route", 0.0), rec.get("scores_mean", {}).get("score_composed", 0.0), rec.get("status", "Unknown")
            except Exception:
                pass
    return None, None, "Not run"

h_route, h_cat, h_sc = "Route", "Ability Category", "Scenario Type"
h_b_pct, h_s2_pct = "Base %", "Stg2 %"
h_b_sc, h_s2_sc = "Base DS", "Stg2 DS"
h_diff = "Δ Score"

sep = "_" * 120
dash = "-"

print(sep)
print(f"| {h_route:<7} | {h_cat:<17} | {h_sc:<33} | {h_b_pct:<8} | {h_s2_pct:<8} | {h_b_sc:<8} | {h_s2_sc:<8} | {h_diff:<8} |")
print(f"|{dash*9}|{dash*19}|{dash*35}|{dash*10}|{dash*10}|{dash*10}|{dash*10}|{dash*10}|")

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
        
    print(f"| {r:<7} | {cat:<17} | {name:<33} | {b_pct_str:<8} | {s2_pct_str:<8} | {b_sc_str:<8} | {s2_sc_str:<8} | {diff_str:<8} |")

print(sep)
'
