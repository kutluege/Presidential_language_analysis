"""Phase 4b — leader geometry in the original embedding space.

Usage:
    python -m src.geometry --model qwen3_embedding_8b [--suffix _noceremonial]

All numbers here are cosine values computed in the full embedding space (4096-d for Qwen3,
1024-d for BGE-M3). Nothing is projected. Interpretation is always "semantic similarity between
the collected speech corpora", never similarity between people or ideologies.

Outputs (outputs/tables/):
    leader_cosine_similarity{tag}.csv        5x5 leader-centroid cosine similarity
    leader_cosine_distance{tag}.csv          1 - similarity
    leader_pairs{tag}.csv                    the 10 pairs, sorted
    speech_cosine_similarity{tag}.csv        20x20 speech-centroid similarity
    chunk_knn_per_chunk{tag}.csv             per chunk: share of its k nearest neighbours per leader
    chunk_knn_leader_matrix{tag}.csv         row = chunk's leader, col = neighbour leader (observed share)
    chunk_knn_leader_shares{tag}.csv         long form with expected share and observed/expected ratio
    cross_leader_pairs{tag}.csv              most similar chunk pairs from different leaders (with excerpts)
    leader_cross_neighbor_similarity{tag}.csv  mean similarity of a leader's chunks to their k nearest chunks of each other leader
    semantic_dispersion{tag}.csv             within-leader concentration / spread
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

from .config import leader_slugs, load_config, path_for, primary_model_key, result_tag
from .vectors import cosine_matrix, leader_centroids, load_embeddings, pair_table, speech_centroids


def knn_analysis(emb: np.ndarray, index: pd.DataFrame, leaders: list[str], k: int, n_pairs: int = 30):
    n = len(emb)
    S = emb @ emb.T
    speech = index["speech_id"].astype(str).to_numpy()
    leader = index["leader"].astype(str).to_numpy()
    same_speech = speech[:, None] == speech[None, :]
    S_masked = np.where(same_speech, -np.inf, S)

    # k nearest neighbours excluding the same speech
    nn_idx = np.argsort(-S_masked, axis=1)[:, :k]
    nn_leader = leader[nn_idx]
    per_chunk = pd.DataFrame({"chunk_id": index["chunk_id"], "speech_id": speech, "leader": leader})
    for L in leaders:
        per_chunk[f"nn_share_{L}"] = (nn_leader == L).mean(axis=1)
    per_chunk["same_leader_share"] = (nn_leader == leader[:, None]).mean(axis=1)
    per_chunk["mean_nn_similarity"] = np.take_along_axis(S, nn_idx, axis=1).mean(axis=1)

    # expected share under random neighbours (per chunk: leader's chunks outside this speech / all outside)
    exp = np.zeros((n, len(leaders)))
    for j, L in enumerate(leaders):
        avail = (leader == L)[None, :] & ~same_speech
        exp[:, j] = avail.sum(axis=1) / (~same_speech).sum(axis=1)
    long_rows, obs_mat = [], pd.DataFrame(index=leaders, columns=leaders, dtype=float)
    for A in leaders:
        m = leader == A
        if not m.any():
            continue
        for j, B in enumerate(leaders):
            obs = float(per_chunk.loc[m, f"nn_share_{B}"].mean())
            e = float(exp[m, j].mean())
            obs_mat.loc[A, B] = obs
            long_rows.append({"leader": A, "neighbor_leader": B, "observed_share": obs, "expected_share": e,
                              "ratio_obs_exp": obs / e if e > 0 else np.nan, "n_chunks": int(m.sum())})
    shares = pd.DataFrame(long_rows)

    # leader-to-leader mean cross-neighbour similarity (k nearest chunks of B for each chunk of A)
    cross = pd.DataFrame(index=leaders, columns=leaders, dtype=float)
    for A in leaders:
        ia = np.where(leader == A)[0]
        if len(ia) == 0:
            continue
        for B in leaders:
            vals = []
            for i in ia:
                cand = np.where((leader == B) & ~same_speech[i])[0]
                if len(cand) == 0:
                    continue
                top = np.sort(S[i, cand])[::-1][: min(k, len(cand))]
                vals.append(top.mean())
            cross.loc[A, B] = float(np.mean(vals)) if vals else np.nan

    # most similar cross-leader chunk pairs
    diff_leader = leader[:, None] != leader[None, :]
    cand = np.where(np.triu(diff_leader, 1), S, -np.inf)
    flat = np.argsort(-cand, axis=None)[:n_pairs]
    ii, jj = np.unravel_index(flat, cand.shape)
    texts = index["chunk_text"].astype(str).to_numpy()
    pairs = pd.DataFrame({
        "cosine_similarity": S[ii, jj], "chunk_a": index["chunk_id"].to_numpy()[ii], "leader_a": leader[ii],
        "chunk_b": index["chunk_id"].to_numpy()[jj], "leader_b": leader[jj],
        "excerpt_a": [t[:200].replace("\n", " ") for t in texts[ii]], "excerpt_b": [t[:200].replace("\n", " ") for t in texts[jj]],
    })
    pairing_counts = pairs.apply(lambda r: " – ".join(sorted([r.leader_a, r.leader_b])), axis=1).value_counts()
    return per_chunk, obs_mat, shares, cross, pairs, pairing_counts


def dispersion(emb: np.ndarray, index: pd.DataFrame, sp_cent: np.ndarray, sp_idx: pd.DataFrame,
               ld_cent: np.ndarray, ld_idx: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for li, L in enumerate(ld_idx["leader"]):
        sp_mask = (sp_idx["leader"] == L).to_numpy()
        d_speech_leader = 1.0 - sp_cent[sp_mask] @ ld_cent[li]
        per_speech_chunk_d, chunk_leader_d = [], []
        for sid in sp_idx.loc[sp_mask, "speech_id"]:
            cm = (index["speech_id"].astype(str) == sid).to_numpy()
            c = sp_cent[(sp_idx["speech_id"] == sid).to_numpy()][0]
            per_speech_chunk_d.append(float((1.0 - emb[cm] @ c).mean()))
            chunk_leader_d.append(float((1.0 - emb[cm] @ ld_cent[li]).mean()))
        rows.append({"leader": L, "n_speeches": int(sp_mask.sum()), "n_chunks": int(sp_idx.loc[sp_mask, "n_chunks"].sum()),
                     "mean_dist_speech_to_leader": float(d_speech_leader.mean()),
                     "sd_dist_speech_to_leader": float(d_speech_leader.std(ddof=0)),
                     "mean_dist_chunk_to_speech": float(np.mean(per_speech_chunk_d)),
                     "mean_dist_chunk_to_leader": float(np.mean(chunk_leader_d))})
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 4b: leader geometry (centroids, kNN, dispersion).")
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
    tables = path_for(cfg, "outputs_tables")
    leaders = leader_slugs(cfg)
    k = int(cfg["knn_parameters"]["k"])

    emb, index = load_embeddings(cfg, model_key, args.suffix)
    sp_cent, sp_idx = speech_centroids(emb, index)
    ld_cent, ld_idx = leader_centroids(sp_cent, sp_idx, leaders)
    names = ld_idx["leader"].tolist()

    sim = cosine_matrix(ld_cent)
    pd.DataFrame(sim, index=names, columns=names).to_csv(tables / f"leader_cosine_similarity{tag}.csv", encoding="utf-8")
    pd.DataFrame(1.0 - sim, index=names, columns=names).to_csv(tables / f"leader_cosine_distance{tag}.csv", encoding="utf-8")
    pairs_ld = pair_table(sim, names)
    pairs_ld.to_csv(tables / f"leader_pairs{tag}.csv", index=False, encoding="utf-8")
    sp_sim = cosine_matrix(sp_cent)
    pd.DataFrame(sp_sim, index=sp_idx["speech_id"], columns=sp_idx["speech_id"]).to_csv(
        tables / f"speech_cosine_similarity{tag}.csv", encoding="utf-8")

    per_chunk, obs_mat, shares, cross, pairs, pairing_counts = knn_analysis(emb, index, names, k)
    per_chunk.to_csv(tables / f"chunk_knn_per_chunk{tag}.csv", index=False, encoding="utf-8")
    obs_mat.to_csv(tables / f"chunk_knn_leader_matrix{tag}.csv", encoding="utf-8")
    shares.to_csv(tables / f"chunk_knn_leader_shares{tag}.csv", index=False, encoding="utf-8")
    cross.to_csv(tables / f"leader_cross_neighbor_similarity{tag}.csv", encoding="utf-8")
    pairs.to_csv(tables / f"cross_leader_pairs{tag}.csv", index=False, encoding="utf-8")
    pairing_counts.rename_axis("pairing").reset_index(name="count_in_top_pairs").to_csv(
        tables / f"cross_leader_pairing_counts{tag}.csv", index=False, encoding="utf-8")

    disp = dispersion(emb, index, sp_cent, sp_idx, ld_cent, ld_idx)
    disp.to_csv(tables / f"semantic_dispersion{tag}.csv", index=False, encoding="utf-8")

    print(f"[geometry] tag='{tag}' model={model_key} dim={emb.shape[1]} k={k}")
    print("leader centroid cosine similarity:")
    print(pd.DataFrame(sim, index=names, columns=names).round(3).to_string())
    print("kNN observed share (row = chunk owner, col = neighbour leader):")
    print(obs_mat.astype(float).round(3).to_string())
    print("dispersion:")
    print(disp.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
