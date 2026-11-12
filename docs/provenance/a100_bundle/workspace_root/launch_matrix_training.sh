#!/usr/bin/env bash
# ==============================================================================
# Matrix Training Launcher for Alpamayo 1.5 Action-Only (Stage 2 SFT)
# Supported Targets:
#   - golden_1600
#   - flooded_1600
#   - golden_6400
#   - flooded_6400
# ==============================================================================
set -e
trap '' HUP TERM

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 [golden_1600 | flooded_1600 | golden_6400 | flooded_6400]"
  exit 1
fi

export YOUR_HOME="/workspace"
export RECIPE_DIR="$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft"
export CKPT_DIR_A1="$YOUR_HOME/Alpamayo-1.5-10B-A1-format"
export HF_HOME="$YOUR_HOME/.cache/huggingface"
export HF_HUB_OFFLINE=1
export USE_WANDB=no

case "$TARGET" in
  golden_1600)
    export DATASET_DIR="$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_golden_1600"
    export CKPT_DIR_A15="$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"
    export OUTPUT_DIR="output_stage2_golden_1600"
    NUM_EPOCHS=10
    WARMUP_STEPS=100
    SAVE_STEPS=50
    ;;
  flooded_1600)
    export DATASET_DIR="$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_flooded_1600"
    export CKPT_DIR_A15="$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15"
    export OUTPUT_DIR="output_stage2_flooded_1600"
    NUM_EPOCHS=10
    WARMUP_STEPS=100
    SAVE_STEPS=50
    ;;
  golden_6400)
    export DATASET_DIR="$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_golden_6400"
    export CKPT_DIR_A15="$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Golden-6400-A15"
    export OUTPUT_DIR="output_stage2_golden_6400"
    NUM_EPOCHS=10
    WARMUP_STEPS=200
    SAVE_STEPS=400
    ;;
  flooded_6400)
    export DATASET_DIR="$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_flooded_6400"
    export CKPT_DIR_A15="$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Flooded-6400-A15"
    export OUTPUT_DIR="output_stage2_flooded_6400"
    NUM_EPOCHS=10
    WARMUP_STEPS=200
    SAVE_STEPS=400
    ;;
  *)
    echo "Unknown target: $TARGET"
    echo "Choose one of: golden_1600, flooded_1600, golden_6400, flooded_6400"
    exit 1
    ;;
esac

echo "===================================================================="
echo "Starting Alpamayo 1.5 Matrix Training"
echo "Target:         $TARGET"
echo "Dataset:        $DATASET_DIR"
echo "Output:         $RECIPE_DIR/$OUTPUT_DIR"
echo "Epochs:         $NUM_EPOCHS"
echo "Warmup Steps:   $WARMUP_STEPS"
echo "Save Steps:     $SAVE_STEPS"
echo "Final A15 Ckpt: $CKPT_DIR_A15"
echo "===================================================================="

cd "$RECIPE_DIR"
source a1_5_sft/bin/activate

DATA_ARGS="data.train_dataset.local_dir=$DATASET_DIR \
  data.train_dataset.annotations_path=$DATASET_DIR/annotations_train.json \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$DATASET_DIR \
  data.val_dataset.annotations_path=$DATASET_DIR/annotations_val.json \
  data.val_dataset.chunk_ids=null"

RESUME_ARG=""
if compgen -G "$RECIPE_DIR/$OUTPUT_DIR/checkpoint-*" > /dev/null; then
  echo "Existing checkpoints detected in $RECIPE_DIR/$OUTPUT_DIR. Automatically resuming..."
  RESUME_ARG="+trainer.resume_from_checkpoint=true"
fi

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path="$CKPT_DIR_A1" \
  model.stage1_vlm_checkpoint_path="$CKPT_DIR_A1" \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=$WARMUP_STEPS \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=$NUM_EPOCHS \
  trainer.save_steps=$SAVE_STEPS \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir="$OUTPUT_DIR" \
  $RESUME_ARG

echo "===================================================================="
echo "Training completed for $TARGET. Converting checkpoint to Alpamayo 1.5 format..."
echo "===================================================================="

cd "$YOUR_HOME/alpamayo-recipes"
LATEST_CKPT=$(ls -d "$RECIPE_DIR/$OUTPUT_DIR"/checkpoint-* 2>/dev/null | sort -V | tail -1)

if [[ -n "$LATEST_CKPT" ]]; then
  echo "Converting latest checkpoint $LATEST_CKPT -> $CKPT_DIR_A15"
  python scripts/convert_checkpoint.py to-a15 \
    --input "$LATEST_CKPT" \
    --output "$CKPT_DIR_A15" \
    --overwrite
  echo "Conversion complete!"

  echo "Packaging converted model to tar.gz: ${CKPT_DIR_A15}.tar.gz"
  if command -v pigz > /dev/null 2>&1; then
    tar --use-compress-program=pigz -chf "${CKPT_DIR_A15}.tar.gz" -C "$YOUR_HOME" "$(basename "$CKPT_DIR_A15")"
  else
    tar -chzf "${CKPT_DIR_A15}.tar.gz" -C "$YOUR_HOME" "$(basename "$CKPT_DIR_A15")"
  fi
  echo "tar.gz archive complete: ${CKPT_DIR_A15}.tar.gz"
else
  echo "Warning: No checkpoint found in $RECIPE_DIR/$OUTPUT_DIR to convert."
fi
