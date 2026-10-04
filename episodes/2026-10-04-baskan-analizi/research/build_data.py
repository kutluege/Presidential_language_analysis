"""Verify every number used in the episode (v2: five-chart story) and export clean animation data.

Run from anywhere inside the repository:
    python episodes/2026-10-04-baskan-analizi/research/build_data.py

The chunk embeddings (.npy) are git-ignored, so nothing is re-embedded. Instead each leader-level
number is recomputed from the next lower level the pipeline saved, then compared with the value the
pipeline reported (primary model KaLM-Embedding-Gemma3-12B-2511, all chunks, English corpus):

  themes       leader = mean of speech percentiles        <- theme_profile_speech.csv
  rhetoric     leader = mean of speech percentiles        <- framing_speech.csv
  emotion      speech = mean of chunks, leader = mean of speeches <- emotion_scores_chunks.csv
  style        z-score 11 dims over 20 speeches -> leader mean -> cosine  <- framing_speech + emotion_profile_speech
  content      leader-centroid cosine from speech cosine matrix           <- speech_cosine_similarity.csv
  dispersion   speech -> leader distance from speech cosine matrix         <- speech_cosine_similarity.csv
Bootstrap shares / intervals and chunk -> speech dispersion cannot be recomputed from saved tables;
they are read as reported and marked "table" in the log.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "config.yaml").exists())
T = ROOT / "outputs" / "tables"
HERE = Path(__file__).resolve().parent
OUT = HERE / "data"
TOL = 1e-4
LEADERS = ["erdogan", "macron", "merkel", "putin", "trump"]
NAMES = {"erdogan": "Erdoğan", "macron": "Macron", "merkel": "Merkel", "putin": "Putin", "trump": "Trump"}
THEMES = {"national_identity": "Ulusal kimlik ve birlik", "security_military": "Güvenlik ve askeriye",
          "economy_welfare": "Ekonomi ve refah", "foreign_policy": "Dış politika ve jeopolitik",
          "democracy_institutions": "Demokrasi, hukuk ve kurumlar", "social_solidarity": "Toplumsal dayanışma ve değerler",
          "crisis_resilience": "Kriz, tehdit ve dayanıklılık", "future_reform_technology": "Gelecek, reform ve teknoloji"}
RHET = {"conflict_threat_framing": "Çatışma / tehdit", "cooperation_solidarity_framing": "İş birliği",
        "past_orientation": "Geçmiş", "future_orientation": "Gelecek", "us_vs_them": "Biz–onlar",
        "gratitude_recognition": "Teşekkür", "promises_commitments": "Vaat"}
EMO = {"fam_affiliative_positive": "Olumlu / birleştirici", "fam_threat_negative": "Korku, üzüntü, kayıp",
       "fam_hostility": "Düşmanlık, onaylamama", "valence": "Duygu değeri (olumlu − olumsuz)"}
LOG: list[str] = []


def log(msg: str) -> None:
    print(msg)
    LOG.append(msg)


def check(label: str, rec: float, rep: float, tol: float = TOL) -> float:
    ok = abs(rec - rep) <= tol
    log(f"[{'OK ' if ok else 'BAD'}] {label}: recomputed {rec:.6f} | reported {rep:.6f}")
    if not ok:
        raise SystemExit(f"mismatch: {label}")
    return rec


tr = lambda x, d=2: f"{x:.{d}f}".replace(".", ",")      # brand: decimal comma
pct = lambda x, d=1: "%" + tr(100 * x, d)                # brand: % before the number
card = lambda x: int(round(100 * x))                    # FIFA-card style: percentile x 100


def spearman(a, b) -> float:
    return float(pd.Series(a).rank().corr(pd.Series(b).rank()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    speeches = pd.read_csv(ROOT / "data" / "metadata.csv")
    speeches["speech_id"] = speeches.filename.str.replace(".txt", "", regex=False)

    # ------------------------------------------------------------------ 1. themes
    log("== 1. Themes: leader = mean of speech percentiles")
    tps = pd.read_csv(T / "theme_profile_speech.csv")
    tpl = pd.read_csv(T / "theme_profile_leader.csv").set_index("leader")
    stab = pd.read_csv(T / "bootstrap_top_theme_stability.csv")
    rows = []
    for L in LEADERS:
        for k in THEMES:
            v = check(f"theme {L} {k}", tps[tps.leader == L][f"{k}_pct"].mean(), tpl.loc[L, f"{k}_pct"])
            s = stab[(stab.leader == L) & (stab.theme == k)].iloc[0]
            rows.append({"leader": L, "name": NAMES[L], "theme": k, "theme_tr": THEMES[k], "value": round(v, 4),
                         "share_top1": s.share_top1, "share_top3": s.share_top3})
    th = pd.DataFrame(rows)
    th["rank"] = th.groupby("leader").value.rank(ascending=False).astype(int)
    top = pd.read_csv(T / "top_themes_by_leader.csv").query("method == 'embedding_pct'")
    for r in top.itertuples():
        if th[(th.leader == r.leader) & (th["rank"] == r.rank)].theme.iloc[0] != r.theme:
            raise SystemExit(f"top-theme order mismatch {r.leader} {r.rank}")
    log("[OK ] top-3 order matches top_themes_by_leader.csv; top-3 / top-1 shares: table")
    th.sort_values(["leader", "rank"]).to_csv(OUT / "temalar.csv", index=False)
    erd = tps[tps.leader == "erdogan"][["speech_id", "democracy_institutions_pct", "foreign_policy_pct"]]
    erd_wo = erd[erd.speech_id != "erdogan1"].democracy_institutions_pct.mean()
    log("Erdoğan democracy/law by speech: " + ", ".join(f"{r.speech_id} {r.democracy_institutions_pct:.3f}" for r in erd.itertuples())
        + f" | mean without erdogan1 (symposium) {erd_wo:.3f}")

    # ------------------------------------------------------------------ 2. rhetoric radar
    log("== 2. Rhetorical dimensions: leader = mean of speech percentiles")
    fs = pd.read_csv(T / "framing_speech.csv")
    slp = pd.read_csv(T / "style_leader_profile.csv").set_index("leader")
    rk = pd.read_csv(T / "style_rankings.csv")
    rows = []
    for L in LEADERS:
        for k in RHET:
            v = check(f"rhetoric {L} {k}", fs[fs.leader == L][f"{k}_pct"].mean(), slp.loc[L, f"{k}_pct"])
            r = rk[(rk.dimension == k) & (rk.leader == L)].iloc[0]
            rows.append({"leader": L, "name": NAMES[L], "dimension": k, "dimension_tr": RHET[k], "value": round(v, 4),
                         "card": card(v), "rank": int(r["rank"]), "ci_low": round(r.ci_low, 3), "ci_high": round(r.ci_high, 3),
                         "share_rank1": r.share_rank1})
    rh = pd.DataFrame(rows)
    rh.to_csv(OUT / "radar_kartlar.csv", index=False)
    spread = rh.groupby("leader").value.agg(lambda s: s.max() - s.min())
    log("radar range (max-min) per leader: " + ", ".join(f"{L} {spread[L]:.3f}" for L in LEADERS))
    log("rank-1 shares (table): " + ", ".join(f"{r.name} {r.dimension_tr} {r.share_rank1:.3f}" for r in rh[rh['rank'] == 1].itertuples()))

    # ------------------------------------------------------------------ 3. emotion
    log("== 3. Emotion: speech = mean of chunks, leader = mean of speeches")
    ec = pd.read_csv(T / "emotion_scores_chunks.csv")
    eps = pd.read_csv(T / "emotion_profile_speech.csv").set_index("speech_id")
    epl = pd.read_csv(T / "emotion_profile_leader.csv").set_index("leader")
    sp_mean = ec.groupby("speech_id")[list(EMO) + ["emo_gratitude"]].mean()
    for sid in sp_mean.index:
        for c in EMO:
            check(f"emotion speech {sid} {c}", sp_mean.loc[sid, c], eps.loc[sid, c])
    rows = []
    for L in LEADERS:
        for c in EMO:
            v = check(f"emotion leader {L} {c}", eps[eps.leader == L][c].mean(), epl.loc[L, c])
            r = rk[(rk.dimension == c.replace("fam_", "")) & (rk.leader == L)].iloc[0]
            rows.append({"leader": L, "name": NAMES[L], "measure": c, "measure_tr": EMO[c], "value": round(v, 4),
                         "value_tr": pct(v) if c != "valence" else tr(v), "rank": int(r["rank"]),
                         "ci_low": round(r.ci_low, 3), "ci_high": round(r.ci_high, 3), "share_rank1": r.share_rank1,
                         "corpus_mean": round(r.corpus_mean, 3)})
    em = pd.DataFrame(rows)
    em.to_csv(OUT / "duygu.csv", index=False)
    tg = eps[eps.leader == "trump"][["emo_gratitude", "valence"]]
    log("Trump per speech gratitude / valence: " + ", ".join(f"{i} {r.emo_gratitude:.3f}/{r.valence:.3f}" for i, r in tg.iterrows())
        + "  (trump2 = 323-word excerpt compilation)")

    # ------------------------------------------------------------------ 4. style vs content
    log("== 4. Style similarity (11 z-scored dims) and content similarity")
    dims = [f"{k}_pct" for k in RHET] + ["fam_affiliative_positive", "fam_threat_negative", "fam_hostility", "valence"]
    sp = fs.merge(eps.reset_index()[["speech_id"] + dims[7:]], on="speech_id")
    X = sp[dims].to_numpy(float)
    Z = (X - X.mean(0)) / X.std(0, ddof=0)
    Lz = np.vstack([Z[(sp.leader == L).to_numpy()].mean(0) for L in LEADERS])
    Ln = Lz / np.linalg.norm(Lz, axis=1, keepdims=True)
    S = Ln @ Ln.T
    ssl = pd.read_csv(T / "style_similarity_leader.csv", index_col=0)
    scos = pd.read_csv(T / "speech_cosine_similarity.csv", index_col=0)
    lead = {sid: next(L for L in LEADERS if sid.startswith(L)) for sid in scos.index}
    blk = lambda a, b: scos.loc[[i for i in scos.index if lead[i] == a], [j for j in scos.columns if lead[j] == b]].to_numpy().sum()
    lcs = pd.read_csv(T / "leader_cosine_similarity.csv", index_col=0)
    stp = pd.read_csv(T / "style_pairs.csv")
    rows = []
    for i, a in enumerate(LEADERS):
        for j, b in enumerate(LEADERS[i + 1:], i + 1):
            s_ = check(f"style cosine {a}-{b}", S[i, j], ssl.loc[a, b])
            c_ = check(f"content cosine {a}-{b}", blk(a, b) / np.sqrt(blk(a, a) * blk(b, b)), lcs.loc[a, b])
            p = stp[(stp.leader_a == a) & (stp.leader_b == b)].iloc[0]
            rows.append({"pair": f"{NAMES[a]}–{NAMES[b]}", "a": a, "b": b, "style_cosine": round(s_, 3), "style_cosine_tr": tr(s_),
                         "style_share_closest": p.share_closest_pair, "content_cosine": round(c_, 3), "_c": c_, "_s": s_, "content_cosine_tr": tr(c_, 3)})
    st = pd.DataFrame(rows)
    st["style_rank"] = st._s.rank(ascending=False).astype(int)
    st["content_rank"] = st._c.rank(ascending=False).astype(int)
    st.sort_values("style_rank").drop(columns=["_c", "_s"]).to_csv(OUT / "stil_ciftler.csv", index=False)
    rho = check("Spearman content vs style cosine", spearman(st._c, st._s),
                pd.read_csv(T / "content_vs_style.csv").spearman_content_vs_style_cosine.iloc[0])
    cr = pd.read_csv(T / "bootstrap_pair_rank_stability.csv")
    mm_share = float(cr[(cr.leader_a == "macron") & (cr.leader_b == "merkel")].share_most_similar_pair.iloc[0])
    log(f"Macron–Merkel content rank-1 share (table) {mm_share:.3f}")

    # ------------------------------------------------------------------ 5. dispersion
    log("== 5. Dispersion: speech -> leader distance from the speech cosine matrix")
    sd = pd.read_csv(T / "semantic_dispersion.csv").set_index("leader")
    bd = pd.read_csv(T / "bootstrap_dispersion_ci.csv").set_index("leader")
    rows, per_speech = [], []
    for L in LEADERS:
        ids = [i for i in scos.index if lead[i] == L]
        M = scos.loc[ids, ids].to_numpy()
        d = 1 - M.sum(1) / np.sqrt(M.sum())          # 1 - cos(speech_i, leader centroid)
        v = check(f"dispersion speech->leader {L}", d.mean(), sd.loc[L, "mean_dist_speech_to_leader"])
        per_speech += [{"leader": L, "speech_id": s, "dist_to_leader": round(x, 4)} for s, x in zip(ids, d)]
        rows.append({"leader": L, "name": NAMES[L], "speech_to_leader": round(v, 4), "speech_to_leader_tr": tr(v, 3),
                     "chunk_to_speech": round(sd.loc[L, "mean_dist_chunk_to_speech"], 4),
                     "chunk_to_speech_tr": tr(sd.loc[L, "mean_dist_chunk_to_speech"], 3),
                     "ci_low": round(bd.loc[L, "ci_low"], 4), "ci_high": round(bd.loc[L, "ci_high"], 4)})
    dp = pd.DataFrame(rows)
    dp.to_csv(OUT / "dagilim.csv", index=False)
    pd.DataFrame(per_speech).to_csv(OUT / "dagilim_konusma.csv", index=False)
    e = pd.DataFrame(per_speech).query("leader == 'erdogan'").set_index("speech_id").dist_to_leader
    log("Erdoğan speech distances: " + ", ".join(f"{k} {v:.3f}" for k, v in e.items()) + "; chunk->speech: table")
    # Erdoğan spread without the symposium speech (centroid of the 4 New Year messages)
    ids = [i for i in scos.index if lead[i] == "erdogan" and i != "erdogan1"]
    M = scos.loc[ids, ids].to_numpy()
    erd4 = float((1 - M.sum(1) / np.sqrt(M.sum())).mean())
    log(f"Erdoğan speech->leader distance without erdogan1: {erd4:.4f}")

    # ------------------------------------------------------------------ corpus facts
    c = {"speeches": int(len(speeches)), "per_leader": speeches.groupby("leader").size().to_dict(),
         "new_year": int(speeches.speech_type.str.startswith("new_year").sum()),
         "types_other": speeches[~speeches.speech_type.str.startswith("new_year")][["speech_id", "speech_type"]].to_dict("records"),
         "translated": speeches[speeches.text_is_translation.astype(str).str.lower() == "true"].leader.unique().tolist()}
    log(f"corpus: {c['speeches']} speeches, {c['new_year']} New Year messages, other: {c['types_other']}")

    # ------------------------------------------------------------------ animation JSON
    def top3(L):
        return [{"theme_tr": r.theme_tr, "value": r.value, "value_tr": tr(r.value), "stable_top3_tr": pct(r.share_top3, 0)}
                for r in th[(th.leader == L) & (th["rank"] <= 3)].sort_values("rank").itertuples()]

    def em_rows(c_):
        return [{"name": r.name, "value": r.value, "value_tr": r.value_tr, "ci": [r.ci_low, r.ci_high]}
                for r in em[em.measure == c_].sort_values("value", ascending=False).itertuples()]

    anim = {
        "_note": "Recomputed by build_data.py from pipeline tables (verification_log.txt). *_tr = brand display strings.",
        "_model": "KaLM-Embedding-Gemma3-12B-2511 (themes, rhetoric, content); GoEmotions + sentiment classifier (emotion)",
        "corpus": c,
        "B1_temalar": {
            "scale_note": "0,50 = 20 konuşmanın ortalaması",
            "leaders": [{"name": NAMES[L], "top3": top3(L)} for L in LEADERS],
            "erdogan_democracy_by_speech": [{"speech_id": r.speech_id, "value_tr": tr(r.democracy_institutions_pct)} for r in erd.itertuples()],
            "erdogan_democracy_without_symposium_tr": tr(erd_wo)},
        "B2_fifa_kartlari": {
            "scale_note": "50 = ortalama (yüzdelik × 100)",
            "order": list(RHET.values()),
            "cards": [{"name": NAMES[L], "stats": {r.dimension_tr: r.card for r in rh[rh.leader == L].itertuples()},
                       "range": card(spread[L])} for L in LEADERS],
            "spoken": {"Putin": {"Teşekkür": card(rh.query("leader=='putin' and dimension=='gratitude_recognition'").value.iloc[0]),
                                 "Vaat": card(rh.query("leader=='putin' and dimension=='promises_commitments'").value.iloc[0])},
                       "Trump": {"Biz–onlar": card(rh.query("leader=='trump' and dimension=='us_vs_them'").value.iloc[0])},
                       "Merkel": {"İş birliği": card(rh.query("leader=='merkel' and dimension=='cooperation_solidarity_framing'").value.iloc[0])},
                       "Macron": {"Gelecek": card(rh.query("leader=='macron' and dimension=='future_orientation'").value.iloc[0])}}},
        "B3_duygu": {k: em_rows(k) for k in EMO},
        "B4_stil": {
            "style_pairs": [{"pair": r.pair, "style_cosine_tr": r.style_cosine_tr, "rank": int(r.style_rank)} for r in st.sort_values("style_rank").itertuples()],
            "macron_merkel": {"content_cosine_tr": st.query("pair=='Macron–Merkel'").content_cosine_tr.iloc[0],
                              "content_rank": int(st.query("pair=='Macron–Merkel'").content_rank.iloc[0]),
                              "style_cosine_tr": st.query("pair=='Macron–Merkel'").style_cosine_tr.iloc[0],
                              "style_rank": int(st.query("pair=='Macron–Merkel'").style_rank.iloc[0])},
            "spearman_content_style_tr": tr(rho)},
        "B5_dagilim": {"speech_to_leader": [{"name": r.name, "value_tr": r.speech_to_leader_tr} for r in dp.sort_values("speech_to_leader").itertuples()],
                       "chunk_to_speech": [{"name": r.name, "value_tr": r.chunk_to_speech_tr} for r in dp.sort_values("chunk_to_speech").itertuples()],
                       "erdogan_by_speech": [{"speech_id": k, "value_tr": tr(v, 3)} for k, v in e.items()],
                       "erdogan_without_symposium_tr": tr(erd4, 3)},
    }
    (OUT / "animation_data.json").write_text(json.dumps(anim, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "verification_log.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    log("wrote data/ and verification_log.txt")


if __name__ == "__main__":
    main()
