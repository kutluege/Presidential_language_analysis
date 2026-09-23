"""Phase 3 — interpretable theme and framing scores per chunk.

Usage:
    python -m src.theme_scoring --model qwen3_embedding_8b [--suffix _noceremonial] [--no-nli]

Three independent signals per chunk and theme (never keyword counting as the score):
  {theme}_cos     Option A — cosine similarity between the chunk embedding and the theme
                  description embedded with the SAME model. With query_language=matched the
                  description is in the chunk's own language (tr/fr/de/en).
  {theme}_cos_en  the same with English descriptions for every chunk (robustness).
  {theme}_pct     percentile rank of {theme}_cos over all chunks of the corpus (0..1). Identical
                  reference for every leader; 0.5 = corpus average. This is the value used for
                  the radar charts.
  {theme}_rel     {theme}_cos minus the corpus mean of that theme (cosine units).
  {theme}_nli     Option B — multilingual zero-shot NLI probability (multi-label, so several
                  themes can be high or all can be low).
  {theme}_kw      diagnostic only — keyword hits per 100 words from the multilingual lists.
Framings (conflict_threat_framing, cooperation_solidarity_framing) get _cos, _cos_en, _pct, _rel,
_nli in the same way.

Outputs: outputs/tables/theme_scores_chunks{tag}.csv, theme_method_agreement{tag}.csv,
         theme_language_diagnostic{tag}.csv; NLI cache in artifacts/embeddings/nli_scores{suffix}.parquet
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .config import framing_keys, load_config, path_for, primary_model_key, result_tag, seed_everything, theme_keys
from .textutils import count_words

NLI_FRAMING_LABELS = {
    "conflict_threat_framing": "threat, enemies, conflict and war",
    "cooperation_solidarity_framing": "cooperation, unity, peace and solidarity",
}


def percentile_rank(x: np.ndarray) -> np.ndarray:
    """Average-rank percentile in [0, 1] (ties share the mean rank)."""
    from scipy.stats import rankdata

    return (rankdata(x, method="average") - 0.5) / len(x)


def cosine_scores(chunk_emb: np.ndarray, q_emb: np.ndarray, queries: pd.DataFrame, langs: pd.Series,
                  kind: str, key: str, mode: str) -> np.ndarray:
    """Per-chunk cosine to the (kind,key) description; mode 'matched' picks the chunk language."""
    sub = queries[(queries["kind"] == kind) & (queries["key"] == key)]
    by_lang = {r.lang: q_emb[r.Index] for r in sub.itertuples()}
    if mode == "en" or len(by_lang) == 1:
        return chunk_emb @ by_lang["en"]
    out = np.empty(len(chunk_emb), dtype=np.float32)
    for lang in set(langs):
        mask = (langs == lang).to_numpy()
        out[mask] = chunk_emb[mask] @ by_lang.get(lang, by_lang["en"])
    return out


def keyword_rate(texts: list[str], langs: list[str], kw_cfg: dict, key: str) -> np.ndarray:
    lists = kw_cfg.get(key, {})
    rates = np.zeros(len(texts), dtype=np.float32)
    compiled: dict[str, re.Pattern] = {}
    for lang, words in lists.items():
        alts = "|".join(re.escape(w.lower()) for w in words)
        compiled[lang] = re.compile(rf"(?<!\w)(?:{alts})\w*", re.I)
    for i, (t, lang) in enumerate(zip(texts, langs)):
        pat = compiled.get(lang) or compiled.get("en")
        if pat is None:
            continue
        n_words = max(count_words(t), 1)
        rates[i] = 100.0 * len(pat.findall(t.lower())) / n_words
    return rates


def nli_scores(texts: list[str], labels: dict[str, str], cfg: dict, cache: Path) -> pd.DataFrame:
    """Zero-shot multi-label NLI; cached per chunk set (independent of the embedding model)."""
    if cache.exists():
        df = pd.read_parquet(cache)
        if len(df) == len(texts) and all(c in df.columns for c in labels):
            return df
    import torch
    from transformers import pipeline

    ts = cfg["theme_scoring"]
    device = 0 if torch.cuda.is_available() else -1
    clf = pipeline("zero-shot-classification", model=ts["nli_model"], device=device)
    label_texts = list(labels.values())
    inv = {v: k for k, v in labels.items()}
    out = {k: np.zeros(len(texts), dtype=np.float32) for k in labels}
    bs = int(ts.get("nli_batch_size", 16))
    for start in range(0, len(texts), bs):
        batch = texts[start:start + bs]
        res = clf(batch, candidate_labels=label_texts, hypothesis_template=ts["nli_hypothesis_template"],
                  multi_label=True, batch_size=bs)
        if isinstance(res, dict):
            res = [res]
        for i, r in enumerate(res):
            for lab, sc in zip(r["labels"], r["scores"]):
                out[inv[lab]][start + i] = sc
        print(f"[theme_scoring] NLI {min(start + bs, len(texts))}/{len(texts)}", end="\r", flush=True)
    print()
    df = pd.DataFrame(out)
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache, index=False)
    return df


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 3: theme and framing scores per chunk.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None, help="embedding model key (default: primary)")
    ap.add_argument("--suffix", default="", help="artifact suffix, e.g. _noceremonial or _translated_en")
    ap.add_argument("--no-nli", action="store_true")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    seed_everything(int(cfg["random_seed"]))
    model_key = args.model or primary_model_key(cfg)
    tag = result_tag(cfg, model_key, args.suffix)
    emb_dir = path_for(cfg, "artifacts_embeddings")
    tables = path_for(cfg, "outputs_tables")
    tables.mkdir(parents=True, exist_ok=True)

    chunk_emb = np.load(emb_dir / f"{model_key}{args.suffix}_chunks.npy")
    index = pd.read_parquet(emb_dir / f"{model_key}{args.suffix}_index.parquet")
    q_emb = np.load(emb_dir / f"{model_key}_queries.npy")
    queries = pd.read_parquet(emb_dir / f"{model_key}_queries.parquet")
    langs = index["language"].astype(str)
    texts = index["chunk_text"].astype(str).tolist()
    mode = cfg["theme_scoring"].get("query_language", "matched")
    themes, framings = theme_keys(cfg), framing_keys(cfg)
    kw_cfg = cfg.get("theme_keywords_diagnostic", {})

    df = index[["chunk_id", "speech_id", "leader", "language", "speech_date", "speech_type", "chunk_index",
                "n_chunks_in_speech", "relative_position", "token_count", "word_count"]].copy()
    for kind, keys in (("theme", themes), ("framing", framings)):
        for key in keys:
            cos = cosine_scores(chunk_emb, q_emb, queries, langs, kind, key, mode)
            cos_en = cosine_scores(chunk_emb, q_emb, queries, langs, kind, key, "en")
            df[f"{key}_cos"] = cos
            df[f"{key}_cos_en"] = cos_en
            df[f"{key}_pct"] = percentile_rank(cos)
            df[f"{key}_rel"] = cos - cos.mean()
            if kind == "theme":
                df[f"{key}_kw"] = keyword_rate(texts, langs.tolist(), kw_cfg, key)

    # top theme per chunk (embedding) and a "no theme stands out" indicator
    pct_mat = df[[f"{k}_pct" for k in themes]].to_numpy()
    df["top_theme_emb"] = [themes[i] for i in pct_mat.argmax(1)]
    df["top_theme_margin"] = np.sort(pct_mat, axis=1)[:, -1] - np.sort(pct_mat, axis=1)[:, -2]

    if not args.no_nli:
        labels = {t["key"]: t.get("nli_label") or t["label"].replace(" & ", " and ").lower() for t in cfg["theme_definitions"]}
        for k, f in cfg["framing_definitions"].items():
            labels[k] = f.get("nli_label") or NLI_FRAMING_LABELS.get(k) or f["label"].lower()
        cache = emb_dir / f"nli_scores{args.suffix}.parquet"
        nli = nli_scores(texts, labels, cfg, cache)
        for k in list(themes) + list(framings):
            df[f"{k}_nli"] = nli[k].to_numpy()
        nli_mat = df[[f"{k}_nli" for k in themes]].to_numpy()
        df["top_theme_nli"] = [themes[i] for i in nli_mat.argmax(1)]

    out = tables / f"theme_scores_chunks{tag}.csv"
    df.to_csv(out, index=False, encoding="utf-8")

    # --- agreement between methods -----------------------------------------------------------
    from scipy.stats import spearmanr

    rows = []
    for k in list(themes) + list(framings):
        r = {"key": k, "spearman_cos_vs_cos_en": spearmanr(df[f"{k}_cos"], df[f"{k}_cos_en"]).statistic}
        if f"{k}_nli" in df:
            r["spearman_cos_vs_nli"] = spearmanr(df[f"{k}_cos"], df[f"{k}_nli"]).statistic
            r["spearman_cos_en_vs_nli"] = spearmanr(df[f"{k}_cos_en"], df[f"{k}_nli"]).statistic
        if f"{k}_kw" in df:
            r["spearman_cos_vs_kw"] = spearmanr(df[f"{k}_cos"], df[f"{k}_kw"]).statistic
            r["kw_nonzero_share"] = float((df[f"{k}_kw"] > 0).mean())
        r["mean_cos"] = float(df[f"{k}_cos"].mean())
        r["sd_cos"] = float(df[f"{k}_cos"].std())
        rows.append(r)
    agree = pd.DataFrame(rows)
    if "top_theme_nli" in df:
        agree.attrs["top_theme_agreement"] = float((df["top_theme_emb"] == df["top_theme_nli"]).mean())
        agree["top_theme_agreement_emb_vs_nli"] = agree.attrs["top_theme_agreement"]
    agree.to_csv(tables / f"theme_method_agreement{tag}.csv", index=False, encoding="utf-8")

    # --- language diagnostic: mean cosine per language, matched vs English descriptions --------
    diag = []
    for lang, g in df.groupby("language"):
        for k in themes:
            diag.append({"language": lang, "theme": k, "n_chunks": len(g), "mean_cos_matched": g[f"{k}_cos"].mean(),
                         "mean_cos_en": g[f"{k}_cos_en"].mean(), "mean_pct": g[f"{k}_pct"].mean()})
    pd.DataFrame(diag).to_csv(tables / f"theme_language_diagnostic{tag}.csv", index=False, encoding="utf-8")

    print(f"[theme_scoring] model={model_key} suffix='{args.suffix}' tag='{tag}' chunks={len(df)} query_language={mode}")
    print(agree.round(3).to_string(index=False))
    print(f"[theme_scoring] wrote {out.name}, theme_method_agreement{tag}.csv, theme_language_diagnostic{tag}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
