#!/bin/bash
# ==============================================================================
# Record Both Checkpoint 1730 (100% DS) and Checkpoint 6400 (1.9% DS) on Route 1956 (ParkingExit)
# ==============================================================================
set -e

cd /home/aimslab/lead
LOG_FILE="/home/aimslab/lead/outputs/record_video_1956_both.log"
mkdir -p /home/aimslab/lead/outputs

echo "Starting sequential recording of ParkingExit (Route 1956) for Ckpt 1730 and Ckpt 6400..." | tee -a "$LOG_FILE"

# 1. Clean up any existing processes
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 2

# 2. Record Ckpt 1730 (Expected: 100.0 DS)
echo "==========================================================" | tee -a "$LOG_FILE"
echo "PHASE 1: Recording Checkpoint 1730 on ParkingExit (Route 1956)" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
bash scripts/common/record_route_video.sh "src/lead/routes/benchmark_routes/bench2drive/1956.xml" "ParkingExit" "1730" 2>&1 | tee -a "$LOG_FILE"

# 3. Clean up between runs to ensure clean VRAM and state
echo "Cleaning up Phase 1 services..." | tee -a "$LOG_FILE"
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock
sleep 3

# 4. Record Ckpt 6400 (Expected: 1.9 DS - Early Stall)
echo "==========================================================" | tee -a "$LOG_FILE"
echo "PHASE 2: Recording Checkpoint 6400 on ParkingExit (Route 1956)" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
bash scripts/common/record_route_video.sh "src/lead/routes/benchmark_routes/bench2drive/1956.xml" "ParkingExit" "6400" 2>&1 | tee -a "$LOG_FILE"

# 5. Clean up services after Phase 2
pkill -9 -f "CarlaUE4" 2>/dev/null || true
pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
rm -f /tmp/alpamayo_flashdrive.sock

echo "==========================================================" | tee -a "$LOG_FILE"
echo "BOTH VIDEOS SUCCESSFULLY RECORDED!" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
ls -lh /home/aimslab/lead/outputs/videos/*ParkingExit* | tee -a "$LOG_FILE"
