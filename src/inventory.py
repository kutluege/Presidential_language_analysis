"""Phase 0 — corpus inventory and validation.

Usage (from the project root):
    python -m src.inventory                       # data/original, recursive
    python -m src.inventory --input-dir . --no-recurse   # flat files still sitting in the root
    python -m src.inventory --no-tokenizer        # skip the HF tokenizer, use the word heuristic

Read-only with respect to the speech files. Produces:
    outputs/tables/corpus_inventory.csv
    outputs/tables/suspicious_files.csv
    outputs/phase0_report.md
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import textutils as tu
from .chunking import chunk_counts_summary, chunk_paragraphs
from .config import PROJECT_ROOT, leader_slugs, load_config, path_for
from .tokenizer_utils import get_token_counter

META_FIELDS = ["speech_date", "speech_type", "source", "title"]
FILENAME_YEAR_RE = re.compile(r"(19[5-9]\d|20[0-4]\d)")

INVENTORY_COLUMNS = [
    "leader", "filename", "relative_path", "language_expected", "language_detected", "encoding",
    "word_count", "char_count", "paragraph_count", "token_count", "estimated_chunk_count",
    "short_chunks", "mean_chunk_tokens", "speech_date", "date_confidence", "speech_type", "source",
    "title", "review_status", "notes", "missing_metadata", "years_in_text", "flags",
]


# ----------------------------------------------------------------------------------------------
def discover_files(input_dir: Path, leaders: list[str], recurse: bool = True) -> list[tuple[str, Path]]:
    pattern = input_dir.rglob("*.txt") if recurse else input_dir.glob("*.txt")
    found: list[tuple[str, Path]] = []
    for p in sorted(pattern):
        rel = p.relative_to(input_dir)
        leader = "unknown"
        if len(rel.parts) > 1 and rel.parts[0].lower() in leaders:
            leader = rel.parts[0].lower()
        else:
            m = re.match(r"^([A-Za-z]+)", p.stem)
            if m and m.group(1).lower() in leaders:
                leader = m.group(1).lower()
        found.append((leader, p))
    return found


def load_metadata(meta_path: Path) -> dict[str, dict]:
    if not meta_path.exists():
        return {}
    df = pd.read_csv(meta_path, dtype=str, keep_default_na=False, encoding="utf-8")
    return {row["filename"]: row.to_dict() for _, row in df.iterrows()}


def md_table(rows: list[dict], columns: list[str], headers: list[str] | None = None) -> str:
    headers = headers or columns
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "\\|").replace("\n", " ") for c in columns) + " |")
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------
def build_inventory(cfg: dict, input_dir: Path, recurse: bool, use_tokenizer: bool) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    inv_cfg = cfg["inventory"]
    ch_cfg = cfg["chunking"]
    leaders = leader_slugs(cfg)
    metadata = load_metadata(path_for(cfg, "metadata"))
    count_many, token_method = get_token_counter(cfg, allow_tokenizer=use_tokenizer)

    files = discover_files(input_dir, leaders, recurse)
    rows: list[dict] = []
    flags: dict[str, list[tuple[str, str]]] = defaultdict(list)
    shingles: dict[str, set] = {}
    hashes: dict[str, str] = {}

    for leader, path in files:
        fname = path.name
        text, enc = tu.read_text(path)
        paragraphs = tu.split_paragraphs(text)
        words = tu.count_words(text)
        expected_lang = cfg["leaders"].get(leader, {}).get("language", "")
        detected, _scores = tu.detect_language(text, inv_cfg.get("language_min_ratio", 0.03))

        for flag, detail in tu.scan_artifacts(text, inv_cfg):
            flags[fname].append((flag, detail))
        if leader == "unknown":
            flags[fname].append(("unknown_leader", "filename prefix / folder does not match a configured leader"))
        if 0 < words < inv_cfg["min_words_warn"]:
            flags[fname].append(("very_short", f"{words} words < {inv_cfg['min_words_warn']}"))
        if words and detected == "unknown":
            flags[fname].append(("language_unknown", "stopword heuristic could not identify the language"))
        elif words and expected_lang and detected != expected_lang:
            flags[fname].append(("language_mismatch", f"expected {expected_lang}, detected {detected}"))

        chunks = chunk_paragraphs(
            paragraphs, count_many,
            min_tokens=ch_cfg["chunk_min_tokens"], max_tokens=ch_cfg["chunk_max_tokens"],
            short_chunk_merge_tolerance=ch_cfg.get("short_chunk_merge_tolerance", 1.15),
        )
        summary = chunk_counts_summary(chunks)

        meta = metadata.get(fname)
        if meta is None:
            flags[fname].append(("not_in_metadata", "no row in data/metadata.csv"))
            meta = {}
        missing = [f for f in META_FIELDS if not str(meta.get(f, "")).strip()]
        if missing:
            flags[fname].append(("missing_metadata", ", ".join(missing)))
        review = str(meta.get("review_status", "")).strip().lower()
        if review and review != "ok":
            flags[fname].append((f"review:{review}", str(meta.get("notes", "")).strip()[:160]))
        fy = FILENAME_YEAR_RE.search(path.stem)
        sd = str(meta.get("speech_date", "")).strip()
        if fy and sd and sd[:4] != fy.group(1):
            flags[fname].append(("filename_year_vs_speech_date", f"filename says {fy.group(1)}, speech_date is {sd}"))

        if words:
            hashes[fname] = hashlib.sha1(tu.normalize_for_hash(text).encode("utf-8")).hexdigest()
            shingles[fname] = tu.word_shingles(text, inv_cfg.get("shingle_size", 8))

        rows.append({
            "leader": leader,
            "filename": fname,
            "relative_path": str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path),
            "language_expected": expected_lang,
            "language_detected": detected if words else "",
            "encoding": enc,
            "word_count": words,
            "char_count": len(text),
            "paragraph_count": len(paragraphs),
            "token_count": sum(c.token_count for c in chunks),
            "estimated_chunk_count": summary["n_chunks"],
            "short_chunks": summary["n_short"],
            "mean_chunk_tokens": summary["mean_tokens"],
            "speech_date": sd,
            "date_confidence": str(meta.get("date_confidence", "")).strip(),
            "speech_type": str(meta.get("speech_type", "")).strip(),
            "source": str(meta.get("source", "")).strip(),
            "title": str(meta.get("title", "")).strip(),
            "review_status": str(meta.get("review_status", "")).strip(),
            "notes": str(meta.get("notes", "")).strip(),
            "missing_metadata": ";".join(missing),
            "years_in_text": ";".join(str(y) for y in tu.years_in_text(text)),
        })

    # --- pairwise duplicate / fragment detection (files with text only) ---------------------
    names = [n for n in hashes]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if hashes[a] == hashes[b]:
                flags[a].append(("exact_duplicate", f"identical to {b}"))
                flags[b].append(("exact_duplicate", f"identical to {a}"))
                continue
            jac = tu.jaccard(shingles[a], shingles[b])
            if jac >= inv_cfg["near_duplicate_jaccard"]:
                flags[a].append(("near_duplicate", f"jaccard {jac:.2f} with {b}"))
                flags[b].append(("near_duplicate", f"jaccard {jac:.2f} with {a}"))
                continue
            cont = tu.containment(shingles[a], shingles[b])
            if cont >= inv_cfg.get("fragment_containment", 0.5):
                small, big = (a, b) if len(shingles[a]) <= len(shingles[b]) else (b, a)
                flags[small].append(("possible_fragment_of", f"{cont:.0%} of its 8-word shingles occur in {big}"))
                flags[big].append(("contains_fragment", f"{small} appears to be an excerpt of this file"))

    # --- leader-level flags -----------------------------------------------------------------
    df = pd.DataFrame(rows, columns=[c for c in INVENTORY_COLUMNS if c != "flags"])
    min_speeches = cfg["corpus"]["min_speeches_per_leader"]
    for leader, grp in df.groupby("leader"):
        n_text = int((grp["word_count"] > 0).sum())
        if leader != "unknown" and n_text < min_speeches:
            for fname in grp["filename"]:
                flags[fname].append(("below_min_speeches", f"{leader} has {n_text} speech(es) with text < {min_speeches}"))
        types = [t for t in grp["speech_type"] if t]
        if types:
            majority, n_major = Counter(types).most_common(1)[0]
            if n_major / len(grp) >= 0.6:
                for fname, t in zip(grp["filename"], grp["speech_type"]):
                    if t != majority:
                        flags[fname].append(("speech_type_outlier", f"'{t or 'blank'}' vs leader majority '{majority}'"))
            else:
                mix = ", ".join(f"{k}×{v}" for k, v in Counter(t or "blank" for t in grp["speech_type"]).items())
                for fname in grp["filename"]:
                    flags[fname].append(("mixed_speech_types", f"{leader} has no dominant speech type: {mix}"))

    df["flags"] = df["filename"].map(lambda f: ";".join(sorted({fl for fl, _ in flags.get(f, [])})))
    df = df[INVENTORY_COLUMNS]

    susp_rows = [
        {"filename": f, "leader": df.loc[df["filename"] == f, "leader"].iloc[0], "flag": fl, "detail": d}
        for f in df["filename"] for fl, d in flags.get(f, [])
    ]
    susp = pd.DataFrame(susp_rows, columns=["filename", "leader", "flag", "detail"])

    orphans = sorted(set(metadata) - set(df["filename"]))
    info = {"token_method": token_method, "input_dir": str(input_dir), "metadata_orphans": orphans}
    return df, susp, info


# ----------------------------------------------------------------------------------------------
def write_report(cfg: dict, df: pd.DataFrame, susp: pd.DataFrame, info: dict, report_path: Path) -> str:
    ch = cfg["chunking"]
    leaders_cfg = cfg["leaders"]
    min_speeches = cfg["corpus"]["min_speeches_per_leader"]
    lines: list[str] = []
    add = lines.append

    add("# Phase 0 — Corpus Inventory Report")
    add("")
    add(f"Generated: {datetime.now():%Y-%m-%d %H:%M} · input: `{info['input_dir']}` · config: `{Path(cfg['_config_path']).name}`  ")
    add(f"Token counting: `{info['token_method']}`  ")
    add("")
    add("> Scope: this report describes the *collected speech files* only. It makes no claim about the speakers.")
    add("")

    # 1. speeches per leader
    add("## 1. Speeches per leader")
    add("")
    lead_rows = []
    blockers: list[str] = []
    for slug, lc in leaders_cfg.items():
        grp = df[df["leader"] == slug]
        n_files, n_text = len(grp), int((grp["word_count"] > 0).sum())
        n_empty = n_files - n_text
        status = "OK" if n_text >= min_speeches else ("NO TEXT" if n_text == 0 else f"BELOW MIN ({n_text} < {min_speeches})")
        if n_text < min_speeches:
            blockers.append(f"{lc['short_name']}: {status.lower()}")
        langs = ", ".join(f"{k}×{v}" for k, v in Counter(grp.loc[grp['word_count'] > 0, 'language_detected']).items()) or "—"
        lead_rows.append({
            "leader": lc["display_name"], "expected_lang": lc["language"], "files": n_files, "with_text": n_text,
            "empty": n_empty, "words": int(grp["word_count"].sum()),
            "mean_words": int(round(grp.loc[grp["word_count"] > 0, "word_count"].mean())) if n_text else 0,
            "est_chunks": int(grp["estimated_chunk_count"].sum()), "detected_langs": langs, "status": status,
        })
    unknown = df[df["leader"] == "unknown"]
    if len(unknown):
        lead_rows.append({"leader": "(unrecognized)", "expected_lang": "", "files": len(unknown), "with_text": int((unknown["word_count"] > 0).sum()),
                          "empty": int((unknown["word_count"] == 0).sum()), "words": int(unknown["word_count"].sum()), "mean_words": "",
                          "est_chunks": int(unknown["estimated_chunk_count"].sum()), "detected_langs": "", "status": "UNKNOWN LEADER"})
    add(md_table(lead_rows, ["leader", "expected_lang", "files", "with_text", "empty", "words", "mean_words", "est_chunks", "detected_langs", "status"]))
    add("")
    tot_text = int((df["word_count"] > 0).sum())
    add(f"Total: **{len(df)} files**, {tot_text} with text, {len(df) - tot_text} empty · **{int(df['word_count'].sum()):,} words** · **{int(df['estimated_chunk_count'].sum())} estimated chunks**.")
    add("")

    # 2. languages
    add("## 2. Language distribution (files with text)")
    add("")
    lang_counts = Counter(df.loc[df["word_count"] > 0, "language_detected"])
    add(md_table([{"language": k or "?", "files": v} for k, v in sorted(lang_counts.items())], ["language", "files"]))
    mism = susp[susp["flag"].isin(["language_mismatch", "language_unknown"])]
    add("")
    add("Language mismatches: " + ("none." if mism.empty else "; ".join(f"`{r.filename}` ({r.detail})" for r in mism.itertuples())))
    add("")
    add("_Detection is a stopword-ratio heuristic meant to catch the wrong language in the wrong folder, not a linguistic classifier._")
    add("")

    # 3. word counts
    add("## 3. Word counts per speech")
    add("")
    cols = ["leader", "filename", "word_count", "paragraph_count", "token_count", "estimated_chunk_count", "language_detected", "speech_date", "speech_type"]
    add(md_table(df.sort_values(["leader", "filename"]).to_dict("records"), cols))
    add("")

    # 4. suspicious
    add("## 4. Suspicious files and flags")
    add("")
    if susp.empty:
        add("No flags raised.")
    else:
        add(md_table(susp.sort_values(["leader", "filename", "flag"]).to_dict("records"), ["filename", "leader", "flag", "detail"]))
        add("")
        add("Flag counts: " + ", ".join(f"`{k}`×{v}" for k, v in Counter(susp["flag"]).most_common()))
    add("")
    add("_Nothing was modified or removed. Flags are proposals for Phase 1 (preprocessing) and for the collector._")
    add("")

    # 5. chunking
    add("## 5. Proposed chunking")
    add("")
    add(f"Parameters: min {ch['chunk_min_tokens']} · max {ch['chunk_max_tokens']} · target ≈{ch['chunk_target_tokens']} tokens · no overlap · "
        f"paragraph boundaries preferred, over-long paragraphs split at sentence ends, short orphans merged with a neighbour.")
    add("")
    add(f"Estimates below run the *same* `chunk_paragraphs` function Phase 1 will use, with token counts from `{info['token_method']}`.")
    add("")
    add(md_table(df[df["word_count"] > 0].sort_values(["leader", "filename"]).to_dict("records"),
                 ["leader", "filename", "paragraph_count", "token_count", "estimated_chunk_count", "short_chunks", "mean_chunk_tokens"]))
    add("")
    per_leader = df.groupby("leader")["estimated_chunk_count"].sum()
    add("Chunks per leader: " + ", ".join(f"{leaders_cfg.get(k, {}).get('short_name', k)} {int(v)}" for k, v in per_leader.items()))
    add("")

    # 6. metadata
    add("## 6. Metadata verification (`data/metadata.csv`)")
    add("")
    meta_rows = df[["leader", "filename", "speech_date", "date_confidence", "speech_type", "source", "title", "missing_metadata"]].copy()
    meta_rows["source"] = meta_rows["source"].map(lambda s: "✓" if s else "—")
    add(md_table(meta_rows.sort_values(["leader", "filename"]).to_dict("records"),
                 ["leader", "filename", "speech_date", "date_confidence", "speech_type", "source", "title", "missing_metadata"]))
    add("")
    conf = Counter(df["date_confidence"].replace("", "blank"))
    add("Date confidence: " + ", ".join(f"`{k}`×{v}" for k, v in conf.most_common()))
    add("")
    if info["metadata_orphans"]:
        add("Metadata rows without a file: " + ", ".join(f"`{o}`" for o in info["metadata_orphans"]))
        add("")
    n_no_source = int((df["source"] == "").sum())
    if n_no_source:
        add(f"**{n_no_source} of {len(df)} files have no `source`.** Please add the URL/origin of each transcript; it is required for traceability in the video.")
        add("")
    review = df[(df["review_status"] != "") & (df["review_status"].str.lower() != "ok")]
    if len(review):
        add("### Collector review items (from `metadata.csv`)")
        add("")
        for r in review.sort_values(["leader", "filename"]).itertuples():
            add(f"- **`{r.filename}`** — `{r.review_status}`: {r.notes}")
        add("")

    # 7. phase 1 preview
    add("## 7. What Phase 1 (preprocessing) would clean — proposals only")
    add("")
    preview_map = {
        "speaker_label_prefix": "strip the leading speaker label (e.g. `President of Russia Vladimir Putin:`); log the removed text",
        "truncated_start": "first word is truncated — sits inside the speaker label, so it disappears with it; otherwise fix the source file",
        "excess_whitespace": "collapse runs of spaces to one space (no wording change)",
        "stage_directions": "remove `[applause]`-style tags; log each removal",
        "html_remnants": "remove HTML tags/entities; log each removal",
        "urls": "remove URLs / navigation remnants; log each removal",
        "timestamps": "remove transcript timestamps; log each removal",
        "repeated_lines": "drop repeated header/footer lines; log them",
        "interviewer_pattern": "review manually — interviewer questions must not be embedded as the leader's words",
        "third_person_narration": "review manually — news commentary around the transcript must be cut",
    }
    present = [f for f in preview_map if f in set(susp["flag"])]
    if present:
        for f in present:
            files_f = ", ".join(f"`{x}`" for x in susp.loc[susp["flag"] == f, "filename"])
            add(f"- **{f}** → {preview_map[f]}  \n  files: {files_f}")
    else:
        add("- No cleaning actions suggested by the automatic scan.")
    add("")
    add("All removals will be written to `data/processed/preprocessing_report.md`; original files are never edited.")
    add("")

    # 8. readiness
    add("## 8. Readiness for Phase 1")
    add("")
    empties = df.loc[df["word_count"] == 0, "filename"].tolist()
    if empties:
        add(f"**BLOCKER — {len(empties)} empty file(s):** " + ", ".join(f"`{e}`" for e in empties))
        add("")
    if blockers:
        add("**Leaders below the minimum speech count:** " + "; ".join(blockers))
        add("")
    excl = df.loc[df["review_status"].str.lower() == "exclude_candidate", "filename"].tolist()
    if excl:
        add("**Decision needed — exclude candidates:** " + ", ".join(f"`{e}`" for e in excl)
            + ". If excluded, re-check the per-leader minimum above.")
        add("")
    if not empties and not blockers:
        add("No hard blockers. Review the warnings and decisions above, then Phase 1 can run.")
        add("")
    add("Corpus caveats to repeat in the video: speeches differ in year and format; leaders have unequal speech counts; "
        "Putin and Trump are English (Putin via official English transcript) while the others are in the original language. "
        "Every later result is a statement about *this* corpus.")
    add("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 0 corpus inventory (read-only).")
    ap.add_argument("--config", default=None)
    ap.add_argument("--input-dir", default=None, help="defaults to paths.data_original")
    ap.add_argument("--no-recurse", action="store_true", help="only *.txt directly inside --input-dir")
    ap.add_argument("--out-dir", default=None, help="defaults to paths.outputs_tables")
    ap.add_argument("--report", default=None, help="defaults to outputs/phase0_report.md")
    ap.add_argument("--no-tokenizer", action="store_true", help="use the words×ratio heuristic instead of the HF tokenizer")
    args = ap.parse_args(argv)

    # Windows consoles often default to a legacy code page (cp1254 here); keep report text intact.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    input_dir = Path(args.input_dir).resolve() if args.input_dir else path_for(cfg, "data_original")
    out_dir = Path(args.out_dir) if args.out_dir else path_for(cfg, "outputs_tables")
    report_path = Path(args.report) if args.report else path_for(cfg, "outputs") / "phase0_report.md"
    out_dir.mkdir(parents=True, exist_ok=True)

    df, susp, info = build_inventory(cfg, input_dir, recurse=not args.no_recurse, use_tokenizer=not args.no_tokenizer)
    df.to_csv(out_dir / "corpus_inventory.csv", index=False, encoding="utf-8")
    susp.to_csv(out_dir / "suspicious_files.csv", index=False, encoding="utf-8")
    report = write_report(cfg, df, susp, info, report_path)

    # console summary: sections 1 and 8 only
    sec = report.split("\n## ")
    print("## " + sec[1].strip())
    print()
    print("## " + sec[-1].strip())
    print()
    print(f"[inventory] {len(df)} files → {out_dir / 'corpus_inventory.csv'}")
    print(f"[inventory] {len(susp)} flags → {out_dir / 'suspicious_files.csv'}")
    print(f"[inventory] report → {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
