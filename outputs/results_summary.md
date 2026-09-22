# Results summary — political-speech-geometry

Generated 2026-09-22 19:08. Primary model `Qwen/Qwen3-Embedding-8B`; robustness model `BAAI/bge-m3`. 20 speeches · 21,117 clean words · 304 chunks · 4096-d embeddings.

> All similarity, distance and theme values describe the collected speech corpora, not ideology, personality, political quality or the people themselves.

> 2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space.

## Leader-centroid cosine similarity (primary model)

| leader | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.000 | 0.581 | 0.621 | 0.595 | 0.593 |
| Macron | 0.581 | 1.000 | 0.698 | 0.643 | 0.633 |
| Merkel | 0.621 | 0.698 | 1.000 | 0.678 | 0.660 |
| Putin | 0.595 | 0.643 | 0.678 | 1.000 | 0.744 |
| Trump | 0.593 | 0.633 | 0.660 | 0.744 | 1.000 |

## Three most represented themes per collected speech set

| leader | 1st | 2nd | 3rd |
|---|---|---|---|
| Erdoğan | Foreign Policy & Geopolitics | National Identity & Unity | Crisis, Threat & Resilience |
| Macron | Future, Reform & Technology | Economy & Welfare | Democracy, Law & Institutions |
| Merkel | Social Solidarity & Values | Future, Reform & Technology | Crisis, Threat & Resilience |
| Putin | Social Solidarity & Values | National Identity & Unity | Security & Military |
| Trump | Economy & Welfare | Security & Military | Democracy, Law & Institutions |

## Framing measurements (mean percentile / top-quartile rate)

| leader | conflict_threat_framing_pct | cooperation_solidarity_framing_pct | conflict_threat_framing_rate | cooperation_solidarity_framing_rate |
|---|---|---|---|---|
| Erdoğan | 0.607 | 0.512 | 0.371 | 0.230 |
| Macron | 0.499 | 0.431 | 0.238 | 0.168 |
| Merkel | 0.354 | 0.519 | 0.127 | 0.352 |
| Putin | 0.426 | 0.633 | 0.153 | 0.375 |
| Trump | 0.504 | 0.489 | 0.126 | 0.197 |

## Semantic concentration

| leader | n_speeches | n_chunks | mean_dist_speech_to_leader | mean_dist_chunk_to_speech |
|---|---|---|---|---|
| Erdoğan | 5 | 85 | 0.065 | 0.258 |
| Macron | 4 | 99 | 0.025 | 0.326 |
| Merkel | 4 | 46 | 0.050 | 0.334 |
| Putin | 4 | 26 | 0.039 | 0.174 |
| Trump | 3 | 48 | 0.049 | 0.243 |

## Robustness — material changes

| check | comparison | metric | value |
|---|---|---|---|
| A | qwen3_embedding_8b vs bge_m3 | leader_pair_similarity_spearman | -0.3697 |
| A | qwen3_embedding_8b vs bge_m3 | most_similar_pair | putin–trump | macron–merkel |
| A | qwen3_embedding_8b vs bge_m3 | least_similar_pair | erdogan–macron | putin–trump |
| A | qwen3_embedding_8b vs bge_m3 | theme_profile_spearman_macron | 0.4048 |
| A | qwen3_embedding_8b vs bge_m3 | theme_profile_spearman_merkel | 0.1905 |
| A | qwen3_embedding_8b vs bge_m3 | framing_leader_order_spearman_conflict_threat_framing | -0.8 |
| A | qwen3_embedding_8b vs bge_m3 | framing_leader_order_spearman_cooperation_solidarity_framing | 0.2 |
| C | bge_m3 all content vs bge_m3 ceremonial removed | most_similar_pair | macron–merkel | erdogan–macron |
| E | without trump2 | top3_themes_trump | ['Economy & Welfare', 'Security & Military', 'Democracy, Law & Institutions'] → ['Foreign Policy & Geopolitics', 'National Identity & Unity', 'Security & Military'] |
| F | embedding vs NLI | leader_theme_spearman_macron | -0.2857 |
| F | embedding vs NLI | leader_theme_spearman_merkel | 0.0952 |
| F | embedding vs NLI | leader_theme_spearman_trump | 0.4286 |

See `robustness_report.md`, `clusters_report.md`, `clusters_report__qwen3_embedding_8b_leadercentered.md`, `phase0_report.md`, `data/processed/preprocessing_report.md`.

## Files

Plots (`outputs/plots/`, PNG + SVG): `conflict_cooperation_comparison.png`, `leader_similarity_heatmap.png`, `pca_chunks.png`, `radar_all_leaders.png`, `radar_erdogan.png`, `radar_macron.png`, `radar_merkel.png`, `radar_putin.png`, `radar_trump.png`, `semantic_dispersion.png`, `theme_comparison.png`, `top_themes_by_leader.png`, `umap_chunks.png`

Tables (`outputs/tables/`): `bootstrap_dispersion_ci.csv`, `bootstrap_dispersion_ci__bge_m3.csv`, `bootstrap_dispersion_ci__bge_m3_noceremonial.csv`, `bootstrap_dispersion_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_framing_ci.csv`, `bootstrap_framing_ci__bge_m3.csv`, `bootstrap_framing_ci__bge_m3_noceremonial.csv`, `bootstrap_framing_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_leader_similarity_ci.csv`, `bootstrap_leader_similarity_ci__bge_m3.csv`, `bootstrap_leader_similarity_ci__bge_m3_noceremonial.csv`, `bootstrap_leader_similarity_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_pair_difference.csv`, `bootstrap_pair_difference__bge_m3.csv`, `bootstrap_pair_difference__bge_m3_noceremonial.csv`, `bootstrap_pair_difference__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_pair_rank_stability.csv`, `bootstrap_pair_rank_stability__bge_m3.csv`, `bootstrap_pair_rank_stability__bge_m3_noceremonial.csv`, `bootstrap_pair_rank_stability__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_theme_profile_ci.csv`, `bootstrap_theme_profile_ci__bge_m3.csv`, `bootstrap_theme_profile_ci__bge_m3_noceremonial.csv`, `bootstrap_theme_profile_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_top_theme_stability.csv`, `bootstrap_top_theme_stability__bge_m3.csv`, `bootstrap_top_theme_stability__bge_m3_noceremonial.csv`, `bootstrap_top_theme_stability__qwen3_embedding_8b_noceremonial.csv`, `chunk_cluster_labels.csv`, `chunk_cluster_labels__qwen3_embedding_8b_leadercentered.csv`, `chunk_knn_leader_matrix.csv`, `chunk_knn_leader_matrix__bge_m3.csv`, `chunk_knn_leader_matrix__bge_m3_noceremonial.csv`, `chunk_knn_leader_matrix__qwen3_embedding_8b_noceremonial.csv`, `chunk_knn_leader_shares.csv`, `chunk_knn_leader_shares__bge_m3.csv`, `chunk_knn_leader_shares__bge_m3_noceremonial.csv`, `chunk_knn_leader_shares__qwen3_embedding_8b_noceremonial.csv`, `chunk_knn_per_chunk.csv`, `chunk_knn_per_chunk__bge_m3.csv`, `chunk_knn_per_chunk__bge_m3_noceremonial.csv`, `chunk_knn_per_chunk__qwen3_embedding_8b_noceremonial.csv`, `cluster_passages.csv`, `cluster_passages__qwen3_embedding_8b_leadercentered.csv`, `clusters_summary.csv`, `clusters_summary__qwen3_embedding_8b_leadercentered.csv`, `corpus_inventory.csv`, `cross_leader_pairing_counts.csv`, `cross_leader_pairing_counts__bge_m3.csv`, `cross_leader_pairing_counts__bge_m3_noceremonial.csv`, `cross_leader_pairing_counts__qwen3_embedding_8b_noceremonial.csv`, `cross_leader_pairs.csv`, `cross_leader_pairs__bge_m3.csv`, `cross_leader_pairs__bge_m3_noceremonial.csv`, `cross_leader_pairs__qwen3_embedding_8b_noceremonial.csv`, `framing_leader.csv`, `framing_leader__bge_m3.csv`, `framing_leader__bge_m3_noceremonial.csv`, `framing_leader__qwen3_embedding_8b_noceremonial.csv`, `framing_speech.csv`, `framing_speech__bge_m3.csv`, `framing_speech__bge_m3_noceremonial.csv`, `framing_speech__qwen3_embedding_8b_noceremonial.csv`, `hdbscan_parameter_grid.csv`, `hdbscan_parameter_grid__qwen3_embedding_8b_leadercentered.csv`, `leader_cosine_distance.csv`, `leader_cosine_distance__bge_m3.csv`, `leader_cosine_distance__bge_m3_noceremonial.csv`, `leader_cosine_distance__qwen3_embedding_8b_noceremonial.csv`, `leader_cosine_similarity.csv`, `leader_cosine_similarity__bge_m3.csv`, `leader_cosine_similarity__bge_m3_noceremonial.csv`, `leader_cosine_similarity__qwen3_embedding_8b_noceremonial.csv`, `leader_cross_neighbor_similarity.csv`, `leader_cross_neighbor_similarity__bge_m3.csv`, `leader_cross_neighbor_similarity__bge_m3_noceremonial.csv`, `leader_cross_neighbor_similarity__qwen3_embedding_8b_noceremonial.csv`, `leader_pairs.csv`, `leader_pairs__bge_m3.csv`, `leader_pairs__bge_m3_noceremonial.csv`, `leader_pairs__qwen3_embedding_8b_noceremonial.csv`, `robustness_summary.csv`, `semantic_dispersion.csv`, `semantic_dispersion__bge_m3.csv`, `semantic_dispersion__bge_m3_noceremonial.csv`, `semantic_dispersion__qwen3_embedding_8b_noceremonial.csv`, `speech_cosine_similarity.csv`, `speech_cosine_similarity__bge_m3.csv`, `speech_cosine_similarity__bge_m3_noceremonial.csv`, `speech_cosine_similarity__qwen3_embedding_8b_noceremonial.csv`, `suspicious_files.csv`, `theme_language_diagnostic.csv`, `theme_language_diagnostic__bge_m3.csv`, `theme_language_diagnostic__bge_m3_noceremonial.csv`, `theme_language_diagnostic__qwen3_embedding_8b_noceremonial.csv`, `theme_method_agreement.csv`, `theme_method_agreement__bge_m3.csv`, `theme_method_agreement__bge_m3_noceremonial.csv`, `theme_method_agreement__qwen3_embedding_8b_noceremonial.csv`, `theme_profile_leader.csv`, `theme_profile_leader__bge_m3.csv`, `theme_profile_leader__bge_m3_noceremonial.csv`, `theme_profile_leader__qwen3_embedding_8b_noceremonial.csv`, `theme_profile_speech.csv`, `theme_profile_speech__bge_m3.csv`, `theme_profile_speech__bge_m3_noceremonial.csv`, `theme_profile_speech__qwen3_embedding_8b_noceremonial.csv`, `theme_scores_chunks.csv`, `theme_scores_chunks__bge_m3.csv`, `theme_scores_chunks__bge_m3_noceremonial.csv`, `theme_scores_chunks__qwen3_embedding_8b_noceremonial.csv`, `top_themes_by_leader.csv`, `top_themes_by_leader__bge_m3.csv`, `top_themes_by_leader__bge_m3_noceremonial.csv`, `top_themes_by_leader__qwen3_embedding_8b_noceremonial.csv`
