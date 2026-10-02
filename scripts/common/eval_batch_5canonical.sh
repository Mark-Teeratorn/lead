#!/bin/bash
# ==============================================================================
# 5 Canonical Bench2Drive Benchmark: Baseline vs. Selected Model (by Path)
# ==============================================================================
# Evaluates Baseline (Alpamayo 1.5) vs. any selected Action Expert model
# across the 5 canonical benchmark routes:
#   1. Merging: Route 23687 (HighwayExit)
#   2. Emergency Brake: Route 14194 (PedestrianCrossing)
#   3. Overtaking: Route 2513 (ConstructionObstacle)
#   4. Give Way: Route 2790 (InvadingTurn)
#   5. Traffic Signs: Route 3144 (VanillaSignalizedTurnEncounterRedLight)
#
# Usage:
#   bash scripts/common/eval_batch_5canonical.sh [PATH_TO_MODEL] [--force] [--gui]
#
# Examples:
#   # 1. Test Action Model 2 (Default):
#   bash scripts/common/eval_batch_5canonical.sh /home/aimslab/checkpoints/action_experts/action_model_2
#   # (or simply: bash scripts/common/eval_batch_5canonical.sh)
#
#   # 2. Test Action Model 1:
#   bash scripts/common/eval_batch_5canonical.sh /home/aimslab/checkpoints/action_experts/action_model_1
#
#   # 3. Via environment variable:
#   MODEL_PATH="/home/aimslab/checkpoints/action_experts/action_model_2" bash scripts/common/eval_batch_5canonical.sh
# ==============================================================================

set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

ROUTES=(
    "src/lead/routes/benchmark_routes/bench2drive/23687.xml"
    "src/lead/routes/benchmark_routes/bench2drive/14194.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2513.xml"
    "src/lead/routes/benchmark_routes/bench2drive/2790.xml"
    "src/lead/routes/benchmark_routes/bench2drive/3144.xml"
)

BASE_MODEL_PATH="z-lab/Alpamayo-1.5-10B"

# Default target is action_model_2 unless specified
TARGET_INPUT="${MODEL_PATH:-/home/aimslab/checkpoints/action_experts/action_model_2}"
FORCE=0
GUI_FLAG=""

for arg in "$@"; do
    case "$arg" in
        --force)
            FORCE=1
            ;;
        --gui)
            GUI_FLAG="--gui"
            ;;
        --help|-h)
            echo "Usage: $0 [PATH_TO_MODEL] [--force] [--gui]"
            echo ""
            echo "Always compares Baseline vs. Selected Model across all 5 canonical routes."
            echo ""
            echo "Arguments:"
            echo "  PATH_TO_MODEL : Path to action expert directory (defaults to action_model_2)"
            echo "  --force       : Re-evaluate routes even if completed results already exist"
            echo "  --gui         : Launch with CARLA spectator visual window"
            echo ""
            echo "Examples:"
            echo "  $0 /home/aimslab/checkpoints/action_experts/action_model_2"
            echo "  $0 /home/aimslab/checkpoints/action_experts/action_model_1"
            echo "  $0"
            exit 0
            ;;
        *)
            if [ -e "$arg" ] || [ -e "/home/aimslab/checkpoints/action_experts/$arg" ]; then
                if [ -e "/home/aimslab/checkpoints/action_experts/$arg" ] && [ ! -e "$arg" ]; then
                    TARGET_INPUT="/home/aimslab/checkpoints/action_experts/$arg"
                else
                    TARGET_INPUT="$arg"
                fi
            elif [ "$arg" = "1" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_1"
            elif [ "$arg" = "2" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_2"
            elif [ "$arg" = "3" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_3"
            elif [ "$arg" = "4" ] || [ "$arg" = "4_nonema" ] || [ "$arg" = "nonema" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4"
            elif [ "$arg" = "4_ema" ] || [ "$arg" = "ema" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4_ema"
            elif [ "$arg" = "1730" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4"
            else
                echo "Warning: unrecognized argument '$arg', ignoring."
            fi
            ;;
    esac
done

MODEL_PATH="$(realpath "$TARGET_INPUT" 2>/dev/null || echo "$TARGET_INPUT")"
MODEL_NAME="$(basename "$MODEL_PATH")"

# Derive clean evaluation tag & label
case "$MODEL_NAME" in
    action_model_1|checkpoint-600)
        MODEL_TAG="stage2"
        MODEL_LABEL="Action Model 1 (Ckpt 600)"
        ;;
    action_model_2|checkpoint-640)
        MODEL_TAG="model2"
        MODEL_LABEL="Action Model 2 (Ckpt 640)"
        ;;
    action_model_3|checkpoint-600\(3\)|checkpoint-600_3)
        MODEL_TAG="model3"
        MODEL_LABEL="Action Model 3 (Ckpt 600-3)"
        ;;
    action_model_4_ema)
        MODEL_TAG="model4_ema"
        MODEL_LABEL="Action Model 4 EMA (Ckpt 1730)"
        ;;
    action_model_4|action_model_4_nonema)
        MODEL_TAG="model4_nonema"
        MODEL_LABEL="Action Model 4 (Ckpt 1730 Non-EMA)"
        ;;
    action_model_4*|checkpoint-1730*|*1730*)
        MODEL_TAG="model4_nonema"
        MODEL_LABEL="Action Model 4 (Ckpt 1730)"
        ;;
    *)
        MODEL_TAG="${MODEL_TAG:-$MODEL_NAME}"
        MODEL_LABEL="$MODEL_NAME"
        ;;
esac

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
            echo "[$tag] Existing completed baseline run found for route $route_id ($alt_ckpt). Reusing existing score."
            return 0
        fi
    fi

    echo ""
    echo "----------------------------------------------------------"
    echo "[$tag] Starting Route: $route_id ($route)"
    echo "----------------------------------------------------------"

    # Reset any lingering server sockets and CARLA instances
    rm -f "/tmp/alpamayo_flashdrive.sock"
    pkill -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 2

    local model_arg=""
    if [ -n "$model_path" ] && [ "$model_path" != "$BASE_MODEL_PATH" ]; then
        model_arg="$model_path"
    fi

    MODEL_TAG="$tag" MODEL_PATH="$model_arg" bash scripts/common/eval_alpamayo_b2d.sh "$route" $GUI_FLAG > "$log_file" 2>&1 || {
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
    print(f"  [{sys.argv[3]}] Route {sys.argv[2]}: Route Comp = {score_route:.1f}%, Driving Score = {score_composed:.1f}, Status = {status}")
except Exception as e:
    print(f"  [{sys.argv[3]}] Error parsing checkpoint: {e}")
' "$ckpt_path" "$route_id" "$tag"
    fi

    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 2
}

# 1. Run Baseline (reuses existing results if already completed)
echo ""
echo "=========================================================="
echo "Batch Evaluation: Baseline (z-lab/Alpamayo-1.5-10B)"
echo "=========================================================="
for route in "${ROUTES[@]}"; do
    run_single_route "base" "$BASE_MODEL_PATH" "$route"
done

# 2. Run Selected Model
echo ""
echo "=========================================================="
echo "Batch Evaluation: $MODEL_LABEL"
echo "Model Path:       $MODEL_PATH"
echo "=========================================================="
for route in "${ROUTES[@]}"; do
    run_single_route "$MODEL_TAG" "$MODEL_PATH" "$route"
done

# 3. Print Side-by-Side Comparison Scorecard
echo ""
echo "==================================================================================================="
echo "              5 CANONICAL ABILITIES SCORECARD: BASELINE vs. $MODEL_LABEL"
echo "==================================================================================================="

python3 -c '
import json, os, sys

target_tag = sys.argv[1]
target_label = sys.argv[2]

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
                if rec and "scores_mean" in rec and rec["scores_mean"]:
                    return rec.get("scores_mean", {}).get("score_route", 0.0), rec.get("scores_mean", {}).get("score_composed", 0.0), rec.get("status", "Unknown")
            except Exception:
                pass
    return None, None, "Not run"

h_route, h_cat, h_sc = "Route", "Ability Category", "Scenario Type"
h_b_pct = "Base %"
h_t_pct = f"{target_label[:6]} %"
h_b_sc = "Base DS"
h_t_sc = f"{target_label[:6]} DS"
h_diff = "Δ Score"

sep = "-" * 115
print(sep)
print(f"| {h_route:<7} | {h_cat:<17} | {h_sc:<28} | {h_b_pct:<8} | {h_t_pct:<8} | {h_b_sc:<8} | {h_t_sc:<8} | {h_diff:<8} |")
print(sep)

for r in routes:
    cat, name = categories[r]
    b_pct, b_sc, _ = get_stats("base", r)
    t_pct, t_sc, _ = get_stats(target_tag, r)
    
    b_pct_str = f"{b_pct:>6.1f} %" if b_pct is not None else "Pending"
    t_pct_str = f"{t_pct:>6.1f} %" if t_pct is not None else "Pending"
    b_sc_str = f"{b_sc:>8.1f}" if b_sc is not None else "Pending"
    t_sc_str = f"{t_sc:>8.1f}" if t_sc is not None else "Pending"
    
    if b_sc is not None and t_sc is not None:
        diff = t_sc - b_sc
        diff_str = f"{diff:>+8.1f}"
    else:
        diff_str = "    --  "
        
    print(f"| {r:<7} | {cat:<17} | {name:<28} | {b_pct_str:<8} | {t_pct_str:<8} | {b_sc_str:<8} | {t_sc_str:<8} | {diff_str:<8} |")

print(sep)
' "$MODEL_TAG" "$MODEL_LABEL"
