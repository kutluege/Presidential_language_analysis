"""Shared vector helpers: loading artifacts, centroid hierarchy, cosine matrices.

Aggregation hierarchy (identical everywhere):
    chunk embeddings (unit length)
      -> speech centroid  = normalise(mean of the speech's chunk vectors)
      -> leader centroid  = normalise(mean of the leader's speech centroids)
Every speech therefore has equal weight in its leader, regardless of length.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import path_for


def l2norm(x: np.ndarray, axis: int = -1) -> np.ndarray:
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.clip(n, 1e-12, None)


def load_embeddings(cfg: dict, model_key: str, suffix: str = "") -> tuple[np.ndarray, pd.DataFrame]:
    emb_dir = path_for(cfg, "artifacts_embeddings")
    emb = np.load(emb_dir / f"{model_key}{suffix}_chunks.npy").astype(np.float32)
    index = pd.read_parquet(emb_dir / f"{model_key}{suffix}_index.parquet")
    assert len(emb) == len(index), "embedding / index length mismatch"
    return l2norm(emb), index


def load_scores(cfg: dict, tag: str) -> pd.DataFrame:
    return pd.read_csv(path_for(cfg, "outputs_tables") / f"theme_scores_chunks{tag}.csv")


def speech_centroids(emb: np.ndarray, index: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    """One normalised centroid per speech_id (order of first appearance)."""
    speech_ids = index["speech_id"].astype(str)
    order = list(dict.fromkeys(speech_ids))
    cents, rows = [], []
    for sid in order:
        mask = (speech_ids == sid).to_numpy()
        cents.append(emb[mask].mean(axis=0))
        first = index[mask].iloc[0]
        rows.append({"speech_id": sid, "leader": first["leader"], "language": first.get("language", ""),
                     "speech_date": first.get("speech_date", ""), "speech_type": first.get("speech_type", ""),
                     "n_chunks": int(mask.sum())})
    return l2norm(np.vstack(cents)), pd.DataFrame(rows)


def leader_centroids(sp_cent: np.ndarray, sp_index: pd.DataFrame, leaders: list[str]) -> tuple[np.ndarray, pd.DataFrame]:
    cents, rows = [], []
    for leader in leaders:
        mask = (sp_index["leader"] == leader).to_numpy()
        if not mask.any():
            continue
        cents.append(sp_cent[mask].mean(axis=0))
        rows.append({"leader": leader, "n_speeches": int(mask.sum()), "n_chunks": int(sp_index.loc[mask, "n_chunks"].sum())})
    return l2norm(np.vstack(cents)), pd.DataFrame(rows)


def cosine_matrix(a: np.ndarray, b: np.ndarray | None = None) -> np.ndarray:
    b = a if b is None else b
    return np.clip(l2norm(a) @ l2norm(b).T, -1.0, 1.0)


def pair_table(sim: np.ndarray, names: list[str], value_name: str = "cosine_similarity") -> pd.DataFrame:
    rows = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            rows.append({"leader_a": names[i], "leader_b": names[j], value_name: float(sim[i, j]),
                         "cosine_distance": float(1.0 - sim[i, j])})
    return pd.DataFrame(rows).sort_values(value_name, ascending=False).reset_index(drop=True)
