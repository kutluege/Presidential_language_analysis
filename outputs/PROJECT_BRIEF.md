# Project brief — political-speech-geometry

Generated 2026-09-23 13:10 from the repository's result tables. This single file is meant to be handed to a person or a language model that has not seen the repository. Everything below is a statement about the *collected speech files*; nothing measures ideology, political quality, personality, competence or morality, and nothing is an endorsement or a criticism of anyone.

## 1. What the project is

A small, reproducible NLP experiment on the content, semantic geometry and rhetorical style of public speeches by five political leaders (Recep Tayyip Erdoğan, Emmanuel Macron, Angela Merkel, Vladimir Putin, Donald Trump), built as material for an Instagram explainer video in which the author appears on camera as an AI engineer. The stated goals: (1) examine which themes each speech set emphasises and how often, (2) measure how semantically close the speech sets are in an embedding space, (3) rank the sets on measurable, descriptive style dimensions (rhetorical framing and emotional tone), (4) analyse the semantic content of the messages, and (5) surface embedding-geometry facts an engineer can explain to a general audience.

Ground rules kept throughout: all similarity, distance, theme, rhetorical and emotional values describe the collected corpora; 'ranking' means sorted measurements with confidence intervals; every claim is traceable to a table, a numeric metric and a documented method; 2D projections are for visualisation only; each speech weighs the same inside its leader's aggregate so long speeches do not dominate.

## 2. The corpus

20 speeches, 23,905 cleaned words, 250 chunks (paragraph-based, 80–180 tokens, no overlap, median 107 tokens). Mostly New Year addresses from different years; one Erdoğan symposium speech, one Trump farewell address, one Trump inaugural address, and one Trump file that is a compilation of excerpts from several occasions (kept at the collector's request; its effect is reported as a robustness check).

| speech_id | leader | speech_date | speech_type | word_count_clean | title |
|---|---|---|---|---|---|
| erdogan1 | Erdoğan |  | symposium_speech | 904 | SETA symposium speech on the presidential system |
| erdogan2022 | Erdoğan | 2022-12-31 | new_year_message | 1098 | New Year message 2022/23 |
| erdogan2023 | Erdoğan | 2023-12-31 | new_year_message | 1102 | New Year message 2023/24 |
| erdogan2024 | Erdoğan | 2024-12-31 | new_year_message | 931 | New Year message 2024/25 |
| erdogan2025 | Erdoğan | 2025-12-31 | new_year_message | 1206 | New Year message 2025/26 |
| macron2022 | Macron | 2022-12-31 | new_year_address | 2943 | Vœux aux Français 2023 |
| macron2023 | Macron | 2023-12-31 | new_year_address | 1933 | Vœux aux Français 2024 |
| macron2024 | Macron | 2024-12-31 | new_year_address | 1606 | Vœux aux Français 2025 |
| macron2025 | Macron | 2025-12-31 | new_year_address | 1451 | Vœux aux Français 2026 |
| merkel1 | Merkel | 2016-12-31 | new_year_address | 987 | Neujahrsansprache 2017 |
| merkel2 | Merkel | 2017-12-31 | new_year_address | 868 | Neujahrsansprache 2018 |
| merkel2020 | Merkel | 2019-12-31 | new_year_address | 936 | Neujahrsansprache 2020 |
| merkel3 | Merkel | 2018-12-31 | new_year_address | 881 | Neujahrsansprache 2019 |
| putin2022 | Putin | 2022-12-31 | new_year_address | 1118 | New Year address 2023 |
| putin2023 | Putin | 2023-12-31 | new_year_address | 491 | New Year address 2024 |
| putin2024 | Putin | 2024-12-31 | new_year_address | 430 | New Year address 2025 |
| putin2025 | Putin | 2025-12-31 | new_year_address | 458 | New Year address 2026 |
| trump1 | Trump | 2021-01-19 | farewell_address | 2782 | Farewell address |
| trump2 | Trump |  | composite_excerpts | 323 | Compilation of short excerpts |
| trump3 | Trump | 2017-01-20 | inaugural_address | 1457 | Inaugural address 2017 |

**Language history — the central methodological story.** Run 1 (2026-09-22) analysed the texts in their original languages: Turkish (Erdoğan), French (Macron), German (Merkel), English (Putin via official transcript, Trump). The embedding model saw language before content: 69–100% of a chunk's nearest neighbours came from the same leader, and Erdoğan's Turkish speeches sat in all four least-similar leader pairs. Because each leader spoke a different language, leader and language could not be separated. For run 2 (2026-09-23) the collector translated the Turkish, French and German speeches into English (paragraph structure preserved) and the whole analysis was redone; run 1 is archived in `old_results/`. The price of translation: for Erdoğan, Macron and Merkel the English text also carries the translator's choices, so style measurements describe the translated text.

## 3. Pipeline (what was actually computed)

1. **Inventory & validation** of every file (word/paragraph counts, language check, artifacts, duplicates, metadata) → `outputs/phase0_report.md`.
2. **Conservative cleaning**, every removal logged: four `President of Russia Vladimir Putin:` speaker labels, the oath ceremony spoken by other people at the top of the Trump inaugural, two lone `*` separator lines → `data/processed/preprocessing_report.md`.
3. **Chunking** into paragraph-based chunks of 80–180 tokens (Qwen3 tokenizer; identical chunks for both models); a second chunk set with ceremonial openings/closings stripped for robustness.
4. **Embeddings** with two models on identical chunks: primary `tencent/KaLM-Embedding-Gemma3-12B-2511` (3840-d, 11.8B parameters, bf16, peak 22.83 GB VRAM, 6.8 s for all chunks on one RTX 5090) and robustness `Qwen/Qwen3-Embedding-8B` (4096-d). All vectors unit-normalised.
5. **Theme scoring** (8 fixed themes) and **rhetorical scoring** (7 dimensions): cosine similarity between each chunk and a written description embedded with the same model, expressed as a corpus percentile (0.5 = corpus average); a multilingual zero-shot NLI classifier as a second opinion; keyword hits only as a diagnostic.
6. **Emotional tone** with independent classifiers: GoEmotions (28 labels, multi-label) grouped into families, plus a three-class sentiment model (valence = P(positive) − P(negative)).
7. **Aggregation** chunk → speech (mean) → leader (mean of speeches). **Centroids**: normalised speech centroids, leader centroid = normalised mean of speech centroids.
8. **Geometry**: 5×5 leader cosine similarity/distance; chunk-level k-nearest-neighbour analysis (k=10, same speech excluded) with observed vs expected same-leader share; cross-leader chunk pairs; within-leader dispersion.
9. **Style profile**: per speech, 7 rhetorical percentiles + 3 emotion family means + valence, z-scored across the 20 speeches; leader = mean; Euclidean distance and cosine between leaders; hierarchical clustering; rankings per dimension.
10. **Topic discovery** (exploratory): PCA(50) → HDBSCAN, raw and after subtracting each leader's centroid.
11. **Uncertainty**: speech-level bootstrap, 2000 resamples, 95% percentile intervals for every leader-level number; rank-stability shares.
12. **Robustness**: primary vs robustness model; original-language (archived) vs English corpus with the same model; all content vs ceremonial-stripped; centroid vs kNN similarity; with vs without the excerpt compilation; embedding vs NLI; rhetoric vs emotion classifier.
13. **Figures** in square 1:1 and vertical 9:16 (Instagram), PNG at 2160 px + SVG, fixed colour per leader.

## 4. Key numbers

### 4.1 Semantic proximity — leader-centroid cosine similarity, primary model (KaLM-Embedding-Gemma3-12B-2511, English corpus)

|  | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.000 | 0.806 | 0.784 | 0.755 | 0.735 |
| Macron | 0.806 | 1.000 | 0.850 | 0.753 | 0.736 |
| Merkel | 0.784 | 0.850 | 1.000 | 0.736 | 0.729 |
| Putin | 0.755 | 0.753 | 0.736 | 1.000 | 0.701 |
| Trump | 0.735 | 0.736 | 0.729 | 0.701 | 1.000 |

Pairs sorted, with 95% speech-level bootstrap intervals and the share of 2000 resamples in which the pair is the closest / the most distant:

| pair | cosine_similarity | ci_low | ci_high | share_most_similar_pair | share_least_similar_pair |
|---|---|---|---|---|---|
| Macron–Merkel | 0.850 | 0.811 | 0.860 | 1.000 | 0.000 |
| Erdoğan–Macron | 0.806 | 0.751 | 0.812 | 0.000 | 0.000 |
| Erdoğan–Merkel | 0.784 | 0.731 | 0.794 | 0.000 | 0.000 |
| Erdoğan–Putin | 0.755 | 0.679 | 0.776 | 0.000 | 0.050 |
| Macron–Putin | 0.753 | 0.718 | 0.763 | 0.000 | 0.000 |
| Macron–Trump | 0.736 | 0.664 | 0.744 | 0.000 | 0.000 |
| Merkel–Putin | 0.736 | 0.701 | 0.743 | 0.000 | 0.002 |
| Erdoğan–Trump | 0.735 | 0.657 | 0.745 | 0.000 | 0.037 |
| Merkel–Trump | 0.729 | 0.653 | 0.733 | 0.000 | 0.004 |
| Putin–Trump | 0.701 | 0.634 | 0.710 | 0.000 | 0.907 |

### 4.2 The same matrix under the robustness model (Qwen3-Embedding-8B, English corpus)

|  | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.000 | 0.857 | 0.828 | 0.774 | 0.796 |
| Macron | 0.857 | 1.000 | 0.871 | 0.778 | 0.806 |
| Merkel | 0.828 | 0.871 | 1.000 | 0.761 | 0.774 |
| Putin | 0.774 | 0.778 | 0.761 | 1.000 | 0.743 |
| Trump | 0.796 | 0.806 | 0.774 | 0.743 | 1.000 |

### 4.3 Run 1 for comparison — Qwen3-Embedding-8B on the ORIGINAL-LANGUAGE corpus (archived)

|  | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.000 | 0.581 | 0.621 | 0.595 | 0.593 |
| Macron | 0.581 | 1.000 | 0.698 | 0.643 | 0.633 |
| Merkel | 0.621 | 0.698 | 1.000 | 0.678 | 0.660 |
| Putin | 0.595 | 0.643 | 0.678 | 1.000 | 0.744 |
| Trump | 0.593 | 0.633 | 0.660 | 0.744 | 1.000 |

### 4.4 Language effect — same model (Qwen3), original languages → English

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

Same-leader share of a chunk's 10 nearest neighbours (other speeches only), before → after translation, same model:

| leader | old_same_leader_share | new_same_leader_share |
|---|---|---|
| Erdoğan | 0.995 | 0.598 |
| Macron | 0.958 | 0.713 |
| Merkel | 0.689 | 0.479 |
| Putin | 0.919 | 0.762 |
| Trump | 0.867 | 0.658 |

### 4.5 Nearest-neighbour structure in English (primary model; last column = robustness model)

| leader | observed_share | expected_share | ratio_obs_exp | n_chunks | observed_share_robustness_model |
|---|---|---|---|---|---|
| Erdoğan | 0.832 | 0.212 | 3.929 | 63 | 0.598 |
| Macron | 0.891 | 0.238 | 3.742 | 75 | 0.713 |
| Merkel | 0.782 | 0.118 | 6.601 | 38 | 0.479 |
| Putin | 0.919 | 0.076 | 12.141 | 26 | 0.762 |
| Trump | 0.954 | 0.111 | 8.591 | 48 | 0.658 |

Full kNN matrix, primary model (row = chunk's leader, column = share of its 10 nearest neighbours from that leader):

|  | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 0.832 | 0.057 | 0.027 | 0.030 | 0.054 |
| Macron | 0.015 | 0.891 | 0.081 | 0.007 | 0.007 |
| Merkel | 0.029 | 0.142 | 0.782 | 0.018 | 0.029 |
| Putin | 0.042 | 0.027 | 0.012 | 0.919 | 0.000 |
| Trump | 0.023 | 0.008 | 0.002 | 0.013 | 0.954 |

### 4.6 Theme profiles — mean corpus percentile per theme (0.5 = corpus average)

| leader | speeches | chunks | National Identity & Unity | Security & Military | Economy & Welfare | Foreign Policy & Geopolitics | Democracy, Law & Institutions | Social Solidarity & Values | Crisis, Threat & Resilience | Future, Reform & Technology |
|---|---|---|---|---|---|---|---|---|---|---|
| Erdoğan | 5 | 63 | 0.46 | 0.50 | 0.45 | 0.56 | 0.58 | 0.35 | 0.47 | 0.46 |
| Macron | 4 | 75 | 0.46 | 0.44 | 0.55 | 0.48 | 0.49 | 0.50 | 0.53 | 0.69 |
| Merkel | 4 | 38 | 0.42 | 0.44 | 0.53 | 0.52 | 0.56 | 0.60 | 0.46 | 0.61 |
| Putin | 4 | 26 | 0.68 | 0.61 | 0.25 | 0.44 | 0.32 | 0.67 | 0.48 | 0.31 |
| Trump | 3 | 48 | 0.49 | 0.53 | 0.56 | 0.40 | 0.44 | 0.44 | 0.41 | 0.28 |

Three most represented themes per speech set (value, and share of 2000 speech-level bootstrap resamples keeping the theme in the top three):

| leader | #1 | #2 | #3 |
|---|---|---|---|
| Erdoğan | Democracy, Law & Institutions (0.58, top-3 in 69% of resamples) | Foreign Policy & Geopolitics (0.56, top-3 in 100% of resamples) | Security & Military (0.50, top-3 in 67% of resamples) |
| Macron | Future, Reform & Technology (0.69, top-3 in 100% of resamples) | Economy & Welfare (0.55, top-3 in 96% of resamples) | Crisis, Threat & Resilience (0.53, top-3 in 100% of resamples) |
| Merkel | Future, Reform & Technology (0.61, top-3 in 93% of resamples) | Social Solidarity & Values (0.60, top-3 in 99% of resamples) | Democracy, Law & Institutions (0.56, top-3 in 65% of resamples) |
| Putin | National Identity & Unity (0.68, top-3 in 100% of resamples) | Social Solidarity & Values (0.67, top-3 in 100% of resamples) | Security & Military (0.61, top-3 in 99% of resamples) |
| Trump | Economy & Welfare (0.56, top-3 in 100% of resamples) | Security & Military (0.53, top-3 in 96% of resamples) | National Identity & Unity (0.49, top-3 in 74% of resamples) |

Second opinion (zero-shot NLI classifier): top theme per leader = Erdoğan: National Identity & Unity; Macron: National Identity & Unity; Merkel: Social Solidarity & Values; Putin: Social Solidarity & Values; Trump: Social Solidarity & Values. Embedding and NLI pick the same top theme for 34% of chunks (chunk-level Spearman 0.16–0.58).

### 4.7 Rhetorical dimensions — mean corpus percentile, sorted within each dimension (95% bootstrap CI; share of resamples in which rank 1 holds)

**Conflict / Threat Framing** — Trump 0.54 [0.35–0.77]; Putin 0.51 [0.44–0.59]; Erdoğan 0.49 [0.34–0.65]; Merkel 0.49 [0.39–0.58]; Macron 0.44 [0.37–0.50] · rank 1 holds in 48% of resamples

**Cooperation / Solidarity Framing** — Merkel 0.61 [0.54–0.71]; Putin 0.56 [0.43–0.65]; Macron 0.47 [0.37–0.53]; Erdoğan 0.43 [0.27–0.61]; Trump 0.41 [0.15–0.68] · rank 1 holds in 66% of resamples

**Past Orientation** — Putin 0.62 [0.56–0.69]; Erdoğan 0.53 [0.38–0.64]; Macron 0.49 [0.42–0.55]; Trump 0.44 [0.28–0.53]; Merkel 0.38 [0.31–0.47] · rank 1 holds in 88% of resamples

**Future Orientation** — Macron 0.57 [0.55–0.59]; Putin 0.55 [0.44–0.65]; Erdoğan 0.52 [0.33–0.67]; Merkel 0.45 [0.38–0.53]; Trump 0.37 [0.22–0.59] · rank 1 holds in 45% of resamples

**Us-versus-Them Contrast** — Trump 0.65 [0.42–0.91]; Merkel 0.51 [0.41–0.60]; Putin 0.50 [0.41–0.57]; Erdoğan 0.46 [0.38–0.58]; Macron 0.39 [0.31–0.44] · rank 1 holds in 81% of resamples

**Gratitude & Recognition** — Putin 0.70 [0.66–0.74]; Trump 0.51 [0.25–0.67]; Merkel 0.44 [0.42–0.48]; Macron 0.44 [0.41–0.47]; Erdoğan 0.41 [0.28–0.50] · rank 1 holds in 100% of resamples

**Promises & Commitments** — Trump 0.59 [0.48–0.80]; Macron 0.57 [0.55–0.60]; Erdoğan 0.46 [0.32–0.57]; Merkel 0.43 [0.35–0.53]; Putin 0.31 [0.27–0.34] · rank 1 holds in 64% of resamples

Top-quartile rates (share of a leader's chunks in the corpus top quartile of each dimension):

| leader | Conflict / Threat Framing | Cooperation / Solidarity Framing | Past Orientation | Future Orientation | Us-versus-Them Contrast | Gratitude & Recognition | Promises & Commitments |
|---|---|---|---|---|---|---|---|
| Erdoğan | 0.22 | 0.22 | 0.32 | 0.37 | 0.13 | 0.12 | 0.22 |
| Macron | 0.20 | 0.17 | 0.23 | 0.30 | 0.13 | 0.20 | 0.34 |
| Merkel | 0.15 | 0.42 | 0.16 | 0.19 | 0.24 | 0.19 | 0.16 |
| Putin | 0.22 | 0.34 | 0.35 | 0.28 | 0.25 | 0.50 | 0.05 |
| Trump | 0.41 | 0.17 | 0.13 | 0.08 | 0.47 | 0.28 | 0.37 |

### 4.8 Emotional tone (classifier probabilities, leader means; family score = highest member-emotion probability per chunk)

| leader | n_speeches | fam_affiliative_positive | fam_threat_negative | fam_hostility | fam_cognitive_other | fam_neutral | valence | sent_positive | sent_neutral | sent_negative |
|---|---|---|---|---|---|---|---|---|---|---|
| Erdoğan | 5 | 0.387 | 0.035 | 0.014 | 0.158 | 0.301 | 0.418 | 0.538 | 0.343 | 0.120 |
| Macron | 4 | 0.455 | 0.027 | 0.011 | 0.190 | 0.176 | 0.461 | 0.563 | 0.334 | 0.102 |
| Merkel | 4 | 0.460 | 0.031 | 0.020 | 0.107 | 0.226 | 0.519 | 0.611 | 0.297 | 0.092 |
| Putin | 4 | 0.511 | 0.009 | 0.011 | 0.106 | 0.116 | 0.766 | 0.811 | 0.145 | 0.045 |
| Trump | 3 | 0.482 | 0.055 | 0.035 | 0.054 | 0.178 | 0.654 | 0.734 | 0.186 | 0.080 |

**Affiliative / positive emotion** — Putin 0.51 [0.47–0.55]; Trump 0.48 [0.38–0.61]; Merkel 0.46 [0.40–0.56]; Macron 0.46 [0.43–0.48]; Erdoğan 0.39 [0.29–0.50] · rank 1 holds in 58%

**Fear, sadness & loss** — Trump 0.05 [0.00–0.10]; Erdoğan 0.04 [0.01–0.06]; Merkel 0.03 [0.01–0.06]; Macron 0.03 [0.02–0.04]; Putin 0.01 [0.00–0.02] · rank 1 holds in 70%

**Hostility & disapproval** — Trump 0.03 [0.01–0.05]; Merkel 0.02 [0.01–0.04]; Erdoğan 0.01 [0.01–0.02]; Macron 0.01 [0.01–0.01]; Putin 0.01 [0.00–0.02] · rank 1 holds in 85%

**Sentiment valence (positive − negative)** — Putin 0.77 [0.56–0.91]; Trump 0.65 [0.43–0.88]; Merkel 0.52 [0.42–0.62]; Macron 0.46 [0.40–0.56]; Erdoğan 0.42 [0.21–0.63] · rank 1 holds in 79%

Most frequent non-neutral GoEmotions labels per leader (top 5): Erdoğan: approval 0.20, optimism 0.20, desire 0.13, gratitude 0.09, admiration 0.06 · Macron: optimism 0.22, approval 0.21, desire 0.16, gratitude 0.14, admiration 0.10 · Merkel: approval 0.24, optimism 0.19, gratitude 0.14, admiration 0.12, caring 0.07 · Putin: admiration 0.25, caring 0.22, optimism 0.22, approval 0.20, desire 0.10 · Trump: gratitude 0.28, approval 0.19, admiration 0.19, optimism 0.10, love 0.05

### 4.9 Composite style similarity (11 z-scored dimensions)

Cosine similarity of leader style profiles:

|  | Erdoğan | Macron | Merkel | Putin | Trump |
|---|---|---|---|---|---|
| Erdoğan | 1.00 | 0.42 | -0.21 | -0.53 | -0.32 |
| Macron | 0.42 | 1.00 | -0.20 | -0.43 | -0.42 |
| Merkel | -0.21 | -0.20 | 1.00 | -0.34 | 0.12 |
| Putin | -0.53 | -0.43 | -0.34 | 1.00 | -0.35 |
| Trump | -0.32 | -0.42 | 0.12 | -0.35 | 1.00 |

Pairs by style distance (Euclidean on z-scores; smaller = more alike), with bootstrap intervals and the share of resamples in which the pair is the closest:

| pair | style_distance | ci_low | ci_high | style_cosine | share_closest_pair |
|---|---|---|---|---|---|
| Erdoğan–Macron | 1.454 | 1.153 | 3.835 | 0.419 | 0.584 |
| Erdoğan–Merkel | 1.955 | 1.648 | 4.092 | -0.208 | 0.097 |
| Macron–Merkel | 2.073 | 1.649 | 3.533 | -0.198 | 0.288 |
| Merkel–Trump | 2.600 | 2.373 | 5.966 | 0.122 | 0.029 |
| Erdoğan–Trump | 3.081 | 2.866 | 6.289 | -0.319 | 0.002 |
| Merkel–Putin | 3.171 | 2.950 | 4.484 | -0.344 | 0.000 |
| Macron–Trump | 3.295 | 3.024 | 6.125 | -0.419 | 0.000 |
| Erdoğan–Putin | 3.360 | 2.639 | 5.602 | -0.530 | 0.001 |
| Macron–Putin | 3.375 | 3.277 | 4.017 | -0.426 | 0.001 |
| Putin–Trump | 4.068 | 3.836 | 6.606 | -0.350 | 0.000 |

Content similarity vs style similarity across the ten pairs: Spearman 0.21 — saying similar things and sounding alike are largely independent in this corpus.

Leader style profile (z-scores; positive = above the corpus mean of the 20 speeches):

| leader | conflict_threat_framing | cooperation_solidarity_framing | past_orientation | future_orientation | us_vs_them | gratitude_recognition | promises_commitments | affiliative_positive | threat_negative | hostility | valence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Erdoğan | -0.01 | -0.39 | 0.25 | 0.12 | -0.22 | -0.58 | -0.06 | -0.72 | 0.17 | -0.22 | -0.61 |
| Macron | -0.40 | -0.16 | -0.07 | 0.50 | -0.75 | -0.36 | 0.74 | 0.01 | -0.11 | -0.40 | -0.41 |
| Merkel | -0.04 | 0.68 | -0.86 | -0.33 | 0.12 | -0.35 | -0.23 | 0.06 | 0.02 | 0.19 | -0.15 |
| Putin | 0.14 | 0.39 | 0.94 | 0.33 | 0.07 | 1.36 | -1.10 | 0.61 | -0.77 | -0.43 | 0.98 |
| Trump | 0.41 | -0.55 | -0.44 | -0.86 | 1.11 | 0.10 | 0.87 | 0.29 | 0.86 | 1.22 | 0.47 |

### 4.10 Semantic concentration (cosine distances in the original space)

| leader | n_speeches | n_chunks | mean_dist_speech_to_leader | mean_dist_chunk_to_speech | mean_dist_chunk_to_leader |
|---|---|---|---|---|---|
| Erdoğan | 5 | 63 | 0.065 | 0.192 | 0.244 |
| Macron | 4 | 75 | 0.019 | 0.216 | 0.231 |
| Merkel | 4 | 38 | 0.029 | 0.204 | 0.227 |
| Putin | 4 | 26 | 0.026 | 0.131 | 0.154 |
| Trump | 3 | 48 | 0.040 | 0.177 | 0.210 |

### 4.11 Exploratory clustering (PCA 50 → HDBSCAN)

**Raw chunk vectors** (cluster −1 = unassigned noise):

| cluster | size | candidate label (from theme scores) | dominant leader | dominant share | mix entropy | share Erdoğan | share Macron | share Merkel | share Putin | share Trump | frequent terms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| -1 | 81 | (noise — not assigned) | Macron | 0.43 | 0.77 | 0.28 | 0.43 | 0.23 | 0.01 | 0.04 | state, order, better, ensure, federal, necessary, able, held, them, preparing, fully, accountable |
| 0 | 46 | National Identity & Unity / Security & Military | Trump | 0.98 | 0.07 | 0.02 | 0.00 | 0.00 | 0.00 | 0.98 | america, american, americans, administration, president, safe, world, people, across, back, nations, four |
| 1 | 6 | Democracy, Law & Institutions | Erdoğan | 1.00 | -0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | system, sisters, brothers, government, experiences, issue, presidential, multi, gone, constitutional, amendment, party |
| 2 | 25 | Social Solidarity & Values / National Identity & Unity | Putin | 1.00 | -0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | russia, friends, motherland, love, sincere, russian, parents, comrades, happy, always, special, future |
| 3 | 40 | Future, Reform & Technology | Macron | 1.00 | -0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | french, europe, ahead, build, compatriots, stronger, paralympic, olympic, games, pride, growth, live |
| 4 | 20 | Future, Reform & Technology / Social Solidarity & Values | Merkel | 0.95 | 0.12 | 0.05 | 0.00 | 0.95 | 0.00 | 0.00 | germany, well, union, work, values, together, change, future, fellow, stand, police, opportunity |
| 5 | 32 | Foreign Policy & Geopolitics / Economy & Welfare | Erdoğan | 1.00 | -0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | türkiye, goals, century, greet, humanity, calendar, region, feelings, willing, affection, period, economic |

**After subtracting each leader's centroid (leader-centred)** (cluster −1 = unassigned noise):

| cluster | size | candidate label (from theme scores) | dominant leader | dominant share | mix entropy | share Erdoğan | share Macron | share Merkel | share Putin | share Trump | frequent terms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| -1 | 46 | (noise — not assigned) | Macron | 0.37 | 0.93 | 0.15 | 0.37 | 0.09 | 0.17 | 0.22 | support, several, open, course, millions, hands, concern, true, common, first, marked, defending |
| 0 | 9 | National Identity & Unity / Future, Reform & Technology | Macron | 1.00 | -0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | paralympic, olympic, games, french, pride, dame, cathedral, sporting, promised, impossible, rebuilt, paris |
| 1 | 195 | Foreign Policy & Geopolitics / Economy & Welfare | Erdoğan | 0.29 | 0.96 | 0.29 | 0.25 | 0.17 | 0.09 | 0.20 | well, respect, dear, place, live, future, borders, long, jobs, everyone, strength, europe |

### 4.12 Robustness — every material change flagged by the checks

| check | comparison | metric | value | note |
|---|---|---|---|---|
| F | embedding vs NLI | leader_theme_spearman_erdogan | 0.0952 | 8 themes |
| F | embedding vs NLI | leader_theme_spearman_macron | -0.4524 | 8 themes |
| F | embedding vs NLI | leader_theme_spearman_merkel | -0.4048 | 8 themes |
| F | embedding vs NLI | leader_theme_spearman_trump | 0.0 | 8 themes |
| G | original languages vs English | leader_pair_similarity_spearman | -0.4303 | 10 pairs, same model |
| G | original languages vs English | most_similar_pair | putin–trump | macron–merkel | old | new |
| G | original languages vs English | erdogan_pairs_mean_rank | 8.5 → 4.2 | of 10 (1 = most similar) |
| G | original languages vs English | knn_same_leader_share_erdogan | 0.995 → 0.598 | old → new |
| G | original languages vs English | knn_same_leader_share_macron | 0.958 → 0.713 | old → new |
| G | original languages vs English | knn_same_leader_share_merkel | 0.689 → 0.479 | old → new |
| G | original languages vs English | knn_same_leader_share_putin | 0.919 → 0.762 | old → new |
| G | original languages vs English | knn_same_leader_share_trump | 0.867 → 0.658 | old → new |
| G | original languages vs English | theme_profile_spearman_erdogan | 0.2857 | 8 themes (old: language-matched descriptions; new: English) |

Check A (primary vs robustness model on the same English text): Spearman of the ten pair similarities = 0.83; in run 1 (mixed languages, Qwen3 vs BGE-M3) it was −0.37.

Check H (embedding-based rhetorical dimension vs classifier-based emotion, speech level, Spearman over 20 speeches):

| rhetorical | emotion | spearman_speech_level | n_speeches |
|---|---|---|---|
| conflict_threat_framing_pct | fam_hostility | 0.487 | 20 |
| conflict_threat_framing_pct | fam_threat_negative | 0.317 | 20 |
| cooperation_solidarity_framing_pct | fam_affiliative_positive | -0.113 | 20 |
| gratitude_recognition_pct | emo_gratitude | -0.107 | 20 |
| conflict_threat_framing_pct | valence | -0.165 | 20 |
| us_vs_them_pct | fam_hostility | 0.495 | 20 |
| future_orientation_pct | emo_optimism | 0.559 | 20 |

## 5. Figure catalogue (`outputs/plots/`)

Every figure exists as `<name>.png` (square 1080×1080, exported at 2160 px), `<name>_9x16.png` (vertical 1080×1920, exported at 2160×3840) and matching SVGs. Fixed colours: Erdoğan blue #2a78d6, Macron orange #eb6834, Merkel aqua #1baf7a, Putin yellow #eda100, Trump magenta #e87ba4. Vertical versions carry a text block under the chart with the key numbers.

| file | what it shows |
|---|---|
| `radar_<leader>` | Per-leader radar of the eight fixed themes (mean corpus percentile, 0.5 = corpus average); the vertical version adds the top-3 themes with bootstrap stability below the chart. |
| `radar_all_leaders` | All five theme profiles overlaid on the same radar; grey octagon = corpus average. |
| `rhetorical_radar_<leader>` | Per-leader radar of the seven rhetorical dimensions (conflict/threat, cooperation/solidarity, past, future, us-vs-them, gratitude, promises). |
| `rhetorical_radar_all_leaders` | All five rhetorical profiles overlaid; text block lists the highest-scoring leader per dimension. |
| `leader_similarity_heatmap` | 5×5 cosine similarity of leader centroids (primary model); vertical version adds the ten pairs sorted with 95% bootstrap intervals. |
| `umap_chunks` | UMAP projection of all chunks: colour and marker = leader, hollow markers = speech centres, one grey-background facet per leader. Visual only; no distances are read from it. |
| `pca_chunks` | Same layout as UMAP using the first two principal components. |
| `theme_comparison` | Eight small panels (one per theme), leaders sorted by mean percentile with 95% speech-level bootstrap whiskers; identical scale everywhere. |
| `top_themes_by_leader` | For each leader the three most represented themes with values and the share of bootstrap resamples that keep them in the top three. |
| `style_rankings` | Seven panels (one per rhetorical dimension), leaders sorted by measured value with bootstrap whiskers — the 'ranking' figure; overlapping whiskers mean no reliable difference. |
| `conflict_cooperation_comparison` | The two spec-required framing scales alone (conflict/threat vs cooperation/solidarity), same construction. |
| `emotion_profile` | Four panels: affiliative/positive emotion, fear-sadness-loss, hostility/disapproval (GoEmotions families) and sentiment valence; bars from the corpus mean with bootstrap whiskers. |
| `style_similarity_heatmap` | 5×5 cosine similarity of the z-scored style profiles; vertical version adds the ten pairs sorted by style distance with intervals. |
| `style_dendrogram` | Average-linkage hierarchical clustering of the five style profiles; lower joins = more alike. |
| `content_vs_style_scatter` | Ten leader pairs: x = content similarity (embedding centroids), y = style similarity (cosine of style profiles), with the Spearman correlation in the subtitle. |
| `semantic_dispersion` | Two panels: mean distance of speech centres to their leader centre, and of chunks to their speech centre — how concentrated each speech set is. |
| `language_effect` | Slope chart of the ten pair similarities under the same Qwen3 model, original languages (archived run) → English (this run), Erdoğan pairs highlighted; second panel: same-leader nearest-neighbour share before → after translation. |

Run 1's landscape figures (original-language corpus) are in `old_results/outputs/plots/` under the same names.

## 6. Candidate findings for the video (verbatim from `outputs/video_insights.md`)


Generated 2026-09-23 12:50 from the result tables · primary model KaLM-Embedding-Gemma3-12B-2511 · robustness model Qwen3-Embedding-8B. Every finding is about the collected speech corpus and its measurements. None measures ideology, political quality, personality, competence or morality; none is an endorsement.

**Global caution to state on camera:** Erdoğan, Macron and Merkel are analysed in English translation and Putin in an official English transcript; for them, style measurements describe the translated text and therefore also carry the translator's choices. The speeches come from different years and formats, and there are 3–5 per leader. Rankings are sorted measurements with confidence intervals; where intervals overlap, no difference should be claimed.

### Finding 1

**FINDING**  
Translating the corpus into English removed most of the language signal that dominated the first run: chunks stopped clustering by leader nearly as much, and Erdoğan's speeches moved from the edge of the space toward the middle.

**NUMBER**  
Same-leader share of a chunk's 10 nearest neighbours (same model, Qwen3-Embedding-8B): Erdoğan 100% → 60%, Macron 96% → 71%, Merkel 69% → 48%, Putin 92% → 76%, Trump 87% → 66%. Erdoğan's four leader pairs: mean rank 8.5 → 4.2 of 10. Rank correlation of the ten pair similarities between the two corpora: -0.43.

**TECHNICAL EXPLANATION**  
Both runs use identical chunking, aggregation and the same Qwen3-Embedding-8B model; only the text language changed (run 1 archived in old_results/). Language and speaker were confounded in run 1; translation separates them at the price of adding the translator's voice.

**VIDEO VERSION**  
"Konuşmaları İngilizceye çevirince tablo değişti: birinci turda Erdoğan'ın parçalarının komşuları yüzde 100 oranında yine Erdoğan'dı, şimdi yüzde 60. Model önce Türkçeyi görüyordu; şimdi içeriği görüyor."

**CAUTION**  
The English texts of Erdoğan, Macron, Merkel, Putin are translations or official transcripts; what remains is content plus translator style. Putin and Trump did not change between runs.

### Finding 2

**FINDING**  
Even in English, a chunk's nearest neighbours still come from the same leader far more often than chance — the speech sets keep a recognisable content signature, and how strong it looks depends on the model.

**NUMBER**  
Same-leader neighbour share (KaLM-Embedding-Gemma3-12B-2511): Erdoğan 83% (×3.9 vs chance), Macron 89% (×3.7 vs chance), Merkel 78% (×6.6 vs chance), Putin 92% (×12.1 vs chance), Trump 95% (×8.6 vs chance); range 78%–95% against a chance level of 8%–24%. Same text with Qwen3-Embedding-8B: 48%–76%.

**TECHNICAL EXPLANATION**  
kNN (k=10) on 250 unit-normalised vectors, excluding chunks of the same speech; expected share = the leader's share of the remaining chunks. KaLM-Embedding-Gemma3-12B-2511 separates the speech sets more sharply than Qwen3-Embedding-8B does on identical English text.

**VIDEO VERSION**  
"İngilizcede bile bir parçanın en yakın komşuları yüzde 78 ile 95 arasında aynı liderin diğer konuşmalarından geliyor; rastgele olsa bu oran yüzde 8 ile 24 arasında olurdu. İkinci modelde aynı oran yüzde 48 ile 76."

**CAUTION**  
A signature of the collected speech sets (topics, recurring occasions such as New Year addresses, translator style), not a fingerprint of the person; the strength of the signature is model-dependent.

### Finding 3

**FINDING**  
The two speech sets whose centroids sit closest in the KaLM-Embedding-Gemma3-12B-2511 space are Macron–Merkel.

**NUMBER**  
Cosine similarity 0.850 (95% speech-level bootstrap 0.811–0.860); closest pair in 100% of 2000 resamples; rank 1 of 10 under Qwen3-Embedding-8B.

**TECHNICAL EXPLANATION**  
Chunk vectors → normalised speech centroids → normalised leader centroids (equal weight per speech). Agreement between two different embedding models on the same English text is the main robustness test now that language is out of the picture.

**VIDEO VERSION**  
"Yeni modelde en yakın iki konuşma seti Macron–Merkel: kosinüs benzerliği 0.85. İkinci model aynı çifti 1. sıraya koyuyor."

**CAUTION**  
Semantic similarity of the collected speeches, not ideological or personal similarity.

### Finding 4

**FINDING**  
The most distant pair is Putin–Trump; the two models now agree about the overall ordering of the ten pairs.

**NUMBER**  
Putin–Trump: 0.701 (rank 10 of 10 under Qwen3-Embedding-8B). Spearman between the models' pair rankings: 0.83 (run 1, mixed languages: −0.37).

**TECHNICAL EXPLANATION**  
Same chunks, same aggregation, two models (3840-d vs 4096-d). Absolute cosine levels are model-specific; only rankings are compared.

**VIDEO VERSION**  
"En uzak çift Putin–Trump. İki modelin sıralamaları arasındaki korelasyon birinci turda eksi 0.37'ydi, İngilizce metinde 0.83."

**CAUTION**  
With five leaders there are only ten pairs; a rank correlation over ten points is itself uncertain.

### Finding 5

**FINDING**  
The three most represented themes in each collected speech set.

**NUMBER**  
Erdoğan: Democracy, Law & Institutions (0.58, top-3 in 69%); Foreign Policy & Geopolitics (0.56, top-3 in 100%); Security & Military (0.50, top-3 in 67%)  
Macron: Future, Reform & Technology (0.69, top-3 in 100%); Economy & Welfare (0.55, top-3 in 96%); Crisis, Threat & Resilience (0.53, top-3 in 100%)  
Merkel: Future, Reform & Technology (0.61, top-3 in 93%); Social Solidarity & Values (0.60, top-3 in 99%); Democracy, Law & Institutions (0.56, top-3 in 65%)  
Putin: National Identity & Unity (0.68, top-3 in 100%); Social Solidarity & Values (0.67, top-3 in 100%); Security & Military (0.61, top-3 in 99%)  
Trump: Economy & Welfare (0.56, top-3 in 100%); Security & Military (0.53, top-3 in 96%); National Identity & Unity (0.49, top-3 in 74%)  
Values: mean percentile of chunk–theme similarity over the whole corpus (0.5 = corpus average).

**TECHNICAL EXPLANATION**  
Each chunk is compared with eight fixed theme descriptions using the same embedding model; percentiles over all chunks, averaged per speech, then per leader.

**VIDEO VERSION**  
"Her konuşma setinde en çok yer alan tema: Erdoğan için demokrasi, hukuk ve kurumlar, Macron için gelecek, reform ve teknoloji, Merkel için gelecek, reform ve teknoloji, Putin için ulusal kimlik ve birlik, Trump için ekonomi ve refah. İlk üçün tamamı ve güven aralıkları grafikte."

**CAUTION**  
Which themes the collected speeches lean towards relative to this corpus; not why. The NLI classifier ranks themes differently (see the agreement finding).

### Finding 6

**FINDING**  
The most stable theme signal is Future, Reform & Technology in the Macron speeches.

**NUMBER**  
Mean percentile 0.69; top theme of that leader in 100% of 2000 speech-level resamples.

**TECHNICAL EXPLANATION**  
The bootstrap redraws speeches with replacement within each leader and recomputes the profile; a theme that stays on top does not hinge on one speech.

**VIDEO VERSION**  
"En sağlam tema sinyali Macron konuşmalarındaki 'Gelecek, Reform ve Teknoloji': 2000 yeniden örneklemede yüzde 100 oranında birinci."

**CAUTION**  
Stability within this corpus is not generalisation beyond it.

### Finding 7

**FINDING**  
Seven rhetorical dimensions, ranked by measured value (sorted measurements, not a verdict).

**NUMBER**  
Conflict / Threat Framing: Trump 0.54 > Putin 0.51 > Erdoğan 0.49 > Merkel 0.49 > Macron 0.44 — first place holds in 48% of resamples; intervals of 1st and 2nd overlap  
Cooperation / Solidarity Framing: Merkel 0.61 > Putin 0.56 > Macron 0.47 > Erdoğan 0.43 > Trump 0.41 — first place holds in 66% of resamples; intervals of 1st and 2nd overlap  
Past Orientation: Putin 0.62 > Erdoğan 0.53 > Macron 0.49 > Trump 0.44 > Merkel 0.38 — first place holds in 88% of resamples; intervals of 1st and 2nd overlap  
Future Orientation: Macron 0.57 > Putin 0.55 > Erdoğan 0.52 > Merkel 0.45 > Trump 0.37 — first place holds in 45% of resamples; intervals of 1st and 2nd overlap  
Us-versus-Them Contrast: Trump 0.65 > Merkel 0.51 > Putin 0.50 > Erdoğan 0.46 > Macron 0.39 — first place holds in 81% of resamples; intervals of 1st and 2nd overlap  
Gratitude & Recognition: Putin 0.70 > Trump 0.51 > Merkel 0.44 > Macron 0.44 > Erdoğan 0.41 — first place holds in 100% of resamples; intervals of 1st and 2nd overlap  
Promises & Commitments: Trump 0.59 > Macron 0.57 > Erdoğan 0.46 > Merkel 0.43 > Putin 0.31 — first place holds in 64% of resamples; intervals of 1st and 2nd overlap

**TECHNICAL EXPLANATION**  
Each dimension is a written description embedded with the same model; a chunk's score is its cosine similarity, expressed as a corpus percentile; speech means → leader means; 95% speech-level bootstrap intervals and the share of resamples in which the first-ranked leader stays first.

**VIDEO VERSION**  
"Yedi retorik ölçekte ilk sıralar: çatışma / tehdit çerçevesi ölçeğinde Trump, i̇ş birliği / dayanışma çerçevesi ölçeğinde Merkel, geçmişe yönelim ölçeğinde Putin, geleceğe yönelim ölçeğinde Macron, biz-onlar karşıtlığı ölçeğinde Trump, teşekkür ve takdir ölçeğinde Putin, vaatler ve taahhütler ölçeğinde Trump. Ama çoğu farkın güven aralığı örtüşüyor; bunlar sıralı ölçümler, hüküm değil."

**CAUTION**  
Descriptive similarity to a description, in one model, on 20 speeches. Translated leaders (Erdoğan, Macron, Merkel, Putin) carry the translator's phrasing.

### Finding 8

**FINDING**  
Emotional tone, measured by an independent classifier rather than by embeddings.

**NUMBER**  
Affiliative / positive emotion: Putin 0.51 [0.47–0.55], Trump 0.48 [0.38–0.61], Merkel 0.46 [0.40–0.56], Macron 0.46 [0.43–0.48], Erdoğan 0.39 [0.29–0.50]  
Fear, sadness & loss: Trump 0.05 [0.00–0.10], Erdoğan 0.04 [0.01–0.06], Merkel 0.03 [0.01–0.06], Macron 0.03 [0.02–0.04], Putin 0.01 [0.00–0.02]  
Hostility & disapproval: Trump 0.03 [0.01–0.05], Merkel 0.02 [0.01–0.04], Erdoğan 0.01 [0.01–0.02], Macron 0.01 [0.01–0.01], Putin 0.01 [0.00–0.02]  
Sentiment valence (positive − negative): Putin 0.77 [0.56–0.91], Trump 0.65 [0.43–0.88], Merkel 0.52 [0.42–0.62], Macron 0.46 [0.40–0.56], Erdoğan 0.42 [0.21–0.63] Most frequent non-neutral emotion labels: Erdoğan: approval, optimism; Macron: optimism, approval; Merkel: approval, optimism; Putin: admiration, caring; Trump: gratitude, approval

**TECHNICAL EXPLANATION**  
GoEmotions (28 labels, multi-label) grouped into families (family score = highest member probability per chunk) plus a three-class sentiment model (valence = P(positive) − P(negative)); chunk → speech → leader means; 95% speech-level bootstrap.

**VIDEO VERSION**  
"Duygu tonunu embedding'den bağımsız bir sınıflandırıcıyla ölçtük: olumlu-birleştirici duygu, korku-kayıp ve düşmanlık aileleri artı genel duygu değeri. Sonuçlar grafikte, aralıklarıyla."

**CAUTION**  
Classifiers trained on Reddit and Twitter text; political speech is out of domain, and translated leaders are scored on the translation.

### Finding 9

**FINDING**  
On the combined style profile, the two most alike speech sets are Erdoğan–Macron; the least alike are Putin–Trump.

**NUMBER**  
Style distance 1.45 [1.15–3.84], closest pair in 58% of resamples; farthest 4.07. Spearman between content similarity and style similarity over the ten pairs: 0.21.

**TECHNICAL EXPLANATION**  
Style vector per speech = 7 rhetorical percentiles + 3 emotion family means + valence, z-scored across the 20 speeches; leader = mean of its speeches; Euclidean distance and cosine; average-linkage dendrogram.

**VIDEO VERSION**  
"Retorik ve duygu profillerini birleştirince birbirine en çok benzeyen iki set Erdoğan–Macron, en az benzeyen Putin–Trump. İçerik benzerliğiyle stil benzerliği arasındaki korelasyon 0.21."

**CAUTION**  
Style here means these eleven measured dimensions of the English text, nothing more; it is not delivery, voice or charisma.

### Finding 10

**FINDING**  
The speech sets differ in how concentrated they are around their own centre.

**NUMBER**  
Mean cosine distance of speech centroids to the leader centroid: Erdoğan 0.065, Macron 0.019, Merkel 0.029, Putin 0.026, Trump 0.040. Within speeches (chunk → speech centroid): Erdoğan 0.192, Macron 0.216, Merkel 0.204, Putin 0.131, Trump 0.177.

**TECHNICAL EXPLANATION**  
Distances in the original 3840-d space. Speech-type mix (one Erdoğan symposium speech among New Year messages; three different Trump formats) and speech length both affect these numbers.

**VIDEO VERSION**  
"Macron konuşmaları kendi merkezine en yakın (0.019), Erdoğan en dağınık (0.065). Bu tutarlılık değil, derlemin çeşitliliği."

**CAUTION**  
Semantic concentration of the collected files; not 'consistency' of a person.

### Finding 11

**FINDING**  
Unsupervised clustering of the English chunks: how much of the structure is still 'who is speaking' and how much is topic.

**NUMBER**  
HDBSCAN on the raw vectors: 6 clusters; single-leader share of the dominant leader per cluster 95%–100%; 32% unassigned. After subtracting each leader's centroid: 2 clusters, 1 mixed (entropy ≥ 0.75), e.g. 'Foreign Policy & Geopolitics / Economy & Welfare' (195 chunks, 5 leaders).

**TECHNICAL EXPLANATION**  
PCA(50) → HDBSCAN; candidate labels from the fixed-theme scores of the member chunks; leader-centering removes each leader's mean vector so that only within-corpus variation remains.

**VIDEO VERSION**  
"Denetimsiz kümeleme İngilizce metinde bile büyük ölçüde liderleri buluyor; her liderin ortalamasını çıkarınca ekonomi, dış politika, kriz gibi ortak konu kümeleri kalıyor."

**CAUTION**  
Cluster membership depends on parameters (see the grid table); labels are neutral topical candidates.

### Finding 12

**FINDING**  
Independent methods agree only partly, which is why every style number is reported with its method attached.

**NUMBER**  
Embedding vs NLI theme scoring: same top theme for 34% of chunks; chunk-level Spearman 0.16–0.58. Speech-level Spearman between conflict framing (embedding) and the hostility family (classifier): 0.49; cooperation framing vs affiliative emotion: -0.11.

**TECHNICAL EXPLANATION**  
Option A = cosine to descriptions (embedding); Option B = multilingual zero-shot NLI; emotion = supervised classifier. Moderate correlations mean the constructs overlap but are not the same measurement.

**VIDEO VERSION**  
"Aynı şeyi iki yöntemle ölçtüğümüzde parça düzeyinde sadece yüzde 34 aynı birinci temayı buluyoruz. Bu yüzden her sayının yanında yöntemi de söylüyoruz."

**CAUTION**  
Method dependence is a property of the measurements, not a flaw of any speaker.

### Finding 13

**FINDING**  
The whole experiment runs on a small, fully traceable corpus and a single consumer GPU.

**NUMBER**  
20 speeches, 23,905 cleaned English words → 250 chunks (median 107 tokens) → 3840-d vectors from an 11.8B-parameter model (KaLM-Embedding-Gemma3-12B-2511); embedding took 6.8 s at 22.83 GB peak VRAM on an RTX 5090; 2000 speech-level bootstrap resamples for every interval.

**TECHNICAL EXPLANATION**  
Paragraph-based chunking (80–180 tokens, no overlap), unit-normalised embeddings, chunk → speech → leader aggregation, two embedding models, two classifiers, archived first run for the language comparison.

**VIDEO VERSION**  
"Tüm deney 20 konuşma, 250 parça ve 3840 boyutlu vektör; 12 milyar parametreli model hepsini 7 saniyede gömdü, tek bir ekran kartında."

**CAUTION**  
3–5 speeches per leader, mostly New Year addresses from different years; every number is a statement about these files.


## 7. What the data can and cannot support

**Supported by the measurements**
- Language dominated the first analysis; translation removed most of that signal (same-model comparison, section 4.4). This is the cleanest methodological story in the project.
- Even in English, chunks of the same speech set stay close to each other far more than chance (section 4.5) — the sets have a recognisable content signature, whose strength depends on the model.
- Theme profiles, rhetorical dimensions and emotional tone can be reported per leader as sorted measurements with intervals (sections 4.6–4.8). Several first places are stable across bootstrap resamples (e.g. gratitude/recognition and past orientation for the Putin set, us-versus-them for the Trump set, future orientation and reform/technology for the Macron set); many others are not, and their intervals overlap.
- Content similarity and style similarity are nearly unrelated in this corpus (section 4.9): sets that discuss similar things do not necessarily sound alike.
- Two embedding models agree on the pair ordering in English but did not on the mixed-language corpus (section 4.12).

**Not supported / must not be claimed**
- Anything about the people: ideology, sincerity, competence, aggression, honesty, character. The measurements describe collected texts, several of them translations, most of them a single genre (New Year addresses), 3–5 per leader.
- Causal explanations of why a theme or tone appears (occasion, year, speechwriter, translator and genre are all confounded).
- Fine-grained rankings where the 95% intervals overlap — which is most of them. The safe phrasing is "in these speeches, X measured highest on Y, and the interval is wide/narrow".
- Generalisation beyond this corpus: stability across bootstrap resamples of the same speeches is not stability across a leader's other speeches.
- Emotion-classifier absolutes: the classifiers were trained on Reddit/Twitter text and see translated speech; treat them as relative, method-dependent signals.

## 8. Files to look at

`outputs/video_insights.md` (findings with Turkish spoken lines and cautions) · `outputs/methodology_for_video.md` (Turkish explanations of embeddings, chunks, cosine, centroids, translation, bootstrap, UMAP) · `outputs/results_summary.md` (tables index) · `outputs/robustness_report.md` · `outputs/clusters_report*.md` · `outputs/phase0_report.md` · `data/processed/preprocessing_report.md` · `old_results/README.md` (run 1) · `README.md` (how to run) · `config.yaml` (every parameter and every theme/dimension description).
