"""Verify every number used in the episode and export clean animation data.

Run from the repository root:
    python episodes/2026-10-04-baskan-analizi/research/build_data.py

Nothing here re-embeds text (the .npy embeddings are git-ignored). Instead every
leader-level number is recomputed independently from the lower-level tables the
pipeline saved, and compared with the value the pipeline reported:

  * leader-centroid cosine  <- speech_cosine_similarity*.csv
      leader centroid = normalised mean of unit speech centroids, so
      cos(A, B) = sum_ij s_ij / sqrt(sum_AA * sum_BB)  (sums over speech-sim blocks)
  * same-leader kNN share    <- chunk_knn_per_chunk*.csv (mean over a leader's chunks)
  * pair ranks / deltas      <- the recomputed similarities
Any mismatch above TOL stops the script.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "data"
NEW = ROOT / "outputs" / "tables"
OLD = ROOT / "old_results" / "outputs" / "tables"
TOL = 1e-4
LEADERS = ["erdogan", "macron", "merkel", "putin", "trump"]
NAMES = {"erdogan": "Erdoğan", "macron": "Macron", "merkel": "Merkel", "putin": "Putin", "trump": "Trump"}
# language each leader's text was in during run 1 (old_results/README.md, data/metadata.csv)
LANG_RUN1 = {"erdogan": "TR", "macron": "FR", "merkel": "DE", "putin": "EN", "trump": "EN"}
LOG: list[str] = []


def log(msg: str) -> None:
    print(msg)
    LOG.append(msg)


def check(label: str, recomputed: float, reported: float) -> float:
    ok = abs(recomputed - reported) <= TOL
    log(f"[{'OK ' if ok else 'BAD'}] {label}: recomputed {recomputed:.6f} | reported {reported:.6f}")
    if not ok:
        raise SystemExit(f"mismatch: {label}")
    return recomputed


def leader_sim_from_speeches(path: Path) -> pd.DataFrame:
    s = pd.read_csv(path, index_col=0)
    lead = {sid: next(L for L in LEADERS if sid.startswith(L)) for sid in s.index}
    out = pd.DataFrame(index=LEADERS, columns=LEADERS, dtype=float)
    blk = lambda a, b: s.loc[[i for i in s.index if lead[i] == a], [j for j in s.columns if lead[j] == b]].to_numpy().sum()
    for a in LEADERS:
        for b in LEADERS:
            out.loc[a, b] = blk(a, b) / np.sqrt(blk(a, a) * blk(b, b))
    return out


def pairs(sim: pd.DataFrame) -> pd.DataFrame:
    rows = [{"a": a, "b": b, "sim": float(sim.loc[a, b])} for i, a in enumerate(LEADERS) for b in LEADERS[i + 1:]]
    df = pd.DataFrame(rows)
    df["rank"] = df["sim"].rank(ascending=False).astype(int)
    return df


def verify_matrix(label: str, speech_csv: Path, leader_csv: Path) -> pd.DataFrame:
    rec = leader_sim_from_speeches(speech_csv)
    rep = pd.read_csv(leader_csv, index_col=0)
    for i, a in enumerate(LEADERS):
        for b in LEADERS[i + 1:]:
            check(f"{label} {a}-{b}", rec.loc[a, b], rep.loc[a, b])
    return rec


def knn_share(per_chunk_csv: Path, shares_csv: Path, label: str) -> dict:
    pc = pd.read_csv(per_chunk_csv)
    rep = pd.read_csv(shares_csv)
    rep = rep[rep.leader == rep.neighbor_leader].set_index("leader")
    out = {}
    for L in LEADERS:
        sub = pc[pc.leader == L]
        v = check(f"{label} kNN same-leader share {L}", sub.same_leader_share.mean(), rep.loc[L, "observed_share"])
        out[L] = {"share": v, "expected": float(rep.loc[L, "expected_share"]), "n_chunks": int(len(sub))}
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    log("== 1. Leader-centroid similarity, recomputed from speech-level similarity")
    q_old = verify_matrix("run1 qwen3 (original languages)", OLD / "speech_cosine_similarity.csv", OLD / "leader_cosine_similarity.csv")
    q_new = verify_matrix("run2 qwen3 (English)", NEW / "speech_cosine_similarity__qwen3_embedding_8b.csv", NEW / "leader_cosine_similarity__qwen3_embedding_8b.csv")
    k_new = verify_matrix("run2 kalm (English)", NEW / "speech_cosine_similarity.csv", NEW / "leader_cosine_similarity.csv")
    b_old = verify_matrix("run1 bge-m3 (original languages)", OLD / "speech_cosine_similarity__bge_m3.csv", OLD / "leader_cosine_similarity__bge_m3.csv")

    log("== 2. Same model (Qwen3-Embedding-8B), original languages -> English")
    po, pn, pk, pb = pairs(q_old), pairs(q_new), pairs(k_new), pairs(b_old)
    m = po.merge(pn, on=["a", "b"], suffixes=("_run1", "_run2")).merge(pk.rename(columns={"sim": "sim_kalm", "rank": "rank_kalm"}), on=["a", "b"])
    m = m.merge(pb.rename(columns={"sim": "sim_run1_bge", "rank": "rank_run1_bge"}), on=["a", "b"])
    m["delta"] = m.sim_run2 - m.sim_run1
    m["pair"] = m.a.map(NAMES) + "–" + m.b.map(NAMES)
    m["lang_run1"] = m.a.map(LANG_RUN1) + "–" + m.b.map(LANG_RUN1)
    m["both_english_in_run1"] = (m.a.map(LANG_RUN1) == "EN") & (m.b.map(LANG_RUN1) == "EN")
    rep = pd.read_csv(NEW / "language_effect_pairs.csv").set_index("pair")
    for r in m.itertuples():
        key = f"{r.a}–{r.b}"
        check(f"delta {key}", r.delta, rep.loc[key, "delta"])
        if (r.rank_run1, r.rank_run2) != (rep.loc[key, "old_rank"], rep.loc[key, "new_rank"]):
            raise SystemExit(f"rank mismatch {key}")
    log("[OK ] all 10 old/new ranks match language_effect_pairs.csv")
    m = m.sort_values("rank_run1")
    cols = ["pair", "a", "b", "lang_run1", "both_english_in_run1", "sim_run1", "rank_run1", "sim_run2", "rank_run2",
            "delta", "sim_kalm", "rank_kalm", "sim_run1_bge", "rank_run1_bge"]
    m[cols].round(4).to_csv(OUT / "pairs_run1_vs_run2.csv", index=False)
    others = m[~m.both_english_in_run1]
    log(f"non-EN/EN pairs: delta min {others.delta.min():.3f}, max {others.delta.max():.3f}; "
        f"Putin–Trump delta {m[m.both_english_in_run1].delta.iloc[0]:+.5f}")
    erd = m[(m.a == "erdogan") | (m.b == "erdogan")]
    log(f"Erdoğan pairs mean rank {erd.rank_run1.mean():.2f} -> {erd.rank_run2.mean():.2f}")

    log("== 3. Nearest-neighbour same-leader share, recomputed from per-chunk tables")
    k_old = knn_share(OLD / "chunk_knn_per_chunk.csv", OLD / "chunk_knn_leader_shares.csv", "run1 qwen3")
    k_q = knn_share(NEW / "chunk_knn_per_chunk__qwen3_embedding_8b.csv", NEW / "chunk_knn_leader_shares__qwen3_embedding_8b.csv", "run2 qwen3")
    k_k = knn_share(NEW / "chunk_knn_per_chunk.csv", NEW / "chunk_knn_leader_shares.csv", "run2 kalm")
    knn = pd.DataFrame([{
        "leader": L, "name": NAMES[L], "lang_run1": LANG_RUN1[L],
        "share_run1_qwen3": k_old[L]["share"], "expected_run1": k_old[L]["expected"], "n_chunks_run1": k_old[L]["n_chunks"],
        "share_run2_qwen3": k_q[L]["share"], "expected_run2": k_q[L]["expected"], "n_chunks_run2": k_q[L]["n_chunks"],
        "share_run2_kalm": k_k[L]["share"],
    } for L in LEADERS])
    knn.round(4).to_csv(OUT / "knn_same_leader_share.csv", index=False)
    # "out of 10 neighbours" version for the dot animation (rounded, documented as such)
    log("Erdoğan neighbours out of 10: run1 %.2f -> run2 %.2f" % (10 * k_old["erdogan"]["share"], 10 * k_q["erdogan"]["share"]))

    log("== 4. Bootstrap stability of the top / bottom pair (read from tables, 2000 resamples)")
    bo = pd.read_csv(OLD / "bootstrap_pair_rank_stability.csv")
    bq = pd.read_csv(NEW / "bootstrap_pair_rank_stability__qwen3_embedding_8b.csv")
    bk = pd.read_csv(NEW / "bootstrap_pair_rank_stability.csv")
    pt = lambda d: d[(d.leader_a == "putin") & (d.leader_b == "trump")].iloc[0]
    boot = {
        "run1_qwen3_putin_trump_share_most_similar": float(pt(bo).share_most_similar_pair),
        "run2_qwen3_putin_trump_share_least_similar": float(pt(bq).share_least_similar_pair),
        "run2_kalm_putin_trump_share_least_similar": float(pt(bk).share_least_similar_pair),
        "run2_kalm_macron_merkel_share_most_similar": float(bk[(bk.leader_a == "macron") & (bk.leader_b == "merkel")].iloc[0].share_most_similar_pair),
    }
    for k, v in boot.items():
        log(f"{k}: {v:.4f}")

    log("== 5. Rank agreement")
    sp = lambda x, y: float(pd.Series(x).rank().corr(pd.Series(y).rank()))
    rho_lang = sp(m.sim_run1.values, m.sim_run2.values)
    rho_models = sp(m.sim_run2.values, m.sim_kalm.values)
    check("Spearman run1 vs run2 (qwen3)", rho_lang, -0.4303)
    check("Spearman qwen3 vs kalm on English", round(rho_models, 2), 0.83)

    log("== 6. Control: Putin and Trump texts identical in both runs?")
    co = pd.read_csv(ROOT / "old_results" / "data_processed" / "chunks.csv")
    cn = pd.read_csv(ROOT / "data" / "processed" / "chunks.csv")
    for L in ["putin", "trump"]:
        same = co[co.leader == L].chunk_text.tolist() == cn[cn.leader == L].chunk_text.tolist()
        log(f"{L}: chunk texts identical across runs = {same}")
    corpus = {"speeches": int(cn.speech_id.nunique()), "chunks_run2": int(len(cn)), "chunks_run1": int(len(co)),
              "speeches_per_leader": cn.groupby("leader").speech_id.nunique().to_dict()}
    log(f"corpus: {corpus}")

    tr = lambda x, d=3: f"{x:.{d}f}".replace(".", ",")          # brand: decimal comma
    pct = lambda x, d=1: "%" + tr(100 * x, d)
    pairs_run1 = m.sort_values("rank_run1")
    anim = {
        "_note": "All values recomputed by build_data.py from pipeline tables (see verification_log.txt). "
                 "*_tr fields are display strings in brand format (decimal comma, % before the number).",
        "leaders": [{"id": L, "name": NAMES[L], "lang_run1": LANG_RUN1[L], "lang_run2": "EN"} for L in LEADERS],
        "corpus": corpus,
        "A1_siralama_tur1": {
            "model": "Qwen3-Embedding-8B", "corpus": "original languages (run 1)",
            "rows": [{"rank": int(r.rank_run1), "pair": r.pair, "lang": r.lang_run1, "sim": round(r.sim_run1, 3),
                      "sim_tr": tr(r.sim_run1), "highlight": bool(r.both_english_in_run1)} for r in pairs_run1.itertuples()],
            "bootstrap_top_share": round(boot["run1_qwen3_putin_trump_share_most_similar"], 3),
            "bootstrap_top_share_tr": pct(boot["run1_qwen3_putin_trump_share_most_similar"]),
            "bootstrap_n": 2000},
        "A2_dil_rozetleri": [{"name": NAMES[L], "badge_run1": LANG_RUN1[L], "badge_run2": "EN",
                              "flips_in_A3": LANG_RUN1[L] != "EN"} for L in LEADERS],
        "A4_egim_sira": [{"pair": r.pair, "rank_run1": int(r.rank_run1), "rank_run2": int(r.rank_run2),
                          "highlight": bool(r.both_english_in_run1)} for r in pairs_run1.itertuples()],
        "A5_kipirdamadi": {
            "putin_trump": {"sim_run1_tr": tr(float(m[m.both_english_in_run1].sim_run1.iloc[0])),
                            "sim_run2_tr": tr(float(m[m.both_english_in_run1].sim_run2.iloc[0]))},
            "others": [{"pair": r.pair, "delta": round(r.delta, 3), "delta_tr": "+" + tr(r.delta)}
                       for r in m[~m.both_english_in_run1].sort_values("delta", ascending=False).itertuples()]},
        "A6_komsular": {
            "model": "Qwen3-Embedding-8B (same model both runs)", "k": 10,
            "share_run1": round(k_old["erdogan"]["share"], 3), "share_run1_tr": pct(k_old["erdogan"]["share"]),
            "share_run2": round(k_q["erdogan"]["share"], 3), "share_run2_tr": pct(k_q["erdogan"]["share"]),
            "filled_dots_run1": int(round(10 * k_old["erdogan"]["share"])),
            "filled_dots_run2": int(round(10 * k_q["erdogan"]["share"])),
            "_dots_note": "dot counts are the rounded average over all Erdoğan paragraphs; the % label is exact"},
        "A8_ikinci_model": {
            "model": "KaLM-Embedding-Gemma3-12B-2511", "corpus": "English (run 2)",
            "rows": [{"rank": int(r.rank_kalm), "pair": r.pair, "sim_tr": tr(r.sim_kalm), "highlight": bool(r.both_english_in_run1)}
                     for r in m.sort_values("rank_kalm").itertuples()],
            "bottom_share_tr": pct(boot["run2_kalm_putin_trump_share_least_similar"]),
            "spearman_with_qwen3_english": round(rho_models, 2)},
        "bootstrap": {k: round(v, 3) for k, v in boot.items()},
        "spearman_run1_vs_run2_same_model": round(rho_lang, 2),
        "run1_bge_m3_note": {"_why": "second model of run 1; did NOT rank Putin–Trump first even in original languages",
                             "putin_trump_rank": int(m[m.both_english_in_run1].rank_run1_bge.iloc[0]),
                             "top_pair": m.sort_values("rank_run1_bge").pair.iloc[0],
                             "erdogan_knn_same_leader_share": round(float(pd.read_csv(OLD / "chunk_knn_per_chunk__bge_m3.csv").query("leader == 'erdogan'").same_leader_share.mean()), 3)},
    }
    (OUT / "animation_data.json").write_text(json.dumps(anim, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT.parent / "verification_log.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    log("wrote data/ and verification_log.txt")


if __name__ == "__main__":
    main()
