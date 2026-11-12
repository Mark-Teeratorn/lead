#!/usr/bin/env bash
set -e
trap '' HUP TERM

echo "===================================================================="
echo "MATRIX TRAINING PIPELINE: golden_1600 -> zip -> flooded_1600"
echo "Start time: $(date -u)"
echo "===================================================================="

# Step 1: Self-healing loop for golden_1600 until finished & zipped
while [[ ! -f "/workspace/Alpamayo-1.5-10B-Matrix-Golden-1600-A15.zip" ]]; do
  echo "Running / continuing golden_1600 training (saves every 50 steps)..."
  /workspace/launch_matrix_training.sh golden_1600 || {
    echo "Process exited or interrupted. Checking status in 5 seconds..."
    sleep 5
  }
done

echo "golden_1600 is complete, converted, and zipped."

# Step 2: Self-healing loop for flooded_1600 until finished & zipped
echo "===================================================================="
echo "Starting flooded_1600 training..."
echo "Start time: $(date -u)"
echo "===================================================================="

while [[ ! -f "/workspace/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.zip" ]]; do
  echo "Running / continuing flooded_1600 training (saves every 50 steps)..."
  /workspace/launch_matrix_training.sh flooded_1600 || {
    echo "Process exited or interrupted. Checking status in 5 seconds..."
    sleep 5
  }
done

echo "===================================================================="
echo "PIPELINE COMPLETED SUCCESSFULLY: $(date -u)"
echo "===================================================================="
