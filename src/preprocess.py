"""Phase 1a — conservative text cleaning.

Usage:
    python -m src.preprocess                     # data/original  -> data/processed/
    python -m src.preprocess --variant translated_en   # data/translated_en -> data/processed/translated_en/

Removes only obvious non-speech artifacts (speaker labels, stage directions, HTML, URLs,
timestamps, repeated header/footer lines, symbol-only separator lines, file-specific blocks
declared in config.yaml) and normalises whitespace. Every removal is logged to
preprocessing_report.md. Original files are never modified.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import textutils as tu
from .config import PROJECT_ROOT, leader_slugs, load_config, path_for
from .inventory import discover_files, load_metadata

ZERO_WIDTH_RE = re.compile(r"[​‌‍﻿]")
SYMBOL_LINE_RE = re.compile(r"^[ \t]*[^\w\s]{1,5}[ \t]*$", re.M)


def _log(removals: list[dict], rule: str, removed: str, note: str = "") -> None:
    removed = removed.strip()
    if removed:
        removals.append({"rule": rule, "chars": len(removed), "removed": removed[:300], "note": note})


def clean_speech(text: str, filename: str, pp: dict) -> tuple[str, list[dict], int]:
    """Return (clean_text, removals, whitespace_chars_changed)."""
    removals: list[dict] = []
    text = text.replace(" ", " ")
    text = ZERO_WIDTH_RE.sub("", text)

    # 1. file-specific block removal (declared in config)
    rule = (pp.get("file_rules") or {}).get(filename)
    if rule and rule.get("drop_paragraphs_before_match"):
        pat = re.compile(rule["drop_paragraphs_before_match"])
        paras = tu.split_paragraphs(text)
        idx = next((i for i, p in enumerate(paras) if pat.search(p)), None)
        if idx is None:
            removals.append({"rule": "file_rule_not_applied", "chars": 0, "removed": "",
                             "note": f"pattern {rule['drop_paragraphs_before_match']!r} not found; nothing removed"})
        elif idx > 0:
            _log(removals, "file_rule:drop_paragraphs_before_match", "\n\n".join(paras[:idx]), rule.get("reason", ""))
            text = "\n\n".join(paras[idx:])

    # 2. leading speaker label
    if pp.get("strip_leading_speaker_label", True):
        stripped = text.lstrip()
        done = False
        for pat in pp.get("speaker_label_patterns", []) or []:
            m = re.match(pat, stripped, flags=re.I)
            if m:
                _log(removals, "speaker_label_prefix", m.group(0), "configured pattern")
                text = stripped[m.end():]
                done = True
                break
        if not done:
            m = tu.SPEAKER_LABEL_RE.match(stripped)
            if m:
                _log(removals, "speaker_label_prefix", m.group(0), "generic Title-Case label at file start")
                text = stripped[m.end():]

    # 3. artifact regexes
    for flag, regex, key in (
        ("html", tu.HTML_RE, "remove_html"),
        ("url", tu.URL_RE, "remove_urls"),
        ("timestamp", tu.TIMESTAMP_RE, "remove_timestamps"),
        ("stage_direction", tu.STAGE_DIRECTION_RE, "remove_stage_directions"),
    ):
        if pp.get(key, True):
            for m in regex.finditer(text):
                _log(removals, flag, m.group(0))
            text = regex.sub(" ", text)

    # 4. symbol-only lines (e.g. "*")
    if pp.get("remove_symbol_only_lines", True):
        for m in SYMBOL_LINE_RE.finditer(text):
            _log(removals, "symbol_only_line", m.group(0))
        text = SYMBOL_LINE_RE.sub("", text)

    # 5. repeated header/footer lines
    min_rep = int(pp.get("remove_repeated_lines_min_count", 3) or 0)
    if min_rep:
        for line, n in tu.repeated_lines(text, min_rep):
            _log(removals, "repeated_line", line, f"occurred {n}x")
            text = "\n".join(l for l in text.split("\n") if l.strip() != line)

    # 6. whitespace normalisation (wording unchanged)
    before = text
    if pp.get("collapse_whitespace", True):
        text = re.sub(r"[^\S\n]+", " ", text)
        text = "\n".join(l.strip() for l in text.split("\n"))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
    ws_changed = abs(len(before) - len(text))
    return text, removals, ws_changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 1a: conservative cleaning of the speech files.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--variant", default="original", choices=["original", "translated_en"])
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    pp = cfg.get("preprocess", {})
    src_dir = path_for(cfg, "data_original" if args.variant == "original" else "data_translated_en")
    out_dir = path_for(cfg, "data_processed") / ("" if args.variant == "original" else args.variant)
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = load_metadata(path_for(cfg, "metadata"))

    files = discover_files(src_dir, leader_slugs(cfg), recurse=True)
    if not files:
        print(f"[preprocess] no .txt files under {src_dir} — nothing to do (variant={args.variant})")
        return 0

    rows, report = [], []
    report.append(f"# Preprocessing report — variant `{args.variant}`\n")
    report.append(f"Generated {datetime.now():%Y-%m-%d %H:%M}. Source: `{src_dir.relative_to(PROJECT_ROOT)}`. "
                  "Original files were not modified. Every removal is listed below.\n")
    totals: dict[str, int] = {}
    for leader, path in files:
        raw, enc = tu.read_text(path)
        if not raw.strip():
            report.append(f"## {path.name}\n\nEMPTY FILE — skipped.\n")
            continue
        clean, removals, ws = clean_speech(raw, path.name, pp)
        meta = metadata.get(path.name, {})
        speech_id = path.stem
        rows.append({
            "speech_id": speech_id, "leader": leader, "filename": path.name,
            "language": meta.get("language", cfg["leaders"].get(leader, {}).get("language", "")),
            "speech_date": meta.get("speech_date", ""), "date_confidence": meta.get("date_confidence", ""),
            "speech_type": meta.get("speech_type", ""), "source": meta.get("source", ""),
            "title": meta.get("title", ""), "review_status": meta.get("review_status", ""),
            "word_count_raw": tu.count_words(raw), "word_count_clean": tu.count_words(clean),
            "paragraph_count": len(tu.split_paragraphs(clean)),
            "chars_removed": sum(r["chars"] for r in removals), "whitespace_chars_changed": ws,
            "n_removals": len(removals), "clean_text": clean,
        })
        report.append(f"## {path.name}  ({leader})\n")
        report.append(f"words raw → clean: {tu.count_words(raw)} → {tu.count_words(clean)} · "
                      f"removals: {len(removals)} ({sum(r['chars'] for r in removals)} chars) · whitespace chars changed: {ws}\n")
        for r in removals:
            totals[r["rule"]] = totals.get(r["rule"], 0) + 1
            snippet = r["removed"].replace("\n", " ⏎ ")
            report.append(f"- **{r['rule']}** ({r['chars']} chars){' — ' + r['note'] if r['note'] else ''}: `{snippet}`")
        if not removals:
            report.append("- no content removed (whitespace normalisation only)")
        report.append("")

    df = pd.DataFrame(rows)
    if df["speech_id"].duplicated().any():
        raise SystemExit("duplicate speech_id (file stems must be unique across leaders)")
    df.to_csv(out_dir / "speeches_clean.csv", index=False, encoding="utf-8")
    summary = ["## Summary\n", f"{len(df)} speeches · {int(df['word_count_raw'].sum()):,} raw words → "
               f"{int(df['word_count_clean'].sum()):,} clean words · removal counts by rule: "
               + (", ".join(f"`{k}`×{v}" for k, v in sorted(totals.items())) or "none"), ""]
    report[2:2] = summary
    (out_dir / "preprocessing_report.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(summary))
    print(f"[preprocess] wrote {out_dir / 'speeches_clean.csv'} and preprocessing_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
