"""Token counting for chunk sizing.

Prefers the primary embedding model's tokenizer (small download, no weights). Falls back to a
words-per-token heuristic and reports which method was used so every report can state it.
"""
from __future__ import annotations

import os
from typing import Callable, Sequence

from .textutils import count_words

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")  # Windows without Developer Mode

TokenCounter = Callable[[Sequence[str]], list[int]]


def get_token_counter(cfg: dict, allow_tokenizer: bool = True) -> tuple[TokenCounter, str]:
    ch = cfg["chunking"]
    name = ch["tokenizer"]
    ratio = float(ch.get("fallback_tokens_per_word", 1.5))

    def heuristic(texts: Sequence[str]) -> list[int]:
        return [int(round(count_words(t) * ratio)) for t in texts]

    if not allow_tokenizer:
        return heuristic, f"heuristic_words_x{ratio} (tokenizer disabled)"
    try:
        from transformers import AutoTokenizer

        tok = AutoTokenizer.from_pretrained(name)

        def count_many(texts: Sequence[str]) -> list[int]:
            if not texts:
                return []
            enc = tok(list(texts), add_special_tokens=False, return_attention_mask=False)
            return [len(ids) for ids in enc["input_ids"]]

        return count_many, f"hf_tokenizer:{name}"
    except Exception as exc:  # network / missing package / HF error
        return heuristic, f"heuristic_words_x{ratio} (tokenizer unavailable: {type(exc).__name__}: {exc})"
