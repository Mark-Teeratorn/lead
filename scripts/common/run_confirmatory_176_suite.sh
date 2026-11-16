#!/bin/bash
# ==============================================================================
# Pre-Specified Confirmatory 176-Route Suite Runner (Waves 1-4)
# ==============================================================================
# Evaluates the 176 unseen confirmatory routes (Bench2Drive 220 minus the 44
# exploratory canonical routes) across the 4 models required by H1, H2, H3:
#   - Golden-1600 (model_matrix_golden_1600) [finishing now]
#   - Base        (base)                     [H1 comparator]
#   - Golden-6400 (model_matrix_golden_6400) [H2 comparator]
#   - Flooded-6400(model_matrix_flooded_6400) [matched comparator; tag corrected 12 Nov 2026: "model_6400" is the historical checkpoint and must not receive Matrix-Flooded results]
#
# Routes are ordered into 4 scenario-balanced waves of 44 routes (1 unseen route
# per scenario type per wave). After every wave, evaluate_confirmatory_plan.py
# updates outputs/confirmatory_statistical_report.json.
# ==============================================================================

set -e
cd /home/aimslab/lead

LOG_FILE="outputs/confirmatory_176_suite_progress.log"
SOCK_PATH="/tmp/alpamayo_flashdrive.sock"
FLASHDRIVE_PYTHON="/home/aimslab/flashdrive/.venv/bin/python"

touch "$LOG_FILE"

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

server_is_alive() {
    [ -S "$SOCK_PATH" ] && python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(2); s.connect('$SOCK_PATH'); s.close()" 2>/dev/null
}

start_model_server() {
    local model_dir="$1"
    local label="$2"

    log "[ConfirmatoryRunner] Switching FlashDrive Server to: $label"
    rm -f "$SOCK_PATH"
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    sleep 3

    local model_arg=""
    if [ -n "$model_dir" ] && [ "$model_dir" != "BASE" ]; then
        model_arg="--model-path $model_dir"
    fi

    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    PYTORCH_ALLOC_CONF=expandable_segments:True \
    $FLASHDRIVE_PYTHON -u /home/aimslab/flashdrive/scripts/flashdrive_server.py \
        $model_arg \
        --socket-path "$SOCK_PATH" > "/tmp/flashdrive_server_${label}.log" 2>&1 &

    for i in $(seq 1 600); do
        if server_is_alive; then
            log "[ConfirmatoryRunner] Server ready for $label."
            return 0
        fi
        sleep 1
    done

    log "[ConfirmatoryRunner] ERROR: Server failed to start for $label."
    return 1
}

route_is_done() {
    local tag="$1"
    local rid="$2"
    local ckpt="outputs/local_evaluation/${tag}_${rid}/checkpoint_endpoint.json"
    [ -f "$ckpt" ] && grep -q '"score_composed"' "$ckpt" 2>/dev/null
}

# 1. Wait for active Golden-1600 220-route run to finish if still running
while pgrep -f "run_full_220_matrix_golden_1600.sh" >/dev/null || pgrep -f "watchdog_full_220_matrix_golden_1600.sh" >/dev/null; do
    G16_DONE=$(python3 -c "
import glob, json
c = 0
for p in glob.glob('outputs/local_evaluation/model_matrix_golden_1600_*/checkpoint_endpoint.json'):
    try:
        if json.load(open(p)).get('_checkpoint', {}).get('records'): c += 1
    except: pass
print(c)
")
    if [ "$G16_DONE" -ge 220 ]; then
        break
    fi
    log "[ConfirmatoryRunner $(date +%H:%M:%S)] Waiting for Golden-1600 to finish ($G16_DONE / 220)..."
    sleep 60
done

# 2. Generate the 4 scenario-balanced waves (44 routes per wave = 176 unseen routes)
mapfile -t WAVE_LINES < <(python3 - <<'E'
import json, xml.etree.ElementTree as ET

r44 = set(json.load(open('outputs/final_2x2_anova_matrix_report.json'))['per_route_scores'].keys())
tree = ET.parse('/home/aimslab/Bench2Drive/leaderboard/data/bench2drive220.xml')
by_sc = {}
for r in tree.getroot().findall('route'):
    rid = r.get('id')
    if rid in r44:
        continue
    sc = r.find('scenarios/scenario').get('type')
    by_sc.setdefault(sc, []).append(rid)

for wave_idx in range(4):
    wave_routes = []
    for sc in sorted(by_sc.keys()):
        if wave_idx < len(by_sc[sc]):
            wave_routes.append(by_sc[sc][wave_idx])
    print(" ".join(wave_routes))
E
)

MODELS_SPEC=(
    "base|BASE"
    "model_matrix_golden_6400|/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
    "model_matrix_flooded_6400|/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Flooded-6400-A15"
)

for w_idx in 0 1 2 3; do
    WAVE_NUM=$((w_idx + 1))
    read -r -a WAVE_ROUTES <<< "${WAVE_LINES[$w_idx]}"
    log "================================================================================"
    log "[ConfirmatoryRunner] Starting Confirmatory Wave $WAVE_NUM / 4 (${#WAVE_ROUTES[@]} unseen routes)"
    log "================================================================================"

    for mspec in "${MODELS_SPEC[@]}"; do
        IFS='|' read -r TAG MPATH <<< "$mspec"

        # Count how many routes in this wave still need to run for this model
        NEED_RUN=0
        for rid in "${WAVE_ROUTES[@]}"; do
            if ! route_is_done "$TAG" "$rid"; then
                NEED_RUN=$((NEED_RUN + 1))
            fi
        done

        if [ "$NEED_RUN" -eq 0 ]; then
            log "[Wave $WAVE_NUM] Model $TAG already completed all ${#WAVE_ROUTES[@]} routes in Wave $WAVE_NUM. Skipping."
            continue
        fi

        start_model_server "$MPATH" "$TAG"

        IDX=0
        for rid in "${WAVE_ROUTES[@]}"; do
            IDX=$((IDX + 1))
            if route_is_done "$TAG" "$rid"; then
                continue
            fi

            log "[Wave $WAVE_NUM | $TAG | $IDX/${#WAVE_ROUTES[@]}] Running Route $rid..."
            pkill -9 -f "CarlaUE4" 2>/dev/null || true
            pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
            sleep 2

            if ! server_is_alive; then
                start_model_server "$MPATH" "$TAG"
            fi

            MODEL_TAG="$TAG" \
            MODEL_PATH="$([ "$MPATH" = "BASE" ] && echo "" || echo "$MPATH")" \
            bash scripts/common/eval_alpamayo_b2d.sh "src/lead/routes/benchmark_routes/bench2drive/${rid}.xml" >> "$LOG_FILE" 2>&1 || {
                log "[Wave $WAVE_NUM | $TAG] Route $rid exited non-zero."
            }
        done
    done

    log "[ConfirmatoryRunner] Wave $WAVE_NUM complete! Updating statistical report..."
    python3 scripts/common/evaluate_confirmatory_plan.py | tee -a "$LOG_FILE"
done

log "================================================================================"
log "[ConfirmatoryRunner] All 4 Confirmatory Waves (176 unseen routes) Completed!"
log "================================================================================"

