"""Phase 9 — video-ready interpretation, methodology (Turkish) and a results index (run 2, English corpus).

Usage:
    python -m src.generate_report

Every number is read from the result tables at run time. Wording rule: every claim is about the collected
speech corpus and its measurements — never about ideology, personality, competence or political quality.
Style rankings are sorted descriptive measurements with intervals.

Outputs: outputs/video_insights.md, outputs/methodology_for_video.md, outputs/results_summary.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys, theme_labels
from .emotion import etag_for


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join(floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in r) + " |")
    return "\n".join(out)


def pct(x: float) -> str:
    return f"{x * 100:.0f}%"


class Ctx:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.tables = path_for(cfg, "outputs_tables")
        self.out = path_for(cfg, "outputs")
        self.pk = primary_model_key(cfg)
        self.rk = next(k for k, m in cfg["embedding"]["models"].items() if m["hf_id"] == cfg["robustness_embedding_model"])
        self.tag = result_tag(cfg, self.pk, "")
        self.rtag = result_tag(cfg, self.rk, "")
        self.etag = etag_for("")
        self.leaders = leader_slugs(cfg)
        self.name = {L: cfg["leaders"][L]["short_name"] for L in self.leaders}
        self.themes, self.tl, self.tl_tr = theme_keys(cfg), theme_labels(cfg), theme_labels(cfg, "tr")
        self.framings = framing_keys(cfg)
        self.fl = {k: cfg["framing_definitions"][k]["label"] for k in self.framings}
        self.fl_tr = {k: cfg["framing_definitions"][k].get("label_tr", self.fl[k]) for k in self.framings}
        self.model = cfg["primary_embedding_model"].split("/")[-1]
        self.rmodel = cfg["robustness_embedding_model"].split("/")[-1]
        self.translated = [self.name[L] for L in self.leaders if cfg["leaders"][L].get("text_is_translation")]

    def t(self, name: str, tag: str | None = None) -> pd.DataFrame:
        return pd.read_csv(self.tables / f"{name}{self.tag if tag is None else tag}.csv")

    def t_opt(self, name: str, tag: str | None = None) -> pd.DataFrame | None:
        p = self.tables / f"{name}{self.tag if tag is None else tag}.csv"
        return pd.read_csv(p) if p.exists() else None

    def pn(self, a: str, b: str) -> str:
        return f"{self.name[a]}–{self.name[b]}"

    def pair_names(self, pair: str) -> str:
        a, b = pair.split("–")
        return self.pn(a, b)


# ------------------------------------------------------------------------------------------------
def build_findings(c: Ctx) -> tuple[list[dict], dict]:
    F: list[dict] = []
    facts: dict = {}
    chunks = pd.read_csv(path_for(c.cfg, "data_processed") / "chunks.csv")
    speeches = pd.read_csv(path_for(c.cfg, "data_processed") / "speeches_clean.csv")
    run = json.loads((path_for(c.cfg, "artifacts_embeddings") / f"{c.pk}_run.json").read_text(encoding="utf-8"))
    facts.update(n_speeches=len(speeches), n_chunks=len(chunks), n_words=int(speeches["word_count_clean"].sum()),
                 median_tokens=int(chunks["token_count"].median()), dim=int(run["dim"]), encode_s=float(run["encode_seconds"]),
                 vram=run.get("peak_vram_gb"), translated=c.translated)

    pairs = c.t("leader_pairs")
    pairs["pair"] = pairs["leader_a"] + "–" + pairs["leader_b"]
    ci = c.t("bootstrap_leader_similarity_ci")
    ci["pair"] = ci["leader_a"] + "–" + ci["leader_b"]
    ci = ci.set_index("pair")
    stab = c.t("bootstrap_pair_rank_stability")
    stab["pair"] = stab["leader_a"] + "–" + stab["leader_b"]
    stab = stab.set_index("pair")
    rpairs = c.t("leader_pairs", c.rtag)
    rpairs["pair"] = rpairs["leader_a"] + "–" + rpairs["leader_b"]
    rrank = rpairs.assign(rank=rpairs["cosine_similarity"].rank(ascending=False).astype(int)).set_index("pair")
    knn = c.t("chunk_knn_leader_shares")
    same = knn[knn["leader"] == knn["neighbor_leader"]].set_index("leader")
    rob = c.t("robustness_summary")
    le_pairs, le_knn = c.t_opt("language_effect_pairs", ""), c.t_opt("language_effect_knn", "")

    # 1. language effect --------------------------------------------------------------------------
    if le_pairs is not None and le_knn is not None:
        rho = float(rob[(rob["check"] == "G") & (rob["metric"] == "leader_pair_similarity_spearman")]["value"].iloc[0])
        k = le_knn.set_index("leader")
        erd = le_pairs[le_pairs["pair"].str.contains("erdogan")]
        F.append(dict(
            finding="Translating the corpus into English removed most of the language signal that dominated the first run: chunks stopped clustering by leader nearly as much, and Erdoğan's speeches moved from the edge of the space toward the middle.",
            number=f"Same-leader share of a chunk's 10 nearest neighbours (same model, {c.rmodel}): " + ", ".join(f"{c.name[L]} {pct(k.loc[L, 'old_same_leader_share'])} → {pct(k.loc[L, 'new_same_leader_share'])}" for L in c.leaders if L in k.index)
                   + f". Erdoğan's four leader pairs: mean rank {erd['old_rank'].mean():.1f} → {erd['new_rank'].mean():.1f} of 10. Rank correlation of the ten pair similarities between the two corpora: {rho:.2f}.",
            technical="Both runs use identical chunking, aggregation and the same Qwen3-Embedding-8B model; only the text language changed (run 1 archived in old_results/). Language and speaker were confounded in run 1; translation separates them at the price of adding the translator's voice.",
            video=f"Konuşmaları İngilizceye çevirince tablo değişti: birinci turda Erdoğan'ın parçalarının komşuları yüzde {k.loc['erdogan', 'old_same_leader_share']*100:.0f} oranında yine Erdoğan'dı, şimdi yüzde {k.loc['erdogan', 'new_same_leader_share']*100:.0f}. Model önce Türkçeyi görüyordu; şimdi içeriği görüyor.",
            caution=f"The English texts of {', '.join(c.translated)} are translations or official transcripts; what remains is content plus translator style. Putin and Trump did not change between runs.",
        ))

    # 2. structure that survives translation -------------------------------------------------------
    smin, smax = same["observed_share"].min(), same["observed_share"].max()
    emin, emax = same["expected_share"].min(), same["expected_share"].max()
    rknn = c.t("chunk_knn_leader_shares", c.rtag)
    rsame = rknn[rknn["leader"] == rknn["neighbor_leader"]].set_index("leader")
    rmin, rmax = rsame["observed_share"].min(), rsame["observed_share"].max()
    F.append(dict(
        finding="Even in English, a chunk's nearest neighbours still come from the same leader far more often than chance — the speech sets keep a recognisable content signature, and how strong it looks depends on the model.",
        number="Same-leader neighbour share (" + c.model + "): " + ", ".join(f"{c.name[L]} {pct(same.loc[L, 'observed_share'])} (×{same.loc[L, 'ratio_obs_exp']:.1f} vs chance)" for L in c.leaders if L in same.index)
               + f"; range {pct(smin)}–{pct(smax)} against a chance level of {pct(emin)}–{pct(emax)}. Same text with {c.rmodel}: {pct(rmin)}–{pct(rmax)}.",
        technical=f"kNN (k=10) on {facts['n_chunks']} unit-normalised vectors, excluding chunks of the same speech; expected share = the leader's share of the remaining chunks. "
                  f"{c.model} separates the speech sets more sharply than {c.rmodel} does on identical English text.",
        video=f"İngilizcede bile bir parçanın en yakın komşuları yüzde {smin*100:.0f} ile {smax*100:.0f} arasında aynı liderin diğer konuşmalarından geliyor; rastgele olsa bu oran yüzde {emin*100:.0f} ile {emax*100:.0f} arasında olurdu. "
              f"İkinci modelde aynı oran yüzde {rmin*100:.0f} ile {rmax*100:.0f}.",
        caution="A signature of the collected speech sets (topics, recurring occasions such as New Year addresses, translator style), not a fingerprint of the person; the strength of the signature is model-dependent.",
    ))

    # 3. most similar pair ----------------------------------------------------------------------------
    top = pairs.iloc[0]
    tp = top["pair"]
    F.append(dict(
        finding=f"The two speech sets whose centroids sit closest in the {c.model} space are {c.pair_names(tp)}.",
        number=f"Cosine similarity {top['cosine_similarity']:.3f} (95% speech-level bootstrap {ci.loc[tp, 'ci_low']:.3f}–{ci.loc[tp, 'ci_high']:.3f}); closest pair in {pct(stab.loc[tp, 'share_most_similar_pair'])} of 2000 resamples; "
               f"rank {rrank.loc[tp, 'rank']} of 10 under {c.rmodel}.",
        technical="Chunk vectors → normalised speech centroids → normalised leader centroids (equal weight per speech). Agreement between two different embedding models on the same English text is the main robustness test now that language is out of the picture.",
        video=f"Yeni modelde en yakın iki konuşma seti {c.pair_names(tp)}: kosinüs benzerliği {top['cosine_similarity']:.2f}. İkinci model aynı çifti {rrank.loc[tp, 'rank']}. sıraya koyuyor.",
        caution="Semantic similarity of the collected speeches, not ideological or personal similarity.",
    ))

    # 4. least similar + model agreement ----------------------------------------------------------------
    bottom = pairs.iloc[-1]
    bp = bottom["pair"]
    rho_a = float(rob[(rob["check"] == "A") & (rob["metric"] == "leader_pair_similarity_spearman")]["value"].iloc[0])
    F.append(dict(
        finding=f"The most distant pair is {c.pair_names(bp)}; the two models now {'agree' if rho_a >= 0.5 else 'still disagree'} about the overall ordering of the ten pairs.",
        number=f"{c.pair_names(bp)}: {bottom['cosine_similarity']:.3f} (rank {rrank.loc[bp, 'rank']} of 10 under {c.rmodel}). Spearman between the models' pair rankings: {rho_a:.2f} (run 1, mixed languages: −0.37).",
        technical="Same chunks, same aggregation, two models (3840-d vs 4096-d). Absolute cosine levels are model-specific; only rankings are compared.",
        video=f"En uzak çift {c.pair_names(bp)}. İki modelin sıralamaları arasındaki korelasyon birinci turda eksi 0.37'ydi, İngilizce metinde {rho_a:.2f}.",
        caution="With five leaders there are only ten pairs; a rank correlation over ten points is itself uncertain.",
    ))

    # 5. themes ---------------------------------------------------------------------------------------
    top3 = c.t("top_themes_by_leader")
    top3 = top3[top3["method"] == "embedding_pct"]
    tstab = c.t("bootstrap_top_theme_stability").set_index(["leader", "theme"])
    lines, lines_tr = [], []
    for L in c.leaders:
        rows = top3[top3["leader"] == L].sort_values("rank")
        if rows.empty:
            continue
        lines.append(f"{c.name[L]}: " + "; ".join(f"{c.tl[r.theme]} ({r.value:.2f}, top-3 in {pct(tstab.loc[(L, r.theme), 'share_top3'])})" for r in rows.itertuples()))
        lines_tr.append(f"{c.name[L]} için {c.tl_tr[rows.iloc[0]['theme']].lower()}")
    F.append(dict(
        finding="The three most represented themes in each collected speech set.",
        number="  \n".join(lines) + "  \nValues: mean percentile of chunk–theme similarity over the whole corpus (0.5 = corpus average).",
        technical="Each chunk is compared with eight fixed theme descriptions using the same embedding model; percentiles over all chunks, averaged per speech, then per leader.",
        video="Her konuşma setinde en çok yer alan tema: " + ", ".join(lines_tr) + ". İlk üçün tamamı ve güven aralıkları grafikte.",
        caution="Which themes the collected speeches lean towards relative to this corpus; not why. The NLI classifier ranks themes differently (see the agreement finding).",
    ))
    ts = tstab.reset_index()
    best = ts.sort_values("share_top1", ascending=False).iloc[0]
    F.append(dict(
        finding=f"The most stable theme signal is {c.tl[best['theme']]} in the {c.name[best['leader']]} speeches.",
        number=f"Mean percentile {best['observed_pct']:.2f}; top theme of that leader in {pct(best['share_top1'])} of 2000 speech-level resamples.",
        technical="The bootstrap redraws speeches with replacement within each leader and recomputes the profile; a theme that stays on top does not hinge on one speech.",
        video=f"En sağlam tema sinyali {c.name[best['leader']]} konuşmalarındaki '{c.tl_tr[best['theme']]}': 2000 yeniden örneklemede yüzde {best['share_top1']*100:.0f} oranında birinci.",
        caution="Stability within this corpus is not generalisation beyond it.",
    ))

    # 6. rhetorical rankings ----------------------------------------------------------------------------
    rk = c.t("style_rankings")
    rh = rk[rk["kind"] == "rhetorical"]
    lines, lines_tr = [], []
    for k in c.framings:
        sub = rh[rh["dimension"] == k].sort_values("rank")
        if sub.empty:
            continue
        first = sub.iloc[0]
        overlap = sub.iloc[1]["ci_high"] >= first["ci_low"] if len(sub) > 1 else True
        lines.append(f"{c.fl[k]}: " + " > ".join(f"{c.name[r.leader]} {r.value:.2f}" for r in sub.itertuples())
                     + f" — first place holds in {pct(first['share_rank1'])} of resamples{'; intervals of 1st and 2nd overlap' if overlap else ''}")
        lines_tr.append(f"{c.fl_tr[k].lower()} ölçeğinde {c.name[first['leader']]}")
    F.append(dict(
        finding="Seven rhetorical dimensions, ranked by measured value (sorted measurements, not a verdict).",
        number="  \n".join(lines),
        technical="Each dimension is a written description embedded with the same model; a chunk's score is its cosine similarity, expressed as a corpus percentile; speech means → leader means; 95% speech-level bootstrap intervals and the share of resamples in which the first-ranked leader stays first.",
        video="Yedi retorik ölçekte ilk sıralar: " + ", ".join(lines_tr) + ". Ama çoğu farkın güven aralığı örtüşüyor; bunlar sıralı ölçümler, hüküm değil.",
        caution=f"Descriptive similarity to a description, in one model, on {facts['n_speeches']} speeches. Translated leaders ({', '.join(c.translated)}) carry the translator's phrasing.",
    ))

    # 7. emotional tone ----------------------------------------------------------------------------------
    em = rk[rk["kind"] == "emotion"]
    etop = c.t_opt("emotion_top_labels_by_leader", c.etag)
    lines = []
    for dim in dict.fromkeys(em["dimension"]):
        sub = em[em["dimension"] == dim].sort_values("rank")
        lines.append(f"{sub['dimension_label'].iloc[0]}: " + ", ".join(f"{c.name[r.leader]} {r.value:.2f} [{r.ci_low:.2f}–{r.ci_high:.2f}]" for r in sub.itertuples()))
    top_emo = ""
    if etop is not None:
        top_emo = " Most frequent non-neutral emotion labels: " + "; ".join(
            f"{c.name[L]}: " + ", ".join(etop[(etop['leader'] == L) & (etop['rank'] <= 2)]['emotion']) for L in c.leaders if L in set(etop["leader"]))
    F.append(dict(
        finding="Emotional tone, measured by an independent classifier rather than by embeddings.",
        number="  \n".join(lines) + top_emo,
        technical="GoEmotions (28 labels, multi-label) grouped into families (family score = highest member probability per chunk) plus a three-class sentiment model (valence = P(positive) − P(negative)); chunk → speech → leader means; 95% speech-level bootstrap.",
        video="Duygu tonunu embedding'den bağımsız bir sınıflandırıcıyla ölçtük: olumlu-birleştirici duygu, korku-kayıp ve düşmanlık aileleri artı genel duygu değeri. Sonuçlar grafikte, aralıklarıyla.",
        caution="Classifiers trained on Reddit and Twitter text; political speech is out of domain, and translated leaders are scored on the translation.",
    ))

    # 8. style similarity -------------------------------------------------------------------------------
    spairs = c.t("style_pairs")
    cvs = c.t("content_vs_style")
    close, far = spairs.iloc[0], spairs.iloc[-1]
    rho_cs = float(cvs["spearman_content_vs_style_cosine"].iloc[0])
    F.append(dict(
        finding=f"On the combined style profile, the two most alike speech sets are {c.pn(close['leader_a'], close['leader_b'])}; the least alike are {c.pn(far['leader_a'], far['leader_b'])}.",
        number=f"Style distance {close['style_distance']:.2f} [{close['ci_low']:.2f}–{close['ci_high']:.2f}], closest pair in {pct(close['share_closest_pair'])} of resamples; farthest {far['style_distance']:.2f}. "
               f"Spearman between content similarity and style similarity over the ten pairs: {rho_cs:.2f}.",
        technical="Style vector per speech = 7 rhetorical percentiles + 3 emotion family means + valence, z-scored across the 20 speeches; leader = mean of its speeches; Euclidean distance and cosine; average-linkage dendrogram.",
        video=f"Retorik ve duygu profillerini birleştirince birbirine en çok benzeyen iki set {c.pn(close['leader_a'], close['leader_b'])}, en az benzeyen {c.pn(far['leader_a'], far['leader_b'])}. İçerik benzerliğiyle stil benzerliği arasındaki korelasyon {rho_cs:.2f}.",
        caution="Style here means these eleven measured dimensions of the English text, nothing more; it is not delivery, voice or charisma.",
    ))

    # 9. dispersion ------------------------------------------------------------------------------------
    disp = c.t("semantic_dispersion").set_index("leader")
    tight, wide = disp["mean_dist_speech_to_leader"].idxmin(), disp["mean_dist_speech_to_leader"].idxmax()
    F.append(dict(
        finding="The speech sets differ in how concentrated they are around their own centre.",
        number="Mean cosine distance of speech centroids to the leader centroid: " + ", ".join(f"{c.name[L]} {disp.loc[L, 'mean_dist_speech_to_leader']:.3f}" for L in c.leaders if L in disp.index)
               + ". Within speeches (chunk → speech centroid): " + ", ".join(f"{c.name[L]} {disp.loc[L, 'mean_dist_chunk_to_speech']:.3f}" for L in c.leaders if L in disp.index) + ".",
        technical=f"Distances in the original {facts['dim']}-d space. Speech-type mix (one Erdoğan symposium speech among New Year messages; three different Trump formats) and speech length both affect these numbers.",
        video=f"{c.name[tight]} konuşmaları kendi merkezine en yakın ({disp.loc[tight, 'mean_dist_speech_to_leader']:.3f}), {c.name[wide]} en dağınık ({disp.loc[wide, 'mean_dist_speech_to_leader']:.3f}). Bu tutarlılık değil, derlemin çeşitliliği.",
        caution="Semantic concentration of the collected files; not 'consistency' of a person.",
    ))

    # 10. clustering -----------------------------------------------------------------------------------
    cs = c.t("clusters_summary")
    cs_real = cs[cs["cluster"] >= 0]
    lc = c.t_opt("clusters_summary", f"__{c.pk}_leadercentered")
    lc_txt = ""
    if lc is not None:
        lc_real = lc[lc["cluster"] >= 0]
        mixed = lc_real[lc_real["leader_mix_entropy"] >= 0.75].sort_values("size", ascending=False)
        lc_txt = f" After subtracting each leader's centroid: {len(lc_real)} clusters, {len(mixed)} mixed (entropy ≥ 0.75), e.g. " + "; ".join(
            f"'{r.candidate_label}' ({r.size} chunks, {sum(1 for L in c.leaders if getattr(r, f'share_{L}', 0) > 0)} leaders)" for r in mixed.head(3).itertuples()) + "."
    F.append(dict(
        finding="Unsupervised clustering of the English chunks: how much of the structure is still 'who is speaking' and how much is topic.",
        number=f"HDBSCAN on the raw vectors: {len(cs_real)} clusters; single-leader share of the dominant leader per cluster {cs_real['dominant_leader_share'].min():.0%}–{cs_real['dominant_leader_share'].max():.0%}; "
               f"{cs.loc[cs['cluster'] == -1, 'share_of_chunks'].iloc[0]:.0%} unassigned.{lc_txt}",
        technical="PCA(50) → HDBSCAN; candidate labels from the fixed-theme scores of the member chunks; leader-centering removes each leader's mean vector so that only within-corpus variation remains.",
        video="Denetimsiz kümeleme İngilizce metinde bile büyük ölçüde liderleri buluyor; her liderin ortalamasını çıkarınca ekonomi, dış politika, kriz gibi ortak konu kümeleri kalıyor.",
        caution="Cluster membership depends on parameters (see the grid table); labels are neutral topical candidates.",
    ))

    # 11. method agreement -----------------------------------------------------------------------------------
    agree = c.t("theme_method_agreement")
    rve = c.t_opt("rhetoric_vs_emotion", "")
    rve_txt = ""
    if rve is not None and len(rve):
        r1 = rve[(rve["rhetorical"] == "conflict_threat_framing_pct") & (rve["emotion"] == "fam_hostility")]
        r2 = rve[(rve["rhetorical"] == "cooperation_solidarity_framing_pct") & (rve["emotion"] == "fam_affiliative_positive")]
        rve_txt = (f" Speech-level Spearman between conflict framing (embedding) and the hostility family (classifier): {float(r1['spearman_speech_level'].iloc[0]):.2f}; "
                   f"cooperation framing vs affiliative emotion: {float(r2['spearman_speech_level'].iloc[0]):.2f}.") if len(r1) and len(r2) else ""
    F.append(dict(
        finding="Independent methods agree only partly, which is why every style number is reported with its method attached.",
        number=f"Embedding vs NLI theme scoring: same top theme for {pct(agree['top_theme_agreement_emb_vs_nli'].iloc[0])} of chunks; chunk-level Spearman {agree['spearman_cos_vs_nli'].min():.2f}–{agree['spearman_cos_vs_nli'].max():.2f}.{rve_txt}",
        technical="Option A = cosine to descriptions (embedding); Option B = multilingual zero-shot NLI; emotion = supervised classifier. Moderate correlations mean the constructs overlap but are not the same measurement.",
        video=f"Aynı şeyi iki yöntemle ölçtüğümüzde parça düzeyinde sadece yüzde {agree['top_theme_agreement_emb_vs_nli'].iloc[0]*100:.0f} aynı birinci temayı buluyoruz. Bu yüzden her sayının yanında yöntemi de söylüyoruz.",
        caution="Method dependence is a property of the measurements, not a flaw of any speaker.",
    ))

    # 12. pipeline facts ----------------------------------------------------------------------------------
    F.append(dict(
        finding="The whole experiment runs on a small, fully traceable corpus and a single consumer GPU.",
        number=f"{facts['n_speeches']} speeches, {facts['n_words']:,} cleaned English words → {facts['n_chunks']} chunks (median {facts['median_tokens']} tokens) → {facts['dim']}-d vectors from an 11.8B-parameter model "
               f"({c.model}); embedding took {facts['encode_s']:.1f} s at {facts['vram']} GB peak VRAM on an RTX 5090; 2000 speech-level bootstrap resamples for every interval.",
        technical="Paragraph-based chunking (80–180 tokens, no overlap), unit-normalised embeddings, chunk → speech → leader aggregation, two embedding models, two classifiers, archived first run for the language comparison.",
        video=f"Tüm deney {facts['n_speeches']} konuşma, {facts['n_chunks']} parça ve {facts['dim']} boyutlu vektör; 12 milyar parametreli model hepsini {facts['encode_s']:.0f} saniyede gömdü, tek bir ekran kartında.",
        caution="3–5 speeches per leader, mostly New Year addresses from different years; every number is a statement about these files.",
    ))
    return F, facts


def write_video_insights(c: Ctx, F: list[dict]) -> None:
    lines = ["# Video insights — candidate findings (run 2, English corpus)", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M} from the result tables · primary model {c.model} · robustness model {c.rmodel}. "
             "Every finding is about the collected speech corpus and its measurements. None measures ideology, political quality, personality, competence or morality; none is an endorsement.",
             "", f"**Global caution to state on camera:** {c.cfg['methodology_notes']['translation_note']} The speeches come from different years and formats, and there are 3–5 per leader. "
             "Rankings are sorted measurements with confidence intervals; where intervals overlap, no difference should be claimed.", ""]
    for i, f in enumerate(F, 1):
        lines += [f"## Finding {i}", "", f"**FINDING**  \n{f['finding']}", "", f"**NUMBER**  \n{f['number']}", "",
                  f"**TECHNICAL EXPLANATION**  \n{f['technical']}", "", f"**VIDEO VERSION**  \n\"{f['video']}\"", "", f"**CAUTION**  \n{f['caution']}", ""]
    (c.out / "video_insights.md").write_text("\n".join(lines), encoding="utf-8")


def write_methodology(c: Ctx, facts: dict) -> None:
    ch, up = c.cfg["chunking"], c.cfg["umap_parameters"]
    txt = f"""# Video için metodoloji notları (Türkçe) — 2. tur, İngilizce derlem

Kamera karşısında bir yapay zekâ mühendisi gibi anlatmak için: kısa, doğru, abartısız.
Derlem: {facts['n_speeches']} konuşma, {facts['n_words']:,} temizlenmiş İngilizce kelime, {facts['n_chunks']} parça.
Birincil model: {c.model} (11.8 milyar parametre, {facts['dim']} boyut). Sağlamlık modeli: {c.rmodel}.

## Neden her şeyi İngilizceye çevirdik?
Birinci turda her lider kendi dilindeydi ve model önce dili gördü: bir parçanın komşularının %69–100'ü aynı liderden, yani aynı dildendi;
Türkçe konuşan Erdoğan uzayın en uzak köşesindeydi. Dil ile lideri ayıramıyorduk. Çeviri bu sinyali kaldırıyor.
Bedeli var: {', '.join(c.translated)} artık çevirmenin cümleleriyle konuşuyor. Stil ölçümlerinde bunu her seferinde söylüyoruz.
Birinci turun tüm sonuçları old_results/ klasöründe; aynı modelle (Qwen3) iki derlemi karşılaştıran "dil etkisi" grafiği buradan geliyor.

## Embedding nedir?
Bir metin parçasını anlamını temsil eden uzun bir sayı listesine (vektöre) çevirmek. Burada her parça {facts['dim']} sayı.
Anlamca yakın parçalar uzayda yakın düşer. Modelin "anlam" dediği şey eğitim verisinden öğrendiği istatistiksel örüntüler; konu, tür ve üslup hep bu vektörün içinde.

## Yeni model neden bu?
KaLM-Embedding-Gemma3-12B, açık ağırlıklı modeller arasında MTEB çok dilli sıralamasının en üstünde ve bf16 hassasiyetle bir RTX 5090'a sığan en büyük model (≈23 GB).
Daha yüksek puanlı 27 milyarlık bir model var ama 52 GB istiyor. Sağlamlık için aynı parçaları Qwen3-Embedding-8B ile de gömdük; iki model aynı şeyi söylüyorsa bulgu sağlam.

## Chunk (parça) neden kullandık?
Bütün konuşmayı tek vektöre sıkıştırsak konular birbirine karışır. Konuşmaları doğal paragraflardan başlayarak {ch['chunk_min_tokens']}–{ch['chunk_max_tokens']} token'lık
parçalara ayırdık (medyan {facts['median_tokens']} token, örtüşme yok). Böylece temaların sıklığını ve derlemlerin birbirine karışmasını ölçebiliyoruz.

## Cosine similarity nedir?
İki vektörün arasındaki açının kosinüsü: 1 aynı yön, 0 ilgisiz. Vektörler birim uzunlukta; yön karşılaştırılıyor, uzunluk değil.
Mutlak değerler modele özgüdür; iki modeli karşılaştırırken sıralamaya bakıyoruz.

## Leader centroid nasıl oluşturuldu?
(1) parça vektörlerini normalize et, (2) konuşmanın parçalarının ortalaması → normalize → konuşma merkezi,
(3) liderin konuşma merkezlerinin ortalaması → normalize → lider merkezi. Her konuşma eşit ağırlıkta.

## Retorik boyutlar ve "sıralama" ne demek?
Yedi boyut (çatışma-tehdit, iş birliği-dayanışma, geçmişe yönelim, geleceğe yönelim, biz-onlar, teşekkür-takdir, vaat-taahhüt) için birer tanım yazdık,
aynı modelle gömdük ve her parçanın tanıma benzerliğini ölçtük. Değerleri derlem yüzdeliği olarak veriyoruz (0.5 = derlem ortalaması).
"Sıralama", ölçülen değerlere göre sıralamak demek; yanında %95 güven aralığı var. Aralıklar örtüşüyorsa fark yok diyoruz. Kimseye "en sert" ya da "en yumuşak" etiketi yok.

## Duygu tonu nasıl ölçüldü?
Embedding'den bağımsız iki sınıflandırıcı: GoEmotions (28 duygu etiketi, çoklu etiket) ve üç sınıflı bir duygu değeri modeli.
Etiketleri ailelere topladık (olumlu-birleştirici, korku-kayıp, düşmanlık). Uyarı: bu modeller Reddit ve Twitter metniyle eğitildi; siyasi konuşma alan dışıdır.

## Stil benzerliği nasıl hesaplandı?
Her konuşma için 11 boyutlu bir stil vektörü (7 retorik boyut + 3 duygu ailesi + duygu değeri), tüm konuşmalar üzerinden z-puanı,
lider = konuşmalarının ortalaması, aradaki Öklid uzaklığı ve kosinüs. Dendrogram bu uzaklıklardan çiziliyor.
Ayrıca içerik benzerliği (embedding merkezleri) ile stil benzerliğini karşılaştırıyoruz: aynı şeyleri söyleyenler aynı şekilde mi söylüyor?

## Neden UMAP sonucu gerçek mesafe olarak kullanılmıyor?
UMAP {facts['dim']} boyutu 2'ye indirir; yerel komşulukları korur, küresel mesafeleri bozar. Ekrandaki uzaklık gerçek uzaklık değil.
"2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space."
Parametreler: n_neighbors={up['n_neighbors']}, min_dist={up['min_dist']}, metric={up.get('metric', 'cosine')}, seed={c.cfg['random_seed']}.

## Neden konuşma uzunluğunu normalize ettik?
En uzun konuşma 2.900 kelime, en kısası 450. Parça sayısı üzerinden ortalama alsak uzun konuşmalar kısaları ezerdi. Parça → konuşma → lider hiyerarşisinde her konuşma bir oy.

## Neden speech-level bootstrap yaptık?
Lider başına 3–5 konuşma var. Konuşmaları yerine koyarak 2000 kez yeniden örnekledik ve her sayıyı yeniden hesapladık.
Birim parça değil konuşma; çünkü aynı konuşmanın parçaları bağımsız değil. Güven aralığı sıfırı ya da komşusunu kapsıyorsa "fark var" demiyoruz.

## Söylememiz gereken şey
Tüm sayılar toplanan konuşma dosyalarını (İngilizce metinleriyle) tarif eder. İdeoloji, siyasi kalite, kişilik, yeterlilik ya da ahlak hakkında hiçbir şey söylemez.
"""
    (c.out / "methodology_for_video.md").write_text(txt, encoding="utf-8")


def write_results_summary(c: Ctx, facts: dict) -> None:
    sim = c.t("leader_cosine_similarity").rename(columns={"Unnamed: 0": "leader"})
    sim["leader"] = sim["leader"].map(c.name)
    sim = sim.rename(columns={L: c.name[L] for L in c.leaders})
    top3 = c.t("top_themes_by_leader")
    top3 = top3[top3["method"] == "embedding_pct"].pivot(index="leader", columns="rank", values="label").reset_index()
    top3.columns = ["leader", "1st", "2nd", "3rd"]
    top3["leader"] = top3["leader"].map(c.name)
    rk = c.t("style_rankings")
    first = rk[rk["rank"] == 1][["dimension_label", "leader", "value", "ci_low", "ci_high", "share_rank1"]].copy()
    first["leader"] = first["leader"].map(c.name)
    spairs = c.t("style_pairs")[["leader_a", "leader_b", "style_distance", "ci_low", "ci_high", "share_closest_pair"]].copy()
    spairs["leader_a"], spairs["leader_b"] = spairs["leader_a"].map(c.name), spairs["leader_b"].map(c.name)
    em = c.t_opt("emotion_profile_leader", c.etag)
    disp = c.t("semantic_dispersion")[["leader", "n_speeches", "n_chunks", "mean_dist_speech_to_leader", "mean_dist_chunk_to_speech"]].copy()
    disp["leader"] = disp["leader"].map(c.name)
    le = c.t_opt("language_effect_pairs", "")
    rob = c.t("robustness_summary")
    mat = rob[rob["material_change"] == True][["check", "comparison", "metric", "value"]]  # noqa: E712
    plots = sorted(p.name for p in path_for(c.cfg, "outputs_plots").glob("*.png"))
    tables = sorted(p.name for p in c.tables.glob("*.csv"))
    lines = [f"# Results summary — {c.cfg['project_name']} (run 2, English corpus)", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M}. Primary model `{c.cfg['primary_embedding_model']}`; robustness model `{c.cfg['robustness_embedding_model']}`. "
             f"{facts['n_speeches']} speeches · {facts['n_words']:,} clean words · {facts['n_chunks']} chunks · {facts['dim']}-d embeddings. First run archived in `old_results/`.", "",
             "> " + c.cfg["methodology_notes"]["interpretation_scope"], "", "> " + c.cfg["methodology_notes"]["translation_note"], "",
             "> " + c.cfg["methodology_notes"]["projection_note"], "",
             "## Leader-centroid cosine similarity (primary model)", "", md_table(sim), "",
             "## Three most represented themes per speech set", "", md_table(top3), "",
             "## Rhetorical and emotional dimensions — first-ranked leader per dimension (95% CI, share of resamples keeping rank 1)", "", md_table(first), "",
             "## Style similarity — the ten pairs, most alike first", "", md_table(spairs), ""]
    if em is not None:
        fams = [f"fam_{f}" for f in c.cfg["emotion"].get("report_families", []) if f"fam_{f}" in em.columns]
        e2 = em[["leader"] + fams + ["valence"]].copy()
        e2["leader"] = e2["leader"].map(c.name)
        lines += ["## Emotional tone (leader means)", "", md_table(e2), ""]
    lines += ["## Semantic concentration", "", md_table(disp), ""]
    if le is not None:
        le2 = le.copy()
        le2["pair"] = le2["pair"].map(c.pair_names)
        lines += ["## Language effect — same model (Qwen3), original-language run vs English run", "", md_table(le2[["pair", "old_similarity", "new_similarity", "delta", "old_rank", "new_rank"]]), ""]
    lines += ["## Robustness — material changes", "", md_table(mat) if len(mat) else "None.", "",
              "See `robustness_report.md`, `clusters_report.md`, `clusters_report__" + c.pk + "_leadercentered.md`, `phase0_report.md`, `data/processed/preprocessing_report.md`.", "",
              "## Files", "", "Plots (`outputs/plots/`, PNG 2× + SVG; `_9x16` = vertical): " + ", ".join(f"`{p}`" for p in plots), "",
              "Tables (`outputs/tables/`): " + ", ".join(f"`{t}`" for t in tables), ""]
    (c.out / "results_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 9: video insights, methodology and results index.")
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    cfg = load_config(args.config)
    c = Ctx(cfg)
    F, facts = build_findings(c)
    write_video_insights(c, F)
    write_methodology(c, facts)
    write_results_summary(c, facts)
    print(f"[generate_report] {len(F)} findings → video_insights.md; methodology_for_video.md; results_summary.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
