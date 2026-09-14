# ruff: noqa: T201 — a CI step reports to stdout by design.
"""Download a few random released logs into a data root.

Draws the logs from the ln2697/lead-123d dataset on the Hub, seeded so a rerun
draws the same ones, and fetches both sensor views and the town map of each.
Run inside the lead environment.

Usage: download_released_logs.py <count> <seed> <revision> <data_root>
"""

import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.hf_api import RepoFile, RepoFolder

REPO_ID = "ln2697/lead-123d"
VIEWS = ("normal_view", "perturbated_view")


def subdirectories(api: HfApi, path: str, revision: str) -> list[str]:
    """Paths of the directories directly under ``path`` in the dataset repo.

    Args:
        api: Hub client.
        path: Directory in the repo, e.g. ``logs/normal_view``.
        revision: Commit or branch of the dataset repo.

    Returns:
        The sorted directory paths.
    """
    entries = api.list_repo_tree(REPO_ID, path, repo_type="dataset", revision=revision)
    return sorted(entry.path for entry in entries if isinstance(entry, RepoFolder))


def main() -> None:
    """Pick the logs, print them, and download them into the data root."""
    count, seed, revision = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    data_root = Path(sys.argv[4])
    api = HfApi()
    rng = random.Random(seed)
    # snapshot_download would list the whole repo, hundreds of thousands of
    # files, before matching its patterns; that alone takes over 10 minutes.
    # Listing the few log directories directly takes a fraction of a second.
    file_paths: list[str] = []
    scenario_dirs = subdirectories(api, "logs/normal_view", revision)
    for scenario_dir in rng.sample(scenario_dirs, count):
        log_dir = rng.choice(subdirectories(api, scenario_dir, revision))
        log_name = Path(log_dir).name
        town = log_name.split("_")[0].lower()
        print(f"{log_dir} (map: {town})")
        for view in VIEWS:
            view_log_dir = f"logs/{view}/{Path(scenario_dir).name}/{log_name}"
            entries = api.list_repo_tree(
                REPO_ID,
                view_log_dir,
                repo_type="dataset",
                revision=revision,
                recursive=True,
            )
            file_paths.extend(
                entry.path for entry in entries if isinstance(entry, RepoFile)
            )
        file_paths.append(f"maps/carla/carla_{town}.arrow")

    def download(file_path: str) -> None:
        hf_hub_download(
            REPO_ID,
            file_path,
            repo_type="dataset",
            revision=revision,
            local_dir=data_root,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(download, sorted(set(file_paths))))
    print(f"Downloaded {len(set(file_paths))} files into {data_root}")


if __name__ == "__main__":
    main()
