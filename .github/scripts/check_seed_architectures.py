# ruff: noqa: T201 — a CI check reports to stdout by design.
"""Group downloaded checkpoints by family and check that the seeds agree.

A family is a directory of seed directories, each holding config.yaml next to
one model*.pth. Every seed must have the parameter names and shapes of the
family's first seed, which is the only one CI drives. Prints one checkpoint
directory per family, relative to the root. Perception pretrain families have
no trained planner and are checked but not printed. Run from the repo root
inside the lead environment.
"""

import sys
from pathlib import Path

import torch
import yaml


def parameter_shapes(checkpoint_dir: Path) -> dict[str, tuple[int, ...]]:
    """Tensor shapes of a checkpoint's state dict by parameter name.

    Args:
        checkpoint_dir: Directory holding one model*.pth.

    Returns:
        The shape of every tensor in the state dict, keyed by its name.
    """
    (weights_file,) = checkpoint_dir.glob("model*.pth")
    state_dict = torch.load(weights_file, map_location="cpu", weights_only=True)
    return {name: tuple(tensor.shape) for name, tensor in state_dict.items()}


def main() -> None:
    """Check every family and print its first seed's directory."""
    checkpoint_root = Path(sys.argv[1])
    families: dict[Path, list[Path]] = {}
    for config_file in sorted(checkpoint_root.rglob("config.yaml")):
        families.setdefault(config_file.parent.parent, []).append(config_file.parent)
    assert families, f"no checkpoint under {checkpoint_root}"
    for family_dir, seed_dirs in families.items():
        reference = parameter_shapes(seed_dirs[0])
        for seed_dir in seed_dirs[1:]:
            shapes = parameter_shapes(seed_dir)
            differing = sorted(
                name
                for name in reference.keys() | shapes.keys()
                if reference.get(name) != shapes.get(name)
            )
            assert not differing, (
                f"{seed_dir} differs from {seed_dirs[0]} in {len(differing)} "
                f"parameters, e.g. {differing[:5]}"
            )
        with open(seed_dirs[0] / "config.yaml", encoding="utf-8") as f:
            is_pretraining = yaml.safe_load(f)["policy"]["transfuser"]["is_pretraining"]
        print(
            f"{family_dir.name}: {len(seed_dirs)} seeds, one architecture"
            + (", pretrain only, not driven" if is_pretraining else ""),
            file=sys.stderr,
        )
        if not is_pretraining:
            print(seed_dirs[0].relative_to(checkpoint_root))


if __name__ == "__main__":
    main()
