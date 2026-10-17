#!/bin/bash
# ==============================================================================
# Record Both Checkpoint 1730 (100% RC, 90.7 DS) and Checkpoint 6400 (50% RC, 18.0 DS)
# on Route 14194 (PedestrianCrossing)
# ==============================================================================
set -e

cd /home/aimslab/lead
LOG_FILE="/home/aimslab/lead/outputs/record_video_14194_both.log"
mkdir -p /home/aimslab/lead/outputs

echo "Starting sequential recording of PedestrianCrossing (Route 14194)..." > "$LOG_FILE"

# Clean up any existing processes
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 2

# PHASE 1: Record Ckpt 1730 (Expected: 100% RC, 90.7 DS)
echo "==========================================================" >> "$LOG_FILE"
echo "PHASE 1: Recording Checkpoint 1730 on PedestrianCrossing (Route 14194)" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"
bash scripts/common/record_route_video.sh "src/lead/routes/benchmark_routes/bench2drive/14194.xml" "PedestrianCrossing" "1730" >> "$LOG_FILE" 2>&1

# Sleep and clean up before Phase 2
sleep 3
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 2

# PHASE 2: Record Ckpt 6400 (Expected: 50% RC, 18.0 DS)
echo "==========================================================" >> "$LOG_FILE"
echo "PHASE 2: Recording Checkpoint 6400 on PedestrianCrossing (Route 14194)" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"
bash scripts/common/record_route_video.sh "src/lead/routes/benchmark_routes/bench2drive/14194.xml" "PedestrianCrossing" "6400" >> "$LOG_FILE" 2>&1

# Final cleanup
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock

echo "==========================================================" >> "$LOG_FILE"
echo "PEDESTRIAN CROSSING VIDEOS SUCCESSFULLY RECORDED!" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"
ls -lh /home/aimslab/lead/outputs/videos/*PedestrianCrossing* >> "$LOG_FILE" 2>&1
