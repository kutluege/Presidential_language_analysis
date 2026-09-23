# Robustness report

Each check compares two complete result sets computed with the same pipeline. Rank correlations (Spearman) are the main yardstick because absolute cosine levels differ between models. Items marked ⚠ are material changes and are carried into the caution sections of the video findings.

## Material changes

- **F** embedding vs NLI — leader_theme_spearman_erdogan: 0.0952
- **F** embedding vs NLI — leader_theme_spearman_macron: -0.4524
- **F** embedding vs NLI — leader_theme_spearman_merkel: -0.4048
- **F** embedding vs NLI — leader_theme_spearman_trump: 0.0
- **G** original languages vs English — leader_pair_similarity_spearman: -0.4303
- **G** original languages vs English — most_similar_pair: putin–trump | macron–merkel
- **G** original languages vs English — erdogan_pairs_mean_rank: 8.5 → 4.2
- **G** original languages vs English — knn_same_leader_share_erdogan: 0.995 → 0.598
- **G** original languages vs English — knn_same_leader_share_macron: 0.958 → 0.713
- **G** original languages vs English — knn_same_leader_share_merkel: 0.689 → 0.479
- **G** original languages vs English — knn_same_leader_share_putin: 0.919 → 0.762
- **G** original languages vs English — knn_same_leader_share_trump: 0.867 → 0.658
- **G** original languages vs English — theme_profile_spearman_erdogan: 0.2857

### A: kalm_embedding_gemma3_12b vs qwen3_embedding_8b

- Leader-pair similarities: Spearman **0.83**, Pearson 0.92 over 10 pairs. Most similar pair: **macron–merkel** vs **macron–merkel**; least similar: putin–trump vs putin–trump. Mean off-diagonal similarity 0.758 vs 0.799 (absolute cosine levels are model-specific and not comparable across models).

| pair | kalm_embedding_gemma3_12b | qwen3_embedding_8b | rank kalm_embedding_gemma3_12b | rank qwen3_embedding_8b |
|---|---|---|---|---|
| macron–merkel | 0.850 | 0.871 | 1 | 1 |
| erdogan–macron | 0.806 | 0.857 | 2 | 2 |
| erdogan–merkel | 0.784 | 0.828 | 3 | 3 |
| erdogan–putin | 0.755 | 0.774 | 4 | 7 |
| macron–putin | 0.753 | 0.778 | 5 | 6 |
| macron–trump | 0.736 | 0.806 | 6 | 4 |
| merkel–putin | 0.736 | 0.761 | 7 | 9 |
| erdogan–trump | 0.735 | 0.796 | 8 | 5 |
| merkel–trump | 0.729 | 0.774 | 9 | 8 |
| putin–trump | 0.701 | 0.743 | 10 | 10 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **0.86**, top-3 overlap 2.6/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme kalm_embedding_gemma3_12b | top theme qwen3_embedding_8b |
|---|---|---|---|---|
| erdogan | 0.857 | 2 | Democracy, Law & Institutions | Foreign Policy & Geopolitics |
| macron | 0.619 | 2 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 0.857 | 3 | Future, Reform & Technology | Social Solidarity & Values |
| putin | 0.905 | 3 | National Identity & Unity | Social Solidarity & Values |
| trump | 0.952 | 3 | Economy & Welfare | Economy & Welfare |

- conflict_threat_framing: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b: erdogan 0.49, macron 0.44, merkel 0.49, putin 0.51, trump 0.54; qwen3_embedding_8b: erdogan 0.48, macron 0.47, merkel 0.47, putin 0.53, trump 0.60)
- cooperation_solidarity_framing: leader ordering Spearman **0.60** (kalm_embedding_gemma3_12b: erdogan 0.43, macron 0.47, merkel 0.61, putin 0.56, trump 0.41; qwen3_embedding_8b: erdogan 0.39, macron 0.47, merkel 0.55, putin 0.66, trump 0.52)
- past_orientation: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b: erdogan 0.53, macron 0.49, merkel 0.38, putin 0.62, trump 0.44; qwen3_embedding_8b: erdogan 0.51, macron 0.48, merkel 0.36, putin 0.72, trump 0.49)
- future_orientation: leader ordering Spearman **0.60** (kalm_embedding_gemma3_12b: erdogan 0.52, macron 0.57, merkel 0.45, putin 0.55, trump 0.37; qwen3_embedding_8b: erdogan 0.48, macron 0.56, merkel 0.45, putin 0.56, trump 0.50)
- us_vs_them: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b: erdogan 0.46, macron 0.39, merkel 0.51, putin 0.50, trump 0.65; qwen3_embedding_8b: erdogan 0.41, macron 0.40, merkel 0.46, putin 0.56, trump 0.77)
- gratitude_recognition: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b: erdogan 0.41, macron 0.44, merkel 0.44, putin 0.70, trump 0.51; qwen3_embedding_8b: erdogan 0.37, macron 0.46, merkel 0.42, putin 0.74, trump 0.68)
- promises_commitments: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b: erdogan 0.46, macron 0.57, merkel 0.43, putin 0.31, trump 0.59; qwen3_embedding_8b: erdogan 0.44, macron 0.54, merkel 0.45, putin 0.44, trump 0.69)
- Dispersion ordering (speech→leader distance): Spearman **1.00**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 0.83→0.60, macron 0.89→0.71, merkel 0.78→0.48, putin 0.92→0.76, trump 0.95→0.66

### B: original vs English-normalised corpus

_skipped — `data/translated_en/` contains no translations yet. Add them and run: preprocess/chunking/embed/theme_scoring/aggregate/geometry with `--variant translated_en`, then rerun robustness._

### C: kalm_embedding_gemma3_12b all content vs kalm_embedding_gemma3_12b ceremonial removed

- Leader-pair similarities: Spearman **0.96**, Pearson 0.98 over 10 pairs. Most similar pair: **macron–merkel** vs **macron–merkel**; least similar: putin–trump vs putin–trump. Mean off-diagonal similarity 0.758 vs 0.767 (absolute cosine levels are model-specific and not comparable across models).

| pair | kalm_embedding_gemma3_12b all content | kalm_embedding_gemma3_12b ceremonial removed | rank kalm_embedding_gemma3_12b all content | rank kalm_embedding_gemma3_12b ceremonial removed |
|---|---|---|---|---|
| macron–merkel | 0.850 | 0.844 | 1 | 1 |
| erdogan–macron | 0.806 | 0.811 | 2 | 2 |
| erdogan–merkel | 0.784 | 0.777 | 3 | 3 |
| erdogan–putin | 0.755 | 0.773 | 4 | 4 |
| macron–putin | 0.753 | 0.769 | 5 | 5 |
| macron–trump | 0.736 | 0.749 | 6 | 7 |
| merkel–putin | 0.736 | 0.736 | 7 | 8 |
| erdogan–trump | 0.735 | 0.752 | 8 | 6 |
| merkel–trump | 0.729 | 0.733 | 9 | 9 |
| putin–trump | 0.701 | 0.723 | 10 | 10 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **0.98**, top-3 overlap 3.0/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme kalm_embedding_gemma3_12b all content | top theme kalm_embedding_gemma3_12b ceremonial removed |
|---|---|---|---|---|
| erdogan | 0.976 | 3 | Democracy, Law & Institutions | Democracy, Law & Institutions |
| macron | 0.976 | 3 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 1.000 | 3 | Future, Reform & Technology | Future, Reform & Technology |
| putin | 0.976 | 3 | National Identity & Unity | Social Solidarity & Values |
| trump | 0.857 | 3 | Economy & Welfare | Security & Military |

- conflict_threat_framing: leader ordering Spearman **1.00** (kalm_embedding_gemma3_12b all content: erdogan 0.49, macron 0.44, merkel 0.49, putin 0.51, trump 0.54; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.49, macron 0.43, merkel 0.45, putin 0.52, trump 0.70)
- cooperation_solidarity_framing: leader ordering Spearman **0.60** (kalm_embedding_gemma3_12b all content: erdogan 0.43, macron 0.47, merkel 0.61, putin 0.56, trump 0.41; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.44, macron 0.47, merkel 0.57, putin 0.62, trump 0.51)
- past_orientation: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b all content: erdogan 0.53, macron 0.49, merkel 0.38, putin 0.62, trump 0.44; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.52, macron 0.48, merkel 0.33, putin 0.64, trump 0.51)
- future_orientation: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b all content: erdogan 0.52, macron 0.57, merkel 0.45, putin 0.55, trump 0.37; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.51, macron 0.58, merkel 0.39, putin 0.55, trump 0.45)
- us_vs_them: leader ordering Spearman **0.90** (kalm_embedding_gemma3_12b all content: erdogan 0.46, macron 0.39, merkel 0.51, putin 0.50, trump 0.65; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.46, macron 0.39, merkel 0.48, putin 0.55, trump 0.77)
- gratitude_recognition: leader ordering Spearman **0.70** (kalm_embedding_gemma3_12b all content: erdogan 0.41, macron 0.44, merkel 0.44, putin 0.70, trump 0.51; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.41, macron 0.43, merkel 0.40, putin 0.74, trump 0.56)
- promises_commitments: leader ordering Spearman **1.00** (kalm_embedding_gemma3_12b all content: erdogan 0.46, macron 0.57, merkel 0.43, putin 0.31, trump 0.59; kalm_embedding_gemma3_12b ceremonial removed: erdogan 0.45, macron 0.57, merkel 0.39, putin 0.35, trump 0.66)
- Dispersion ordering (speech→leader distance): Spearman **1.00**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 0.83→0.81, macron 0.89→0.89, merkel 0.78→0.76, putin 0.92→0.82, trump 0.95→0.94

### C: qwen3_embedding_8b all content vs qwen3_embedding_8b ceremonial removed

- Leader-pair similarities: Spearman **1.00**, Pearson 0.98 over 10 pairs. Most similar pair: **macron–merkel** vs **macron–merkel**; least similar: putin–trump vs putin–trump. Mean off-diagonal similarity 0.799 vs 0.805 (absolute cosine levels are model-specific and not comparable across models).

| pair | qwen3_embedding_8b all content | qwen3_embedding_8b ceremonial removed | rank qwen3_embedding_8b all content | rank qwen3_embedding_8b ceremonial removed |
|---|---|---|---|---|
| macron–merkel | 0.871 | 0.871 | 1 | 1 |
| erdogan–macron | 0.857 | 0.861 | 2 | 2 |
| erdogan–merkel | 0.828 | 0.824 | 3 | 3 |
| macron–trump | 0.806 | 0.820 | 4 | 4 |
| erdogan–trump | 0.796 | 0.816 | 5 | 5 |
| macron–putin | 0.778 | 0.788 | 6 | 6 |
| erdogan–putin | 0.774 | 0.783 | 7 | 7 |
| merkel–trump | 0.774 | 0.778 | 8 | 8 |
| merkel–putin | 0.761 | 0.753 | 9 | 9 |
| putin–trump | 0.743 | 0.752 | 10 | 10 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **0.95**, top-3 overlap 2.6/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme qwen3_embedding_8b all content | top theme qwen3_embedding_8b ceremonial removed |
|---|---|---|---|---|
| erdogan | 0.881 | 2 | Foreign Policy & Geopolitics | Foreign Policy & Geopolitics |
| macron | 1.000 | 3 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 0.952 | 3 | Social Solidarity & Values | Democracy, Law & Institutions |
| putin | 1.000 | 3 | Social Solidarity & Values | Social Solidarity & Values |
| trump | 0.881 | 2 | Economy & Welfare | Security & Military |

- conflict_threat_framing: leader ordering Spearman **1.00** (qwen3_embedding_8b all content: erdogan 0.48, macron 0.47, merkel 0.47, putin 0.53, trump 0.60; qwen3_embedding_8b ceremonial removed: erdogan 0.48, macron 0.47, merkel 0.46, putin 0.52, trump 0.68)
- cooperation_solidarity_framing: leader ordering Spearman **0.90** (qwen3_embedding_8b all content: erdogan 0.39, macron 0.47, merkel 0.55, putin 0.66, trump 0.52; qwen3_embedding_8b ceremonial removed: erdogan 0.40, macron 0.47, merkel 0.51, putin 0.66, trump 0.59)
- past_orientation: leader ordering Spearman **0.90** (qwen3_embedding_8b all content: erdogan 0.51, macron 0.48, merkel 0.36, putin 0.72, trump 0.49; qwen3_embedding_8b ceremonial removed: erdogan 0.51, macron 0.48, merkel 0.32, putin 0.71, trump 0.54)
- future_orientation: leader ordering Spearman **0.90** (qwen3_embedding_8b all content: erdogan 0.48, macron 0.56, merkel 0.45, putin 0.56, trump 0.50; qwen3_embedding_8b ceremonial removed: erdogan 0.48, macron 0.57, merkel 0.42, putin 0.55, trump 0.54)
- us_vs_them: leader ordering Spearman **1.00** (qwen3_embedding_8b all content: erdogan 0.41, macron 0.40, merkel 0.46, putin 0.56, trump 0.77; qwen3_embedding_8b ceremonial removed: erdogan 0.41, macron 0.40, merkel 0.45, putin 0.56, trump 0.79)
- gratitude_recognition: leader ordering Spearman **1.00** (qwen3_embedding_8b all content: erdogan 0.37, macron 0.46, merkel 0.42, putin 0.74, trump 0.68; qwen3_embedding_8b ceremonial removed: erdogan 0.37, macron 0.46, merkel 0.39, putin 0.74, trump 0.68)
- promises_commitments: leader ordering Spearman **0.60** (qwen3_embedding_8b all content: erdogan 0.44, macron 0.54, merkel 0.45, putin 0.44, trump 0.69; qwen3_embedding_8b ceremonial removed: erdogan 0.44, macron 0.55, merkel 0.43, putin 0.45, trump 0.72)
- Dispersion ordering (speech→leader distance): Spearman **1.00**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 0.60→0.59, macron 0.71→0.70, merkel 0.48→0.42, putin 0.76→0.67, trump 0.66→0.62

### D: leader-centroid similarity vs chunk-level cross-neighbour similarity (primary model)

- Spearman(centroid similarity, mean cross-neighbour similarity) = **0.75**; Spearman(centroid similarity, symmetric kNN share) = **0.64** over 10 pairs. Top pair by centroid: macron–merkel; by cross-neighbour similarity: macron–merkel.

| pair | centroid_similarity | cross_neighbor_similarity | knn_share_symmetric |
|---|---|---|---|
| macron–merkel | 0.850 | 0.592 | 0.112 |
| erdogan–macron | 0.806 | 0.558 | 0.036 |
| erdogan–merkel | 0.784 | 0.539 | 0.028 |
| erdogan–putin | 0.755 | 0.570 | 0.036 |
| macron–putin | 0.753 | 0.573 | 0.017 |
| macron–trump | 0.736 | 0.522 | 0.007 |
| merkel–putin | 0.736 | 0.557 | 0.015 |
| erdogan–trump | 0.735 | 0.517 | 0.038 |
| merkel–trump | 0.729 | 0.511 | 0.016 |
| putin–trump | 0.701 | 0.528 | 0.006 |

### E: with vs without `trump2` (flagged as a compilation of excerpts)

- Trump centroid similarities with/without `trump2` (max |Δ| = 0.006); ordering of the other leaders unchanged.

| pair | with | without | delta |
|---|---|---|---|
| trump–erdogan | 0.735 | 0.741 | 0.006 |
| trump–macron | 0.736 | 0.741 | 0.006 |
| trump–merkel | 0.729 | 0.735 | 0.006 |
| trump–putin | 0.701 | 0.706 | 0.005 |

- Trump top-3 themes with `trump2`: Economy & Welfare, Security & Military, National Identity & Unity; without: National Identity & Unity, Security & Military, Economy & Welfare. Max theme-percentile change: 0.152.

### F: theme-scoring method agreement (primary model)

- Leader-level theme ranking, language-matched vs English descriptions: median Spearman **1.00**. Embedding vs NLI: median Spearman **0.00**. Chunk-level (from theme_method_agreement): matched-vs-English Spearman 1.00–1.00, embedding-vs-NLI 0.16–0.58, same top theme for 34% of chunks.

| leader | spearman_matched_vs_en | top_matched | top_en | spearman_emb_vs_nli | top_nli |
|---|---|---|---|---|---|
| erdogan | 1.000 | Crisis, Threat & Resilience | Crisis, Threat & Resilience | 0.095 | National Identity & Unity |
| macron | 1.000 | Crisis, Threat & Resilience | Crisis, Threat & Resilience | -0.452 | National Identity & Unity |
| merkel | 1.000 | Crisis, Threat & Resilience | Crisis, Threat & Resilience | -0.405 | Social Solidarity & Values |
| putin | 1.000 | National Identity & Unity | National Identity & Unity | 0.667 | Social Solidarity & Values |
| trump | 1.000 | Security & Military | Security & Military | 0.000 | Social Solidarity & Values |

### G: language effect — `qwen3_embedding_8b` on the original-language corpus (archived) vs the English corpus

- Leader-pair similarities, same model: Spearman **-0.43** between the two corpora. Most similar pair: putin–trump (original) → macron–merkel (English). Erdoğan's four pairs move from mean rank 8.5 to 4.2 of 10; mean off-diagonal similarity 0.645 → 0.799.

| pair | old_similarity | new_similarity | delta | old_rank | new_rank |
|---|---|---|---|---|---|
| putin–trump | 0.744 | 0.743 | -0.000 | 1 | 10 |
| macron–merkel | 0.698 | 0.871 | 0.173 | 2 | 1 |
| merkel–putin | 0.678 | 0.761 | 0.083 | 3 | 9 |
| merkel–trump | 0.660 | 0.774 | 0.114 | 4 | 8 |
| macron–putin | 0.643 | 0.778 | 0.135 | 5 | 6 |
| macron–trump | 0.633 | 0.806 | 0.173 | 6 | 4 |
| erdogan–merkel | 0.621 | 0.828 | 0.207 | 7 | 3 |
| erdogan–putin | 0.595 | 0.774 | 0.179 | 8 | 7 |
| erdogan–trump | 0.593 | 0.796 | 0.203 | 9 | 5 |
| erdogan–macron | 0.581 | 0.857 | 0.276 | 10 | 2 |

- Same-leader share of the 10 nearest neighbours: Erdoğan 100% → 60%, Macron 96% → 71%, Merkel 69% → 48%, Putin 92% → 76%, Trump 87% → 66%

- Theme profiles (old run scored against language-matched descriptions, new run against English): median Spearman **0.76**.

| leader | spearman_8_themes | top3_overlap |
|---|---|---|
| erdogan | 0.286 | 1 |
| macron | 0.857 | 3 |
| merkel | 0.762 | 2 |
| putin | 0.952 | 3 |
| trump | 0.643 | 2 |

_Caveat: the English texts are translations for Erdoğan, Macron and Merkel; the comparison mixes the language effect with the translator's choices._

### H: rhetorical dimensions (embedding) vs emotional tone (classifier), speech level

- Two independent methods (embedding similarity to a description vs a supervised classifier) agree where the correlations are clearly positive and diverge where they are near zero:

| rhetorical | emotion | spearman_speech_level | n_speeches |
|---|---|---|---|
| conflict_threat_framing_pct | fam_hostility | 0.487 | 20 |
| conflict_threat_framing_pct | fam_threat_negative | 0.317 | 20 |
| cooperation_solidarity_framing_pct | fam_affiliative_positive | -0.113 | 20 |
| gratitude_recognition_pct | emo_gratitude | -0.107 | 20 |
| conflict_threat_framing_pct | valence | -0.165 | 20 |
| us_vs_them_pct | fam_hostility | 0.495 | 20 |
| future_orientation_pct | emo_optimism | 0.559 | 20 |
