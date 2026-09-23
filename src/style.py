"""Phase 4c — composite style profile, style similarity between leaders, and ranked style dimensions.

Usage:
    python -m src.style --model kalm_embedding_gemma3_12b [--suffix _noceremonial]

Style vector of a speech = [rhetorical dimensions as corpus percentiles] + [emotion family means] + [valence],
z-scored across all speeches. Leader style = mean of its speeches' z-vectors (each speech weighs equally).

Outputs (outputs/tables/):
    style_leader_profile{tag}.csv       raw and z-scored dimension means per leader
    style_rankings{tag}.csv             per dimension: leaders sorted by value with 95% speech-level bootstrap CI
    style_distance_leader{tag}.csv      5x5 Euclidean distance between leader style vectors
    style_similarity_leader{tag}.csv    5x5 cosine similarity of the same vectors
    style_pairs{tag}.csv                10 pairs ranked by style distance, with bootstrap CI and "closest pair" share
    content_vs_style{tag}.csv           content (embedding) similarity vs style similarity per pair + Spearman
Artifacts: artifacts/bootstrap/{model}{suffix}_style_linkage.npy (scipy linkage matrix for the dendrogram)

Everything here is descriptive: "sorted measurements with intervals", never a judgement of quality.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.stats import spearmanr

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag
from .emotion import etag_for


def dimension_spec(cfg: dict) -> list[dict]:
    """Ordered list of style dimensions: key (column in the merged speech table), label, kind."""
    sc = cfg["style_similarity"]
    fm = sc.get("framing_metric", "pct")
    dims = [{"col": f"{k}_{fm}", "key": k, "label": cfg["framing_definitions"][k]["label"],
             "label_tr": cfg["framing_definitions"][k].get("label_tr", ""), "kind": "rhetorical"} for k in framing_keys(cfg)]
    flabels = cfg["emotion"].get("family_labels", {})
    for fam in sc.get("emotion_families", []):
        dims.append({"col": f"fam_{fam}", "key": fam, "label": flabels.get(fam, fam), "label_tr": "", "kind": "emotion"})
    if sc.get("include_valence", True):
        dims.append({"col": "valence", "key": "valence", "label": "Sentiment valence (positive − negative)", "label_tr": "Duygu değeri", "kind": "emotion"})
    return dims


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 4c: style profile, rankings and style similarity.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    model_key = args.model or primary_model_key(cfg)
    tag = result_tag(cfg, model_key, args.suffix)
    etag = etag_for(args.suffix)
    tables = path_for(cfg, "outputs_tables")
    bs_dir = path_for(cfg, "artifacts_bootstrap")
    bs_dir.mkdir(parents=True, exist_ok=True)
    leaders = leader_slugs(cfg)
    names = {L: cfg["leaders"][L]["short_name"] for L in leaders}
    B = int(cfg["bootstrap_iterations"])
    level = float(cfg.get("bootstrap_confidence_level", 0.95))
    rng = np.random.default_rng(int(cfg["random_seed"]))
    dims = dimension_spec(cfg)

    fr = pd.read_csv(tables / f"framing_speech{tag}.csv")
    em = pd.read_csv(tables / f"emotion_profile_speech{etag}.csv")
    sp = fr.merge(em[["speech_id"] + [d["col"] for d in dims if d["kind"] == "emotion"]], on="speech_id", how="inner")
    missing = [d["col"] for d in dims if d["col"] not in sp.columns]
    if missing:
        raise SystemExit(f"style: missing columns {missing}")
    cols = [d["col"] for d in dims]
    X = sp[cols].to_numpy(float)
    mu, sd = X.mean(axis=0), X.std(axis=0, ddof=0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    sp_leaders = sp["leader"].astype(str).to_numpy()
    groups = {L: np.where(sp_leaders == L)[0] for L in leaders if (sp_leaders == L).any()}
    L_list = list(groups)

    # --- leader profiles (raw + z) --------------------------------------------------------------
    prof_rows = []
    for L in L_list:
        g = groups[L]
        row = {"leader": L, "n_speeches": len(g)}
        for j, d in enumerate(dims):
            row[d["col"]] = float(X[g, j].mean())
            row[f"z_{d['col']}"] = float(Z[g, j].mean())
        prof_rows.append(row)
    prof = pd.DataFrame(prof_rows)
    prof.to_csv(tables / f"style_leader_profile{tag}.csv", index=False, encoding="utf-8")
    Lz = np.vstack([Z[groups[L]].mean(axis=0) for L in L_list])

    # --- bootstrap: dimension means and pair distances ----------------------------------------
    n_dim, n_L = len(dims), len(L_list)
    boot_means = np.empty((B, n_L, n_dim), dtype=np.float32)
    boot_z = np.empty((B, n_L, n_dim), dtype=np.float32)
    for b in range(B):
        for li, L in enumerate(L_list):
            g = groups[L]
            draw = rng.choice(g, size=len(g), replace=True)
            boot_means[b, li] = X[draw].mean(axis=0)
            boot_z[b, li] = Z[draw].mean(axis=0)
    lo_q, hi_q = (1 - level) / 2 * 100, 100 - (1 - level) / 2 * 100

    rank_rows = []
    for j, d in enumerate(dims):
        vals = {L: float(X[groups[L], j].mean()) for L in L_list}
        order = sorted(vals, key=vals.get, reverse=True)
        for rank, L in enumerate(order, 1):
            li = L_list.index(L)
            rank_rows.append({"dimension": d["key"], "dimension_label": d["label"], "kind": d["kind"], "leader": L, "leader_name": names[L],
                              "rank": rank, "value": vals[L], "z_value": float(Z[groups[L], j].mean()),
                              "ci_low": float(np.percentile(boot_means[:, li, j], lo_q)), "ci_high": float(np.percentile(boot_means[:, li, j], hi_q)),
                              "share_rank1": float((boot_means[:, :, j].argmax(axis=1) == li).mean()),
                              "n_speeches": len(groups[L]), "corpus_mean": float(mu[j]), "corpus_sd": float(sd[j])})
    rankings = pd.DataFrame(rank_rows)
    rankings.to_csv(tables / f"style_rankings{tag}.csv", index=False, encoding="utf-8")

    # --- style distance / similarity between leaders --------------------------------------------
    D = np.sqrt(((Lz[:, None, :] - Lz[None, :, :]) ** 2).sum(-1))
    Ln = Lz / np.clip(np.linalg.norm(Lz, axis=1, keepdims=True), 1e-12, None)
    S = Ln @ Ln.T
    pd.DataFrame(D, index=L_list, columns=L_list).to_csv(tables / f"style_distance_leader{tag}.csv", encoding="utf-8")
    pd.DataFrame(S, index=L_list, columns=L_list).to_csv(tables / f"style_similarity_leader{tag}.csv", encoding="utf-8")
    Zl = linkage(Lz, method=cfg["style_similarity"].get("linkage", "average"), metric="euclidean")
    np.save(bs_dir / f"{model_key}{args.suffix}_style_linkage.npy", Zl)

    pairs = [(i, j) for i in range(n_L) for j in range(i + 1, n_L)]
    boot_D = np.stack([np.sqrt(((boot_z[:, i, :] - boot_z[:, j, :]) ** 2).sum(-1)) for i, j in pairs], axis=1)  # B × P
    closest = boot_D.argmin(axis=1)
    pair_rows = []
    for p, (i, j) in enumerate(pairs):
        pair_rows.append({"leader_a": L_list[i], "leader_b": L_list[j], "style_distance": float(D[i, j]), "style_cosine": float(S[i, j]),
                          "ci_low": float(np.percentile(boot_D[:, p], lo_q)), "ci_high": float(np.percentile(boot_D[:, p], hi_q)),
                          "share_closest_pair": float((closest == p).mean())})
    pairs_df = pd.DataFrame(pair_rows).sort_values("style_distance").reset_index(drop=True)
    pairs_df["rank"] = np.arange(1, len(pairs_df) + 1)
    pairs_df.to_csv(tables / f"style_pairs{tag}.csv", index=False, encoding="utf-8")

    # --- content vs style ------------------------------------------------------------------------
    content = pd.read_csv(tables / f"leader_pairs{tag}.csv")
    content["pair"] = content.apply(lambda r: "–".join(sorted([r.leader_a, r.leader_b])), axis=1)
    pairs_df["pair"] = pairs_df.apply(lambda r: "–".join(sorted([r.leader_a, r.leader_b])), axis=1)
    cvs = content[["pair", "cosine_similarity"]].rename(columns={"cosine_similarity": "content_similarity"}).merge(
        pairs_df[["pair", "style_distance", "style_cosine", "rank"]].rename(columns={"rank": "style_rank"}), on="pair")
    cvs["content_rank"] = cvs["content_similarity"].rank(ascending=False).astype(int)
    rho = spearmanr(cvs["content_similarity"], cvs["style_cosine"]).statistic
    cvs["spearman_content_vs_style_cosine"] = rho
    cvs.sort_values("content_similarity", ascending=False).to_csv(tables / f"content_vs_style{tag}.csv", index=False, encoding="utf-8")

    print(f"[style] tag='{tag}' dims={len(dims)} speeches={len(sp)} B={B}")
    print(pairs_df[["leader_a", "leader_b", "style_distance", "ci_low", "ci_high", "share_closest_pair"]].round(3).to_string(index=False))
    print(f"[style] Spearman(content similarity, style cosine) over {len(cvs)} pairs = {rho:.2f}")
    show = rankings[rankings["rank"] == 1][["dimension", "leader", "value", "share_rank1"]]
    print("[style] rank-1 leader per dimension (share of bootstrap resamples where rank 1 holds):")
    print(show.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
