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
