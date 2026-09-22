"""Configuration loading, project paths and seeding shared by every phase."""
from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else DEFAULT_CONFIG
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_config_path"] = str(cfg_path)
    return cfg


def path_for(cfg: dict[str, Any], key: str) -> Path:
    """Resolve a `paths:` entry relative to the project root."""
    p = Path(cfg["paths"][key])
    return p if p.is_absolute() else PROJECT_ROOT / p


def ensure_dirs(cfg: dict[str, Any], *keys: str) -> None:
    for key in keys:
        path_for(cfg, key).mkdir(parents=True, exist_ok=True)


def leader_slugs(cfg: dict[str, Any]) -> list[str]:
    return list(cfg["leaders"].keys())


def seed_everything(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
