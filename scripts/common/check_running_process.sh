#!/bin/bash
# ==============================================================================
# Bench2Drive / Alpamayo Evaluation Process & Status Monitor
# ==============================================================================
# Displays:
#   1. GPU utilization, VRAM, and temperature (via nvidia-smi)
#   2. Active CARLA & FlashDrive server processes
#   3. Current batch evaluation script & active route
#   4. Live log tail of the active evaluation
#   5. Results of already completed routes in the current run
#
# Usage:
#   bash scripts/common/check_running_process.sh           # Single status snapshot
#   bash scripts/common/check_running_process.sh --watch   # Live refresh every 3s
# ==============================================================================

cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

WATCH_MODE=0
if [ "$1" = "--watch" ] || [ "$1" = "-w" ]; then
    WATCH_MODE=1
fi

display_status() {
    clear 2>/dev/null || echo "=================================================="
    echo "=================================================================================="
    echo "            BENCH2DRIVE & CARLA EVALUATION PROCESS MONITOR"
    echo "                           $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================================================="

    # 1. GPU Status
    echo ""
    echo "-------------------------------- [ 1. GPU STATUS ] -------------------------------"
    if command -v nvidia-smi >/dev/null 2>&1; then
        nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader | \
            awk -F', ' '{printf "GPU #%s: %s | Util: %-4s | VRAM: %s / %s | Temp: %-3s | Power: %s\n", $1, $2, $3, $4, $5, $6, $7}'
    else
        echo "nvidia-smi not available."
    fi

    # 2. Active Processes
    echo ""
    echo "--------------------------- [ 2. EVALUATION PROCESSES ] --------------------------"
    printf "%-8s %-6s %-6s %-8s %s\n" "PID" "%CPU" "%MEM" "ELAPSED" "PROCESS"
    echo "----------------------------------------------------------------------------------"
    
    ps -eo pid,pcpu,pmem,etime,cmd | grep -E "eval_batch_|eval_alpamayo_|leaderboard_evaluator|flashdrive_server|CarlaUE4" | grep -v grep | while read -r pid pcpu pmem etime cmd; do
        pname="Unknown"
        case "$cmd" in
            *eval_batch_5canonical.sh*) pname="[Batch 5 Canonical Script]" ;;
            *eval_batch_44scenarios.sh*) pname="[Batch 44 Scenarios Script]" ;;
            *eval_alpamayo_b2d.sh*)    pname="[Route Runner Script]" ;;
            *leaderboard_evaluator.py*) pname="[Leaderboard Evaluator]" ;;
            *flashdrive_server.py*)    pname="[FlashDrive Model Server]" ;;
            *CarlaUE4*)                 pname="[CARLA UE4 Simulator]" ;;
            *)                          pname="[$(echo "$cmd" | awk '{print $1}')]" ;;
        esac
        printf "%-8s %-6s %-6s %-8s %-32s\n" "$pid" "$pcpu" "$pmem" "$etime" "$pname"
    done

    # 3. Current Route & Active Log
    echo ""
    echo "--------------------------- [ 3. CURRENT ACTIVE ROUTE ] --------------------------"
    
    # Locate most recently updated eval.log in outputs/local_evaluation
    latest_log=$(find outputs/local_evaluation -name "eval.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | awk '{print $2}')
    
    if [ -n "$latest_log" ] && [ -f "$latest_log" ]; then
        run_dir=$(dirname "$latest_log")
        run_name=$(basename "$run_dir")
        log_mtime=$(stat -c '%y' "$latest_log" | cut -d'.' -f1)
        echo "Active Route Output: $run_name (Last modified: $log_mtime)"
        echo ""
        echo "Tail of $latest_log (last 10 lines):"
        echo ".................................................................................."
        tail -n 10 "$latest_log" 2>/dev/null || echo "Unable to read log."
        echo ".................................................................................."
    else
        echo "No active evaluation log found."
    fi

    # 4. Completed Routes Summary in Most Recent Tag
    echo ""
    echo "------------------------- [ 4. RECENT COMPLETED ROUTES ] -------------------------"
    python3 -c '
import glob, json, os

ckpts = sorted(glob.glob("outputs/local_evaluation/*/checkpoint_endpoint.json"), key=os.path.getmtime, reverse=True)
if not ckpts:
    print("No finished checkpoints recorded yet.")
else:
    printf = lambda s: print(s)
    printf(f"Found {len(ckpts)} completed route records (showing latest 8):")
    print("-" * 82)
    print(f"| {\"Run Tag / Folder\":<32} | {\"Route Comp %\":<12} | {\"Driving Score\":<14} | {\"Status\":<12} |")
    print("-" * 82)
    for p in ckpts[:8]:
        folder = os.path.basename(os.path.dirname(p))
        try:
            with open(p) as f:
                data = json.load(f)
            rec = data.get("_checkpoint", {}).get("global_record", {})
            comp = rec.get("scores_mean", {}).get("score_route", 0.0)
            ds = rec.get("scores_mean", {}).get("score_composed", 0.0)
            stat = rec.get("status", "Unknown")
            print(f"| {folder:<32} | {comp:>10.1f} % | {ds:>14.1f} | {stat:<12} |")
        except Exception:
            print(f"| {folder:<32} | {\"Error\":<12} | {\"Error\":<14} | {\"Error\":<12} |")
    print("-" * 82)
' 2>/dev/null || true

    echo "=================================================================================="
}

if [ "$WATCH_MODE" -eq 1 ]; then
    while true; do
        display_status
        echo "Watching live (refreshing every 3s... press Ctrl+C to stop)"
        sleep 3
    done
else
    display_status
    echo "Tip: Run with --watch (or -w) for real-time live monitoring:"
    echo "     bash scripts/common/check_running_process.sh --watch"
fi
