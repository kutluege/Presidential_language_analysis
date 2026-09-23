"""Project brief — one self-contained Markdown file describing the whole project for a reader (or a language
model) that has not seen the repository: goal and rules, corpus, pipeline, both runs, every key number, a
catalogue of the figures with what each shows, the findings, and what the data can and cannot support.

Usage:
    python -m src.generate_brief          → outputs/PROJECT_BRIEF.md

Numbers are read from the result tables at run time so the brief never drifts from the data.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PROJECT_ROOT, framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys, theme_labels
from .emotion import etag_for
from .generate_report import md_table


def read_opt(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def matrix_md(df: pd.DataFrame, names: dict[str, str], fmt: str = "{:.3f}") -> str:
    m = df.set_index(df.columns[0])
    m.index = [names.get(i, i) for i in m.index]
    m.columns = [names.get(c, c) for c in m.columns]
    return md_table(m.reset_index().rename(columns={"index": ""}), fmt)


FIGURES = [
    ("radar_<leader>", "Per-leader radar of the eight fixed themes (mean corpus percentile, 0.5 = corpus average); the vertical version adds the top-3 themes with bootstrap stability below the chart."),
    ("radar_all_leaders", "All five theme profiles overlaid on the same radar; grey octagon = corpus average."),
    ("rhetorical_radar_<leader>", "Per-leader radar of the seven rhetorical dimensions (conflict/threat, cooperation/solidarity, past, future, us-vs-them, gratitude, promises)."),
    ("rhetorical_radar_all_leaders", "All five rhetorical profiles overlaid; text block lists the highest-scoring leader per dimension."),
    ("leader_similarity_heatmap", "5×5 cosine similarity of leader centroids (primary model); vertical version adds the ten pairs sorted with 95% bootstrap intervals."),
    ("umap_chunks", "UMAP projection of all chunks: colour and marker = leader, hollow markers = speech centres, one grey-background facet per leader. Visual only; no distances are read from it."),
    ("pca_chunks", "Same layout as UMAP using the first two principal components."),
    ("theme_comparison", "Eight small panels (one per theme), leaders sorted by mean percentile with 95% speech-level bootstrap whiskers; identical scale everywhere."),
    ("top_themes_by_leader", "For each leader the three most represented themes with values and the share of bootstrap resamples that keep them in the top three."),
    ("style_rankings", "Seven panels (one per rhetorical dimension), leaders sorted by measured value with bootstrap whiskers — the 'ranking' figure; overlapping whiskers mean no reliable difference."),
    ("conflict_cooperation_comparison", "The two spec-required framing scales alone (conflict/threat vs cooperation/solidarity), same construction."),
    ("emotion_profile", "Four panels: affiliative/positive emotion, fear-sadness-loss, hostility/disapproval (GoEmotions families) and sentiment valence; bars from the corpus mean with bootstrap whiskers."),
    ("style_similarity_heatmap", "5×5 cosine similarity of the z-scored style profiles; vertical version adds the ten pairs sorted by style distance with intervals."),
    ("style_dendrogram", "Average-linkage hierarchical clustering of the five style profiles; lower joins = more alike."),
    ("content_vs_style_scatter", "Ten leader pairs: x = content similarity (embedding centroids), y = style similarity (cosine of style profiles), with the Spearman correlation in the subtitle."),
    ("semantic_dispersion", "Two panels: mean distance of speech centres to their leader centre, and of chunks to their speech centre — how concentrated each speech set is."),
    ("language_effect", "Slope chart of the ten pair similarities under the same Qwen3 model, original languages (archived run) → English (this run), Erdoğan pairs highlighted; second panel: same-leader nearest-neighbour share before → after translation."),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write outputs/PROJECT_BRIEF.md")
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    T = path_for(cfg, "outputs_tables")
    OUT = path_for(cfg, "outputs")
    OLD = PROJECT_ROOT / cfg["paths"].get("old_results_tables", "old_results/outputs/tables")
    pk = primary_model_key(cfg)
    rk = next(k for k, m in cfg["embedding"]["models"].items() if m["hf_id"] == cfg["robustness_embedding_model"])
    tag, rtag, etag = result_tag(cfg, pk, ""), result_tag(cfg, rk, ""), etag_for("")
    leaders = leader_slugs(cfg)
    names = {L: cfg["leaders"][L]["short_name"] for L in leaders}
    themes, tl = theme_keys(cfg), theme_labels(cfg)
    framings = framing_keys(cfg)
    fl = {k: cfg["framing_definitions"][k]["label"] for k in framings}
    model, rmodel = cfg["primary_embedding_model"], cfg["robustness_embedding_model"]

    speeches = pd.read_csv(path_for(cfg, "data_processed") / "speeches_clean.csv", keep_default_na=False)
    chunks = pd.read_csv(path_for(cfg, "data_processed") / "chunks.csv")
    run = json.loads((path_for(cfg, "artifacts_embeddings") / f"{pk}_run.json").read_text(encoding="utf-8"))
    n_words = int(speeches["word_count_clean"].sum())

    L: list[str] = []
    add = L.append
    add(f"# Project brief — political-speech-geometry")
    add("")
    add(f"Generated {datetime.now():%Y-%m-%d %H:%M} from the repository's result tables. This single file is meant to be handed to a person or a "
        "language model that has not seen the repository. Everything below is a statement about the *collected speech files*; nothing measures "
        "ideology, political quality, personality, competence or morality, and nothing is an endorsement or a criticism of anyone.")
    add("")

    # ---- 1. goal and rules
    add("## 1. What the project is")
    add("")
    add("A small, reproducible NLP experiment on the content, semantic geometry and rhetorical style of public speeches by five political leaders "
        "(Recep Tayyip Erdoğan, Emmanuel Macron, Angela Merkel, Vladimir Putin, Donald Trump), built as material for an Instagram explainer video in which the author "
        "appears on camera as an AI engineer. The stated goals: (1) examine which themes each speech set emphasises and how often, (2) measure how semantically "
        "close the speech sets are in an embedding space, (3) rank the sets on measurable, descriptive style dimensions (rhetorical framing and emotional tone), "
        "(4) analyse the semantic content of the messages, and (5) surface embedding-geometry facts an engineer can explain to a general audience.")
    add("")
    add("Ground rules kept throughout: all similarity, distance, theme, rhetorical and emotional values describe the collected corpora; 'ranking' means sorted "
        "measurements with confidence intervals; every claim is traceable to a table, a numeric metric and a documented method; 2D projections are for "
        "visualisation only; each speech weighs the same inside its leader's aggregate so long speeches do not dominate.")
    add("")

    # ---- 2. corpus
    add("## 2. The corpus")
    add("")
    add(f"{len(speeches)} speeches, {n_words:,} cleaned words, {len(chunks)} chunks (paragraph-based, 80–180 tokens, no overlap, median {int(chunks['token_count'].median())} tokens). "
        "Mostly New Year addresses from different years; one Erdoğan symposium speech, one Trump farewell address, one Trump inaugural address, and one Trump file "
        "that is a compilation of excerpts from several occasions (kept at the collector's request; its effect is reported as a robustness check).")
    add("")
    sp = speeches[["speech_id", "leader", "speech_date", "speech_type", "word_count_clean", "title"]].copy()
    sp["leader"] = sp["leader"].map(names)
    add(md_table(sp.sort_values(["leader", "speech_id"]), "{:.0f}"))
    add("")
    add("**Language history — the central methodological story.** Run 1 (2026-09-22) analysed the texts in their original languages: Turkish (Erdoğan), French (Macron), "
        "German (Merkel), English (Putin via official transcript, Trump). The embedding model saw language before content: 69–100% of a chunk's nearest neighbours came "
        "from the same leader, and Erdoğan's Turkish speeches sat in all four least-similar leader pairs. Because each leader spoke a different language, leader and language "
        "could not be separated. For run 2 (2026-09-23) the collector translated the Turkish, French and German speeches into English (paragraph structure preserved) and the "
        "whole analysis was redone; run 1 is archived in `old_results/`. The price of translation: for Erdoğan, Macron and Merkel the English text also carries the translator's "
        "choices, so style measurements describe the translated text.")
    add("")

    # ---- 3. pipeline
    add("## 3. Pipeline (what was actually computed)")
    add("")
    add(f"""1. **Inventory & validation** of every file (word/paragraph counts, language check, artifacts, duplicates, metadata) → `outputs/phase0_report.md`.
2. **Conservative cleaning**, every removal logged: four `President of Russia Vladimir Putin:` speaker labels, the oath ceremony spoken by other people at the top of the Trump inaugural, two lone `*` separator lines → `data/processed/preprocessing_report.md`.
3. **Chunking** into paragraph-based chunks of 80–180 tokens (Qwen3 tokenizer; identical chunks for both models); a second chunk set with ceremonial openings/closings stripped for robustness.
4. **Embeddings** with two models on identical chunks: primary `{model}` ({run['dim']}-d, 11.8B parameters, bf16, peak {run.get('peak_vram_gb')} GB VRAM, {run['encode_seconds']:.1f} s for all chunks on one RTX 5090) and robustness `{rmodel}` (4096-d). All vectors unit-normalised.
5. **Theme scoring** (8 fixed themes) and **rhetorical scoring** (7 dimensions): cosine similarity between each chunk and a written description embedded with the same model, expressed as a corpus percentile (0.5 = corpus average); a multilingual zero-shot NLI classifier as a second opinion; keyword hits only as a diagnostic.
6. **Emotional tone** with independent classifiers: GoEmotions (28 labels, multi-label) grouped into families, plus a three-class sentiment model (valence = P(positive) − P(negative)).
7. **Aggregation** chunk → speech (mean) → leader (mean of speeches). **Centroids**: normalised speech centroids, leader centroid = normalised mean of speech centroids.
8. **Geometry**: 5×5 leader cosine similarity/distance; chunk-level k-nearest-neighbour analysis (k=10, same speech excluded) with observed vs expected same-leader share; cross-leader chunk pairs; within-leader dispersion.
9. **Style profile**: per speech, 7 rhetorical percentiles + 3 emotion family means + valence, z-scored across the 20 speeches; leader = mean; Euclidean distance and cosine between leaders; hierarchical clustering; rankings per dimension.
10. **Topic discovery** (exploratory): PCA(50) → HDBSCAN, raw and after subtracting each leader's centroid.
11. **Uncertainty**: speech-level bootstrap, 2000 resamples, 95% percentile intervals for every leader-level number; rank-stability shares.
12. **Robustness**: primary vs robustness model; original-language (archived) vs English corpus with the same model; all content vs ceremonial-stripped; centroid vs kNN similarity; with vs without the excerpt compilation; embedding vs NLI; rhetoric vs emotion classifier.
13. **Figures** in square 1:1 and vertical 9:16 (Instagram), PNG at 2160 px + SVG, fixed colour per leader.""")
    add("")

    # ---- 4. key numbers
    add("## 4. Key numbers")
    add("")
    add(f"### 4.1 Semantic proximity — leader-centroid cosine similarity, primary model ({model.split('/')[-1]}, English corpus)")
    add("")
    add(matrix_md(pd.read_csv(T / f"leader_cosine_similarity{tag}.csv"), names))
    add("")
    ci = pd.read_csv(T / f"bootstrap_leader_similarity_ci{tag}.csv")
    stab = pd.read_csv(T / f"bootstrap_pair_rank_stability{tag}.csv")
    ci = ci.merge(stab[["leader_a", "leader_b", "share_most_similar_pair", "share_least_similar_pair"]], on=["leader_a", "leader_b"])
    ci["pair"] = ci["leader_a"].map(names) + "–" + ci["leader_b"].map(names)
    add("Pairs sorted, with 95% speech-level bootstrap intervals and the share of 2000 resamples in which the pair is the closest / the most distant:")
    add("")
    add(md_table(ci[["pair", "cosine_similarity", "ci_low", "ci_high", "share_most_similar_pair", "share_least_similar_pair"]]))
    add("")
    add(f"### 4.2 The same matrix under the robustness model ({rmodel.split('/')[-1]}, English corpus)")
    add("")
    add(matrix_md(pd.read_csv(T / f"leader_cosine_similarity{rtag}.csv"), names))
    add("")
    old_sim = read_opt(OLD / "leader_cosine_similarity.csv")
    if old_sim is not None:
        add(f"### 4.3 Run 1 for comparison — {rmodel.split('/')[-1]} on the ORIGINAL-LANGUAGE corpus (archived)")
        add("")
        add(matrix_md(old_sim, names))
        add("")
    le = read_opt(T / "language_effect_pairs.csv")
    lk = read_opt(T / "language_effect_knn.csv")
    if le is not None and lk is not None:
        add("### 4.4 Language effect — same model (Qwen3), original languages → English")
        add("")
        le2 = le.copy()
        le2["pair"] = le2["pair"].map(lambda p: "–".join(names[x] for x in p.split("–")))
        add(md_table(le2[["pair", "old_similarity", "new_similarity", "delta", "old_rank", "new_rank"]].sort_values("old_similarity", ascending=False), "{:.3f}"))
        add("")
        lk2 = lk.copy()
        lk2["leader"] = lk2["leader"].map(names)
        add("Same-leader share of a chunk's 10 nearest neighbours (other speeches only), before → after translation, same model:")
        add("")
        add(md_table(lk2, "{:.3f}"))
        add("")
    knn = pd.read_csv(T / f"chunk_knn_leader_shares{tag}.csv")
    same = knn[knn["leader"] == knn["neighbor_leader"]][["leader", "observed_share", "expected_share", "ratio_obs_exp", "n_chunks"]].copy()
    rk_knn = pd.read_csv(T / f"chunk_knn_leader_shares{rtag}.csv")
    rsame = rk_knn[rk_knn["leader"] == rk_knn["neighbor_leader"]].set_index("leader")["observed_share"]
    same["observed_share_robustness_model"] = same["leader"].map(rsame)
    same["leader"] = same["leader"].map(names)
    add(f"### 4.5 Nearest-neighbour structure in English (primary model; last column = robustness model)")
    add("")
    add(md_table(same))
    add("")
    add("Full kNN matrix, primary model (row = chunk's leader, column = share of its 10 nearest neighbours from that leader):")
    add("")
    add(matrix_md(pd.read_csv(T / f"chunk_knn_leader_matrix{tag}.csv"), names))
    add("")

    add("### 4.6 Theme profiles — mean corpus percentile per theme (0.5 = corpus average)")
    add("")
    prof = pd.read_csv(T / f"theme_profile_leader{tag}.csv")
    tp = prof[["leader", "n_speeches", "n_chunks"] + [f"{k}_pct" for k in themes]].copy()
    tp.columns = ["leader", "speeches", "chunks"] + [tl[k] for k in themes]
    tp["leader"] = tp["leader"].map(names)
    add(md_table(tp, "{:.2f}"))
    add("")
    top3 = pd.read_csv(T / f"top_themes_by_leader{tag}.csv")
    top3 = top3[top3["method"] == "embedding_pct"]
    ts = pd.read_csv(T / f"bootstrap_top_theme_stability{tag}.csv").set_index(["leader", "theme"])
    rows = []
    for Ld in leaders:
        r = top3[top3["leader"] == Ld].sort_values("rank")
        rows.append({"leader": names[Ld], **{f"#{i}": f"{tl[x.theme]} ({x.value:.2f}, top-3 in {ts.loc[(Ld, x.theme), 'share_top3']:.0%} of resamples)" for i, x in enumerate(r.itertuples(), 1)}})
    add("Three most represented themes per speech set (value, and share of 2000 speech-level bootstrap resamples keeping the theme in the top three):")
    add("")
    add(md_table(pd.DataFrame(rows)))
    add("")
    nli_top = pd.read_csv(T / f"top_themes_by_leader{tag}.csv")
    nli_top = nli_top[(nli_top["method"] == "nli") & (nli_top["rank"] == 1)]
    agree = pd.read_csv(T / f"theme_method_agreement{tag}.csv")
    add(f"Second opinion (zero-shot NLI classifier): top theme per leader = " + "; ".join(f"{names[r.leader]}: {r.label}" for r in nli_top.itertuples())
        + f". Embedding and NLI pick the same top theme for {agree['top_theme_agreement_emb_vs_nli'].iloc[0]:.0%} of chunks (chunk-level Spearman {agree['spearman_cos_vs_nli'].min():.2f}–{agree['spearman_cos_vs_nli'].max():.2f}).")
    add("")

    add("### 4.7 Rhetorical dimensions — mean corpus percentile, sorted within each dimension (95% bootstrap CI; share of resamples in which rank 1 holds)")
    add("")
    rk_df = pd.read_csv(T / f"style_rankings{tag}.csv")
    for k in framings:
        sub = rk_df[rk_df["dimension"] == k].sort_values("rank")
        add(f"**{fl[k]}** — " + "; ".join(f"{names[r.leader]} {r.value:.2f} [{r.ci_low:.2f}–{r.ci_high:.2f}]" for r in sub.itertuples())
            + f" · rank 1 holds in {sub.iloc[0]['share_rank1']:.0%} of resamples")
        add("")
    fr = pd.read_csv(T / f"framing_leader{tag}.csv")
    rates = fr[["leader"] + [f"{k}_rate" for k in framings]].copy()
    rates.columns = ["leader"] + [fl[k] for k in framings]
    rates["leader"] = rates["leader"].map(names)
    add("Top-quartile rates (share of a leader's chunks in the corpus top quartile of each dimension):")
    add("")
    add(md_table(rates, "{:.2f}"))
    add("")

    add("### 4.8 Emotional tone (classifier probabilities, leader means; family score = highest member-emotion probability per chunk)")
    add("")
    em = pd.read_csv(T / f"emotion_profile_leader{etag}.csv")
    fams = [f"fam_{f}" for f in cfg["emotion"]["report_families"] if f"fam_{f}" in em.columns]
    e2 = em[["leader", "n_speeches"] + fams + ["valence", "sent_positive", "sent_neutral", "sent_negative"]].copy()
    e2["leader"] = e2["leader"].map(names)
    add(md_table(e2, "{:.3f}"))
    add("")
    for k in [d for d in dict.fromkeys(rk_df[rk_df["kind"] == "emotion"]["dimension"])]:
        sub = rk_df[rk_df["dimension"] == k].sort_values("rank")
        add(f"**{sub['dimension_label'].iloc[0]}** — " + "; ".join(f"{names[r.leader]} {r.value:.2f} [{r.ci_low:.2f}–{r.ci_high:.2f}]" for r in sub.itertuples())
            + f" · rank 1 holds in {sub.iloc[0]['share_rank1']:.0%}")
        add("")
    etop = read_opt(T / f"emotion_top_labels_by_leader{etag}.csv")
    if etop is not None:
        add("Most frequent non-neutral GoEmotions labels per leader (top 5): " + " · ".join(
            f"{names[Ld]}: " + ", ".join(f"{r.emotion} {r.mean_probability:.2f}" for r in etop[etop['leader'] == Ld].sort_values('rank').itertuples()) for Ld in leaders))
        add("")

    add("### 4.9 Composite style similarity (11 z-scored dimensions)")
    add("")
    add("Cosine similarity of leader style profiles:")
    add("")
    add(matrix_md(pd.read_csv(T / f"style_similarity_leader{tag}.csv"), names, "{:.2f}"))
    add("")
    spairs = pd.read_csv(T / f"style_pairs{tag}.csv")
    spairs["pair"] = spairs["leader_a"].map(names) + "–" + spairs["leader_b"].map(names)
    add("Pairs by style distance (Euclidean on z-scores; smaller = more alike), with bootstrap intervals and the share of resamples in which the pair is the closest:")
    add("")
    add(md_table(spairs[["pair", "style_distance", "ci_low", "ci_high", "style_cosine", "share_closest_pair"]]))
    add("")
    cvs = pd.read_csv(T / f"content_vs_style{tag}.csv")
    add(f"Content similarity vs style similarity across the ten pairs: Spearman {cvs['spearman_content_vs_style_cosine'].iloc[0]:.2f} — saying similar things and sounding alike are largely independent in this corpus.")
    add("")
    add("Leader style profile (z-scores; positive = above the corpus mean of the 20 speeches):")
    add("")
    slp = pd.read_csv(T / f"style_leader_profile{tag}.csv")
    zcols = [c for c in slp.columns if c.startswith("z_")]
    z2 = slp[["leader"] + zcols].copy()
    z2.columns = ["leader"] + [c[2:].replace("_pct", "").replace("fam_", "") for c in zcols]
    z2["leader"] = z2["leader"].map(names)
    add(md_table(z2, "{:.2f}"))
    add("")

    add("### 4.10 Semantic concentration (cosine distances in the original space)")
    add("")
    disp = pd.read_csv(T / f"semantic_dispersion{tag}.csv")
    d2 = disp[["leader", "n_speeches", "n_chunks", "mean_dist_speech_to_leader", "mean_dist_chunk_to_speech", "mean_dist_chunk_to_leader"]].copy()
    d2["leader"] = d2["leader"].map(names)
    add(md_table(d2, "{:.3f}"))
    add("")

    add("### 4.11 Exploratory clustering (PCA 50 → HDBSCAN)")
    add("")
    for label, path in (("raw chunk vectors", T / f"clusters_summary{tag}.csv"), ("after subtracting each leader's centroid (leader-centred)", T / f"clusters_summary__{pk}_leadercentered.csv")):
        cs = read_opt(path)
        if cs is None:
            continue
        c2 = cs[["cluster", "size", "candidate_label", "dominant_leader", "dominant_leader_share", "leader_mix_entropy"] + [f"share_{Ld}" for Ld in leaders] + ["frequent_terms"]].copy()
        c2["dominant_leader"] = c2["dominant_leader"].map(lambda x: names.get(x, x))
        c2.columns = ["cluster", "size", "candidate label (from theme scores)", "dominant leader", "dominant share", "mix entropy"] + [f"share {names[Ld]}" for Ld in leaders] + ["frequent terms"]
        add(f"**{label.capitalize()}** (cluster −1 = unassigned noise):")
        add("")
        add(md_table(c2, "{:.2f}"))
        add("")

    add("### 4.12 Robustness — every material change flagged by the checks")
    add("")
    rob = pd.read_csv(T / "robustness_summary.csv")
    mat = rob[rob["material_change"] == True][["check", "comparison", "metric", "value", "note"]]  # noqa: E712
    add(md_table(mat) if len(mat) else "None.")
    add("")
    a_rho = rob[(rob["check"] == "A") & (rob["metric"] == "leader_pair_similarity_spearman")]["value"]
    if len(a_rho):
        add(f"Check A (primary vs robustness model on the same English text): Spearman of the ten pair similarities = {float(a_rho.iloc[0]):.2f}; in run 1 (mixed languages, Qwen3 vs BGE-M3) it was −0.37.")
        add("")
    rve = read_opt(T / "rhetoric_vs_emotion.csv")
    if rve is not None:
        add("Check H (embedding-based rhetorical dimension vs classifier-based emotion, speech level, Spearman over 20 speeches):")
        add("")
        add(md_table(rve))
        add("")

    # ---- 5. figures
    add("## 5. Figure catalogue (`outputs/plots/`)")
    add("")
    add("Every figure exists as `<name>.png` (square 1080×1080, exported at 2160 px), `<name>_9x16.png` (vertical 1080×1920, exported at 2160×3840) and matching SVGs. "
        "Fixed colours: Erdoğan blue #2a78d6, Macron orange #eb6834, Merkel aqua #1baf7a, Putin yellow #eda100, Trump magenta #e87ba4. Vertical versions carry a text block under the chart with the key numbers.")
    add("")
    add(md_table(pd.DataFrame([{"file": f"`{n}`", "what it shows": d} for n, d in FIGURES])))
    add("")
    add("Run 1's landscape figures (original-language corpus) are in `old_results/outputs/plots/` under the same names.")
    add("")

    # ---- 6. findings
    vi = (OUT / "video_insights.md")
    if vi.exists():
        add("## 6. Candidate findings for the video (verbatim from `outputs/video_insights.md`)")
        add("")
        body = vi.read_text(encoding="utf-8").split("\n", 1)[1]
        add(body.replace("\n## Finding", "\n### Finding"))
        add("")

    # ---- 7. can / cannot
    add("## 7. What the data can and cannot support")
    add("")
    add("""**Supported by the measurements**
- Language dominated the first analysis; translation removed most of that signal (same-model comparison, section 4.4). This is the cleanest methodological story in the project.
- Even in English, chunks of the same speech set stay close to each other far more than chance (section 4.5) — the sets have a recognisable content signature, whose strength depends on the model.
- Theme profiles, rhetorical dimensions and emotional tone can be reported per leader as sorted measurements with intervals (sections 4.6–4.8). Several first places are stable across bootstrap resamples (e.g. gratitude/recognition and past orientation for the Putin set, us-versus-them for the Trump set, future orientation and reform/technology for the Macron set); many others are not, and their intervals overlap.
- Content similarity and style similarity are nearly unrelated in this corpus (section 4.9): sets that discuss similar things do not necessarily sound alike.
- Two embedding models agree on the pair ordering in English but did not on the mixed-language corpus (section 4.12).

**Not supported / must not be claimed**
- Anything about the people: ideology, sincerity, competence, aggression, honesty, character. The measurements describe collected texts, several of them translations, most of them a single genre (New Year addresses), 3–5 per leader.
- Causal explanations of why a theme or tone appears (occasion, year, speechwriter, translator and genre are all confounded).
- Fine-grained rankings where the 95% intervals overlap — which is most of them. The safe phrasing is "in these speeches, X measured highest on Y, and the interval is wide/narrow".
- Generalisation beyond this corpus: stability across bootstrap resamples of the same speeches is not stability across a leader's other speeches.
- Emotion-classifier absolutes: the classifiers were trained on Reddit/Twitter text and see translated speech; treat them as relative, method-dependent signals.
""")
    add("## 8. Files to look at")
    add("")
    add("`outputs/video_insights.md` (findings with Turkish spoken lines and cautions) · `outputs/methodology_for_video.md` (Turkish explanations of embeddings, chunks, cosine, centroids, translation, bootstrap, UMAP) · "
        "`outputs/results_summary.md` (tables index) · `outputs/robustness_report.md` · `outputs/clusters_report*.md` · `outputs/phase0_report.md` · `data/processed/preprocessing_report.md` · "
        "`old_results/README.md` (run 1) · `README.md` (how to run) · `config.yaml` (every parameter and every theme/dimension description).")
    add("")

    (OUT / "PROJECT_BRIEF.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[generate_brief] wrote {OUT / 'PROJECT_BRIEF.md'} ({sum(len(x) for x in L) / 1000:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
