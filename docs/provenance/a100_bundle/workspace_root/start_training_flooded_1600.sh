#!/usr/bin/env bash
set -e

rm -f /workspace/train_flooded_1600.pid

echo "==================================================================" >> /workspace/train_flooded_1600.log
echo "STARTING/RESUMING MATRIX TRAINING (flooded_1600): $(date -u)" >> /workspace/train_flooded_1600.log
echo "==================================================================" >> /workspace/train_flooded_1600.log

nohup /workspace/launch_matrix_training.sh flooded_1600 >> /workspace/train_flooded_1600.log 2>&1 &
TRAIN_PID=$!
disown -h $TRAIN_PID 2>/dev/null || true
echo $TRAIN_PID > /workspace/train_flooded_1600.pid
echo "Training process launched in background with PID: $TRAIN_PID"
