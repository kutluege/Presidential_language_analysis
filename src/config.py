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


def primary_model_key(cfg: dict[str, Any]) -> str:
    """Key under embedding.models whose hf_id equals primary_embedding_model."""
    for key, m in cfg["embedding"]["models"].items():
        if m["hf_id"] == cfg["primary_embedding_model"]:
            return key
    return next(iter(cfg["embedding"]["models"]))


def result_tag(cfg: dict[str, Any], model_key: str, suffix: str = "") -> str:
    """Suffix appended to output table names.

    The primary model on the full original chunk set gets the plain spec filenames (tag "");
    every other combination gets `__{model_key}{suffix}` so results are never mixed.
    """
    if model_key == primary_model_key(cfg) and not suffix:
        return ""
    return f"__{model_key}{suffix}"


def theme_keys(cfg: dict[str, Any]) -> list[str]:
    return [t["key"] for t in cfg["theme_definitions"]]


def theme_labels(cfg: dict[str, Any], lang: str = "en") -> dict[str, str]:
    return {t["key"]: (t.get(f"label_{lang}") or t["label"]) for t in cfg["theme_definitions"]}


def framing_keys(cfg: dict[str, Any]) -> list[str]:
    return list(cfg["framing_definitions"].keys())


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
