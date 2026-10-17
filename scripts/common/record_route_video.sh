#!/bin/bash
# ==============================================================================
# Record Sped-Up Smooth Video Demonstration
# Model: Action Model 4 (Checkpoint 1730 Non-EMA)
# Scenario: InvadingTurn (Route 2790) - 100.0 DS
# ==============================================================================
set -e

cd /home/aimslab/lead

ROUTE_XML="${1:-src/lead/routes/benchmark_routes/bench2drive/2790.xml}"
ROUTE_ID=$(basename "$ROUTE_XML" .xml)
SCENARIO_NAME="${2:-InvadingTurn}"
MODEL_CHOICE="${3:-1730}"

VIDEO_DIR="/home/aimslab/lead/outputs/videos"
mkdir -p "$VIDEO_DIR"

if [ "$MODEL_CHOICE" = "20050" ] || [ "$MODEL_CHOICE" = "model_v4" ] || [ "$MODEL_CHOICE" = "v4" ]; then
    MODEL_PATH="/home/aimslab/checkpoints/action_experts/model_v4"
    MODEL_LABEL="Model v4: Ckpt 20050 (Balanced)"
    MODEL_TAG="model_v4_video"
    OUTPUT_MP4="$VIDEO_DIR/model_v4_20050_${SCENARIO_NAME}_route${ROUTE_ID}_smooth.mp4"
    FRAMES_DIR="$VIDEO_DIR/frames_${ROUTE_ID}_20050"
elif [ "$MODEL_CHOICE" = "6400" ]; then
    MODEL_PATH="/home/aimslab/checkpoints/action_experts/checkpoint-6400"
    MODEL_LABEL="Model 5: Ckpt 6400 (v3 Flooded)"
    MODEL_TAG="model5_video"
    OUTPUT_MP4="$VIDEO_DIR/model5_6400_${SCENARIO_NAME}_route${ROUTE_ID}_smooth.mp4"
    FRAMES_DIR="$VIDEO_DIR/frames_${ROUTE_ID}_6400"
else
    MODEL_PATH="/home/aimslab/checkpoints/action_experts/action_model_4_nonema"
    MODEL_LABEL="Model 4: Ckpt 1730 (Non-EMA Balanced)"
    MODEL_TAG="model4_video"
    OUTPUT_MP4="$VIDEO_DIR/model4_1730_${SCENARIO_NAME}_route${ROUTE_ID}_smooth.mp4"
    FRAMES_DIR="$VIDEO_DIR/frames_${ROUTE_ID}_1730"
fi

rm -rf "$FRAMES_DIR"
mkdir -p "$FRAMES_DIR"

echo "=========================================================="
echo "   RECORDING BENCH2DRIVE SPED-UP SMOOTH VIDEO"
echo "=========================================================="
echo "Scenario:        $SCENARIO_NAME (Route $ROUTE_ID)"
echo "Route File:      $ROUTE_XML"
echo "Model Choice:    $MODEL_CHOICE ($MODEL_LABEL)"
echo "Model Path:      $MODEL_PATH"
echo "Frames Dir:      $FRAMES_DIR"
echo "Output Video:    $OUTPUT_MP4"
echo "Playback FPS:    24 FPS (Sped-up ~2.4x for fluid smoothness)"
echo "=========================================================="

export RECORD_VIDEO_DIR="$FRAMES_DIR"
export VIDEO_OUTPUT_PATH="$OUTPUT_MP4"
export VIDEO_FPS="24"
export VIDEO_MODEL_LABEL="$MODEL_LABEL"
export VIDEO_SCENARIO_LABEL="$SCENARIO_NAME (Route $ROUTE_ID)"
export MODEL_PATH="$MODEL_PATH"
export MODEL_TAG="$MODEL_TAG"

# Run single route evaluation
bash scripts/common/eval_alpamayo_b2d.sh "$ROUTE_XML"

if [ -f "$OUTPUT_MP4" ]; then
    echo ""
    echo "=========================================================="
    echo "   VIDEO RECORDING COMPLETE!"
    echo "=========================================================="
    ls -lh "$OUTPUT_MP4"
    
    # Also generate a 10 FPS (1.0x real-time simulation) version for comparison
    REALTIME_MP4="${OUTPUT_MP4%_smooth.mp4}_realtime_10fps.mp4"
    echo "Generating real-time (10 FPS) companion video: $REALTIME_MP4"
    ffmpeg -y -framerate 10 -i "$FRAMES_DIR/frame_%05d.jpg" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "$REALTIME_MP4" 2>/dev/null || true
    
    # Copy to artifact directory for easy download/preview
    ARTIFACT_DIR="/home/aimslab/.gemini/antigravity-ide/brain/a4159320-cec9-4e6d-beb7-b31a0168afce"
    if [ -d "$ARTIFACT_DIR" ]; then
        cp "$OUTPUT_MP4" "$ARTIFACT_DIR/"
        echo "Copied smooth video to artifact directory: $ARTIFACT_DIR/$(basename "$OUTPUT_MP4")"
    fi
    
    # Clean up services
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
    rm -f /tmp/alpamayo_flashdrive.sock
else
    echo "Error: Video was not generated."
    pkill -9 -f "CarlaUE4" 2>/dev/null || true
    pkill -9 -f "flashdrive_server.py" 2>/dev/null || true
    rm -f /tmp/alpamayo_flashdrive.sock
    exit 1
fi
