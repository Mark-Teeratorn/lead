#!/bin/bash
set -e

# Clean up any stale PID files or old state
rm -f /workspace/train_stage2_v4.pid /workspace/training_watchdog.pid

echo "Launching Alpamayo Stage 2 v4 training in detached session (setsid)..."
setsid /workspace/launch_stage2_v4.sh > /workspace/train_stage2_v4.log 2>&1 &
TRAIN_PID=$!
echo $TRAIN_PID > /workspace/train_stage2_v4.pid
echo "Training process launched with detached PID: $TRAIN_PID"

echo "Launching Training Watchdog & Email Daemon in detached session (setsid)..."
setsid python3 /workspace/monitor_training_and_notify.py > /workspace/watchdog_stdout.log 2>&1 &
WATCHDOG_PID=$!
echo $WATCHDOG_PID > /workspace/training_watchdog.pid
echo "Watchdog process launched with detached PID: $WATCHDOG_PID"

echo "Both processes successfully detached. Live log: /workspace/train_stage2_v4.log"
