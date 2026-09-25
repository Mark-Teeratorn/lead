#!/bin/bash
# Installs CARLA 0.9.16 with its additional maps into the given directory
# (default: 3rd_party/CARLA/standard_0916).
set -e
cd "$(dirname "$(realpath "${BASH_SOURCE:-$0}")")/../.."

_target="${1:-3rd_party/CARLA/standard_0916}"
mkdir -p "$_target"
cd "$_target"

_bucket=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux
_fetch() {
	if [ -f "$1" ] && tar -tzf "$1" >/dev/null 2>&1; then
		echo "$1 already downloaded and valid, skipping download."
		return 0
	fi
	if command -v aria2c >/dev/null 2>&1; then
		aria2c -x 16 -s 16 -k 1M -c -o "$1" --user-agent="Mozilla/5.0" "$_bucket/$3" ||
			wget -c -O "$1" --user-agent="Mozilla/5.0" "$_bucket/$3"
	else
		wget -c -O "$1" --user-agent="Mozilla/5.0" "$_bucket/$3"
	fi
	tar -tzf "$1" >/dev/null
}

_fetch CARLA_0916.tar.gz https://tiny.carla.org/carla-0-9-16-linux CARLA_0.9.16.tar.gz
tar -xzf CARLA_0916.tar.gz
cd Import
_fetch AdditionalMaps_0.9.16.tar.gz https://tiny.carla.org/additional-maps-0-9-16-linux AdditionalMaps_0.9.16.tar.gz
cd ..
# ImportAssets.sh extracts with `tar --keep-newer-files`, which reports every
# already-present file and exits 2. That happens on any re-run over a tree a
# cancelled job left behind, and is not a failure: the Town13 check below is the
# real test of a complete import.
bash ImportAssets.sh || true
test -d CarlaUE4/Content/Carla/Maps/Town13
