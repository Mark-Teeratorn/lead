#!/bin/bash
# Re-run of the three fully loaded 6,400-sample checkpoints on the two states chosen by the rule of
# ANALYSIS_ADDENDUM section 27 (states 7 and 120), with the replay code and seeds unchanged, saving the plan
# waypoints and the camera frames for the qualitative figure. One process per expert, as in the replay itself.
# Outputs go to /mnt/disk2 (the root disk is nearly full); the stored replays in outputs/same_input are not touched.
cd /home/aimslab/lead
A=/home/aimslab/checkpoints/action_experts
PY=/home/aimslab/flashdrive/.venv/bin/python
OUT=/mnt/disk2/r4_sameinput/qualitative
mkdir -p "$OUT"
run() { $PY -u scripts/evaluation/same_input_replay.py --full-patch --out-dir "$OUT" --name "$1-Full" --model-path "$2" \
            --states 7,120 --save-plans-dir "$OUT/plans" --n-reset-check 0 > "$OUT/run_$1-Full.log" 2>&1
        echo "$(date '+%F %T') $1-Full exit $?" >> "$OUT/run_all.log"; }
run Golden-6400 "$A/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
run Flooded-6400-Matched "$A/extracted_matrix_flooded_6400"
run Balanced-6400 /mnt/disk2/checkpoints/action_experts/extracted_matrix_fgbalanced_6400
echo "$(date '+%F %T') QUALITATIVE DONE" >> "$OUT/run_all.log"
