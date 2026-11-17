#!/bin/bash
# Same-input replay with the checkpoints loaded in full (ANALYSIS_ADDENDUM section 24): one process per expert.
cd /home/aimslab/lead
A=/home/aimslab/checkpoints/action_experts
PY=/home/aimslab/flashdrive/.venv/bin/python
run() { $PY -u scripts/evaluation/same_input_replay.py --full-patch --out-dir outputs/same_input --name "$1-Full" --model-path "$2" > "outputs/same_input/run_$1-Full.log" 2>&1; echo "$(date '+%F %T') $1-Full exit $?" >> outputs/same_input/run_all.log; }
run Golden-6400 "$A/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
run Flooded-6400-Matched "$A/extracted_matrix_flooded_6400"
run Balanced-6400 /mnt/disk2/checkpoints/action_experts/extracted_matrix_fgbalanced_6400
run Golden-1600 "$A/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"
run Flooded-1600 "$A/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15"
echo "$(date '+%F %T') FULL DONE" >> outputs/same_input/run_all.log
# Diagnostics for addendum section 23 (first 24 states): does a second Base process reproduce the first, and does an
# empty load_state_dict call change the served model?
$PY -u scripts/evaluation/same_input_replay.py --out-dir outputs/same_input --name Base-Repeat --model-path BASE --limit 24 --n-reset-check 0 > outputs/same_input/run_Base-Repeat.log 2>&1; echo "$(date '+%F %T') Base-Repeat exit $?" >> outputs/same_input/run_all.log
$PY -u scripts/evaluation/same_input_replay.py --out-dir outputs/same_input --name Base-EmptyLoad --model-path BASE --empty-load --limit 24 --n-reset-check 0 > outputs/same_input/run_Base-EmptyLoad.log 2>&1; echo "$(date '+%F %T') Base-EmptyLoad exit $?" >> outputs/same_input/run_all.log
echo "$(date '+%F %T') DIAGNOSTICS DONE" >> outputs/same_input/run_all.log
