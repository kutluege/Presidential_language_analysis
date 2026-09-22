# Robustness report

Each check compares two complete result sets computed with the same pipeline. Rank correlations (Spearman) are the main yardstick because absolute cosine levels differ between models. Items marked ⚠ are material changes and are carried into the caution sections of the video findings.

## Material changes

- **A** qwen3_embedding_8b vs bge_m3 — leader_pair_similarity_spearman: -0.3697
- **A** qwen3_embedding_8b vs bge_m3 — most_similar_pair: putin–trump | macron–merkel
- **A** qwen3_embedding_8b vs bge_m3 — least_similar_pair: erdogan–macron | putin–trump
- **A** qwen3_embedding_8b vs bge_m3 — theme_profile_spearman_macron: 0.4048
- **A** qwen3_embedding_8b vs bge_m3 — theme_profile_spearman_merkel: 0.1905
- **A** qwen3_embedding_8b vs bge_m3 — framing_leader_order_spearman_conflict_threat_framing: -0.8
- **A** qwen3_embedding_8b vs bge_m3 — framing_leader_order_spearman_cooperation_solidarity_framing: 0.2
- **C** bge_m3 all content vs bge_m3 ceremonial removed — most_similar_pair: macron–merkel | erdogan–macron
- **E** without trump2 — top3_themes_trump: ['Economy & Welfare', 'Security & Military', 'Democracy, Law & Institutions'] → ['Foreign Policy & Geopolitics', 'National Identity & Unity', 'Security & Military']
- **F** embedding vs NLI — leader_theme_spearman_macron: -0.2857
- **F** embedding vs NLI — leader_theme_spearman_merkel: 0.0952
- **F** embedding vs NLI — leader_theme_spearman_trump: 0.4286

### A: qwen3_embedding_8b vs bge_m3

- Leader-pair similarities: Spearman **-0.37**, Pearson -0.36 over 10 pairs. Most similar pair: **putin–trump** vs **macron–merkel** ⚠ differs; least similar: erdogan–macron vs putin–trump ⚠ differs. Mean off-diagonal similarity 0.645 vs 0.880 (absolute cosine levels are model-specific and not comparable across models).

| pair | qwen3_embedding_8b | bge_m3 | rank qwen3_embedding_8b | rank bge_m3 |
|---|---|---|---|---|
| putin–trump | 0.744 | 0.824 | 1 | 10 |
| macron–merkel | 0.698 | 0.942 | 2 | 1 |
| merkel–putin | 0.678 | 0.838 | 3 | 9 |
| merkel–trump | 0.660 | 0.864 | 4 | 6 |
| macron–putin | 0.643 | 0.860 | 5 | 7 |
| macron–trump | 0.633 | 0.880 | 6 | 4 |
| erdogan–merkel | 0.621 | 0.924 | 7 | 3 |
| erdogan–putin | 0.595 | 0.851 | 8 | 8 |
| erdogan–trump | 0.593 | 0.875 | 9 | 5 |
| erdogan–macron | 0.581 | 0.941 | 10 | 2 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **0.67**, top-3 overlap 2.0/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme qwen3_embedding_8b | top theme bge_m3 |
|---|---|---|---|---|
| erdogan | 0.667 | 2 | Foreign Policy & Geopolitics | Crisis, Threat & Resilience |
| macron | 0.405 | 2 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 0.190 | 1 | Social Solidarity & Values | Social Solidarity & Values |
| putin | 0.810 | 3 | Social Solidarity & Values | Security & Military |
| trump | 0.714 | 2 | Economy & Welfare | National Identity & Unity |

- conflict_threat_framing: leader ordering Spearman **-0.80** (qwen3_embedding_8b: erdogan 0.61, macron 0.50, merkel 0.35, putin 0.43, trump 0.50; bge_m3: erdogan 0.49, macron 0.56, merkel 0.64, putin 0.49, trump 0.25)
- cooperation_solidarity_framing: leader ordering Spearman **0.20** (qwen3_embedding_8b: erdogan 0.51, macron 0.43, merkel 0.52, putin 0.63, trump 0.49; bge_m3: erdogan 0.42, macron 0.67, merkel 0.71, putin 0.43, trump 0.14)
- Dispersion ordering (speech→leader distance): Spearman **0.70**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 1.00→0.47, macron 0.96→0.66, merkel 0.69→0.52, putin 0.92→0.83, trump 0.87→0.66

### B: original vs English-normalised corpus

_skipped — `data/translated_en/` contains no translations yet. Add them and run: preprocess/chunking/embed/theme_scoring/aggregate/geometry with `--variant translated_en`, then rerun robustness._

### C: qwen3_embedding_8b all content vs qwen3_embedding_8b ceremonial removed

- Leader-pair similarities: Spearman **0.99**, Pearson 0.99 over 10 pairs. Most similar pair: **putin–trump** vs **putin–trump**; least similar: erdogan–macron vs erdogan–macron. Mean off-diagonal similarity 0.645 vs 0.649 (absolute cosine levels are model-specific and not comparable across models).

| pair | qwen3_embedding_8b all content | qwen3_embedding_8b ceremonial removed | rank qwen3_embedding_8b all content | rank qwen3_embedding_8b ceremonial removed |
|---|---|---|---|---|
| putin–trump | 0.744 | 0.752 | 1 | 1 |
| macron–merkel | 0.698 | 0.696 | 2 | 2 |
| merkel–putin | 0.678 | 0.674 | 3 | 3 |
| merkel–trump | 0.660 | 0.668 | 4 | 4 |
| macron–putin | 0.643 | 0.647 | 5 | 5 |
| macron–trump | 0.633 | 0.644 | 6 | 6 |
| erdogan–merkel | 0.621 | 0.615 | 7 | 7 |
| erdogan–putin | 0.595 | 0.600 | 8 | 9 |
| erdogan–trump | 0.593 | 0.610 | 9 | 8 |
| erdogan–macron | 0.581 | 0.580 | 10 | 10 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **1.00**, top-3 overlap 2.8/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme qwen3_embedding_8b all content | top theme qwen3_embedding_8b ceremonial removed |
|---|---|---|---|---|
| erdogan | 1.000 | 3 | Foreign Policy & Geopolitics | Foreign Policy & Geopolitics |
| macron | 1.000 | 3 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 0.929 | 2 | Social Solidarity & Values | Future, Reform & Technology |
| putin | 1.000 | 3 | Social Solidarity & Values | Social Solidarity & Values |
| trump | 0.905 | 3 | Economy & Welfare | Security & Military |

- conflict_threat_framing: leader ordering Spearman **1.00** (qwen3_embedding_8b all content: erdogan 0.61, macron 0.50, merkel 0.35, putin 0.43, trump 0.50; qwen3_embedding_8b ceremonial removed: erdogan 0.61, macron 0.49, merkel 0.36, putin 0.42, trump 0.58)
- cooperation_solidarity_framing: leader ordering Spearman **0.60** (qwen3_embedding_8b all content: erdogan 0.51, macron 0.43, merkel 0.52, putin 0.63, trump 0.49; qwen3_embedding_8b ceremonial removed: erdogan 0.52, macron 0.42, merkel 0.50, putin 0.64, trump 0.57)
- Dispersion ordering (speech→leader distance): Spearman **0.90**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 1.00→0.99, macron 0.96→0.95, merkel 0.69→0.66, putin 0.92→0.87, trump 0.87→0.82

### C: bge_m3 all content vs bge_m3 ceremonial removed

- Leader-pair similarities: Spearman **0.95**, Pearson 0.99 over 10 pairs. Most similar pair: **macron–merkel** vs **erdogan–macron** ⚠ differs; least similar: putin–trump vs putin–trump. Mean off-diagonal similarity 0.880 vs 0.885 (absolute cosine levels are model-specific and not comparable across models).

| pair | bge_m3 all content | bge_m3 ceremonial removed | rank bge_m3 all content | rank bge_m3 ceremonial removed |
|---|---|---|---|---|
| macron–merkel | 0.942 | 0.940 | 1 | 2 |
| erdogan–macron | 0.941 | 0.942 | 2 | 1 |
| erdogan–merkel | 0.924 | 0.922 | 3 | 3 |
| macron–trump | 0.880 | 0.879 | 4 | 4 |
| erdogan–trump | 0.875 | 0.878 | 5 | 5 |
| merkel–trump | 0.864 | 0.863 | 6 | 8 |
| macron–putin | 0.860 | 0.875 | 7 | 6 |
| erdogan–putin | 0.851 | 0.864 | 8 | 7 |
| merkel–putin | 0.838 | 0.847 | 9 | 9 |
| putin–trump | 0.824 | 0.844 | 10 | 10 |

- Theme profiles per leader (mean percentile over 8 themes): median Spearman **0.98**, top-3 overlap 2.8/3 on average.

| leader | spearman_8_themes | top3_overlap | top theme bge_m3 all content | top theme bge_m3 ceremonial removed |
|---|---|---|---|---|
| erdogan | 0.881 | 3 | Crisis, Threat & Resilience | Crisis, Threat & Resilience |
| macron | 0.976 | 3 | Future, Reform & Technology | Future, Reform & Technology |
| merkel | 1.000 | 3 | Social Solidarity & Values | Social Solidarity & Values |
| putin | 0.976 | 3 | Security & Military | Security & Military |
| trump | 0.833 | 2 | National Identity & Unity | Security & Military |

- conflict_threat_framing: leader ordering Spearman **1.00** (bge_m3 all content: erdogan 0.49, macron 0.56, merkel 0.64, putin 0.49, trump 0.25; bge_m3 ceremonial removed: erdogan 0.48, macron 0.56, merkel 0.63, putin 0.53, trump 0.28)
- cooperation_solidarity_framing: leader ordering Spearman **1.00** (bge_m3 all content: erdogan 0.42, macron 0.67, merkel 0.71, putin 0.43, trump 0.14; bge_m3 ceremonial removed: erdogan 0.41, macron 0.67, merkel 0.69, putin 0.46, trump 0.16)
- Dispersion ordering (speech→leader distance): Spearman **0.90**.
- Share of a chunk's 10 nearest neighbours (other speeches) that belong to the same leader: erdogan 0.47→0.47, macron 0.66→0.65, merkel 0.52→0.50, putin 0.83→0.73, trump 0.66→0.67

### D: leader-centroid similarity vs chunk-level cross-neighbour similarity (primary model)

- Spearman(centroid similarity, mean cross-neighbour similarity) = **0.61**; Spearman(centroid similarity, symmetric kNN share) = **0.90** over 10 pairs. Top pair by centroid: putin–trump; by cross-neighbour similarity: putin–trump.

| pair | centroid_similarity | cross_neighbor_similarity | knn_share_symmetric |
|---|---|---|---|
| putin–trump | 0.744 | 0.485 | 0.063 |
| macron–merkel | 0.698 | 0.408 | 0.077 |
| merkel–putin | 0.678 | 0.420 | 0.049 |
| merkel–trump | 0.660 | 0.381 | 0.021 |
| macron–putin | 0.643 | 0.435 | 0.018 |
| macron–trump | 0.633 | 0.396 | 0.011 |
| erdogan–merkel | 0.621 | 0.374 | 0.025 |
| erdogan–putin | 0.595 | 0.423 | 0.008 |
| erdogan–trump | 0.593 | 0.381 | 0.011 |
| erdogan–macron | 0.581 | 0.380 | 0.004 |

### E: with vs without `trump2` (flagged as a compilation of excerpts)

- Trump centroid similarities with/without `trump2` (max |Δ| = 0.012); ordering of the other leaders unchanged.

| pair | with | without | delta |
|---|---|---|---|
| trump–erdogan | 0.593 | 0.599 | 0.006 |
| trump–macron | 0.633 | 0.642 | 0.008 |
| trump–merkel | 0.660 | 0.670 | 0.010 |
| trump–putin | 0.744 | 0.756 | 0.012 |

- Trump top-3 themes with `trump2`: Economy & Welfare, Security & Military, Democracy, Law & Institutions; without: Foreign Policy & Geopolitics, National Identity & Unity, Security & Military ⚠ set changes. Max theme-percentile change: 0.083.

### F: theme-scoring method agreement (primary model)

- Leader-level theme ranking, language-matched vs English descriptions: median Spearman **0.98**. Embedding vs NLI: median Spearman **0.43**. Chunk-level (from theme_method_agreement): matched-vs-English Spearman 0.79–0.91, embedding-vs-NLI 0.34–0.57, same top theme for 34% of chunks.

| leader | spearman_matched_vs_en | top_matched | top_en | spearman_emb_vs_nli | top_nli |
|---|---|---|---|---|---|
| erdogan | 0.619 | Crisis, Threat & Resilience | Crisis, Threat & Resilience | 0.524 | Social Solidarity & Values |
| macron | 0.952 | Future, Reform & Technology | Future, Reform & Technology | -0.286 | Social Solidarity & Values |
| merkel | 0.976 | Social Solidarity & Values | Social Solidarity & Values | 0.095 | Social Solidarity & Values |
| putin | 1.000 | Social Solidarity & Values | Social Solidarity & Values | 0.738 | Social Solidarity & Values |
| trump | 1.000 | Social Solidarity & Values | Social Solidarity & Values | 0.429 | Social Solidarity & Values |
