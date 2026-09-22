"""Phase 2 — chunk embeddings (GPU) for one model and one chunk file.

Usage:
    python -m src.embed --model qwen3_embedding_8b                    # data/processed/chunks.csv
    python -m src.embed --model qwen3_embedding_8b --chunks chunks_noceremonial.csv
    python -m src.embed --model bge_m3
    python -m src.embed --model qwen3_embedding_8b --variant translated_en

Artifacts (artifacts/embeddings/):
    {model_key}{suffix}_chunks.npy       float32, L2-normalised, one row per chunk
    {model_key}{suffix}_index.parquet    chunk metadata in the same row order
    {model_key}_queries.npy / .parquet   theme + framing description embeddings (all languages)
    {model_key}{suffix}_run.json         model id, dtype, timings, shapes

Embeddings from different models are never written to the same file and never mixed downstream.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .config import load_config, path_for, seed_everything

LANGS = ["en", "tr", "fr", "de"]


def artifact_suffix(variant: str, chunks_file: str) -> str:
    s = "" if variant == "original" else f"_{variant}"
    if chunks_file.startswith("chunks_") and chunks_file.endswith(".csv"):
        s += "_" + chunks_file[len("chunks_"):-len(".csv")]
    return s


def build_query_table(cfg: dict) -> pd.DataFrame:
    """One row per (concept, language): theme and framing descriptions."""
    rows = []
    for t in cfg["theme_definitions"]:
        for lang in LANGS:
            desc = t["description"] if lang == "en" else t.get(f"description_{lang}")
            if not desc:
                continue
            label = t["label"] if lang != "tr" else t.get("label_tr", t["label"])
            text = f"{label}: {desc}" if lang == "en" else desc
            if lang == "en":
                text += " Related terms: " + ", ".join(t["examples"]) + "."
            rows.append({"query_id": f"theme:{t['key']}:{lang}", "kind": "theme", "key": t["key"], "lang": lang, "text": text})
    for key, f in cfg["framing_definitions"].items():
        for lang in LANGS:
            desc = f["description"] if lang == "en" else f.get(f"description_{lang}")
            if not desc:
                continue
            text = f"{f['label']}: {desc}" if lang == "en" else desc
            if lang == "en":
                text += " Related terms: " + ", ".join(f["concepts"]) + "."
            rows.append({"query_id": f"framing:{key}:{lang}", "kind": "framing", "key": key, "lang": lang, "text": text})
    return pd.DataFrame(rows)


def load_model(cfg: dict, model_key: str):
    import torch
    from sentence_transformers import SentenceTransformer

    mcfg = cfg["embedding"]["models"][model_key]
    dtype = getattr(torch, mcfg.get("dtype", "float32"))
    model_kwargs = {"dtype": dtype}
    if mcfg.get("attn_implementation"):
        model_kwargs["attn_implementation"] = mcfg["attn_implementation"]
    tokenizer_kwargs = {"padding_side": mcfg["padding_side"]} if mcfg.get("padding_side") else None
    device = cfg["embedding"].get("device", "cuda") if torch.cuda.is_available() else "cpu"
    try:
        model = SentenceTransformer(mcfg["hf_id"], device=device, model_kwargs=model_kwargs, tokenizer_kwargs=tokenizer_kwargs)
    except TypeError:  # older transformers expect torch_dtype
        model_kwargs["torch_dtype"] = model_kwargs.pop("dtype")
        model = SentenceTransformer(mcfg["hf_id"], device=device, model_kwargs=model_kwargs, tokenizer_kwargs=tokenizer_kwargs)
    model.max_seq_length = int(mcfg.get("max_seq_length", 512))
    return model, mcfg, device


def encode(model, texts: list[str], batch_size: int, prompt: str | None = None) -> np.ndarray:
    kwargs = dict(batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    if prompt:
        kwargs["prompt"] = prompt
    emb = model.encode(texts, **kwargs)
    emb = np.asarray(emb, dtype=np.float32)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    return emb / np.clip(norms, 1e-12, None)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 2: embed chunks with one model.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", required=True, help="key under embedding.models (qwen3_embedding_8b | bge_m3)")
    ap.add_argument("--variant", default="original", choices=["original", "translated_en"])
    ap.add_argument("--chunks", default="chunks.csv", help="chunks.csv | chunks_noceremonial.csv")
    ap.add_argument("--skip-queries", action="store_true")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    seed_everything(int(cfg["random_seed"]))
    proc = path_for(cfg, "data_processed") / ("" if args.variant == "original" else args.variant)
    chunks_path = proc / args.chunks
    if not chunks_path.exists():
        print(f"[embed] {chunks_path} not found — run preprocess/chunking for variant {args.variant} first")
        return 1
    out_dir = path_for(cfg, "artifacts_embeddings")
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = artifact_suffix(args.variant, args.chunks)
    base = out_dir / f"{args.model}{suffix}"

    chunks = pd.read_csv(chunks_path, dtype={"chunk_text": str}, keep_default_na=False)
    texts = chunks["chunk_text"].astype(str).tolist()

    t0 = time.time()
    model, mcfg, device = load_model(cfg, args.model)
    t_load = time.time() - t0
    print(f"[embed] {args.model} ({mcfg['hf_id']}) on {device}, dtype={mcfg.get('dtype')}, "
          f"max_seq_length={model.max_seq_length}, loaded in {t_load:.0f}s")

    t1 = time.time()
    emb = encode(model, texts, int(mcfg.get("batch_size", 16)))
    t_enc = time.time() - t1
    np.save(base.with_name(base.name + "_chunks.npy"), emb)
    chunks.to_parquet(base.with_name(base.name + "_index.parquet"), index=False)
    print(f"[embed] {emb.shape[0]} chunks -> dim {emb.shape[1]} in {t_enc:.1f}s "
          f"({emb.shape[0] / max(t_enc, 1e-9):.1f} chunks/s)")

    run = {"model_key": args.model, "hf_id": mcfg["hf_id"], "device": device, "dtype": mcfg.get("dtype"),
           "attn_implementation": mcfg.get("attn_implementation"), "variant": args.variant, "chunks_file": args.chunks,
           "n_chunks": int(emb.shape[0]), "dim": int(emb.shape[1]), "load_seconds": round(t_load, 1),
           "encode_seconds": round(t_enc, 1), "normalized": True, "random_seed": int(cfg["random_seed"])}

    if not args.skip_queries:
        q = build_query_table(cfg)
        prompt = None
        tmpl = mcfg.get("query_instruction_template")
        if tmpl:
            task = cfg["theme_scoring"]["query_task_instruction"]
            prompt = tmpl.format(task=task, text="")  # sentence-transformers prepends the prompt
        qemb = encode(model, q["text"].tolist(), int(mcfg.get("batch_size", 16)), prompt=prompt)
        np.save(out_dir / f"{args.model}_queries.npy", qemb)
        q.to_parquet(out_dir / f"{args.model}_queries.parquet", index=False)
        run["n_queries"] = int(len(q))
        run["query_prompt"] = prompt
        print(f"[embed] {len(q)} concept queries embedded (prompt={'yes' if prompt else 'no'})")

    (base.with_name(base.name + "_run.json")).write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[embed] artifacts: {base.name}_chunks.npy, {base.name}_index.parquet, {args.model}_queries.*")
    return 0


if __name__ == "__main__":
    sys.exit(main())
