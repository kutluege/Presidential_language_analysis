"""Paragraph-based semantic chunking.

Phase 0 uses `chunk_paragraphs` only to *estimate* chunk counts; Phase 1 calls the same function
to build data/processed/chunks.csv, so estimates and real counts agree by construction.

Algorithm (no overlapping windows):
  1. Paragraphs longer than `max_tokens` are split at sentence boundaries into pieces <= max.
  2. Neighbouring pieces are merged greedily until a buffer reaches `min_tokens`, never exceeding
     `max_tokens`. A buffer is flushed at the first paragraph boundary at or above `min_tokens`,
     so chunk edges stay on natural paragraph edges.
  3. Orphan chunks shorter than `min_tokens` are absorbed into the smaller neighbour if the merged
     size stays within `max_tokens * short_chunk_merge_tolerance`; otherwise they are kept and
     marked `is_short`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

from .textutils import split_sentences

TokenCounter = Callable[[Sequence[str]], list[int]]


@dataclass
class Chunk:
    text: str
    token_count: int
    paragraph_indices: list[int] = field(default_factory=list)
    is_short: bool = False


def _split_long_paragraph(text: str, tokens: int, max_tokens: int, count_many: TokenCounter) -> list[tuple[str, int]]:
    if tokens <= max_tokens:
        return [(text, tokens)]
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return [(text, tokens)]  # cannot split further without breaking a sentence
    sent_tokens = count_many(sentences)
    pieces: list[tuple[str, int]] = []
    buf: list[str] = []
    buf_tok = 0
    for s, t in zip(sentences, sent_tokens):
        if buf and buf_tok + t > max_tokens:
            pieces.append((" ".join(buf), buf_tok))
            buf, buf_tok = [], 0
        buf.append(s)
        buf_tok += t
    if buf:
        pieces.append((" ".join(buf), buf_tok))
    return pieces


def chunk_paragraphs(
    paragraphs: Sequence[str],
    count_many: TokenCounter,
    min_tokens: int = 80,
    max_tokens: int = 180,
    short_chunk_merge_tolerance: float = 1.15,
) -> list[Chunk]:
    paragraphs = [p for p in paragraphs if p.strip()]
    if not paragraphs:
        return []
    para_tokens = count_many(list(paragraphs))

    # 1. split over-long paragraphs into sentence-bounded pieces
    pieces: list[tuple[str, int, int]] = []  # (text, tokens, paragraph_index)
    for idx, (p, t) in enumerate(zip(paragraphs, para_tokens)):
        for text, tok in _split_long_paragraph(p, t, max_tokens, count_many):
            pieces.append((text, tok, idx))

    # 2. greedy merge to reach min_tokens without exceeding max_tokens
    chunks: list[Chunk] = []
    buf_text: list[str] = []
    buf_tok = 0
    buf_idx: list[int] = []

    def flush() -> None:
        nonlocal buf_text, buf_tok, buf_idx
        if buf_text:
            chunks.append(Chunk("\n\n".join(buf_text), buf_tok, sorted(set(buf_idx))))
        buf_text, buf_tok, buf_idx = [], 0, []

    for text, tok, idx in pieces:
        if buf_text and buf_tok + tok > max_tokens:
            flush()
        buf_text.append(text)
        buf_tok += tok
        buf_idx.append(idx)
        if buf_tok >= min_tokens:
            flush()
    flush()

    # 3. absorb short orphans where possible
    limit = int(max_tokens * short_chunk_merge_tolerance)
    i = 0
    while i < len(chunks):
        c = chunks[i]
        if c.token_count >= min_tokens or len(chunks) == 1:
            i += 1
            continue
        prev_c = chunks[i - 1] if i > 0 else None
        next_c = chunks[i + 1] if i + 1 < len(chunks) else None
        candidates = [(n.token_count, j, n) for j, n in ((i - 1, prev_c), (i + 1, next_c)) if n is not None]
        candidates.sort()
        merged = False
        for _, j, n in candidates:
            if n.token_count + c.token_count <= limit:
                first, second = (n, c) if j < i else (c, n)
                new = Chunk(
                    first.text + "\n\n" + second.text,
                    first.token_count + second.token_count,
                    sorted(set(first.paragraph_indices + second.paragraph_indices)),
                )
                lo, hi = min(i, j), max(i, j)
                chunks[lo : hi + 1] = [new]
                merged = True
                break
        if not merged:
            c.is_short = True
            i += 1
        # if merged, re-examine the merged chunk at position min(i, j)
    return chunks


def chunk_counts_summary(chunks: Sequence[Chunk]) -> dict:
    if not chunks:
        return {"n_chunks": 0, "n_short": 0, "mean_tokens": 0.0, "min_tokens": 0, "max_tokens": 0}
    toks = [c.token_count for c in chunks]
    return {
        "n_chunks": len(chunks),
        "n_short": sum(c.is_short for c in chunks),
        "mean_tokens": round(sum(toks) / len(toks), 1),
        "min_tokens": min(toks),
        "max_tokens": max(toks),
    }


# ----------------------------------------------------------------------------------------------
# Phase 1b CLI: speeches_clean.csv -> chunks.csv
# ----------------------------------------------------------------------------------------------
CHUNK_COLUMNS = [
    "chunk_id", "speech_id", "leader", "language", "speech_date", "speech_type", "source",
    "chunk_index", "n_chunks_in_speech", "relative_position", "chunk_text", "token_count",
    "word_count", "paragraph_indices", "is_short",
]


def build_chunks(speeches: "pd.DataFrame", cfg: dict, count_many: TokenCounter, strip_ceremonial: bool = False):
    import pandas as pd  # local import keeps the pure algorithm dependency-free
    from .textutils import count_words, split_paragraphs

    ch = cfg["chunking"]
    cer = (cfg.get("preprocess", {}) or {}).get("ceremonial", {}) or {}
    rows, log = [], []
    for sp in speeches.itertuples():
        paragraphs = split_paragraphs(str(sp.clean_text))
        offset = 0
        if strip_ceremonial:
            lead, trail = int(cer.get("strip_leading_paragraphs", 1)), int(cer.get("strip_trailing_paragraphs", 2))
            if len(paragraphs) >= int(cer.get("min_paragraphs_to_apply", 6)):
                dropped = paragraphs[:lead] + (paragraphs[-trail:] if trail else [])
                paragraphs = paragraphs[lead: len(paragraphs) - trail if trail else None]
                offset = lead
                log.append({"speech_id": sp.speech_id, "dropped_paragraphs": lead + trail,
                            "dropped_words": sum(count_words(p) for p in dropped)})
        chunks = chunk_paragraphs(
            paragraphs, count_many,
            min_tokens=ch["chunk_min_tokens"], max_tokens=ch["chunk_max_tokens"],
            short_chunk_merge_tolerance=ch.get("short_chunk_merge_tolerance", 1.15),
        )
        n = len(chunks)
        for i, c in enumerate(chunks):
            rows.append({
                "chunk_id": f"{sp.speech_id}_c{i:03d}", "speech_id": sp.speech_id, "leader": sp.leader,
                "language": sp.language, "speech_date": sp.speech_date, "speech_type": sp.speech_type,
                "source": sp.source, "chunk_index": i, "n_chunks_in_speech": n,
                "relative_position": round(i / max(n - 1, 1), 3), "chunk_text": c.text,
                "token_count": c.token_count, "word_count": count_words(c.text),
                "paragraph_indices": ";".join(str(p + offset) for p in c.paragraph_indices),
                "is_short": c.is_short,
            })
    return pd.DataFrame(rows, columns=CHUNK_COLUMNS), log


def main(argv=None) -> int:
    import argparse
    import sys

    import pandas as pd

    from .config import load_config, path_for
    from .tokenizer_utils import get_token_counter

    ap = argparse.ArgumentParser(description="Phase 1b: paragraph-based chunking of cleaned speeches.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--variant", default="original", choices=["original", "translated_en"])
    ap.add_argument("--strip-ceremonial", action="store_true", help="robustness variant: drop opening/closing paragraphs")
    ap.add_argument("--no-tokenizer", action="store_true")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    proc = path_for(cfg, "data_processed") / ("" if args.variant == "original" else args.variant)
    src = proc / "speeches_clean.csv"
    if not src.exists():
        print(f"[chunking] {src} not found — run `python -m src.preprocess --variant {args.variant}` first")
        return 1
    speeches = pd.read_csv(src, dtype=str, keep_default_na=False)
    count_many, method = get_token_counter(cfg, allow_tokenizer=not args.no_tokenizer)
    df, log = build_chunks(speeches, cfg, count_many, strip_ceremonial=args.strip_ceremonial)
    out = proc / ("chunks_noceremonial.csv" if args.strip_ceremonial else "chunks.csv")
    df.to_csv(out, index=False, encoding="utf-8")

    per_leader = df.groupby("leader").agg(chunks=("chunk_id", "count"), speeches=("speech_id", "nunique"),
                                          mean_tokens=("token_count", "mean"), short=("is_short", "sum"))
    print(f"[chunking] tokenizer: {method}")
    print(per_leader.round(1).to_string())
    print(f"[chunking] {len(df)} chunks · tokens min/median/max = {df.token_count.min()}/{int(df.token_count.median())}/{df.token_count.max()}"
          f" · short chunks = {int(df.is_short.sum())}")
    if log:
        print(f"[chunking] ceremonial paragraphs stripped in {len(log)} speeches "
              f"({sum(l['dropped_words'] for l in log)} words)")
    print(f"[chunking] wrote {out}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
