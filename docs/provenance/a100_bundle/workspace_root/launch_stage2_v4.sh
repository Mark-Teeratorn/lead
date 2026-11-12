#!/bin/bash
set -e

export YOUR_HOME=/workspace
export RECIPE_DIR=$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft
export PAI_DIR=$YOUR_HOME/lead-alpamayo-pai_large_v4
export CKPT_DIR_RAW=$YOUR_HOME/Alpamayo-1.5-10B
export CKPT_DIR_A1=${CKPT_DIR_RAW}-A1-format
export CKPT_DIR_A15=$YOUR_HOME/Alpamayo-1.5-10B-Lead-Large-v4-A15
export HF_HOME=$YOUR_HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TRAIN_ANN=$PAI_DIR/annotations_train.json
export VAL_ANN=$PAI_DIR/annotations_val.json
export USE_WANDB=no

DATA_ARGS="data.train_dataset.local_dir=$PAI_DIR data.train_dataset.annotations_path=$TRAIN_ANN \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$PAI_DIR data.val_dataset.annotations_path=$VAL_ANN \
  data.val_dataset.chunk_ids=null"

cd $RECIPE_DIR
source a1_5_sft/bin/activate

echo "=========================================================="
echo "Starting Action-Only Stage 2 Fine-Tuning on v4 Dataset"
echo "Data: 16,040 Curated Samples across 29 chunks (72 GB)"
echo "Schedule: 10 Epochs = 20,050 Optimizer Steps (eff. batch 8)"
echo "Date: $(date -u)"
echo "=========================================================="

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=200 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=400 \
  trainer.save_total_limit=5 \
  trainer.logging_steps=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=output_stage2_lead_v4
