"""Phase 4a — aggregation: chunk -> speech -> leader, plus the centroid hierarchy.

Usage:
    python -m src.aggregate --model qwen3_embedding_8b [--suffix _noceremonial]

Speech-level scores are means over the speech's chunks; leader-level scores are means over the
leader's speeches (each speech weighs the same, however long it is or however many chunks it has).

Outputs (outputs/tables/):
    theme_profile_speech{tag}.csv   theme_profile_leader{tag}.csv   top_themes_by_leader{tag}.csv
    framing_speech{tag}.csv         framing_leader{tag}.csv
Artifacts (artifacts/embeddings/):
    {model}{suffix}_speech_centroids.npy/_speech_index.parquet, {model}{suffix}_leader_centroids.npy/_leader_index.parquet
"""
from __future__ import annotations

import argparse
import re
import sys

import numpy as np
import pandas as pd

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys, theme_labels
from .vectors import leader_centroids, load_embeddings, load_scores, speech_centroids

SCORE_SUFFIXES = ("cos", "cos_en", "pct", "rel", "nli", "kw")


def score_columns(df: pd.DataFrame, keys: list[str]) -> list[str]:
    pat = re.compile(rf"^({'|'.join(map(re.escape, keys))})_({'|'.join(SCORE_SUFFIXES)})$")
    return [c for c in df.columns if pat.match(c)]


def aggregate_scores(chunks: pd.DataFrame, cols: list[str], extra_speech_cols: dict[str, pd.Series] | None = None):
    meta_cols = ["speech_id", "leader", "language", "speech_date", "speech_type"]
    speech = chunks.groupby("speech_id", sort=False).agg({**{c: "first" for c in meta_cols if c != "speech_id"},
                                                          **{c: "mean" for c in cols}, "chunk_id": "count"})
    speech = speech.rename(columns={"chunk_id": "n_chunks"}).reset_index()
    if extra_speech_cols:
        for name, series in extra_speech_cols.items():
            speech[name] = speech["speech_id"].map(series)
            cols = cols + [name]
    leader = speech.groupby("leader", sort=False).agg({**{c: "mean" for c in cols}, "speech_id": "count", "n_chunks": "sum"})
    leader = leader.rename(columns={"speech_id": "n_speeches"}).reset_index()
    return speech, leader


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 4a: chunk -> speech -> leader aggregation and centroids.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    model_key = args.model or primary_model_key(cfg)
    tag = result_tag(cfg, model_key, args.suffix)
    tables = path_for(cfg, "outputs_tables")
    emb_dir = path_for(cfg, "artifacts_embeddings")
    themes, framings = theme_keys(cfg), framing_keys(cfg)
    labels = theme_labels(cfg)
    leaders = leader_slugs(cfg)

    chunks = load_scores(cfg, tag)
    chunks["leader"] = pd.Categorical(chunks["leader"], categories=leaders, ordered=True)

    # --- themes -------------------------------------------------------------------------------
    tcols = score_columns(chunks, themes)
    speech_t, leader_t = aggregate_scores(chunks, tcols)
    speech_t.to_csv(tables / f"theme_profile_speech{tag}.csv", index=False, encoding="utf-8")
    leader_t.to_csv(tables / f"theme_profile_leader{tag}.csv", index=False, encoding="utf-8")

    top_rows = []
    for method, sfx in (("embedding_pct", "pct"), ("embedding_cos", "cos"), ("embedding_cos_en", "cos_en"), ("nli", "nli")):
        cols = [f"{k}_{sfx}" for k in themes if f"{k}_{sfx}" in leader_t.columns]
        if not cols:
            continue
        for r in leader_t.itertuples():
            vals = sorted(((getattr(r, c), c[: -len(sfx) - 1]) for c in cols), reverse=True)
            for rank, (v, k) in enumerate(vals[:3], 1):
                top_rows.append({"leader": r.leader, "method": method, "rank": rank, "theme": k, "label": labels[k],
                                 "value": round(float(v), 4), "n_speeches": r.n_speeches})
    pd.DataFrame(top_rows).to_csv(tables / f"top_themes_by_leader{tag}.csv", index=False, encoding="utf-8")

    # --- framings -----------------------------------------------------------------------------
    fcols = score_columns(chunks, framings)
    thr = float(cfg["theme_scoring"].get("framing_rate_percentile", 0.75))
    rates = {f"{k}_rate": chunks.groupby("speech_id", sort=False)[f"{k}_pct"].apply(lambda s: float((s >= thr).mean()))
             for k in framings}
    speech_f, leader_f = aggregate_scores(chunks, fcols, rates)
    speech_f.to_csv(tables / f"framing_speech{tag}.csv", index=False, encoding="utf-8")
    leader_f.to_csv(tables / f"framing_leader{tag}.csv", index=False, encoding="utf-8")

    # --- centroid hierarchy -------------------------------------------------------------------
    emb, index = load_embeddings(cfg, model_key, args.suffix)
    sp_cent, sp_idx = speech_centroids(emb, index)
    ld_cent, ld_idx = leader_centroids(sp_cent, sp_idx, leaders)
    np.save(emb_dir / f"{model_key}{args.suffix}_speech_centroids.npy", sp_cent)
    sp_idx.to_parquet(emb_dir / f"{model_key}{args.suffix}_speech_index.parquet", index=False)
    np.save(emb_dir / f"{model_key}{args.suffix}_leader_centroids.npy", ld_cent)
    ld_idx.to_parquet(emb_dir / f"{model_key}{args.suffix}_leader_index.parquet", index=False)

    print(f"[aggregate] tag='{tag}': {len(speech_t)} speeches, {len(leader_t)} leaders, {len(tcols)} theme score cols, {len(fcols)} framing cols")
    show = leader_t[["leader", "n_speeches", "n_chunks"] + [f"{k}_pct" for k in themes]].copy()
    show.columns = ["leader", "speeches", "chunks"] + [k[:14] for k in themes]
    print(show.round(3).to_string(index=False))
    print(leader_f[["leader"] + [f"{k}_pct" for k in framings] + [f"{k}_rate" for k in framings]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
