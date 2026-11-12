#!/usr/bin/env bash
set -e

rm -f /workspace/train_golden_1600.pid

echo "==================================================================" >> /workspace/train_golden_1600.log
echo "STARTING/RESUMING MATRIX TRAINING (golden_1600): $(date -u)" >> /workspace/train_golden_1600.log
echo "==================================================================" >> /workspace/train_golden_1600.log

nohup /workspace/launch_matrix_training.sh golden_1600 >> /workspace/train_golden_1600.log 2>&1 &
TRAIN_PID=$!
disown -h $TRAIN_PID 2>/dev/null || true
echo $TRAIN_PID > /workspace/train_golden_1600.pid
echo "Training process launched in background with PID: $TRAIN_PID"
