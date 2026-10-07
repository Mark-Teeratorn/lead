#!/bin/bash
# ==============================================================================
# Bench2Drive 44 Canonical Scenarios Batch Evaluation
# ==============================================================================
# Evaluates an Action Expert model (or Baseline) across all 44 Bench2Drive
# scenario types, covering all 5 core driving abilities:
#   - Merging (16 scenarios)
#   - Emergency Brake (12 scenarios)
#   - Overtaking (9 scenarios)
#   - Give Way (2 scenarios)
#   - Traffic Signs (19 scenarios)
#
# Usage:
#   bash scripts/common/eval_batch_44scenarios.sh [MODEL] [OPTIONS]
#
# Model Shortcuts:
#   1           : Action Model 1 (/home/aimslab/checkpoints/action_experts/action_model_1)
#   2           : Action Model 2 (/home/aimslab/checkpoints/action_experts/action_model_2)
#   3           : Action Model 3 (/home/aimslab/checkpoints/action_experts/action_model_3)
#   4           : Action Model 4 EMA (/home/aimslab/checkpoints/action_experts/action_model_4_ema)
#   /path/to/.. : Any custom action model checkpoint directory
#
# Options:
#   --force        : Re-evaluate routes even if completed results already exist
#   --gui          : Launch CARLA with spectator visual window
#   --with-base    : Also evaluate Baseline (Alpamayo 1.5) on routes lacking baseline runs
#   --base-only    : Evaluate Baseline only across all 44 scenarios
#   --scenario <X> : Run only a specific scenario name (e.g. --scenario Accident)
#   --start-from <N>: Start evaluation from scenario index N (1-44)
#   --summary-only : Display current scorecard and statistics without running CARLA
#   --all-220      : Run all 220 routes (5 routes per scenario) instead of 44 canonical
#
# Examples:
#   bash scripts/common/eval_batch_44scenarios.sh 3
#   bash scripts/common/eval_batch_44scenarios.sh 4 --gui
#   bash scripts/common/eval_batch_44scenarios.sh 3 --summary-only
#   bash scripts/common/eval_batch_44scenarios.sh 3 --scenario Accident
# ==============================================================================

set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

# 44 Canonical routes (1 per scenario type):
# Format: "SCENARIO_NAME:ROUTE_ID:ABILITY_CATEGORY"
SCENARIO_DEFS=(
    "Accident:2534:Overtaking"
    "AccidentTwoWays:1852:Overtaking"
    "BlockedIntersection:2204:Emergency_Brake,Traffic_Signs"
    "ConstructionObstacle:2513:Overtaking"
    "ConstructionObstacleTwoWays:1825:Overtaking"
    "ControlLoss:3561:Emergency_Brake"
    "CrossingBicycleFlow:3086:Merging,Traffic_Signs"
    "DynamicObjectCrossing:17752:Emergency_Brake"
    "EnterActorFlow:2201:Merging,Traffic_Signs"
    "HardBreakRoute:3540:Emergency_Brake"
    "HazardAtSideLane:1790:Overtaking"
    "HazardAtSideLaneTwoWays:3436:Overtaking"
    "HighwayCutIn:2286:Merging"
    "HighwayExit:23687:Merging"
    "InterurbanActorFlow:23901:Merging"
    "InterurbanAdvancedActorFlow:23695:Merging"
    "InvadingTurn:2790:Give_Way"
    "MergerIntoSlowTraffic:2283:Merging"
    "MergerIntoSlowTrafficV2:23771:Merging"
    "NonSignalizedJunctionLeftTurn:2084:Merging,Traffic_Signs"
    "NonSignalizedJunctionLeftTurnEnterFlow:28087:Merging,Traffic_Signs"
    "NonSignalizedJunctionRightTurn:2115:Merging,Traffic_Signs"
    "OppositeVehicleRunningRedLight:2082:Emergency_Brake,Traffic_Signs"
    "OppositeVehicleTakingPriority:2127:Emergency_Brake,Traffic_Signs"
    "ParkedObstacle:1773:Overtaking"
    "ParkedObstacleTwoWays:2664:Overtaking"
    "ParkingCrossingPedestrian:3248:Emergency_Brake"
    "ParkingCutIn:1711:Emergency_Brake"
    "ParkingExit:1956:Merging"
    "PedestrianCrossing:14194:Emergency_Brake,Traffic_Signs"
    "SequentialLaneChange:17563:Merging"
    "SignalizedJunctionLeftTurn:3936:Merging,Traffic_Signs"
    "SignalizedJunctionLeftTurnEnterFlow:28099:Merging,Traffic_Signs"
    "SignalizedJunctionRightTurn:2050:Merging,Traffic_Signs"
    "StaticCutIn:2709:Emergency_Brake"
    "T_Junction:26458:Traffic_Signs"
    "VanillaNonSignalizedTurn:2390:Traffic_Signs"
    "VanillaNonSignalizedTurnEncounterStopsign:2416:Traffic_Signs"
    "VanillaSignalizedTurnEncounterGreenLight:14842:Traffic_Signs"
    "VanillaSignalizedTurnEncounterRedLight:3144:Traffic_Signs"
    "VehicleOpensDoorTwoWays:3464:Overtaking"
    "VehicleTurningRoute:2144:Emergency_Brake,Traffic_Signs"
    "VehicleTurningRoutePedestrian:2164:Emergency_Brake,Traffic_Signs"
    "YieldToEmergencyVehicle:3364:Give_Way"
)

BASE_MODEL_PATH="z-lab/Alpamayo-1.5-10B"

# Defaults
TARGET_INPUT="${MODEL_PATH:-/home/aimslab/checkpoints/action_experts/action_model_3}"
FORCE=0
GUI_FLAG=""
RUN_BASE=0
BASE_ONLY=0
FILTER_SCENARIO=""
START_INDEX=1
SUMMARY_ONLY=0
ALL_220=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force)
            FORCE=1
            shift
            ;;
        --gui)
            GUI_FLAG="--gui"
            shift
            ;;
        --with-base|--both)
            RUN_BASE=1
            shift
            ;;
        --base-only|--base)
            BASE_ONLY=1
            RUN_BASE=1
            shift
            ;;
        --summary-only|--summary)
            SUMMARY_ONLY=1
            shift
            ;;
        --all-220|--full)
            ALL_220=1
            shift
            ;;
        --scenario)
            FILTER_SCENARIO="$2"
            shift 2
            ;;
        --start-from)
            START_INDEX="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [MODEL] [OPTIONS]"
            echo ""
            echo "Evaluates action expert models across all 44 Bench2Drive canonical scenarios."
            echo ""
            echo "Model shortcuts:"
            echo "  1                 : Action Model 1 (checkpoint-600)"
            echo "  2                 : Action Model 2 (checkpoint-640)"
            echo "  3                 : Action Model 3 (checkpoint-600-3) [default]"
            echo "  4                 : Action Model 4 EMA (checkpoint-1730)"
            echo "  /path/to/model    : Path to custom action expert checkpoint"
            echo ""
            echo "Options:"
            echo "  --force           : Re-evaluate routes even if results exist"
            echo "  --gui             : Launch CARLA with spectator visual window"
            echo "  --with-base       : Also evaluate Baseline on missing routes"
            echo "  --base-only       : Evaluate Baseline only"
            echo "  --scenario <NAME> : Evaluate only specified scenario (e.g. Accident)"
            echo "  --start-from <N>  : Start from scenario index N (1-44)"
            echo "  --summary-only    : View current scorecard without running tests"
            echo "  --all-220         : Run all 220 routes (5 routes per scenario)"
            exit 0
            ;;
        *)
            if [ -e "$1" ] || [ -e "/home/aimslab/checkpoints/action_experts/$1" ]; then
                if [ -e "/home/aimslab/checkpoints/action_experts/$1" ] && [ ! -e "$1" ]; then
                    TARGET_INPUT="/home/aimslab/checkpoints/action_experts/$1"
                else
                    TARGET_INPUT="$1"
                fi
            elif [ "$1" = "1" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_1"
            elif [ "$1" = "2" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_2"
            elif [ "$1" = "3" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_3"
            elif [ "$1" = "4" ] || [ "$1" = "4_nonema" ] || [ "$1" = "nonema" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4"
            elif [ "$1" = "4_ema" ] || [ "$1" = "ema" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4_ema"
            elif [ "$1" = "1730" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/action_model_4"
            elif [ "$1" = "5" ] || [ "$1" = "6400" ] || [ "$1" = "checkpoint-6400" ]; then
                TARGET_INPUT="/home/aimslab/checkpoints/action_experts/checkpoint-6400"
            else
                echo "Warning: unrecognized argument '$1', ignoring."
            fi
            shift
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
    checkpoint-6400*|*6400*)
        MODEL_TAG="model_6400"
        MODEL_LABEL="Action Model v3 (Ckpt 6400)"
        ;;
    *)
        MODEL_TAG="${MODEL_TAG:-$MODEL_NAME}"
        MODEL_LABEL="$MODEL_NAME"
        ;;
esac

# Cleanup helper
cleanup() {
    rm -f "/tmp/alpamayo_flashdrive.sock"
    pkill -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
}

run_single_route() {
    local tag="$1"
    local model_path="$2"
    local route="$3"
    local route_id=$(basename "$route" .xml)
    local sc_name="$4"

    mkdir -p "outputs/local_evaluation/${tag}_${route_id}"
    local log_file="outputs/local_evaluation/${tag}_${route_id}/eval.log"
    local ckpt_path="outputs/local_evaluation/${tag}_${route_id}/checkpoint_endpoint.json"
    local alt_ckpt="outputs/local_evaluation/alpamayo_${route_id}/checkpoint_endpoint.json"

    if [ "$FORCE" -eq 0 ]; then
        if [ -f "$ckpt_path" ] && grep -q '"scores_mean"' "$ckpt_path" 2>/dev/null; then
            echo "[$tag] Existing completed run found for $sc_name (route $route_id). Skipping (use --force to re-run)."
            return 0
        elif [ "$tag" = "base" ] && [ -f "$alt_ckpt" ] && grep -q '"scores_mean"' "$alt_ckpt" 2>/dev/null; then
            echo "[$tag] Existing completed baseline run found for $sc_name (route $route_id). Reusing existing score."
            return 0
        fi
    fi

    echo ""
    echo "=========================================================="
    echo "[$tag] Starting Scenario: $sc_name | Route: $route_id"
    echo "=========================================================="

    cleanup
    sleep 2

    local model_arg=""
    if [ -n "$model_path" ] && [ "$model_path" != "$BASE_MODEL_PATH" ]; then
        model_arg="$model_path"
    fi

    MODEL_TAG="$tag" MODEL_PATH="$model_arg" bash scripts/common/eval_alpamayo_b2d.sh "$route" $GUI_FLAG > "$log_file" 2>&1 || {
        echo "[$tag] Route $route_id completed with return code $?."
    }

    echo "[$tag] Finished Route: $route_id ($sc_name)"

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
    print(f"  --> Result: Comp = {score_route:.1f}%, DS = {score_composed:.1f}, Status = {status}")
except Exception as e:
    print(f"  --> Error reading result: {e}")
' "$ckpt_path"
    fi

    cleanup
    sleep 2
}

# Scorecard display function
print_scorecard() {
    python3 -c '
import json, os, sys

target_tag = sys.argv[1]
target_label = sys.argv[2]
scenario_defs = sys.argv[3].split(";")

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
    return None, None, "Pending"

print("")
print("=" * 122)
print(f"               BENCH2DRIVE 44 SCENARIOS SCORECARD: BASELINE vs. {target_label}")
print("=" * 122)

h_idx, h_sc, h_r, h_cat = "#", "Scenario Type", "Route", "Primary Ability"
h_b_pct = "Base %"
h_t_pct = f"{target_label[:6]} %"
h_b_sc = "Base DS"
h_t_sc = f"{target_label[:6]} DS"
h_diff = "Δ Score"
h_stat = "Status"

sep = "-" * 122
print(sep)
print(f"| {h_idx:<2} | {h_sc:<38} | {h_r:<5} | {h_cat:<16} | {h_b_sc:<8} | {h_t_pct:<8} | {h_t_sc:<8} | {h_diff:<8} | {h_stat:<10} |")
print(sep)

completed_count = 0
total_routes = len(scenario_defs)
t_ds_list = []
t_pct_list = []
b_ds_list = []

ability_scores = {
    "Overtaking": [],
    "Merging": [],
    "Emergency_Brake": [],
    "Give_Way": [],
    "Traffic_Signs": []
}

for i, item in enumerate(scenario_defs, 1):
    parts = item.split(":")
    sc_name, r, abilities = parts[0], parts[1], parts[2]
    primary_ability = abilities.split(",")[0]

    b_pct, b_sc, _ = get_stats("base", r)
    t_pct, t_sc, t_stat = get_stats(target_tag, r)

    b_sc_str = f"{b_sc:>8.1f}" if b_sc is not None else "Pending"
    t_pct_str = f"{t_pct:>6.1f} %" if t_pct is not None else "Pending"
    t_sc_str = f"{t_sc:>8.1f}" if t_sc is not None else "Pending"

    if t_sc is not None:
        completed_count += 1
        t_ds_list.append(t_sc)
        t_pct_list.append(t_pct)
        for ab in abilities.split(","):
            if ab in ability_scores:
                ability_scores[ab].append(t_sc)

    if b_sc is not None:
        b_ds_list.append(b_sc)

    if b_sc is not None and t_sc is not None:
        diff = t_sc - b_sc
        diff_str = f"{diff:>+8.1f}"
    else:
        diff_str = "    --  "

    stat_disp = t_stat[:10] if t_stat != "Pending" else "--"
    print(f"| {i:<2} | {sc_name:<38} | {r:<5} | {primary_ability:<16} | {b_sc_str:<8} | {t_pct_str:<8} | {t_sc_str:<8} | {diff_str:<8} | {stat_disp:<10} |")

print(sep)

# Aggregate Summary
avg_t_ds = sum(t_ds_list) / len(t_ds_list) if t_ds_list else 0.0
avg_t_pct = sum(t_pct_list) / len(t_pct_list) if t_pct_list else 0.0
avg_b_ds = sum(b_ds_list) / len(b_ds_list) if b_ds_list else 0.0

print(f"\n[SUMMARY] Progress: {completed_count}/{total_routes} completed")
if t_ds_list:
    print(f"  • {target_label} Average Driving Score (DS): {avg_t_ds:.1f}")
    print(f"  • {target_label} Average Route Completion:   {avg_t_pct:.1f}%")
if b_ds_list:
    print(f"  • Baseline Average Driving Score (DS):        {avg_b_ds:.1f} (across {len(b_ds_list)} routes)")

print("\n[ABILITY BREAKDOWN for " + target_label + "]")
for ab, sc_list in ability_scores.items():
    if sc_list:
        ab_avg = sum(sc_list) / len(sc_list)
        print(f"  • {ab:<17}: {ab_avg:>5.1f} DS  ({len(sc_list)} scenarios tested)")
    else:
        print(f"  • {ab:<17}: Pending")
print("=" * 122)
' "$MODEL_TAG" "$MODEL_LABEL" "$(IFS=';'; echo "${SCENARIO_DEFS[*]}")"
}

# If summary only requested, print table and exit
if [ "$SUMMARY_ONLY" -eq 1 ]; then
    print_scorecard
    exit 0
fi

trap cleanup EXIT INT TERM

# Build routes to run
ROUTES_TO_RUN=()
SCENARIO_NAMES=()

if [ "$ALL_220" -eq 1 ]; then
    echo "[Info] Full 220 routes mode enabled. Locating all routes..."
    # Parse 220 routes from bench2drive220.xml
    while IFS= read -r line; do
        ROUTES_TO_RUN+=("$line")
        SCENARIO_NAMES+=("$(basename "$line" .xml)")
    done < <(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('/home/aimslab/Bench2Drive/leaderboard/data/bench2drive220.xml')
for r in tree.getroot().findall('route'):
    rid = r.get('id')
    print(f'src/lead/routes/benchmark_routes/bench2drive/{rid}.xml')
")
else
    # 44 Canonical Scenarios
    for item in "${SCENARIO_DEFS[@]}"; do
        IFS=':' read -r sc_name rid cat <<< "$item"
        if [ -n "$FILTER_SCENARIO" ] && [ "$sc_name" != "$FILTER_SCENARIO" ]; then
            continue
        fi
        ROUTES_TO_RUN+=("src/lead/routes/benchmark_routes/bench2drive/${rid}.xml")
        SCENARIO_NAMES+=("$sc_name")
    done
fi

TOTAL_SCENARIOS=${#ROUTES_TO_RUN[@]}

echo ""
echo "=========================================================="
echo "   BENCH2DRIVE 44 SCENARIOS EVALUATION"
echo "=========================================================="
echo "Target Model:   $MODEL_LABEL"
echo "Model Path:    $MODEL_PATH"
echo "Total Scenarios to Evaluate: $TOTAL_SCENARIOS"
echo "Starting Index: $START_INDEX"
echo "Force Re-run:  $FORCE"
echo "GUI Mode:      ${GUI_FLAG:-Off (Headless)}"
echo "Run Baseline:  $RUN_BASE"
echo "=========================================================="

# 1. Run Baseline if requested
if [ "$RUN_BASE" -eq 1 ]; then
    echo ""
    echo "=========================================================="
    echo ">>> Running Baseline (z-lab/Alpamayo-1.5-10B)"
    echo "=========================================================="
    for i in "${!ROUTES_TO_RUN[@]}"; do
        idx=$((i + 1))
        if [ "$idx" -lt "$START_INDEX" ]; then
            continue
        fi
        route="${ROUTES_TO_RUN[$i]}"
        sc_name="${SCENARIO_NAMES[$i]}"
        echo "[$idx/$TOTAL_SCENARIOS] Baseline: $sc_name"
        run_single_route "base" "$BASE_MODEL_PATH" "$route" "$sc_name"
    done
fi

# 2. Run Target Model (unless base-only)
if [ "$BASE_ONLY" -eq 0 ]; then
    echo ""
    echo "=========================================================="
    echo ">>> Running Target Model: $MODEL_LABEL"
    echo "=========================================================="
    for i in "${!ROUTES_TO_RUN[@]}"; do
        idx=$((i + 1))
        if [ "$idx" -lt "$START_INDEX" ]; then
            continue
        fi
        route="${ROUTES_TO_RUN[$i]}"
        sc_name="${SCENARIO_NAMES[$i]}"
        echo "[$idx/$TOTAL_SCENARIOS] $MODEL_LABEL: $sc_name"
        run_single_route "$MODEL_TAG" "$MODEL_PATH" "$route" "$sc_name"
    done
fi

# 3. Print Final Scorecard
print_scorecard
