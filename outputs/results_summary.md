# Results summary — political-speech-geometry (run 2, English corpus)

Generated 2026-09-23 12:50. Primary model `tencent/KaLM-Embedding-Gemma3-12B-2511`; robustness model `Qwen/Qwen3-Embedding-8B`. 20 speeches · 23,905 clean words · 250 chunks · 3840-d embeddings. First run archived in `old_results/`.

> All similarity, distance, theme, rhetorical and emotional values describe the collected speech corpora, not ideology, personality, political quality or the people themselves.

> Erdoğan, Macron and Merkel are analysed in English translation and Putin in an official English transcript; for them, style measurements describe the translated text and therefore also carry the translator's choices.

> 2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space.

## Leader-centroid cosine similarity (primary model)

| leader | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.000 | 0.806 | 0.784 | 0.755 | 0.735 |
| Macron | 0.806 | 1.000 | 0.850 | 0.753 | 0.736 |
| Merkel | 0.784 | 0.850 | 1.000 | 0.736 | 0.729 |
| Putin | 0.755 | 0.753 | 0.736 | 1.000 | 0.701 |
| Trump | 0.735 | 0.736 | 0.729 | 0.701 | 1.000 |

## Three most represented themes per speech set

| leader | 1st | 2nd | 3rd |
|---|---|---|---|
| Erdoğan | Democracy, Law & Institutions | Foreign Policy & Geopolitics | Security & Military |
| Macron | Future, Reform & Technology | Economy & Welfare | Crisis, Threat & Resilience |
| Merkel | Future, Reform & Technology | Social Solidarity & Values | Democracy, Law & Institutions |
| Putin | National Identity & Unity | Social Solidarity & Values | Security & Military |
| Trump | Economy & Welfare | Security & Military | National Identity & Unity |

## Rhetorical and emotional dimensions — first-ranked leader per dimension (95% CI, share of resamples keeping rank 1)

| dimension_label | leader | value | ci_low | ci_high | share_rank1 |
|---|---|---|---|---|---|
| Conflict / Threat Framing | Trump | 0.545 | 0.351 | 0.774 | 0.480 |
| Cooperation / Solidarity Framing | Merkel | 0.612 | 0.543 | 0.707 | 0.664 |
| Past Orientation | Putin | 0.618 | 0.564 | 0.690 | 0.880 |
| Future Orientation | Macron | 0.571 | 0.550 | 0.593 | 0.455 |
| Us-versus-Them Contrast | Trump | 0.651 | 0.425 | 0.911 | 0.810 |
| Gratitude & Recognition | Putin | 0.696 | 0.662 | 0.736 | 1.000 |
| Promises & Commitments | Trump | 0.591 | 0.477 | 0.795 | 0.644 |
| Affiliative / positive emotion | Putin | 0.511 | 0.466 | 0.549 | 0.578 |
| Fear, sadness & loss | Trump | 0.055 | 0.002 | 0.096 | 0.696 |
| Hostility & disapproval | Trump | 0.035 | 0.007 | 0.051 | 0.854 |
| Sentiment valence (positive − negative) | Putin | 0.766 | 0.562 | 0.912 | 0.789 |

## Style similarity — the ten pairs, most alike first

| leader_a | leader_b | style_distance | ci_low | ci_high | share_closest_pair |
|---|---|---|---|---|---|
| Erdoğan | Macron | 1.454 | 1.153 | 3.835 | 0.584 |
| Erdoğan | Merkel | 1.955 | 1.648 | 4.092 | 0.097 |
| Macron | Merkel | 2.073 | 1.649 | 3.533 | 0.288 |
| Merkel | Trump | 2.600 | 2.373 | 5.966 | 0.029 |
| Erdoğan | Trump | 3.081 | 2.866 | 6.289 | 0.002 |
| Merkel | Putin | 3.171 | 2.950 | 4.484 | 0.000 |
| Macron | Trump | 3.295 | 3.024 | 6.125 | 0.000 |
| Erdoğan | Putin | 3.360 | 2.639 | 5.602 | 0.001 |
| Macron | Putin | 3.375 | 3.277 | 4.017 | 0.001 |
| Putin | Trump | 4.068 | 3.836 | 6.606 | 0.000 |

## Emotional tone (leader means)

| leader | fam_affiliative_positive | fam_threat_negative | fam_hostility | fam_cognitive_other | fam_neutral | valence |
|---|---|---|---|---|---|---|
| Erdoğan | 0.387 | 0.035 | 0.014 | 0.158 | 0.301 | 0.418 |
| Macron | 0.455 | 0.027 | 0.011 | 0.190 | 0.176 | 0.461 |
| Merkel | 0.460 | 0.031 | 0.020 | 0.107 | 0.226 | 0.519 |
| Putin | 0.511 | 0.009 | 0.011 | 0.106 | 0.116 | 0.766 |
| Trump | 0.482 | 0.055 | 0.035 | 0.054 | 0.178 | 0.654 |

## Semantic concentration

| leader | n_speeches | n_chunks | mean_dist_speech_to_leader | mean_dist_chunk_to_speech |
|---|---|---|---|---|
| Erdoğan | 5 | 63 | 0.065 | 0.192 |
| Macron | 4 | 75 | 0.019 | 0.216 |
| Merkel | 4 | 38 | 0.029 | 0.204 |
| Putin | 4 | 26 | 0.026 | 0.131 |
| Trump | 3 | 48 | 0.040 | 0.177 |

## Language effect — same model (Qwen3), original-language run vs English run

| pair | old_similarity | new_similarity | delta | old_rank | new_rank |
|---|---|---|---|---|---|
| Putin–Trump | 0.744 | 0.743 | -0.000 | 1 | 10 |
| Macron–Merkel | 0.698 | 0.871 | 0.173 | 2 | 1 |
| Merkel–Putin | 0.678 | 0.761 | 0.083 | 3 | 9 |
| Merkel–Trump | 0.660 | 0.774 | 0.114 | 4 | 8 |
| Macron–Putin | 0.643 | 0.778 | 0.135 | 5 | 6 |
| Macron–Trump | 0.633 | 0.806 | 0.173 | 6 | 4 |
| Erdoğan–Merkel | 0.621 | 0.828 | 0.207 | 7 | 3 |
| Erdoğan–Putin | 0.595 | 0.774 | 0.179 | 8 | 7 |
| Erdoğan–Trump | 0.593 | 0.796 | 0.203 | 9 | 5 |
| Erdoğan–Macron | 0.581 | 0.857 | 0.276 | 10 | 2 |

## Robustness — material changes

| check | comparison | metric | value |
|---|---|---|---|
| F | embedding vs NLI | leader_theme_spearman_erdogan | 0.0952 |
| F | embedding vs NLI | leader_theme_spearman_macron | -0.4524 |
| F | embedding vs NLI | leader_theme_spearman_merkel | -0.4048 |
| F | embedding vs NLI | leader_theme_spearman_trump | 0.0 |
| G | original languages vs English | leader_pair_similarity_spearman | -0.4303 |
| G | original languages vs English | most_similar_pair | putin–trump | macron–merkel |
| G | original languages vs English | erdogan_pairs_mean_rank | 8.5 → 4.2 |
| G | original languages vs English | knn_same_leader_share_erdogan | 0.995 → 0.598 |
| G | original languages vs English | knn_same_leader_share_macron | 0.958 → 0.713 |
| G | original languages vs English | knn_same_leader_share_merkel | 0.689 → 0.479 |
| G | original languages vs English | knn_same_leader_share_putin | 0.919 → 0.762 |
| G | original languages vs English | knn_same_leader_share_trump | 0.867 → 0.658 |
| G | original languages vs English | theme_profile_spearman_erdogan | 0.2857 |

See `robustness_report.md`, `clusters_report.md`, `clusters_report__kalm_embedding_gemma3_12b_leadercentered.md`, `phase0_report.md`, `data/processed/preprocessing_report.md`.

## Files

Plots (`outputs/plots/`, PNG 2× + SVG; `_9x16` = vertical): `conflict_cooperation_comparison.png`, `conflict_cooperation_comparison_9x16.png`, `content_vs_style_scatter.png`, `content_vs_style_scatter_9x16.png`, `emotion_profile.png`, `emotion_profile_9x16.png`, `language_effect.png`, `language_effect_9x16.png`, `leader_similarity_heatmap.png`, `leader_similarity_heatmap_9x16.png`, `pca_chunks.png`, `pca_chunks_9x16.png`, `radar_all_leaders.png`, `radar_all_leaders_9x16.png`, `radar_erdogan.png`, `radar_erdogan_9x16.png`, `radar_macron.png`, `radar_macron_9x16.png`, `radar_merkel.png`, `radar_merkel_9x16.png`, `radar_putin.png`, `radar_putin_9x16.png`, `radar_trump.png`, `radar_trump_9x16.png`, `rhetorical_radar_all_leaders.png`, `rhetorical_radar_all_leaders_9x16.png`, `rhetorical_radar_erdogan.png`, `rhetorical_radar_erdogan_9x16.png`, `rhetorical_radar_macron.png`, `rhetorical_radar_macron_9x16.png`, `rhetorical_radar_merkel.png`, `rhetorical_radar_merkel_9x16.png`, `rhetorical_radar_putin.png`, `rhetorical_radar_putin_9x16.png`, `rhetorical_radar_trump.png`, `rhetorical_radar_trump_9x16.png`, `semantic_dispersion.png`, `semantic_dispersion_9x16.png`, `style_dendrogram.png`, `style_dendrogram_9x16.png`, `style_rankings.png`, `style_rankings_9x16.png`, `style_similarity_heatmap.png`, `style_similarity_heatmap_9x16.png`, `theme_comparison.png`, `theme_comparison_9x16.png`, `top_themes_by_leader.png`, `top_themes_by_leader_9x16.png`, `umap_chunks.png`, `umap_chunks_9x16.png`

Tables (`outputs/tables/`): `bootstrap_dispersion_ci.csv`, `bootstrap_dispersion_ci__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_dispersion_ci__qwen3_embedding_8b.csv`, `bootstrap_dispersion_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_framing_ci.csv`, `bootstrap_framing_ci__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_framing_ci__qwen3_embedding_8b.csv`, `bootstrap_framing_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_leader_similarity_ci.csv`, `bootstrap_leader_similarity_ci__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_leader_similarity_ci__qwen3_embedding_8b.csv`, `bootstrap_leader_similarity_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_pair_difference.csv`, `bootstrap_pair_difference__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_pair_difference__qwen3_embedding_8b.csv`, `bootstrap_pair_difference__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_pair_rank_stability.csv`, `bootstrap_pair_rank_stability__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_pair_rank_stability__qwen3_embedding_8b.csv`, `bootstrap_pair_rank_stability__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_theme_profile_ci.csv`, `bootstrap_theme_profile_ci__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_theme_profile_ci__qwen3_embedding_8b.csv`, `bootstrap_theme_profile_ci__qwen3_embedding_8b_noceremonial.csv`, `bootstrap_top_theme_stability.csv`, `bootstrap_top_theme_stability__kalm_embedding_gemma3_12b_noceremonial.csv`, `bootstrap_top_theme_stability__qwen3_embedding_8b.csv`, `bootstrap_top_theme_stability__qwen3_embedding_8b_noceremonial.csv`, `chunk_cluster_labels.csv`, `chunk_cluster_labels__kalm_embedding_gemma3_12b_leadercentered.csv`, `chunk_knn_leader_matrix.csv`, `chunk_knn_leader_matrix__kalm_embedding_gemma3_12b_noceremonial.csv`, `chunk_knn_leader_matrix__qwen3_embedding_8b.csv`, `chunk_knn_leader_matrix__qwen3_embedding_8b_noceremonial.csv`, `chunk_knn_leader_shares.csv`, `chunk_knn_leader_shares__kalm_embedding_gemma3_12b_noceremonial.csv`, `chunk_knn_leader_shares__qwen3_embedding_8b.csv`, `chunk_knn_leader_shares__qwen3_embedding_8b_noceremonial.csv`, `chunk_knn_per_chunk.csv`, `chunk_knn_per_chunk__kalm_embedding_gemma3_12b_noceremonial.csv`, `chunk_knn_per_chunk__qwen3_embedding_8b.csv`, `chunk_knn_per_chunk__qwen3_embedding_8b_noceremonial.csv`, `cluster_passages.csv`, `cluster_passages__kalm_embedding_gemma3_12b_leadercentered.csv`, `clusters_summary.csv`, `clusters_summary__kalm_embedding_gemma3_12b_leadercentered.csv`, `content_vs_style.csv`, `content_vs_style__kalm_embedding_gemma3_12b_noceremonial.csv`, `content_vs_style__qwen3_embedding_8b.csv`, `content_vs_style__qwen3_embedding_8b_noceremonial.csv`, `corpus_inventory.csv`, `cross_leader_pairing_counts.csv`, `cross_leader_pairing_counts__kalm_embedding_gemma3_12b_noceremonial.csv`, `cross_leader_pairing_counts__qwen3_embedding_8b.csv`, `cross_leader_pairing_counts__qwen3_embedding_8b_noceremonial.csv`, `cross_leader_pairs.csv`, `cross_leader_pairs__kalm_embedding_gemma3_12b_noceremonial.csv`, `cross_leader_pairs__qwen3_embedding_8b.csv`, `cross_leader_pairs__qwen3_embedding_8b_noceremonial.csv`, `emotion_profile_leader.csv`, `emotion_profile_leader__noceremonial.csv`, `emotion_profile_speech.csv`, `emotion_profile_speech__noceremonial.csv`, `emotion_scores_chunks.csv`, `emotion_scores_chunks__noceremonial.csv`, `emotion_top_labels_by_leader.csv`, `emotion_top_labels_by_leader__noceremonial.csv`, `framing_leader.csv`, `framing_leader__kalm_embedding_gemma3_12b_noceremonial.csv`, `framing_leader__qwen3_embedding_8b.csv`, `framing_leader__qwen3_embedding_8b_noceremonial.csv`, `framing_speech.csv`, `framing_speech__kalm_embedding_gemma3_12b_noceremonial.csv`, `framing_speech__qwen3_embedding_8b.csv`, `framing_speech__qwen3_embedding_8b_noceremonial.csv`, `hdbscan_parameter_grid.csv`, `hdbscan_parameter_grid__kalm_embedding_gemma3_12b_leadercentered.csv`, `language_effect_knn.csv`, `language_effect_pairs.csv`, `leader_cosine_distance.csv`, `leader_cosine_distance__kalm_embedding_gemma3_12b_noceremonial.csv`, `leader_cosine_distance__qwen3_embedding_8b.csv`, `leader_cosine_distance__qwen3_embedding_8b_noceremonial.csv`, `leader_cosine_similarity.csv`, `leader_cosine_similarity__kalm_embedding_gemma3_12b_noceremonial.csv`, `leader_cosine_similarity__qwen3_embedding_8b.csv`, `leader_cosine_similarity__qwen3_embedding_8b_noceremonial.csv`, `leader_cross_neighbor_similarity.csv`, `leader_cross_neighbor_similarity__kalm_embedding_gemma3_12b_noceremonial.csv`, `leader_cross_neighbor_similarity__qwen3_embedding_8b.csv`, `leader_cross_neighbor_similarity__qwen3_embedding_8b_noceremonial.csv`, `leader_pairs.csv`, `leader_pairs__kalm_embedding_gemma3_12b_noceremonial.csv`, `leader_pairs__qwen3_embedding_8b.csv`, `leader_pairs__qwen3_embedding_8b_noceremonial.csv`, `rhetoric_vs_emotion.csv`, `robustness_summary.csv`, `semantic_dispersion.csv`, `semantic_dispersion__kalm_embedding_gemma3_12b_noceremonial.csv`, `semantic_dispersion__qwen3_embedding_8b.csv`, `semantic_dispersion__qwen3_embedding_8b_noceremonial.csv`, `speech_cosine_similarity.csv`, `speech_cosine_similarity__kalm_embedding_gemma3_12b_noceremonial.csv`, `speech_cosine_similarity__qwen3_embedding_8b.csv`, `speech_cosine_similarity__qwen3_embedding_8b_noceremonial.csv`, `style_distance_leader.csv`, `style_distance_leader__kalm_embedding_gemma3_12b_noceremonial.csv`, `style_distance_leader__qwen3_embedding_8b.csv`, `style_distance_leader__qwen3_embedding_8b_noceremonial.csv`, `style_leader_profile.csv`, `style_leader_profile__kalm_embedding_gemma3_12b_noceremonial.csv`, `style_leader_profile__qwen3_embedding_8b.csv`, `style_leader_profile__qwen3_embedding_8b_noceremonial.csv`, `style_pairs.csv`, `style_pairs__kalm_embedding_gemma3_12b_noceremonial.csv`, `style_pairs__qwen3_embedding_8b.csv`, `style_pairs__qwen3_embedding_8b_noceremonial.csv`, `style_rankings.csv`, `style_rankings__kalm_embedding_gemma3_12b_noceremonial.csv`, `style_rankings__qwen3_embedding_8b.csv`, `style_rankings__qwen3_embedding_8b_noceremonial.csv`, `style_similarity_leader.csv`, `style_similarity_leader__kalm_embedding_gemma3_12b_noceremonial.csv`, `style_similarity_leader__qwen3_embedding_8b.csv`, `style_similarity_leader__qwen3_embedding_8b_noceremonial.csv`, `suspicious_files.csv`, `theme_language_diagnostic.csv`, `theme_language_diagnostic__kalm_embedding_gemma3_12b_noceremonial.csv`, `theme_language_diagnostic__qwen3_embedding_8b.csv`, `theme_language_diagnostic__qwen3_embedding_8b_noceremonial.csv`, `theme_method_agreement.csv`, `theme_method_agreement__kalm_embedding_gemma3_12b_noceremonial.csv`, `theme_method_agreement__qwen3_embedding_8b.csv`, `theme_method_agreement__qwen3_embedding_8b_noceremonial.csv`, `theme_profile_leader.csv`, `theme_profile_leader__kalm_embedding_gemma3_12b_noceremonial.csv`, `theme_profile_leader__qwen3_embedding_8b.csv`, `theme_profile_leader__qwen3_embedding_8b_noceremonial.csv`, `theme_profile_speech.csv`, `theme_profile_speech__kalm_embedding_gemma3_12b_noceremonial.csv`, `theme_profile_speech__qwen3_embedding_8b.csv`, `theme_profile_speech__qwen3_embedding_8b_noceremonial.csv`, `theme_scores_chunks.csv`, `theme_scores_chunks__kalm_embedding_gemma3_12b_noceremonial.csv`, `theme_scores_chunks__qwen3_embedding_8b.csv`, `theme_scores_chunks__qwen3_embedding_8b_noceremonial.csv`, `top_themes_by_leader.csv`, `top_themes_by_leader__kalm_embedding_gemma3_12b_noceremonial.csv`, `top_themes_by_leader__qwen3_embedding_8b.csv`, `top_themes_by_leader__qwen3_embedding_8b_noceremonial.csv`
