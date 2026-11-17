#!/bin/bash
# Same-input replay (ANALYSIS_ADDENDUM section 21): one process per expert, in sequence.
cd /home/aimslab/lead
A=/home/aimslab/checkpoints/action_experts
PY=/home/aimslab/flashdrive/.venv/bin/python
run() { $PY -u scripts/evaluation/same_input_replay.py --out-dir outputs/same_input --name "$1" --model-path "$2" > "outputs/same_input/run_$1.log" 2>&1; echo "$(date '+%F %T') $1 exit $?" >> outputs/same_input/run_all.log; }
run Base BASE
run Golden-6400 "$A/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
run Flooded-6400-Matched "$A/extracted_matrix_flooded_6400"
run Balanced-6400 /mnt/disk2/checkpoints/action_experts/extracted_matrix_fgbalanced_6400
run Golden-1600 "$A/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"
run Flooded-1600 "$A/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15"
echo "$(date '+%F %T') ALL DONE" >> outputs/same_input/run_all.log
