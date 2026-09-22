"""Phase 7 — speech-level bootstrap uncertainty.

Usage:
    python -m src.bootstrap --model qwen3_embedding_8b [--suffix _noceremonial]

The speech (not the chunk) is the resampling unit: within each leader, speeches are drawn with
replacement (same count as observed), then the leader centroid, theme profile, framing means and
dispersion are recomputed. Percentile confidence intervals are reported. With 3–5 speeches per
leader the intervals are wide and coarse by construction — that is the point: they show which
differences the corpus can and cannot support.

Outputs (outputs/tables/):
    bootstrap_leader_similarity_ci{tag}.csv   bootstrap_pair_rank_stability{tag}.csv
    bootstrap_pair_difference{tag}.csv        bootstrap_theme_profile_ci{tag}.csv
    bootstrap_top_theme_stability{tag}.csv    bootstrap_framing_ci{tag}.csv
    bootstrap_dispersion_ci{tag}.csv
Artifacts (artifacts/bootstrap/): {model}{suffix}_sim.npy (B×L×L), {model}{suffix}_theme_pct.npy (B×L×T)
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys
from .vectors import l2norm, load_embeddings, speech_centroids


def ci(arr: np.ndarray, level: float, axis: int = 0) -> tuple[np.ndarray, np.ndarray]:
    lo = (1 - level) / 2 * 100
    return np.percentile(arr, lo, axis=axis), np.percentile(arr, 100 - lo, axis=axis)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 7: speech-level bootstrap confidence intervals.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--iterations", type=int, default=None)
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    model_key = args.model or primary_model_key(cfg)
    tag = result_tag(cfg, model_key, args.suffix)
    tables = path_for(cfg, "outputs_tables")
    bs_dir = path_for(cfg, "artifacts_bootstrap")
    bs_dir.mkdir(parents=True, exist_ok=True)
    B = int(args.iterations or cfg["bootstrap_iterations"])
    level = float(cfg.get("bootstrap_confidence_level", 0.95))
    rng = np.random.default_rng(int(cfg["random_seed"]))
    themes, framings = theme_keys(cfg), framing_keys(cfg)

    emb, index = load_embeddings(cfg, model_key, args.suffix)
    sp_cent, sp_idx = speech_centroids(emb, index)
    speech_theme = pd.read_csv(tables / f"theme_profile_speech{tag}.csv").set_index("speech_id").loc[sp_idx["speech_id"]]
    speech_fram = pd.read_csv(tables / f"framing_speech{tag}.csv").set_index("speech_id").loc[sp_idx["speech_id"]]
    leaders = [L for L in leader_slugs(cfg) if (sp_idx["leader"] == L).any()]
    L, T, F = len(leaders), len(themes), len(framings)
    groups = {Ld: np.where((sp_idx["leader"] == Ld).to_numpy())[0] for Ld in leaders}

    theme_pct = speech_theme[[f"{k}_pct" for k in themes]].to_numpy()
    theme_cos = speech_theme[[f"{k}_cos" for k in themes]].to_numpy()
    fram_metrics = ["pct", "rate", "cos"] + (["nli"] if f"{framings[0]}_nli" in speech_fram else [])
    fram = {m: speech_fram[[f"{k}_{m}" for k in framings]].to_numpy() for m in fram_metrics}

    sim_b = np.empty((B, L, L), dtype=np.float32)
    tpct_b = np.empty((B, L, T), dtype=np.float32)
    tcos_b = np.empty((B, L, T), dtype=np.float32)
    fram_b = {m: np.empty((B, L, F), dtype=np.float32) for m in fram_metrics}
    disp_b = np.empty((B, L), dtype=np.float32)
    n_distinct = {}
    for li, Ld in enumerate(leaders):
        n = len(groups[Ld])
        from math import comb

        n_distinct[Ld] = comb(2 * n - 1, n)  # number of distinct multisets of size n

    for b in range(B):
        cents = np.empty((L, emb.shape[1]), dtype=np.float32)
        for li, Ld in enumerate(leaders):
            g = groups[Ld]
            draw = rng.choice(g, size=len(g), replace=True)
            c = l2norm(sp_cent[draw].mean(axis=0))
            cents[li] = c
            tpct_b[b, li] = theme_pct[draw].mean(axis=0)
            tcos_b[b, li] = theme_cos[draw].mean(axis=0)
            for m in fram_metrics:
                fram_b[m][b, li] = fram[m][draw].mean(axis=0)
            disp_b[b, li] = float((1.0 - sp_cent[draw] @ c).mean())
        sim_b[b] = cents @ cents.T
    np.save(bs_dir / f"{model_key}{args.suffix}_sim.npy", sim_b)
    np.save(bs_dir / f"{model_key}{args.suffix}_theme_pct.npy", tpct_b)

    # point estimates (observed)
    obs_cents = np.vstack([l2norm(sp_cent[groups[Ld]].mean(axis=0)) for Ld in leaders])
    obs_sim = obs_cents @ obs_cents.T
    obs_tpct = np.vstack([theme_pct[groups[Ld]].mean(axis=0) for Ld in leaders])
    obs_tcos = np.vstack([theme_cos[groups[Ld]].mean(axis=0) for Ld in leaders])
    obs_disp = np.array([float((1.0 - sp_cent[groups[Ld]] @ obs_cents[li]).mean()) for li, Ld in enumerate(leaders)])

    # --- pairwise similarity CIs, rank stability, differences ---------------------------------------
    pairs = [(i, j) for i in range(L) for j in range(i + 1, L)]
    lo, hi = ci(sim_b, level)
    rows = []
    for i, j in pairs:
        rows.append({"leader_a": leaders[i], "leader_b": leaders[j], "cosine_similarity": float(obs_sim[i, j]),
                     "boot_mean": float(sim_b[:, i, j].mean()), "ci_low": float(lo[i, j]), "ci_high": float(hi[i, j]),
                     "boot_sd": float(sim_b[:, i, j].std()), "n_speeches_a": len(groups[leaders[i]]), "n_speeches_b": len(groups[leaders[j]])})
    sim_ci = pd.DataFrame(rows).sort_values("cosine_similarity", ascending=False)
    sim_ci.to_csv(tables / f"bootstrap_leader_similarity_ci{tag}.csv", index=False, encoding="utf-8")

    pair_vals = np.stack([sim_b[:, i, j] for i, j in pairs], axis=1)  # B × P
    top = pair_vals.argmax(axis=1)
    bottom = pair_vals.argmin(axis=1)
    stab = pd.DataFrame({"leader_a": [leaders[i] for i, _ in pairs], "leader_b": [leaders[j] for _, j in pairs],
                         "share_most_similar_pair": np.bincount(top, minlength=len(pairs)) / B,
                         "share_least_similar_pair": np.bincount(bottom, minlength=len(pairs)) / B,
                         "observed": [float(obs_sim[i, j]) for i, j in pairs]}).sort_values("observed", ascending=False)
    stab.to_csv(tables / f"bootstrap_pair_rank_stability{tag}.csv", index=False, encoding="utf-8")

    obs_pairs = np.array([obs_sim[i, j] for i, j in pairs])
    top_obs = int(obs_pairs.argmax())
    diff_rows = []
    for p, (i, j) in enumerate(pairs):
        if p == top_obs:
            continue
        d = pair_vals[:, top_obs] - pair_vals[:, p]
        dlo, dhi = ci(d, level)
        diff_rows.append({"top_pair": f"{leaders[pairs[top_obs][0]]}–{leaders[pairs[top_obs][1]]}", "other_pair": f"{leaders[i]}–{leaders[j]}",
                          "observed_difference": float(obs_pairs[top_obs] - obs_pairs[p]), "ci_low": float(dlo), "ci_high": float(dhi),
                          "share_top_greater": float((d > 0).mean())})
    pd.DataFrame(diff_rows).to_csv(tables / f"bootstrap_pair_difference{tag}.csv", index=False, encoding="utf-8")

    # --- theme profile CIs and top-theme stability ---------------------------------------------------
    rows = []
    for metric, arr, obs in (("pct", tpct_b, obs_tpct), ("cos", tcos_b, obs_tcos)):
        lo, hi = ci(arr, level)
        for li, Ld in enumerate(leaders):
            for ti, k in enumerate(themes):
                rows.append({"leader": Ld, "theme": k, "metric": metric, "point": float(obs[li, ti]),
                             "ci_low": float(lo[li, ti]), "ci_high": float(hi[li, ti]), "boot_sd": float(arr[:, li, ti].std()),
                             "n_speeches": len(groups[Ld]), "n_distinct_resamples": n_distinct[Ld]})
    pd.DataFrame(rows).to_csv(tables / f"bootstrap_theme_profile_ci{tag}.csv", index=False, encoding="utf-8")

    rows = []
    ranks = (-tpct_b).argsort(axis=2)  # B × L × T (theme indices sorted desc)
    for li, Ld in enumerate(leaders):
        top1 = ranks[:, li, 0]
        top3 = ranks[:, li, :3]
        for ti, k in enumerate(themes):
            rows.append({"leader": Ld, "theme": k, "share_top1": float((top1 == ti).mean()),
                         "share_top3": float((top3 == ti).any(axis=1).mean()), "observed_pct": float(obs_tpct[li, ti]),
                         "observed_rank": int((-obs_tpct[li]).argsort().argsort()[ti] + 1)})
    pd.DataFrame(rows).to_csv(tables / f"bootstrap_top_theme_stability{tag}.csv", index=False, encoding="utf-8")

    # --- framing CIs ----------------------------------------------------------------------------------
    rows = []
    for m in fram_metrics:
        lo, hi = ci(fram_b[m], level)
        obs = np.vstack([fram[m][groups[Ld]].mean(axis=0) for Ld in leaders])
        for li, Ld in enumerate(leaders):
            for fi, k in enumerate(framings):
                rows.append({"leader": Ld, "framing": k, "metric": m, "point": float(obs[li, fi]), "ci_low": float(lo[li, fi]),
                             "ci_high": float(hi[li, fi]), "boot_sd": float(fram_b[m][:, li, fi].std()), "n_speeches": len(groups[Ld])})
    pd.DataFrame(rows).to_csv(tables / f"bootstrap_framing_ci{tag}.csv", index=False, encoding="utf-8")

    # --- dispersion CIs -------------------------------------------------------------------------------
    lo, hi = ci(disp_b, level)
    pd.DataFrame({"leader": leaders, "mean_dist_speech_to_leader": obs_disp, "ci_low": lo, "ci_high": hi,
                  "n_speeches": [len(groups[Ld]) for Ld in leaders]}).to_csv(
        tables / f"bootstrap_dispersion_ci{tag}.csv", index=False, encoding="utf-8")

    print(f"[bootstrap] tag='{tag}' B={B} level={level:.0%} speeches per leader: " + ", ".join(f"{Ld}={len(groups[Ld])}" for Ld in leaders))
    print(sim_ci[["leader_a", "leader_b", "cosine_similarity", "ci_low", "ci_high"]].round(3).to_string(index=False))
    print(stab[["leader_a", "leader_b", "share_most_similar_pair"]].round(3).head(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
