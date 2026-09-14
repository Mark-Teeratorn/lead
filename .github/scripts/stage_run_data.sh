#!/bin/bash
# Stages this run's data root on this machine: merges the route roots the
# collect-data cells left here, then adds released logs. Fails when no cell ran
# on this machine. Idempotent under a lock, so parallel jobs on one machine
# share the work. Run from the repo root with the lead environment and
# PY123D_DATA_ROOT set to the run's data root.
#
# Usage: stage_run_data.sh <released_log_count> <seed> <dataset_revision>
set -eu

released_log_count=$1
seed=$2
dataset_revision=$3
data_root=${PY123D_DATA_ROOT:?}
run_root=$(dirname "$data_root")

mkdir -p "$data_root"
exec 9>"$run_root/.stage.lock"
flock 9
route_roots=("$run_root"/routes/*/)
if [ ! -d "${route_roots[0]}" ]; then
  echo "::error::No route root of this run on $(hostname): every collect-data cell ran on another machine. Rerun the workflow."
  exit 1
fi
# Logs are distinct per route; the town maps and the dataset config are
# identical copies, so the last one wins.
for route_root in "${route_roots[@]}"; do
  cp -rlf "$route_root". "$data_root/"
done
# Mixes Hub data in beside the fresh routes; the seed makes every job of the
# run draw the same logs. Files already present are skipped.
python .github/scripts/download_released_logs.py \
  "$released_log_count" "$seed" "$dataset_revision" "$data_root"
find "$data_root/logs" -mindepth 3 -maxdepth 3 | sort
echo "expected_log_count=$((${#route_roots[@]} + released_log_count))" >> "${GITHUB_OUTPUT:?}"
