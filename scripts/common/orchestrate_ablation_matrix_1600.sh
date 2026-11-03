#!/bin/bash
# ==============================================================================
# Master Orchestrator: 2x2 Factorial ANOVA Matrix Evaluation (Scale 1600)
# ==============================================================================
# Phase 1: Ensure all 44 routes of Alpamayo-1.5-10B-Matrix-Golden-1600-A15 complete.
# Phase 2: Safely extract and package Alpamayo-1.5-10B-Matrix-Flooded-1600-A15,
#          then run and supervise all 44 routes to completion.
# Phase 3: Compile and report the full 2x2 Factorial ANOVA matrix scorecard.
# ==============================================================================

set -euo pipefail
cd /home/aimslab/lead

ORCH_LOG="outputs/master_orchestrator_1600.log"
STATUS_FILE="outputs/orchestrator_status.txt"
mkdir -p outputs
touch "$ORCH_LOG"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$ORCH_LOG"
}

log "================================================================================"
log "Master Orchestrator Started: 2x2 Matrix 1600 Ablation Study"
log "================================================================================"

# Helper: Count completed checkpoints for a given prefix
count_completed() {
    local prefix="$1"
    python3 -c "
import glob, json
count = 0
for p in glob.glob('outputs/local_evaluation/${prefix}_*/checkpoint_endpoint.json'):
    try:
        with open(p) as f: d = json.load(f)
        if 'scores_mean' in d.get('_checkpoint', {}).get('global_record', {}):
            count += 1
    except Exception:
        pass
print(count)
" 2>/dev/null || echo "0"
}

# ------------------------------------------------------------------------------
# PHASE 1: Supervise Alpamayo-1.5-10B-Matrix-Golden-1600-A15
# ------------------------------------------------------------------------------
echo "PHASE_1_RUNNING" > "$STATUS_FILE"
log "--- PHASE 1: Monitoring Alpamayo-1.5-10B-Matrix-Golden-1600-A15 ---"

while true; do
    GOLDEN_DONE=$(count_completed "model_matrix_golden_1600")
    log "[Phase 1] Alpamayo-1.5-10B-Matrix-Golden-1600-A15 progress: $GOLDEN_DONE / 44 completed."

    if [ "$GOLDEN_DONE" -ge 44 ]; then
        log "[Phase 1] SUCCESS! All 44 routes completed for Alpamayo-1.5-10B-Matrix-Golden-1600-A15."
        break
    fi

    # Ensure watchdog supervisor is alive
    if ! pgrep -f "watchdog_full_44_matrix_golden_1600.sh" > /dev/null; then
        log "[Phase 1] Watchdog supervisor not running. Launching watchdog_full_44_matrix_golden_1600.sh..."
        nohup bash scripts/common/watchdog_full_44_matrix_golden_1600.sh >> outputs/watchdog_supervisor_matrix_golden_1600.log 2>&1 &
    fi

    sleep 60
done

# Stop Golden-1600 watchdog and runner cleanly
pkill -9 -f "watchdog_full_44_matrix_golden_1600.sh" 2>/dev/null || true
pkill -9 -f "run_full_44_matrix_golden_1600.sh" 2>/dev/null || true
pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 5

# ------------------------------------------------------------------------------
# PHASE 2: Prepare and Run Alpamayo-1.5-10B-Matrix-Flooded-1600-A15
# ------------------------------------------------------------------------------
echo "PHASE_2_PREPARING" > "$STATUS_FILE"
log "--- PHASE 2: Preparing Alpamayo-1.5-10B-Matrix-Flooded-1600-A15 ---"

FLOODED_TAR="/home/aimslab/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.tar.gz"
FLOODED_EXTRACT_DIR="/data/checkpoints/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15"
FLOODED_EXPERT_DIR="/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15"

# Step 2.1: Extract if not already extracted
if [ ! -d "$FLOODED_EXTRACT_DIR" ] || [ ! -f "$FLOODED_EXTRACT_DIR/model-00001-of-00005.safetensors" ]; then
    log "[Phase 2] Extracting $FLOODED_TAR into /data/checkpoints/ ..."
    mkdir -p /data/checkpoints
    tar -C /data/checkpoints/ -xzf "$FLOODED_TAR"
    log "[Phase 2] Extraction to /data/checkpoints/ complete."
    
    # Remove tarball from root to free 17.6 GB
    if [ -f "$FLOODED_TAR" ]; then
        rm -f "$FLOODED_TAR"
        log "[Phase 2] Removed root archive $FLOODED_TAR to reclaim disk space."
    fi
else
    log "[Phase 2] Full weights already present at $FLOODED_EXTRACT_DIR."
    if [ -f "$FLOODED_TAR" ]; then
        rm -f "$FLOODED_TAR"
        log "[Phase 2] Removed root archive $FLOODED_TAR to reclaim disk space."
    fi
fi

# Step 2.2: Extract Action Expert weights
if [ ! -f "$FLOODED_EXPERT_DIR/action_expert.safetensors" ]; then
    log "[Phase 2] Extracting Action Expert weights with extract_action_expert.py ..."
    mkdir -p "$FLOODED_EXPERT_DIR"
    /home/aimslab/lead/.venv/bin/python /home/aimslab/flashdrive/scripts/extract_action_expert.py \
        --checkpoint "$FLOODED_EXTRACT_DIR" \
        --output-dir "$FLOODED_EXPERT_DIR" \
        --overwrite
    log "[Phase 2] Action Expert packaging complete."
else
    log "[Phase 2] Action Expert package already exists at $FLOODED_EXPERT_DIR."
fi

# Step 2.3: Launch Flooded-1600 Watchdog Supervisor
echo "PHASE_2_RUNNING" > "$STATUS_FILE"
log "--- Launching Watchdog Supervisor for Alpamayo-1.5-10B-Matrix-Flooded-1600-A15 ---"

nohup bash scripts/common/watchdog_full_44_matrix_flooded_1600.sh >> outputs/watchdog_supervisor_matrix_flooded_1600.log 2>&1 &
FLOODED_WATCHDOG_PID=$!
log "[Phase 2] Launched watchdog_full_44_matrix_flooded_1600.sh with PID $FLOODED_WATCHDOG_PID"

while true; do
    FLOODED_DONE=$(count_completed "model_matrix_flooded_1600")
    log "[Phase 2] Alpamayo-1.5-10B-Matrix-Flooded-1600-A15 progress: $FLOODED_DONE / 44 completed."

    if [ "$FLOODED_DONE" -ge 44 ]; then
        log "[Phase 2] SUCCESS! All 44 routes completed for Alpamayo-1.5-10B-Matrix-Flooded-1600-A15."
        break
    fi

    # Ensure watchdog supervisor is alive
    if ! pgrep -f "watchdog_full_44_matrix_flooded_1600.sh" > /dev/null; then
        log "[Phase 2] Watchdog supervisor not running. Relaunching..."
        nohup bash scripts/common/watchdog_full_44_matrix_flooded_1600.sh >> outputs/watchdog_supervisor_matrix_flooded_1600.log 2>&1 &
    fi

    sleep 60
done

# Clean up Phase 2 processes
pkill -9 -f "watchdog_full_44_matrix_flooded_1600.sh" 2>/dev/null || true
pkill -9 -f "run_full_44_matrix_flooded_1600.sh" 2>/dev/null || true
pkill -9 -f "leaderboard_evaluator.py" 2>/dev/null || true
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 5

# ------------------------------------------------------------------------------
# PHASE 3: Compile Complete 2x2 Factorial ANOVA Scorecard
# ------------------------------------------------------------------------------
echo "PHASE_3_COMPILING" > "$STATUS_FILE"
log "--- PHASE 3: Compiling 2x2 Factorial ANOVA Matrix Scorecard ---"

python3 -c "
import glob, json, re, os

canonical_44 = [
    '2534', '1852', '2204', '2513', '1825', '3561', '3086', '17752', '2201', '3540',
    '1790', '3436', '2286', '23687', '23901', '23695', '2790', '2283', '23771', '2084',
    '28087', '2115', '2082', '2127', '1773', '2664', '3248', '1711', '1956', '14194',
    '17563', '3936', '28099', '2050', '2709', '26458', '2390', '2416', '14842', '3144',
    '3464', '2144', '2164', '3364'
]

models = [
    ('Scale 1600 Flooded', 'model_matrix_flooded_1600', 'Alpamayo-1.5-10B-Matrix-Flooded-1600-A15'),
    ('Scale 1600 Golden',  'model_matrix_golden_1600',  'Alpamayo-1.5-10B-Matrix-Golden-1600-A15'),
    ('Scale 6400 Flooded', 'model_6400',                'checkpoint-6400'),
    ('Scale 6400 Golden',  'model_v4_final',            'checkpoint-20050')
]

def load_model_results(prefix):
    res = {}
    for r in canonical_44:
        p = f'outputs/local_evaluation/{prefix}_{r}/checkpoint_endpoint.json'
        if os.path.exists(p):
            try:
                with open(p) as f: d = json.load(f)
                recs = d.get('_checkpoint', {}).get('records', [])
                if recs and 'scores' in recs[0]:
                    inf = recs[0].get('infractions', {})
                    crashes = len(inf.get('collisions_layout', [])) + len(inf.get('collisions_vehicle', [])) + len(inf.get('collisions_pedestrian', []))
                    res[r] = {
                        'ds': recs[0]['scores']['score_composed'],
                        'rc': recs[0]['scores']['score_route'],
                        'status': recs[0].get('status', 'Unknown'),
                        'crashes': crashes
                    }
            except Exception:
                pass
    return res

report = {}
for label, prefix, full_name in models:
    data = load_model_results(prefix)
    n = len(data)
    mean_ds = sum(d['ds'] for d in data.values()) / n if n > 0 else 0
    mean_rc = sum(d['rc'] for d in data.values()) / n if n > 0 else 0
    succ = sum(1 for d in data.values() if d['status'] == 'Completed')
    crashes = sum(d['crashes'] for d in data.values())
    report[full_name] = {
        'label': label,
        'prefix': prefix,
        'evaluated_routes': n,
        'mean_ds': round(mean_ds, 2),
        'mean_rc': round(mean_rc, 2),
        'success_rate_pct': round((succ / n * 100), 1) if n > 0 else 0,
        'total_crashes': crashes,
        'per_route': data
    }

with open('outputs/final_2x2_anova_matrix_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('=' * 80)
print('FINAL 2x2 FACTORIAL ANOVA MATRIX SCORECARD (44 Bench2Drive Routes)')
print('=' * 80)
print(f\"{'Condition':<22} | {'Checkpoint Name':<42} | {'DS':<6} | {'RC':<6} | {'SR %':<6} | {'Crashes':<7}\")
print('-' * 98)
for label, prefix, full_name in models:
    m = report[full_name]
    print(f\"{m['label']:<22} | {full_name:<42} | {m['mean_ds']:<6.2f} | {m['mean_rc']:<6.2f} | {m['success_rate_pct']:<6.1f} | {m['total_crashes']:<7}\")
print('=' * 80)
" | tee -a "$ORCH_LOG"

echo "ORCHESTRATION_COMPLETE" > "$STATUS_FILE"
log "Master Orchestrator finished successfully at $(date)."
