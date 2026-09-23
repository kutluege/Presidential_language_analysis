"""Phase 3b — emotional tone per chunk (English text) with two small classifiers.

Usage:
    python -m src.emotion                 # data/processed/chunks.csv
    python -m src.emotion --suffix _noceremonial

Independent of the embedding model: results are cached per chunk set in
artifacts/embeddings/emotion_scores{suffix}.parquet and written to
    outputs/tables/emotion_scores_chunks{etag}.csv       (etag = "" or "__noceremonial")
    outputs/tables/emotion_profile_speech{etag}.csv       chunk -> speech means
    outputs/tables/emotion_profile_leader{etag}.csv       speech -> leader means (each speech weighs equally)
    outputs/tables/emotion_top_labels_by_leader{etag}.csv

Columns: emo_{label} (28 GoEmotions sigmoid probabilities), fam_{family} (max member probability),
sent_negative / sent_neutral / sent_positive, valence = sent_positive - sent_negative.
Caveats carried into every report: classifiers trained on Reddit/Twitter text; translated leaders are
scored on the English translation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .config import leader_slugs, load_config, path_for, seed_everything


def etag_for(suffix: str) -> str:
    return "" if not suffix else "__" + suffix.lstrip("_")


def classify(texts: list[str], model_id: str, batch_size: int, max_length: int, sigmoid: bool) -> pd.DataFrame:
    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1
    clf = pipeline("text-classification", model=model_id, device=device, top_k=None,
                   function_to_apply="sigmoid" if sigmoid else "softmax", truncation=True, max_length=max_length)
    rows = []
    for start in range(0, len(texts), batch_size):
        res = clf(texts[start:start + batch_size], batch_size=batch_size)
        for r in res:
            rows.append({d["label"].lower(): float(d["score"]) for d in r})
        print(f"[emotion] {model_id.split('/')[-1]} {min(start + batch_size, len(texts))}/{len(texts)}", end="\r", flush=True)
    print()
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 3b: emotion and sentiment scores per chunk.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--suffix", default="", help="'' for chunks.csv, _noceremonial for chunks_noceremonial.csv")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    seed_everything(int(cfg["random_seed"]))
    ecfg = cfg["emotion"]
    leaders = leader_slugs(cfg)
    chunks_file = "chunks.csv" if not args.suffix else f"chunks{args.suffix}.csv"
    chunks = pd.read_csv(path_for(cfg, "data_processed") / chunks_file, keep_default_na=False)
    texts = chunks["chunk_text"].astype(str).tolist()
    tables = path_for(cfg, "outputs_tables")
    tables.mkdir(parents=True, exist_ok=True)
    cache = path_for(cfg, "artifacts_embeddings") / f"emotion_scores{args.suffix}.parquet"
    etag = etag_for(args.suffix)

    if cache.exists() and not args.force:
        scores = pd.read_parquet(cache)
        if len(scores) != len(chunks) or not (scores["chunk_id"] == chunks["chunk_id"]).all():
            scores = None
    else:
        scores = None
    if scores is None:
        emo = classify(texts, ecfg["emotion_model"], int(ecfg.get("batch_size", 32)), int(ecfg.get("max_length", 512)), sigmoid=True)
        sent = classify(texts, ecfg["sentiment_model"], int(ecfg.get("batch_size", 32)), int(ecfg.get("max_length", 512)), sigmoid=False)
        emo.columns = [f"emo_{c}" for c in emo.columns]
        sent.columns = [f"sent_{c}" for c in sent.columns]
        scores = pd.concat([chunks[["chunk_id"]].reset_index(drop=True), emo, sent], axis=1)
        for fam, members in ecfg["families"].items():
            cols = [f"emo_{m}" for m in members if f"emo_{m}" in scores.columns]
            missing = [m for m in members if f"emo_{m}" not in scores.columns]
            if missing:
                print(f"[emotion] warning: labels not produced by the model: {missing}")
            agg = ecfg.get("family_aggregation", "max")
            scores[f"fam_{fam}"] = scores[cols].max(axis=1) if agg == "max" else scores[cols].mean(axis=1)
        scores["valence"] = scores.get("sent_positive", 0.0) - scores.get("sent_negative", 0.0)
        cache.parent.mkdir(parents=True, exist_ok=True)
        scores.to_parquet(cache, index=False)

    meta_cols = ["chunk_id", "speech_id", "leader", "language", "speech_date", "speech_type", "chunk_index", "token_count", "word_count"]
    df = chunks[meta_cols].merge(scores, on="chunk_id", how="left")
    df.to_csv(tables / f"emotion_scores_chunks{etag}.csv", index=False, encoding="utf-8")

    score_cols = [c for c in df.columns if c.startswith(("emo_", "fam_", "sent_")) or c == "valence"]
    speech = df.groupby("speech_id", sort=False).agg({"leader": "first", "language": "first", "speech_date": "first", "speech_type": "first",
                                                     **{c: "mean" for c in score_cols}, "chunk_id": "count"}).rename(columns={"chunk_id": "n_chunks"}).reset_index()
    speech["leader"] = pd.Categorical(speech["leader"], categories=leaders, ordered=True)
    leader = speech.groupby("leader", sort=False, observed=True).agg({**{c: "mean" for c in score_cols}, "speech_id": "count", "n_chunks": "sum"}).rename(columns={"speech_id": "n_speeches"}).reset_index()
    speech.to_csv(tables / f"emotion_profile_speech{etag}.csv", index=False, encoding="utf-8")
    leader.to_csv(tables / f"emotion_profile_leader{etag}.csv", index=False, encoding="utf-8")

    top_rows = []
    emo_cols = [c for c in score_cols if c.startswith("emo_") and c != "emo_neutral"]
    for r in leader.itertuples():
        vals = sorted(((getattr(r, c), c[4:]) for c in emo_cols), reverse=True)[:5]
        for rank, (v, lab) in enumerate(vals, 1):
            top_rows.append({"leader": r.leader, "rank": rank, "emotion": lab, "mean_probability": round(float(v), 4)})
    pd.DataFrame(top_rows).to_csv(tables / f"emotion_top_labels_by_leader{etag}.csv", index=False, encoding="utf-8")

    fams = [f"fam_{f}" for f in ecfg.get("report_families", [])]
    print(f"[emotion] {len(df)} chunks, {len(speech)} speeches → emotion_profile_leader{etag}.csv")
    print(leader[["leader", "n_speeches"] + fams + ["valence"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
