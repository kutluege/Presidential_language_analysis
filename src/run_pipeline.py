"""Run the whole pipeline in order (Phases 1–9) for the primary and robustness models.

Usage:
    python -m src.run_pipeline                 # everything after Phase 0
    python -m src.run_pipeline --from embed    # resume from a step
    python -m src.run_pipeline --skip-embed    # reuse cached embeddings
    python -m src.run_pipeline --variant translated_en   # once translations exist (English-normalised robustness run)

Steps: preprocess → chunking (+ no-ceremonial) → embed (2 models × 2 chunk sets) → theme_scoring →
aggregate → geometry → clustering (+ leader-centred) → bootstrap → visualization → robustness → generate_report.
Phase 0 (`python -m src.inventory`) is run separately and reviewed before this.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time

from .config import load_config, primary_model_key

STEPS = ["preprocess", "chunking", "embed", "theme_scoring", "emotion", "aggregate", "geometry", "style", "clustering", "bootstrap",
         "visualization", "robustness", "generate_report"]


def run(mod: str, *args: str) -> None:
    cmd = [sys.executable, "-m", f"src.{mod}", *args]
    print(f"\n$ {' '.join(cmd[2:])}", flush=True)
    t0 = time.time()
    res = subprocess.run(cmd, env={**__import__('os').environ, "PYTHONIOENCODING": "utf-8"})
    if res.returncode != 0:
        raise SystemExit(f"step failed: {mod} {' '.join(args)} (exit {res.returncode})")
    print(f"  ↳ done in {time.time() - t0:.0f}s", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run Phases 1–9.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--from", dest="start", default="preprocess", choices=STEPS)
    ap.add_argument("--skip-embed", action="store_true")
    ap.add_argument("--variant", default="original", choices=["original", "translated_en"])
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    pk = primary_model_key(cfg)
    rk = next(k for k, m in cfg["embedding"]["models"].items() if m["hf_id"] == cfg["robustness_embedding_model"])
    models = [pk, rk]
    var = ["--variant", args.variant]
    vsuf = "" if args.variant == "original" else f"_{args.variant}"
    combos = [(m, s) for m in models for s in (vsuf, vsuf + "_noceremonial")]
    start = STEPS.index(args.start)

    def active(step: str) -> bool:
        return STEPS.index(step) >= start

    if active("preprocess"):
        run("preprocess", *var)
    if active("chunking"):
        run("chunking", *var)
        run("chunking", *var, "--strip-ceremonial")
    if active("embed") and not args.skip_embed:
        for m in models:
            run("embed", "--model", m, *var, "--chunks", "chunks.csv")
            run("embed", "--model", m, *var, "--chunks", "chunks_noceremonial.csv")
    if active("theme_scoring"):
        for m, s in combos:
            run("theme_scoring", "--model", m, "--suffix", s)
    if active("emotion"):
        for s in (vsuf, vsuf + "_noceremonial"):
            run("emotion", "--suffix", s)
    for step in ("aggregate", "geometry"):
        if active(step):
            for m, s in combos:
                run(step, "--model", m, "--suffix", s)
    if active("style"):
        for m, s in combos:
            run("style", "--model", m, "--suffix", s)
    if active("clustering"):
        run("clustering", "--model", pk, "--suffix", vsuf)
        run("clustering", "--model", pk, "--suffix", vsuf, "--center-by-leader")
    if active("bootstrap"):
        for m, s in combos:
            run("bootstrap", "--model", m, "--suffix", s)
    if active("visualization"):
        run("visualization", "--model", pk, "--suffix", vsuf)
    if active("robustness"):
        run("robustness")
    if active("generate_report"):
        run("generate_report")
        run("generate_brief")
    print("\npipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
