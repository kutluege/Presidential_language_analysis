"""Phase 5 — secondary, exploratory topic discovery: chunk embeddings -> PCA -> HDBSCAN.

Usage:
    python -m src.clustering --model qwen3_embedding_8b [--suffix _noceremonial]

This does not replace the fixed 8-theme analysis. Cluster labels are neutral topical candidates
derived from the fixed-theme scores of the member chunks (no political interpretation is attached).

Outputs (outputs/tables/):
    hdbscan_parameter_grid{tag}.csv   n_clusters / noise share / relative validity for a small grid
    clusters_summary{tag}.csv         size, leader distribution, candidate label, frequent terms
    cluster_passages{tag}.csv         top-10 passages closest to each cluster centroid
    chunk_cluster_labels{tag}.csv     chunk_id -> cluster (-1 = noise), membership probability
    outputs/clusters_report{tag}.md   human-readable summary
Artifacts (artifacts/clusters/): {model}{suffix}_labels.npy, {model}{suffix}_pca.npy
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

from .config import leader_slugs, load_config, path_for, primary_model_key, result_tag, seed_everything, theme_keys, theme_labels
from .textutils import STOPWORDS
from .vectors import l2norm, load_embeddings, load_scores

EXTRA_STOP = set("""
aber alle allem allen aller alles also auch auf aus bei bin bis bist da damit dann denn derer dessen deshalb
dich dir doch dort durch eben eine einem einen einer eines einig einige einigem einigen einiger einiges einmal er
etwas euer eure eurem euren eurer eures gegen gewesen hab habe hatte hatten hier hin hinter ihm ihn ihnen ihr ihre
ihrem ihren ihrer ihres indem ins ist jede jedem jeden jeder jedes jene jenem jenen jener jenes jetzt kann kein
keine keinem keinen keiner keines können könnte machen man manche manchem manchen mancher manches mein meine
meinem meinen meiner meines mich mir muss musste nach nichts noch nun nur oder ohne sehr sein seine seinem seinen
seiner seines selbst sind solche solchem solchen solcher solches soll sollte sondern sonst über unter viel vom vor
während war waren warst was weg weil weiter welche welchem welchen welcher welches wenn werde wieder will wir wird
wirst wollen wollte würde würden zum zur zwar zwischen dieser diese dieses diesen diesem heute jahr jahre jahren
ainsi alors après aussi autre autres avant avoir bien car ceci cela celle celles celui cependant certain certaine
certaines certains chaque comme comment dans depuis devrait doit donc dont elles encore entre être eux faire fait
fois font hors ici juste leur leurs lors maintenant mais même mes moi moins mon notre nous nouveaux nouvelle
parce parole pas peu peut plus plusieurs pour pourquoi quand quel quelle quelles quels quoi sans sera seront ses
sien sont sous soyez sujet sur tandis tellement tels tes toi ton tous tout toute toutes très trop tu voient vont
votre vous aussi cette celui année années soir
about above after again against also among because been before being below between both cannot could does doing
down during each even ever every from further having here into itself just like made make many more most much
must myself never once only other ought ours ourselves over same shall should some such than then there these
things those through today tonight under until upon very what when where which while whom whose with within
would yours yourself yourselves years going great want know come came said
acaba ama ancak artık aslında bana bazı belki beni benim beri bile bir birçok biri birkaç birşey biz bize bizi
bizim böyle bu buna bunda bundan bunlar bunları bunların bunu bunun burada çok çünkü daha diye eğer gibi hem hep
hepsi her herhangi herkes hiç hiçbir için ile ise işte kadar karşın kendi kendine kendini kez kim kimse mı mi mu
mü nasıl ne neden nedenle nerde nerede nereye niçin niye onlar onlardan onları onların onu onun orada öyle oysa
sanki şey şeyi şeyler şöyle şu şuna şunda şundan şunu tüm üzere veya yani yine yıl yıllar yılında bugün olan olarak
oldu olduğu olduğunu olmak olsun sonra önce tarafından beraber sizleri sizlere hepinizi
""".split())


def tokens_for_terms(text: str) -> list[str]:
    stop = EXTRA_STOP | {w.lower() for s in STOPWORDS.values() for w in s}
    toks = re.findall(r"[^\W\d_]{4,}", text.lower())
    return [t for t in toks if t not in stop]


def frequent_terms(member_texts: list[str], corpus_counts: Counter, n_corpus_docs: int, top: int = 12) -> list[str]:
    counts = Counter()
    for t in member_texts:
        counts.update(set(tokens_for_terms(t)))  # document frequency within cluster
    n = max(len(member_texts), 1)
    scored = []
    for term, c in counts.items():
        if c < 2:
            continue
        p_in = c / n
        p_all = corpus_counts[term] / n_corpus_docs
        scored.append((p_in * np.log((p_in + 1e-6) / (p_all + 1e-6)), term))
    return [t for _, t in sorted(scored, reverse=True)[:top]]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 5: PCA -> HDBSCAN topic discovery (exploratory).")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--center-by-leader", action="store_true",
                    help="subtract each leader's centroid from its chunks before clustering, so that leader/language "
                         "identity is removed and cross-leader topics can surface (outputs get the extra tag _leadercentered)")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    import hdbscan
    from sklearn.decomposition import PCA

    cfg = load_config(args.config)
    seed = int(cfg["random_seed"])
    seed_everything(seed)
    model_key = args.model or primary_model_key(cfg)
    tag = result_tag(cfg, model_key, args.suffix)
    tables = path_for(cfg, "outputs_tables")
    cl_dir = path_for(cfg, "artifacts_clusters")
    cl_dir.mkdir(parents=True, exist_ok=True)
    themes, labels = theme_keys(cfg), theme_labels(cfg)
    leaders = leader_slugs(cfg)

    emb, index = load_embeddings(cfg, model_key, args.suffix)
    scores = load_scores(cfg, tag).set_index("chunk_id").loc[index["chunk_id"]]
    if args.center_by_leader:
        emb = emb.copy()
        for L in leaders:
            m = (index["leader"] == L).to_numpy()
            if m.any():
                emb[m] -= emb[m].mean(axis=0)
        emb = l2norm(emb)
        tag = (tag or f"__{model_key}") + "_leadercentered"
        args.suffix = args.suffix + "_leadercentered"
    n_comp = min(int(cfg["pca_parameters"]["n_components_clustering"]), len(emb) - 1)
    pca = PCA(n_components=n_comp, random_state=seed)
    X = pca.fit_transform(emb)
    explained = float(pca.explained_variance_ratio_.sum())

    # --- parameter grid -------------------------------------------------------------------------
    hp = cfg["hdbscan_parameters"]
    grid_rows = []
    for mcs in (4, 5, 6, 8, 10):
        for ms in (2, 3, 5):
            cl = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=ms, metric=hp.get("metric", "euclidean"),
                                 cluster_selection_method=hp.get("cluster_selection_method", "eom"), gen_min_span_tree=True)
            lab = cl.fit_predict(X)
            grid_rows.append({"min_cluster_size": mcs, "min_samples": ms, "n_clusters": int(lab.max() + 1),
                              "noise_share": float((lab == -1).mean()),
                              "relative_validity": float(getattr(cl, "relative_validity_", np.nan)),
                              "is_primary": mcs == hp["min_cluster_size"] and ms == hp["min_samples"]})
    grid = pd.DataFrame(grid_rows)
    grid.to_csv(tables / f"hdbscan_parameter_grid{tag}.csv", index=False, encoding="utf-8")

    # --- primary clustering -----------------------------------------------------------------------
    clusterer = hdbscan.HDBSCAN(min_cluster_size=int(hp["min_cluster_size"]), min_samples=int(hp["min_samples"]),
                                metric=hp.get("metric", "euclidean"), cluster_selection_method=hp.get("cluster_selection_method", "eom"),
                                gen_min_span_tree=True, prediction_data=False)
    lab = clusterer.fit_predict(X)
    np.save(cl_dir / f"{model_key}{args.suffix}_labels.npy", lab)
    np.save(cl_dir / f"{model_key}{args.suffix}_pca.npy", X)
    chunk_labels = pd.DataFrame({"chunk_id": index["chunk_id"], "speech_id": index["speech_id"], "leader": index["leader"],
                                 "cluster": lab, "membership_probability": clusterer.probabilities_,
                                 "outlier_score": clusterer.outlier_scores_})
    chunk_labels.to_csv(tables / f"chunk_cluster_labels{tag}.csv", index=False, encoding="utf-8")

    texts = index["chunk_text"].astype(str).tolist()
    corpus_counts = Counter()
    for t in texts:
        corpus_counts.update(set(tokens_for_terms(t)))
    leader_arr = index["leader"].astype(str).to_numpy()
    base_share = {L: float((leader_arr == L).mean()) for L in leaders}

    summary_rows, passage_rows, report = [], [], []
    report.append(f"# Exploratory topic discovery — {model_key}{args.suffix}\n")
    report.append(f"PCA {n_comp} components ({explained:.0%} variance kept) → HDBSCAN(min_cluster_size={hp['min_cluster_size']}, "
                  f"min_samples={hp['min_samples']}, {hp.get('metric','euclidean')}, {hp.get('cluster_selection_method','eom')}). "
                  f"{int(lab.max() + 1)} clusters, {(lab == -1).mean():.0%} of chunks unassigned (noise).\n")
    report.append("Candidate labels are the top fixed themes of the member chunks (neutral topical descriptions, not interpretations). "
                  "Cluster membership is exploratory and depends on parameters — see the grid table.\n")
    for c in sorted(set(lab)):
        m = lab == c
        size = int(m.sum())
        counts = Counter(leader_arr[m])
        shares = {L: counts.get(L, 0) / size for L in leaders}
        p = np.array([v for v in shares.values() if v > 0])
        entropy = float(-(p * np.log(p)).sum() / np.log(len(leaders)))
        theme_means = {k: float(scores.loc[m, f"{k}_pct"].mean()) for k in themes}
        ranked = sorted(theme_means.items(), key=lambda kv: kv[1], reverse=True)
        cand = labels[ranked[0][0]] if ranked[0][1] - ranked[1][1] > 0.05 else f"{labels[ranked[0][0]]} / {labels[ranked[1][0]]}"
        if c == -1:
            cand = "(noise — not assigned)"
        centroid = l2norm(emb[m].mean(axis=0))
        sims = emb[m] @ centroid
        order = np.argsort(-sims)[:10]
        idx_members = np.where(m)[0]
        terms = frequent_terms([texts[i] for i in idx_members], corpus_counts, len(texts))
        row = {"cluster": c, "size": size, "share_of_chunks": size / len(lab), "candidate_label": cand,
               "top_theme": ranked[0][0], "top_theme_mean_pct": round(ranked[0][1], 3),
               "second_theme": ranked[1][0], "second_theme_mean_pct": round(ranked[1][1], 3),
               "dominant_leader": counts.most_common(1)[0][0], "dominant_leader_share": round(counts.most_common(1)[0][1] / size, 3),
               "leader_mix_entropy": round(entropy, 3), "n_speeches": int(index.loc[m, "speech_id"].nunique()),
               "frequent_terms": ", ".join(terms)}
        for L in leaders:
            row[f"share_{L}"] = round(shares[L], 3)
            row[f"count_{L}"] = counts.get(L, 0)
        summary_rows.append(row)
        for rank, oi in enumerate(order, 1):
            gi = idx_members[oi]
            passage_rows.append({"cluster": c, "rank": rank, "chunk_id": index["chunk_id"].iloc[gi], "leader": leader_arr[gi],
                                 "speech_id": index["speech_id"].iloc[gi], "similarity_to_centroid": float(sims[oi]),
                                 "passage": texts[gi][:400].replace("\n", " ")})
        report.append(f"## Cluster {c} — {cand}  (n={size}, {size / len(lab):.0%} of chunks)\n")
        report.append("Leader distribution: " + ", ".join(f"{L} {counts.get(L, 0)} ({shares[L]:.0%}; corpus share {base_share[L]:.0%})" for L in leaders)
                      + f" · mixing entropy {entropy:.2f} (1 = perfectly mixed)\n")
        report.append("Theme profile (mean percentile): " + ", ".join(f"{labels[k]} {v:.2f}" for k, v in ranked[:3]) + "\n")
        report.append("Frequent terms (vs corpus): " + (", ".join(terms) or "—") + "\n")
        report.append("Representative passages (closest to centroid):\n")
        for rank, oi in enumerate(order[:5], 1):
            gi = idx_members[oi]
            report.append(f"{rank}. *{leader_arr[gi]} / {index['speech_id'].iloc[gi]}* (cos {sims[oi]:.2f}): "
                          f"{texts[gi][:260].replace(chr(10), ' ')}…")
        report.append("")

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(tables / f"clusters_summary{tag}.csv", index=False, encoding="utf-8")
    pd.DataFrame(passage_rows).to_csv(tables / f"cluster_passages{tag}.csv", index=False, encoding="utf-8")
    report.append("## Parameter grid\n")
    report.append(grid.round(3).to_string(index=False))
    (path_for(cfg, "outputs") / f"clusters_report{tag}.md").write_text("\n".join(report), encoding="utf-8")

    print(f"[clustering] tag='{tag}' PCA {n_comp} comps ({explained:.0%} var) → {int(lab.max() + 1)} clusters, noise {(lab == -1).mean():.0%}")
    print(summary[["cluster", "size", "candidate_label", "dominant_leader", "dominant_leader_share", "leader_mix_entropy"]].to_string(index=False))
    print("grid:")
    print(grid.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
