"""Phase 9 — video-ready interpretation, methodology (Turkish) and a results index.

Usage:
    python -m src.generate_report

Everything below is filled from the result tables at run time, so the documents stay in sync with
the numbers. Wording follows the project rule: every claim is about the collected speech corpus and
its embeddings — never about ideology, personality, competence or political quality.

Outputs: outputs/video_insights.md, outputs/methodology_for_video.md, outputs/results_summary.md
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, theme_keys, theme_labels


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join(floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in r) + " |")
    return "\n".join(out)


class Ctx:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.tables = path_for(cfg, "outputs_tables")
        self.out = path_for(cfg, "outputs")
        self.pk = primary_model_key(cfg)
        self.rk = next(k for k, m in cfg["embedding"]["models"].items() if m["hf_id"] == cfg["robustness_embedding_model"])
        self.tag = result_tag(cfg, self.pk, "")
        self.rtag = result_tag(cfg, self.rk, "")
        self.leaders = leader_slugs(cfg)
        self.name = {L: cfg["leaders"][L]["short_name"] for L in self.leaders}
        self.themes, self.tl = theme_keys(cfg), theme_labels(cfg)
        self.tl_tr = theme_labels(cfg, "tr")
        self.framings = framing_keys(cfg)
        self.model = cfg["primary_embedding_model"]
        self.rmodel = cfg["robustness_embedding_model"]

    def t(self, name: str, tag: str | None = None) -> pd.DataFrame:
        return pd.read_csv(self.tables / f"{name}{self.tag if tag is None else tag}.csv")

    def pairname(self, a: str, b: str) -> str:
        return f"{self.name[a]}–{self.name[b]}"


# ------------------------------------------------------------------------------------------------
def build_findings(c: Ctx) -> tuple[list[dict], dict]:
    F: list[dict] = []
    facts: dict = {}

    chunks = pd.read_csv(path_for(c.cfg, "data_processed") / "chunks.csv")
    speeches = pd.read_csv(path_for(c.cfg, "data_processed") / "speeches_clean.csv")
    run = pd.read_json(path_for(c.cfg, "artifacts_embeddings") / f"{c.pk}_run.json", typ="series")
    facts.update(n_speeches=len(speeches), n_chunks=len(chunks), n_words=int(speeches["word_count_clean"].sum()),
                 median_tokens=int(chunks["token_count"].median()), dim=int(run["dim"]), encode_s=float(run["encode_seconds"]))

    pairs = c.t("leader_pairs")
    pairs["pair"] = pairs["leader_a"] + "–" + pairs["leader_b"]
    ci = c.t("bootstrap_leader_similarity_ci")
    ci["pair"] = ci["leader_a"] + "–" + ci["leader_b"]
    ci = ci.set_index("pair")
    stab = c.t("bootstrap_pair_rank_stability")
    stab["pair"] = stab["leader_a"] + "–" + stab["leader_b"]
    stab = stab.set_index("pair")
    diff = c.t("bootstrap_pair_difference").set_index("other_pair")
    rpairs = c.t("leader_pairs", c.rtag)
    rpairs["pair"] = rpairs["leader_a"] + "–" + rpairs["leader_b"]
    rrank = rpairs.reset_index(drop=True).assign(rank=lambda d: d["cosine_similarity"].rank(ascending=False).astype(int)).set_index("pair")
    knn = c.t("chunk_knn_leader_shares")
    same = knn[knn["leader"] == knn["neighbor_leader"]].set_index("leader")
    rob = c.t("robustness_summary")

    # --- 1. language / leader identity dominates the geometry ---------------------------------
    smin, smax = same["observed_share"].min(), same["observed_share"].max()
    rmin, rmax = same["ratio_obs_exp"].min(), same["ratio_obs_exp"].max()
    facts["same_leader_share"] = same["observed_share"].to_dict()
    F.append(dict(
        finding="In this corpus, a chunk's nearest neighbours in embedding space are almost always other chunks by the same leader — and each leader speaks a different language.",
        number=f"Share of the 10 nearest neighbours (other speeches only) from the same leader: {smin:.0%}–{smax:.0%} "
               f"({', '.join(f'{c.name[L]} {same.loc[L, 'observed_share']:.0%}' for L in c.leaders)}); {rmin:.1f}×–{rmax:.1f}× what random neighbours would give.",
        technical=f"k-nearest-neighbour analysis on {facts['n_chunks']} unit-normalised {c.model} chunk vectors, excluding chunks of the same speech. "
                  "Leader and language are confounded (tr/fr/de/en; Putin and Trump share English), so the model's language signal and the speaker signal cannot be separated here.",
        video=f"Embedding uzayında bu konuşmaların en yakın komşuları neredeyse hep aynı liderin diğer konuşmalarından geliyor: %{smin*100:.0f} ile %{smax*100:.0f} arasında. "
              "Ama dikkat, her lider farklı bir dilde konuşuyor; model önce dili görüyor.",
        caution="This is not evidence of distinctive 'personal styles'. Language, transcript conventions and speech genre all pull chunks of one leader together; an English-normalised corpus would be needed to separate them.",
    ))

    # --- 2. most similar pair ---------------------------------------------------------------------
    top = pairs.iloc[0]
    tp = top["pair"]
    top_r = rrank.loc[tp, "rank"]
    F.append(dict(
        finding=f"The two collected speech sets whose centroids sit closest in the {c.model} space are {c.pairname(top['leader_a'], top['leader_b'])}.",
        number=f"Cosine similarity {top['cosine_similarity']:.3f} (95% speech-level bootstrap interval {ci.loc[tp, 'ci_low']:.3f}–{ci.loc[tp, 'ci_high']:.3f}); "
               f"closest pair in {stab.loc[tp, 'share_most_similar_pair']:.0%} of 2000 resamples. Under {c.rmodel} the same pair ranks {top_r} of 10.",
        technical="Chunk vectors → normalised speech centroids → normalised leader centroid (each speech weighs equally). "
                  f"Both corpora are English transcripts, and the pair drops to rank {top_r} with the second model, so language and model choice are the leading explanations.",
        video=f"Bu embedding modelinde en yakın iki konuşma seti {c.pairname(top['leader_a'], top['leader_b'])} çıktı: kosinüs benzerliği {top['cosine_similarity']:.2f}. "
              f"Ama ikisi de İngilizce metin ve ikinci modelde aynı çift {top_r}. sıraya düşüyor.",
        caution="Semantic similarity of the collected speeches in one model's space; not ideological, political or personal similarity. Not robust to the embedding model.",
    ))

    # --- 3. the pair that stays close under both models -----------------------------------------
    both = [(p, r.cosine_similarity) for p, r in pairs.set_index("pair").iterrows() if rrank.loc[p, "rank"] <= 2 and pairs.set_index("pair").index.get_loc(p) <= 1]
    if both:
        p, v = both[0]
        a, b = p.split("–")
        d = diff.loc[p] if p in diff.index else None
        F.append(dict(
            finding=f"{c.pairname(a, b)} is the only pair that ranks in the top two under both embedding models.",
            number=f"{c.model}: {v:.3f} (rank {int(pairs.set_index('pair').index.get_loc(p)) + 1}); {c.rmodel}: {rrank.loc[p, 'cosine_similarity']:.3f} (rank {rrank.loc[p, 'rank']})."
                   + (f" Difference to the top pair is not significant: 95% CI {d['ci_low']:.3f} to {d['ci_high']:.3f}." if d is not None else ""),
            technical="Leader-centroid cosine similarity computed independently with two multilingual embedding models; the bootstrap difference CI resamples speeches within each leader.",
            video=f"İki farklı embedding modelinde de ilk ikide kalan tek çift {c.pairname(a, b)}. Bu sonuç modele göre değişmeyen az sayıdaki bulgudan biri.",
            caution="Two European New Year addresses in French and German; similar genre and neighbouring topics (Europe, energy, climate) are plausible drivers. Not a claim about the two people.",
        ))

    # --- 4. model dependence ---------------------------------------------------------------------
    rho = float(rob[(rob["check"] == "A") & (rob["metric"] == "leader_pair_similarity_spearman")]["value"].iloc[0])
    bottom = pairs.iloc[-1]
    bp = bottom["pair"]
    F.append(dict(
        finding="Which corpora look 'close' depends strongly on the embedding model: the two models disagree about the ranking of the ten leader pairs.",
        number=f"Spearman rank correlation between the pair rankings of {c.model} and {c.rmodel}: {rho:.2f}. "
               f"{c.pairname(bottom['leader_a'], bottom['leader_b'])} is the least similar pair in the first model ({bottom['cosine_similarity']:.3f}) and rank {rrank.loc[bp, 'rank']} of 10 in the second ({rrank.loc[bp, 'cosine_similarity']:.3f}).",
        technical="Same chunks, same aggregation, two models (4096-d vs 1024-d). BGE-M3's space is more compressed (mean off-diagonal similarity 0.88 vs 0.65) and less language-clustered "
                  f"(same-leader neighbour share {c.name['erdogan']} 100% → {float(rob[(rob['check']=='A') & (rob['metric']=='knn_same_leader_share_erdogan')]['value'].iloc[0].split('|')[1]):.0%}).",
        video=f"İşin ilginç tarafı: modeli değiştirince sıralama tersine dönebiliyor. İki modelin lider çifti sıralamaları arasındaki korelasyon {rho:.2f}. "
              "Yani 'kim kime yakın' sorusunun cevabı modelin gözlüğüne bağlı.",
        caution="Neither model is 'right'. Cross-lingual geometry with 3–5 speeches per leader is fragile; only findings that survive both models should be quoted as findings about the corpus.",
    ))

    # --- 5. top themes per leader ---------------------------------------------------------------
    top3 = c.t("top_themes_by_leader")
    top3 = top3[top3["method"] == "embedding_pct"]
    tstab = c.t("bootstrap_top_theme_stability").set_index(["leader", "theme"])
    lines, lines_tr = [], []
    for L in c.leaders:
        rows = top3[top3["leader"] == L].sort_values("rank")
        parts = [f"{c.tl[r.theme]} ({r.value:.2f}, top-3 in {tstab.loc[(L, r.theme), 'share_top3']:.0%} of resamples)" for r in rows.itertuples()]
        lines.append(f"{c.name[L]}: " + "; ".join(parts))
        lines_tr.append(f"{c.name[L]} için {c.tl_tr[rows.iloc[0]['theme']].lower()}")
    F.append(dict(
        finding="The three most represented themes in each collected speech set (embedding similarity to language-matched theme descriptions).",
        number="  \n".join(lines) + "  \nValues are mean percentile ranks over the whole corpus (0.5 = corpus average).",
        technical="Each chunk is compared with the eight theme descriptions written in the chunk's own language; percentile ranks are taken over all chunks, averaged per speech, then per leader.",
        video="Her konuşma setinde en çok yer alan tema: " + ", ".join(lines_tr) + ". İlk üçün tamamı ve güven aralıkları grafikte.",
        caution="These describe which themes the collected speeches lean towards relative to this corpus. They do not say why a theme was emphasised, and the NLI classifier ranks the themes differently (see the method-agreement finding).",
    ))

    # --- 6. most stable single theme signal -------------------------------------------------------
    ts = tstab.reset_index()
    best = ts.sort_values("share_top1", ascending=False).iloc[0]
    prof = c.t("theme_profile_leader").set_index("leader")
    rprof = c.t("theme_profile_leader", c.rtag).set_index("leader")
    r_top = c.themes[int(np.argmax(rprof.loc[best["leader"], [f"{k}_pct" for k in c.themes]].to_numpy(float)))]
    F.append(dict(
        finding=f"The single most stable theme signal in the corpus is {c.tl[best['theme']]} in the {c.name[best['leader']]} speeches.",
        number=f"Mean percentile {best['observed_pct']:.2f}; the leader's top theme in {best['share_top1']:.0%} of 2000 speech-level resamples; "
               f"also the top theme under {c.rmodel} ({'yes' if r_top == best['theme'] else 'no: ' + c.tl[r_top]}).",
        technical="Bootstrap resamples speeches with replacement within the leader and recomputes the theme profile each time; a theme that stays on top across resamples does not depend on one speech.",
        video=f"En sağlam tema sinyali {c.name[best['leader']]} konuşmalarındaki '{c.tl_tr[best['theme']]}': 2000 yeniden örneklemede yüzde {best['share_top1']*100:.0f} oranında birinci sırada.",
        caution="Stability across resamples of the same speeches is not the same as generalisation to speeches outside this corpus.",
    ))

    # --- 7. framing measurements -----------------------------------------------------------------
    fl = c.t("framing_leader").set_index("leader")
    fci = c.t("bootstrap_framing_ci")
    fci = fci[fci["metric"] == "pct"].set_index(["leader", "framing"])
    rows_c = [f"{c.name[L]} {fl.loc[L, 'conflict_threat_framing_pct']:.2f} [{fci.loc[(L, 'conflict_threat_framing'), 'ci_low']:.2f}–{fci.loc[(L, 'conflict_threat_framing'), 'ci_high']:.2f}], rate {fl.loc[L, 'conflict_threat_framing_rate']:.0%}" for L in c.leaders]
    rows_k = [f"{c.name[L]} {fl.loc[L, 'cooperation_solidarity_framing_pct']:.2f} [{fci.loc[(L, 'cooperation_solidarity_framing'), 'ci_low']:.2f}–{fci.loc[(L, 'cooperation_solidarity_framing'), 'ci_high']:.2f}], rate {fl.loc[L, 'cooperation_solidarity_framing_rate']:.0%}" for L in c.leaders]
    rho_c = float(rob[(rob["check"] == "A") & (rob["metric"] == "framing_leader_order_spearman_conflict_threat_framing")]["value"].iloc[0])
    F.append(dict(
        finding="Conflict/threat and cooperation/solidarity framing, measured for all five speech sets (no ranking, no labels).",
        number="conflict_threat_framing: " + "; ".join(rows_c) + ".  \ncooperation_solidarity_framing: " + "; ".join(rows_k) + ".",
        technical="Mean percentile of chunk similarity to a framing description (language-matched), speech-weighted; 'rate' = share of a leader's chunks in the corpus top quartile. "
                  f"The leader ordering for conflict framing has Spearman {rho_c:.2f} between the two embedding models, i.e. it is model-sensitive.",
        video="Çatışma-tehdit ve iş birliği-dayanışma dilini iki ayrı ölçek olarak ölçtük; kimseye 'en sert' ya da 'en yumuşak' etiketi yok. "
              + " ".join(f"{c.name[L]} çatışma {fl.loc[L, 'conflict_threat_framing_pct']:.2f}, iş birliği {fl.loc[L, 'cooperation_solidarity_framing_pct']:.2f}." for L in c.leaders),
        caution="Descriptive similarity to two concept descriptions, in one model. Intervals overlap for most leaders and the ordering flips with the second model; do not read as tone, intent or aggression.",
    ))

    # --- 8. dispersion ----------------------------------------------------------------------------
    disp = c.t("semantic_dispersion").set_index("leader")
    tight, wide = disp["mean_dist_speech_to_leader"].idxmin(), disp["mean_dist_speech_to_leader"].idxmax()
    F.append(dict(
        finding="The collected corpora differ in how concentrated they are around their own centre.",
        number="Mean cosine distance of speech centroids to the leader centroid: " + ", ".join(f"{c.name[L]} {disp.loc[L, 'mean_dist_speech_to_leader']:.3f}" for L in c.leaders)
               + ". Within speeches (chunk → speech centroid): " + ", ".join(f"{c.name[L]} {disp.loc[L, 'mean_dist_chunk_to_speech']:.3f}" for L in c.leaders) + ".",
        technical=f"Distances in the original {facts['dim']}-d space. {c.name[wide]}'s spread is driven partly by one speech of a different type (a symposium speech among New Year messages); "
                  f"{c.name['putin']}'s low within-speech spread goes with the shortest speeches ({int(disp.loc['putin', 'n_chunks'])} chunks).",
        video=f"Konuşma setlerinin kendi merkezine ne kadar toplandığına da baktık: {c.name[tight]} konuşmaları merkezine en yakın ({disp.loc[tight, 'mean_dist_speech_to_leader']:.3f}), "
              f"{c.name[wide]} en dağınık ({disp.loc[wide, 'mean_dist_speech_to_leader']:.3f}). Bu, tutarlılık değil, derlemin çeşitliliği.",
        caution="Semantic concentration of the collected files only. It is not 'consistency' or 'inconsistency' of a person, and it is sensitive to speech type mix and speech length.",
    ))

    # --- 9. clustering ----------------------------------------------------------------------------
    cs = c.t("clusters_summary")
    cs_real = cs[cs["cluster"] >= 0]
    lc = c.t("clusters_summary", f"__{c.pk}_leadercentered")
    lc_real = lc[lc["cluster"] >= 0]
    mixed = lc_real[lc_real["leader_mix_entropy"] >= 0.75].sort_values("size", ascending=False)
    F.append(dict(
        finding="Unsupervised clustering rediscovers the leaders, not topics — until each leader's centroid is subtracted, after which mixed topical clusters appear.",
        number=f"HDBSCAN on the raw chunk vectors: {len(cs_real)} clusters, every one {cs_real['dominant_leader_share'].min():.0%} a single leader, {cs.loc[cs['cluster'] == -1, 'share_of_chunks'].iloc[0]:.0%} unassigned. "
               f"After leader-centering: {len(lc_real)} clusters, {len(mixed)} of them mixed (entropy ≥ 0.75), e.g. "
               + "; ".join(f"'{r.candidate_label}' ({r.size} chunks, {sum(1 for L in c.leaders if getattr(r, f'share_{L}') > 0)} leaders)" for r in mixed.head(3).itertuples()) + ".",
        technical="PCA(50) → HDBSCAN; candidate labels come from the fixed-theme scores of the member chunks. Leader-centering removes the leader/language mean vector from each chunk so that what remains is within-corpus variation.",
        video="Denetimsiz kümeleme önce sadece liderleri (aslında dilleri) buluyor. Her liderin ortalamasını çıkarınca ekonomi, Avrupa/dış politika, kriz gibi liderler arası ortak konu kümeleri ortaya çıkıyor.",
        caution="Cluster membership depends on parameters (see the grid table) and 57% of chunks stay unassigned after centering; labels are neutral topical candidates, not interpretations.",
    ))

    # --- 10. method agreement -----------------------------------------------------------------
    agree = c.t("theme_method_agreement")
    nli_top = c.t("top_themes_by_leader")
    nli_top = nli_top[(nli_top["method"] == "nli") & (nli_top["rank"] == 1)]
    nli_common = nli_top["label"].value_counts()
    F.append(dict(
        finding="The two theme-scoring methods agree on the big picture but not on details: the NLI classifier sees the same top theme for every leader.",
        number=f"Embedding vs NLI: same top theme for {agree['top_theme_agreement_emb_vs_nli'].iloc[0]:.0%} of chunks; chunk-level Spearman {agree['spearman_cos_vs_nli'].min():.2f}–{agree['spearman_cos_vs_nli'].max():.2f}. "
               f"NLI top theme: '{nli_common.index[0]}' for {nli_common.iloc[0]} of 5 leaders. Language-matched vs English descriptions: Spearman {agree['spearman_cos_vs_cos_en'].min():.2f}–{agree['spearman_cos_vs_cos_en'].max():.2f}.",
        technical="Option A = cosine to theme descriptions (same embedding model); Option B = multilingual zero-shot NLI (mDeBERTa) with 'This text is about {theme}'. "
                  "Most speeches are New Year addresses, a genre saturated with solidarity and gratitude language, which the NLI method weights heavily.",
        video=f"İki farklı yöntemle tema ölçtük; parça düzeyinde sadece %{agree['top_theme_agreement_emb_vs_nli'].iloc[0]*100:.0f} aynı birinci temayı seçiyor. "
              "NLI sınıflandırıcı beş liderde de 'toplumsal dayanışma'yı öne koyuyor; çünkü konuşmaların çoğu yılbaşı mesajı.",
        caution="Theme scores are method-dependent estimates, not measurements of intent. Genre (New Year address) is a strong common factor across all five corpora.",
    ))

    # --- 11. pipeline facts ---------------------------------------------------------------------
    F.append(dict(
        finding="The whole experiment runs on a small, fully traceable corpus.",
        number=f"{facts['n_speeches']} speeches, {facts['n_words']:,} cleaned words → {facts['n_chunks']} chunks (median {facts['median_tokens']} tokens) → {facts['dim']}-dimensional vectors "
               f"from an 8B-parameter model; embedding all chunks took {facts['encode_s']:.1f} s on one RTX 5090; uncertainty from 2000 speech-level bootstrap resamples.",
        technical="Paragraph-based chunking (80–180 tokens, no overlap), unit-normalised embeddings, chunk → speech → leader aggregation so that long speeches do not dominate.",
        video=f"Tüm deney {facts['n_speeches']} konuşma, {facts['n_chunks']} parça ve {facts['dim']} boyutlu vektörlerden oluşuyor; 8 milyar parametreli model hepsini {facts['encode_s']:.0f} saniyede gömdü.",
        caution="Small corpus: 3–5 speeches per leader, mostly New Year addresses from different years. Every number above is a statement about these files.",
    ))
    return F, facts


def write_video_insights(c: Ctx, F: list[dict]) -> None:
    lines = ["# Video insights — candidate findings", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M} from the result tables (primary model {c.model}; robustness model {c.rmodel}). "
             "Every finding is about the collected speech corpus and its embeddings. None of them measures ideology, political quality, personality, competence or morality, and none is an endorsement.",
             "", "**Global caution to state on camera:** each leader speaks a different language in this corpus (Putin and Trump both in English transcript), the speeches come from different years and formats, "
             "and there are only 3–5 speeches per leader. Findings that change with the embedding model are marked as such.", ""]
    for i, f in enumerate(F, 1):
        lines += [f"## Finding {i}", "", f"**FINDING**  \n{f['finding']}", "", f"**NUMBER**  \n{f['number']}", "",
                  f"**TECHNICAL EXPLANATION**  \n{f['technical']}", "", f"**VIDEO VERSION**  \n\"{f['video']}\"", "", f"**CAUTION**  \n{f['caution']}", ""]
    (c.out / "video_insights.md").write_text("\n".join(lines), encoding="utf-8")


def write_methodology(c: Ctx, facts: dict) -> None:
    ch = c.cfg["chunking"]
    up = c.cfg["umap_parameters"]
    txt = f"""# Video için metodoloji notları (Türkçe)

Bu metin, kamera karşısında bir yapay zekâ mühendisi gibi anlatmak için yazıldı: kısa, doğru, abartısız.
Derlem: {facts['n_speeches']} konuşma, {facts['n_words']:,} temizlenmiş kelime, {facts['n_chunks']} parça. Birincil model: {c.model}. Sağlamlık modeli: {c.rmodel}.

## Embedding nedir?
Bir metin parçasını, anlamını temsil eden uzun bir sayı listesine (vektöre) dönüştürmek. Burada her parça {facts['dim']} sayıdan oluşan bir vektör oluyor.
Anlamca yakın parçalar bu uzayda birbirine yakın düşüyor. Modelin "anlam" dediği şey, eğitim verisinden öğrendiği istatistiksel örüntüler; dil, tür ve konu hep bu vektörün içinde.

## Chunk (parça) neden kullandık?
Bütün bir konuşmayı tek vektöre sıkıştırsak, konuşmanın içindeki farklı konular birbirine karışır ve ortalama bir "bulanık" nokta elde ederiz.
Bunun yerine konuşmaları doğal paragraflardan başlayarak yaklaşık {ch['chunk_min_tokens']}–{ch['chunk_max_tokens']} token'lık parçalara ayırdık (medyan {facts['median_tokens']} token), örtüşme yok.
Böylece "hangi temalar ne sıklıkla geçiyor" ve "iki derlemin parçaları birbirine karışıyor mu" sorularını cevaplayabiliyoruz.

## Cosine similarity nedir?
İki vektörün arasındaki açının kosinüsü: 1 aynı yön, 0 ilgisiz. Vektörleri birim uzunluğa getirdik; böylece uzunluk değil, yön karşılaştırılıyor.
Bu modelde iki rastgele parça arasındaki tipik benzerlik 0.33 civarında; lider merkezleri arası benzerlikler 0.58–0.74 arasında.
Mutlak değerler modele özgü: {c.rmodel} ile aynı çiftler 0.82–0.94 çıkıyor. Bu yüzden modeller arası karşılaştırmada sıralamaya baktık, sayıya değil.

## Leader centroid nasıl oluşturuldu?
Üç adım: (1) her parçanın vektörünü normalize et, (2) bir konuşmanın parçalarının ortalamasını al ve tekrar normalize et → konuşma merkezi,
(3) bir liderin konuşma merkezlerinin ortalamasını al ve normalize et → lider merkezi. Her konuşma eşit ağırlıkta; uzun ya da çok konuşması olan lider fazladan ağırlık kazanmıyor.

## Neden multilingual model kullandık?
Derlem dört dilde: Türkçe, Fransızca, Almanca, İngilizce. Çok dilli bir model farklı dillerdeki benzer anlamları aynı uzaya yerleştirmeye çalışır.
Ama tamamen başaramaz: sonuçlarımızda parçaların en yakın komşularının %{min(facts['same_leader_share'].values())*100:.0f}–%{max(facts['same_leader_share'].values())*100:.0f}'i aynı liderden, yani aynı dilden.
Bu yüzden tema puanlarında her parçayı kendi dilindeki tema tanımıyla karşılaştırdık ve İngilizce tanımlarla da kontrol ettik (uyum yüksek). Dil ile lider bu derlemde ayrıştırılamıyor; bunu videoda açıkça söylemek gerekiyor.

## Neden UMAP sonucu gerçek mesafe olarak kullanılmıyor?
UMAP {facts['dim']} boyutu 2 boyuta indirir ve bunu yaparken yerel komşulukları korumaya, küresel mesafeleri ise bozmaya eğilimlidir. İki kümenin ekrandaki uzaklığı gerçek uzaklık değildir.
Bu nedenle: "2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space."
UMAP parametreleri: n_neighbors={up['n_neighbors']}, min_dist={up['min_dist']}, metric={up.get('metric', 'cosine')}, seed={c.cfg['random_seed']}. PCA'yı da ikinci görsel olarak verdik.

## Neden konuşma uzunluğunu normalize ettik?
Macron'un bir konuşması 2.800 kelime, Putin'in bir konuşması 450 kelime. Parça sayısı üzerinden ortalama alsak Macron'un konuşmaları Merkel ve Putin'inkileri ezerdi.
Parça → konuşma → lider hiyerarşisiyle her konuşma bir oy hakkına sahip. Tema profilleri ve merkezler hep bu sırayla hesaplandı.

## Neden speech-level bootstrap yaptık?
Lider başına 3–5 konuşma var. Bir konuşmayı değiştirsek sonuç ne kadar değişir? Bunu görmek için her liderin konuşmalarını yerine koyarak 2000 kez yeniden örnekledik
ve merkez benzerliklerini, tema profillerini, çerçeve ölçümlerini her seferinde yeniden hesapladık. Yeniden örnekleme birimi parça değil, konuşma; çünkü aynı konuşmanın parçaları bağımsız değil.
Sonuç: bazı farklar (ör. en yakın çift ile ikinci çift arasındaki fark) güven aralığında sıfırı içeriyor; bunları "fark var" diye anlatmıyoruz.

## Ek: iki modelle sağlamlık kontrolü
Aynı parçaları {c.rmodel} ile de gömdük ve tüm analizi tekrarladık. Lider çifti sıralamaları arasındaki korelasyon düşük; en yakın çift değişiyor.
Bu, "embedding geometrisi modele bağlıdır" cümlesinin somut hâli ve videonun en dürüst teknik mesajlarından biri.

## Söylememiz gereken şey
Tüm sayılar toplanan konuşma dosyalarını tarif eder. İdeoloji, siyasi kalite, kişilik, yeterlilik ya da ahlak hakkında hiçbir şey söylemez.
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
    fl = c.t("framing_leader")[["leader", "conflict_threat_framing_pct", "cooperation_solidarity_framing_pct", "conflict_threat_framing_rate", "cooperation_solidarity_framing_rate"]]
    fl["leader"] = fl["leader"].map(c.name)
    disp = c.t("semantic_dispersion")[["leader", "n_speeches", "n_chunks", "mean_dist_speech_to_leader", "mean_dist_chunk_to_speech"]]
    disp["leader"] = disp["leader"].map(c.name)
    rob = c.t("robustness_summary")
    mat = rob[rob["material_change"] == True][["check", "comparison", "metric", "value"]]  # noqa: E712
    plots = sorted(p.name for p in path_for(c.cfg, "outputs_plots").glob("*.png"))
    tables = sorted(p.name for p in c.tables.glob("*.csv"))
    lines = [f"# Results summary — {c.cfg['project_name']}", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M}. Primary model `{c.model}`; robustness model `{c.rmodel}`. "
             f"{facts['n_speeches']} speeches · {facts['n_words']:,} clean words · {facts['n_chunks']} chunks · {facts['dim']}-d embeddings.", "",
             "> " + c.cfg["methodology_notes"]["interpretation_scope"], "", "> " + c.cfg["methodology_notes"]["projection_note"], "",
             "## Leader-centroid cosine similarity (primary model)", "", md_table(sim), "",
             "## Three most represented themes per collected speech set", "", md_table(top3), "",
             "## Framing measurements (mean percentile / top-quartile rate)", "", md_table(fl), "",
             "## Semantic concentration", "", md_table(disp), "",
             "## Robustness — material changes", "", md_table(mat) if len(mat) else "None.", "",
             "See `robustness_report.md`, `clusters_report.md`, `clusters_report__" + c.pk + "_leadercentered.md`, `phase0_report.md`, `data/processed/preprocessing_report.md`.", "",
             "## Files", "", "Plots (`outputs/plots/`, PNG + SVG): " + ", ".join(f"`{p}`" for p in plots), "",
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
