"""Phase 8 — robustness checks across models, corpus variants and methods.

Usage:
    python -m src.robustness

Checks (each compares two already-computed result sets, nothing is re-embedded here):
  A  Qwen3-Embedding-8B vs BGE-M3                  (tag ''  vs '__bge_m3')
  B  original vs English-normalised corpus         (skipped if data/translated_en is empty)
  C  all content vs ceremonial opening/closing removed  (both models)
  D  leader-centroid similarity vs chunk-level cross-neighbour similarity (within the primary model)
  E  with vs without trump2 (compilation of excerpts, flagged in metadata)
  F  language-matched vs English theme descriptions; embedding vs NLI theme ranking

Outputs: outputs/tables/robustness_summary.csv, outputs/robustness_report.md
Material changes (top pair flips, rank correlations below 0.5) are listed explicitly, never hidden.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys, theme_labels
from .vectors import l2norm, leader_centroids, load_embeddings, pair_table, speech_centroids

ROWS: list[dict] = []
REPORT: list[str] = []


def add(check: str, comparison: str, metric: str, value, note: str = "", material: bool = False) -> None:
    ROWS.append({"check": check, "comparison": comparison, "metric": metric,
                 "value": (round(float(value), 4) if isinstance(value, (int, float, np.floating)) else value),
                 "material_change": material, "note": note})


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, (float, np.floating)) else str(v) for v in r) + " |")
    return "\n".join(out)


def load_pairs(tables: Path, tag: str) -> pd.DataFrame | None:
    p = tables / f"leader_pairs{tag}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["pair"] = df["leader_a"] + "–" + df["leader_b"]
    return df.set_index("pair")


def compare_result_sets(cfg: dict, tables: Path, check: str, tag_a: str, tag_b: str, name_a: str, name_b: str) -> None:
    themes, framings, leaders = theme_keys(cfg), framing_keys(cfg), leader_slugs(cfg)
    labels = theme_labels(cfg)
    comp = f"{name_a} vs {name_b}"
    REPORT.append(f"### {check}: {comp}\n")
    pa, pb = load_pairs(tables, tag_a), load_pairs(tables, tag_b)
    if pa is None or pb is None:
        REPORT.append(f"_skipped — result set missing ({tag_a!r} / {tag_b!r})_\n")
        add(check, comp, "status", "skipped", "result set missing")
        return
    common = pa.index.intersection(pb.index)
    a, b = pa.loc[common, "cosine_similarity"], pb.loc[common, "cosine_similarity"]
    rho, r = spearmanr(a, b).statistic, pearsonr(a, b).statistic
    top_a, top_b = pa["cosine_similarity"].idxmax(), pb["cosine_similarity"].idxmax()
    bottom_a, bottom_b = pa["cosine_similarity"].idxmin(), pb["cosine_similarity"].idxmin()
    add(check, comp, "leader_pair_similarity_spearman", rho, "10 leader pairs", material=rho < 0.5)
    add(check, comp, "leader_pair_similarity_pearson", r, "10 leader pairs")
    add(check, comp, "most_similar_pair", f"{top_a} | {top_b}", "A | B", material=top_a != top_b)
    add(check, comp, "least_similar_pair", f"{bottom_a} | {bottom_b}", "A | B", material=bottom_a != bottom_b)
    add(check, comp, "mean_offdiagonal_similarity", f"{a.mean():.3f} | {b.mean():.3f}", "A | B")
    REPORT.append(f"- Leader-pair similarities: Spearman **{rho:.2f}**, Pearson {r:.2f} over {len(common)} pairs. "
                  f"Most similar pair: **{top_a}** vs **{top_b}**{' ⚠ differs' if top_a != top_b else ''}; least similar: {bottom_a} vs {bottom_b}"
                  f"{' ⚠ differs' if bottom_a != bottom_b else ''}. Mean off-diagonal similarity {a.mean():.3f} vs {b.mean():.3f} "
                  f"(absolute cosine levels are model-specific and not comparable across models).")
    side = pd.DataFrame({"pair": common, name_a: a.values, name_b: b.values,
                         f"rank {name_a}": a.rank(ascending=False).astype(int).values, f"rank {name_b}": b.rank(ascending=False).astype(int).values})
    REPORT.append("\n" + md(side.sort_values(name_a, ascending=False)) + "\n")

    # theme profiles
    ta = pd.read_csv(tables / f"theme_profile_leader{tag_a}.csv").set_index("leader")
    tb = pd.read_csv(tables / f"theme_profile_leader{tag_b}.csv").set_index("leader")
    rows = []
    for L in leaders:
        if L not in ta.index or L not in tb.index:
            continue
        va = ta.loc[L, [f"{k}_pct" for k in themes]].to_numpy(float)
        vb = tb.loc[L, [f"{k}_pct" for k in themes]].to_numpy(float)
        rho_t = spearmanr(va, vb).statistic
        top3a = {themes[i] for i in np.argsort(-va)[:3]}
        top3b = {themes[i] for i in np.argsort(-vb)[:3]}
        rows.append({"leader": L, "spearman_8_themes": rho_t, "top3_overlap": len(top3a & top3b),
                     f"top theme {name_a}": labels[themes[int(np.argmax(va))]], f"top theme {name_b}": labels[themes[int(np.argmax(vb))]]})
        add(check, comp, f"theme_profile_spearman_{L}", rho_t, "8 themes", material=rho_t < 0.5)
        add(check, comp, f"theme_top3_overlap_{L}", len(top3a & top3b), "of 3")
    tp = pd.DataFrame(rows)
    REPORT.append(f"- Theme profiles per leader (mean percentile over 8 themes): median Spearman **{tp['spearman_8_themes'].median():.2f}**, "
                  f"top-3 overlap {tp['top3_overlap'].mean():.1f}/3 on average.\n")
    REPORT.append(md(tp) + "\n")

    # framing leader ordering
    fa = pd.read_csv(tables / f"framing_leader{tag_a}.csv").set_index("leader")
    fb = pd.read_csv(tables / f"framing_leader{tag_b}.csv").set_index("leader")
    for k in framings:
        common_l = [L for L in leaders if L in fa.index and L in fb.index]
        rho_f = spearmanr(fa.loc[common_l, f"{k}_pct"], fb.loc[common_l, f"{k}_pct"]).statistic
        add(check, comp, f"framing_leader_order_spearman_{k}", rho_f, "5 leaders", material=rho_f < 0.5)
        REPORT.append(f"- {k}: leader ordering Spearman **{rho_f:.2f}** "
                      f"({name_a}: {', '.join(f'{L} {fa.loc[L, k + '_pct']:.2f}' for L in common_l)}; "
                      f"{name_b}: {', '.join(f'{L} {fb.loc[L, k + '_pct']:.2f}' for L in common_l)})")

    # dispersion ordering and kNN same-leader share
    da = pd.read_csv(tables / f"semantic_dispersion{tag_a}.csv").set_index("leader")
    db = pd.read_csv(tables / f"semantic_dispersion{tag_b}.csv").set_index("leader")
    common_l = [L for L in leaders if L in da.index and L in db.index]
    rho_d = spearmanr(da.loc[common_l, "mean_dist_speech_to_leader"], db.loc[common_l, "mean_dist_speech_to_leader"]).statistic
    add(check, comp, "dispersion_speech_to_leader_spearman", rho_d, "5 leaders", material=rho_d < 0.5)
    REPORT.append(f"- Dispersion ordering (speech→leader distance): Spearman **{rho_d:.2f}**.")
    ka = pd.read_csv(tables / f"chunk_knn_leader_matrix{tag_a}.csv", index_col=0)
    kb = pd.read_csv(tables / f"chunk_knn_leader_matrix{tag_b}.csv", index_col=0)
    same_a = np.diag(ka.loc[common_l, common_l].to_numpy(float))
    same_b = np.diag(kb.loc[common_l, common_l].to_numpy(float))
    REPORT.append("- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: "
                  + ", ".join(f"{L} {x:.2f}→{y:.2f}" for L, x, y in zip(common_l, same_a, same_b)) + "\n")
    for L, x, y in zip(common_l, same_a, same_b):
        add(check, comp, f"knn_same_leader_share_{L}", f"{x:.3f} | {y:.3f}", "A | B")


def check_d(cfg: dict, tables: Path, tag: str) -> None:
    REPORT.append("### D: leader-centroid similarity vs chunk-level cross-neighbour similarity (primary model)\n")
    pairs = load_pairs(tables, tag)
    cross = pd.read_csv(tables / f"leader_cross_neighbor_similarity{tag}.csv", index_col=0)
    knn = pd.read_csv(tables / f"chunk_knn_leader_matrix{tag}.csv", index_col=0)
    rows = []
    for p in pairs.index:
        a, b = p.split("–")
        rows.append({"pair": p, "centroid_similarity": pairs.loc[p, "cosine_similarity"],
                     "cross_neighbor_similarity": (cross.loc[a, b] + cross.loc[b, a]) / 2,
                     "knn_share_symmetric": (knn.loc[a, b] + knn.loc[b, a]) / 2})
    df = pd.DataFrame(rows)
    rho1 = spearmanr(df["centroid_similarity"], df["cross_neighbor_similarity"]).statistic
    rho2 = spearmanr(df["centroid_similarity"], df["knn_share_symmetric"]).statistic
    add("D", "centroid vs cross-neighbour", "spearman_centroid_vs_cross_neighbor_similarity", rho1, "10 pairs", material=rho1 < 0.5)
    add("D", "centroid vs cross-neighbour", "spearman_centroid_vs_knn_share", rho2, "10 pairs", material=rho2 < 0.5)
    add("D", "centroid vs cross-neighbour", "top_pair_centroid", df.loc[df["centroid_similarity"].idxmax(), "pair"])
    add("D", "centroid vs cross-neighbour", "top_pair_cross_neighbor", df.loc[df["cross_neighbor_similarity"].idxmax(), "pair"])
    REPORT.append(f"- Spearman(centroid similarity, mean cross-neighbour similarity) = **{rho1:.2f}**; "
                  f"Spearman(centroid similarity, symmetric kNN share) = **{rho2:.2f}** over 10 pairs. "
                  f"Top pair by centroid: {df.loc[df['centroid_similarity'].idxmax(), 'pair']}; by cross-neighbour similarity: "
                  f"{df.loc[df['cross_neighbor_similarity'].idxmax(), 'pair']}.\n")
    REPORT.append(md(df.sort_values("centroid_similarity", ascending=False)) + "\n")


def check_e(cfg: dict, tables: Path, model_key: str, exclude: str = "trump2") -> None:
    REPORT.append(f"### E: with vs without `{exclude}` (flagged as a compilation of excerpts)\n")
    leaders = leader_slugs(cfg)
    themes, labels = theme_keys(cfg), theme_labels(cfg)
    emb, index = load_embeddings(cfg, model_key, "")
    sp_cent, sp_idx = speech_centroids(emb, index)
    ld_all, ld_idx = leader_centroids(sp_cent, sp_idx, leaders)
    keep = (sp_idx["speech_id"] != exclude).to_numpy()
    if keep.all():
        REPORT.append("_speech not found — skipped_\n")
        return
    ld_wo, _ = leader_centroids(sp_cent[keep], sp_idx[keep].reset_index(drop=True), leaders)
    names = ld_idx["leader"].tolist()
    sim_all, sim_wo = ld_all @ ld_all.T, ld_wo @ ld_wo.T
    owner = sp_idx.loc[~keep, "leader"].iloc[0]
    oi = names.index(owner)
    rows = []
    for j, other in enumerate(names):
        if other == owner:
            continue
        rows.append({"pair": f"{owner}–{other}", "with": float(sim_all[oi, j]), "without": float(sim_wo[oi, j]), "delta": float(sim_wo[oi, j] - sim_all[oi, j])})
        add("E", f"without {exclude}", f"similarity_{owner}_{other}", f"{sim_all[oi, j]:.3f} → {sim_wo[oi, j]:.3f}", "with → without",
            material=abs(sim_wo[oi, j] - sim_all[oi, j]) > 0.02)
    df = pd.DataFrame(rows)
    rank_all = pd.Series(sim_all[oi], index=names).drop(owner).rank(ascending=False)
    rank_wo = pd.Series(sim_wo[oi], index=names).drop(owner).rank(ascending=False)
    REPORT.append(f"- {owner.title()} centroid similarities with/without `{exclude}` (max |Δ| = {df['delta'].abs().max():.3f}); "
                  f"ordering of the other leaders {'unchanged' if (rank_all == rank_wo).all() else '**changes**'}.\n")
    REPORT.append(md(df) + "\n")
    sp_theme = pd.read_csv(tables / f"theme_profile_speech{result_tag(cfg, model_key, '')}.csv")
    own = sp_theme[sp_theme["leader"] == owner]
    with_ = own[[f"{k}_pct" for k in themes]].mean()
    without = own[own["speech_id"] != exclude][[f"{k}_pct" for k in themes]].mean()
    t3a = [labels[c[:-4]] for c in with_.sort_values(ascending=False).index[:3]]
    t3b = [labels[c[:-4]] for c in without.sort_values(ascending=False).index[:3]]
    add("E", f"without {exclude}", f"top3_themes_{owner}", f"{t3a} → {t3b}", material=set(t3a) != set(t3b))
    REPORT.append(f"- {owner.title()} top-3 themes with `{exclude}`: {', '.join(t3a)}; without: {', '.join(t3b)}"
                  f"{'' if set(t3a) == set(t3b) else ' ⚠ set changes'}. Max theme-percentile change: {(without - with_).abs().max():.3f}.\n")


def check_f(cfg: dict, tables: Path, tag: str) -> None:
    REPORT.append("### F: theme-scoring method agreement (primary model)\n")
    leaders, themes, labels = leader_slugs(cfg), theme_keys(cfg), theme_labels(cfg)
    prof = pd.read_csv(tables / f"theme_profile_leader{tag}.csv").set_index("leader")
    rows = []
    for L in leaders:
        if L not in prof.index:
            continue
        cos = prof.loc[L, [f"{k}_cos" for k in themes]].to_numpy(float)
        cos_en = prof.loc[L, [f"{k}_cos_en" for k in themes]].to_numpy(float)
        r = {"leader": L, "spearman_matched_vs_en": spearmanr(cos, cos_en).statistic,
             "top_matched": labels[themes[int(np.argmax(cos))]], "top_en": labels[themes[int(np.argmax(cos_en))]]}
        if f"{themes[0]}_nli" in prof.columns:
            nli = prof.loc[L, [f"{k}_nli" for k in themes]].to_numpy(float)
            r["spearman_emb_vs_nli"] = spearmanr(cos, nli).statistic
            r["top_nli"] = labels[themes[int(np.argmax(nli))]]
            add("F", "embedding vs NLI", f"leader_theme_spearman_{L}", r["spearman_emb_vs_nli"], "8 themes", material=r["spearman_emb_vs_nli"] < 0.5)
        add("F", "matched vs English descriptions", f"leader_theme_spearman_{L}", r["spearman_matched_vs_en"], "8 themes", material=r["spearman_matched_vs_en"] < 0.5)
        rows.append(r)
    df = pd.DataFrame(rows)
    agree = pd.read_csv(tables / f"theme_method_agreement{tag}.csv")
    REPORT.append(f"- Leader-level theme ranking, language-matched vs English descriptions: median Spearman **{df['spearman_matched_vs_en'].median():.2f}**. "
                  + (f"Embedding vs NLI: median Spearman **{df['spearman_emb_vs_nli'].median():.2f}**. " if "spearman_emb_vs_nli" in df else "")
                  + f"Chunk-level (from theme_method_agreement): matched-vs-English Spearman {agree['spearman_cos_vs_cos_en'].min():.2f}–{agree['spearman_cos_vs_cos_en'].max():.2f}"
                  + (f", embedding-vs-NLI {agree['spearman_cos_vs_nli'].min():.2f}–{agree['spearman_cos_vs_nli'].max():.2f}, "
                     f"same top theme for {agree['top_theme_agreement_emb_vs_nli'].iloc[0]:.0%} of chunks." if "spearman_cos_vs_nli" in agree else "."))
    REPORT.append("\n" + md(df) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 8: robustness comparisons.")
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    cfg = load_config(args.config)
    tables = path_for(cfg, "outputs_tables")
    pk = primary_model_key(cfg)
    rk = next((k for k, m in cfg["embedding"]["models"].items() if m["hf_id"] == cfg["robustness_embedding_model"]), None)
    REPORT.append("# Robustness report\n")
    REPORT.append("Each check compares two complete result sets computed with the same pipeline. Rank correlations (Spearman) are the "
                  "main yardstick because absolute cosine levels differ between models. Items marked ⚠ are material changes and are "
                  "carried into the caution sections of the video findings.\n")

    compare_result_sets(cfg, tables, "A", result_tag(cfg, pk, ""), result_tag(cfg, rk, ""), pk, rk)
    tr_tag = result_tag(cfg, pk, "_translated_en")
    if (tables / f"leader_pairs{tr_tag}.csv").exists():
        compare_result_sets(cfg, tables, "B", result_tag(cfg, pk, ""), tr_tag, "original (mixed-language)", "translated_en")
    else:
        REPORT.append("### B: original vs English-normalised corpus\n\n_skipped — `data/translated_en/` contains no translations yet. "
                      "Add them and run: preprocess/chunking/embed/theme_scoring/aggregate/geometry with `--variant translated_en`, then rerun robustness._\n")
        add("B", "original vs translated_en", "status", "skipped", "no translations available")
    compare_result_sets(cfg, tables, "C", result_tag(cfg, pk, ""), result_tag(cfg, pk, "_noceremonial"), f"{pk} all content", f"{pk} ceremonial removed")
    compare_result_sets(cfg, tables, "C", result_tag(cfg, rk, ""), result_tag(cfg, rk, "_noceremonial"), f"{rk} all content", f"{rk} ceremonial removed")
    check_d(cfg, tables, result_tag(cfg, pk, ""))
    check_e(cfg, tables, pk)
    check_f(cfg, tables, result_tag(cfg, pk, ""))

    summary = pd.DataFrame(ROWS)
    summary.to_csv(tables / "robustness_summary.csv", index=False, encoding="utf-8")
    material = summary[summary["material_change"] == True]  # noqa: E712
    REPORT.insert(2, "## Material changes\n\n" + ("\n".join(f"- **{r.check}** {r.comparison} — {r.metric}: {r.value}" for r in material.itertuples())
                                                 if len(material) else "None.") + "\n")
    (path_for(cfg, "outputs") / "robustness_report.md").write_text("\n".join(REPORT), encoding="utf-8")
    print(f"[robustness] {len(summary)} metrics, {len(material)} material changes → robustness_summary.csv, robustness_report.md")
    print("\n".join(f"  ⚠ {r.check} {r.comparison} — {r.metric}: {r.value}" for r in material.itertuples()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
