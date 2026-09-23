# Phase 0 — Corpus Inventory Report

Generated: 2026-09-23 12:31 · input: `C:\Users\EKutlu\Desktop\RAG\politics\data\original` · config: `config.yaml`  
Token counting: `hf_tokenizer:Qwen/Qwen3-Embedding-8B`  

> Scope: this report describes the *collected speech files* only. It makes no claim about the speakers.

## 1. Speeches per leader

| leader | expected_lang | files | with_text | empty | words | mean_words | est_chunks | detected_langs | status |
|---|---|---|---|---|---|---|---|---|---|
| Recep Tayyip Erdoğan | en | 5 | 5 | 0 | 5241 | 1048 | 63 | en×5 | OK |
| Emmanuel Macron | en | 4 | 4 | 0 | 7935 | 1984 | 75 | en×4 | OK |
| Angela Merkel | en | 4 | 4 | 0 | 3672 | 918 | 38 | en×4 | OK |
| Vladimir Putin | en | 4 | 4 | 0 | 2517 | 629 | 27 | en×4 | OK |
| Donald Trump | en | 3 | 3 | 0 | 4721 | 1574 | 50 | en×3 | OK |

Total: **20 files**, 20 with text, 0 empty · **24,086 words** · **253 estimated chunks**.

## 2. Language distribution (files with text)

| language | files |
|---|---|
| en | 20 |

Language mismatches: none.

_Detection is a stopword-ratio heuristic meant to catch the wrong language in the wrong folder, not a linguistic classifier._

## 3. Word counts per speech

| leader | filename | word_count | paragraph_count | token_count | estimated_chunk_count | language_detected | speech_date | speech_type |
|---|---|---|---|---|---|---|---|---|
| erdogan | erdogan1.txt | 904 | 25 | 1064 | 10 | en |  | symposium_speech |
| erdogan | erdogan2022.txt | 1098 | 52 | 1359 | 13 | en | 2022-12-31 | new_year_message |
| erdogan | erdogan2023.txt | 1102 | 50 | 1317 | 14 | en | 2023-12-31 | new_year_message |
| erdogan | erdogan2024.txt | 931 | 41 | 1138 | 12 | en | 2024-12-31 | new_year_message |
| erdogan | erdogan2025.txt | 1206 | 48 | 1473 | 14 | en | 2025-12-31 | new_year_message |
| macron | macron2022.txt | 2945 | 55 | 3421 | 27 | en | 2022-12-31 | new_year_address |
| macron | macron2023.txt | 1933 | 37 | 2377 | 19 | en | 2023-12-31 | new_year_address |
| macron | macron2024.txt | 1606 | 44 | 1959 | 16 | en | 2024-12-31 | new_year_address |
| macron | macron2025.txt | 1451 | 20 | 1708 | 13 | en | 2025-12-31 | new_year_address |
| merkel | merkel1.txt | 987 | 28 | 1149 | 10 | en | 2016-12-31 | new_year_address |
| merkel | merkel2.txt | 868 | 27 | 1011 | 10 | en | 2017-12-31 | new_year_address |
| merkel | merkel2020.txt | 936 | 17 | 1094 | 9 | en | 2019-12-31 | new_year_address |
| merkel | merkel3.txt | 881 | 21 | 1004 | 9 | en | 2018-12-31 | new_year_address |
| putin | putin2022.txt | 1123 | 31 | 1337 | 11 | en | 2022-12-31 | new_year_address |
| putin | putin2023.txt | 496 | 17 | 589 | 6 | en | 2023-12-31 | new_year_address |
| putin | putin2024.txt | 435 | 12 | 536 | 5 | en | 2024-12-31 | new_year_address |
| putin | putin2025.txt | 463 | 15 | 558 | 5 | en | 2025-12-31 | new_year_address |
| trump | trump1.txt | 2782 | 57 | 3269 | 28 | en | 2021-01-19 | farewell_address |
| trump | trump2.txt | 323 | 7 | 409 | 3 | en |  | composite_excerpts |
| trump | trump3.txt | 1616 | 84 | 1901 | 19 | en | 2017-01-20 | inaugural_address |

## 4. Suspicious files and flags

| filename | leader | flag | detail |
|---|---|---|---|
| erdogan1.txt | erdogan | missing_metadata | speech_date, source |
| erdogan1.txt | erdogan | review:verify | Not a New Year message: a speech at a SETA symposium held 'on the eve of the historic decision' on the presidential system (likely early 2017). Source text look |
| erdogan1.txt | erdogan | speech_type_outlier | 'symposium_speech' vs leader majority 'new_year_message' |
| erdogan1.txt | erdogan | third_person_narration | 1 sentence(s) narrate the speaker in third person |
| erdogan2022.txt | erdogan | missing_metadata | source |
| erdogan2023.txt | erdogan | missing_metadata | source |
| erdogan2024.txt | erdogan | missing_metadata | source |
| erdogan2025.txt | erdogan | missing_metadata | source |
| macron2022.txt | macron | missing_metadata | source |
| macron2023.txt | macron | missing_metadata | source |
| macron2024.txt | macron | missing_metadata | source |
| macron2025.txt | macron | missing_metadata | source |
| merkel1.txt | merkel | missing_metadata | source |
| merkel2.txt | merkel | missing_metadata | source |
| merkel2020.txt | merkel | filename_year_vs_speech_date | filename says 2020, speech_date is 2019-12-31 |
| merkel2020.txt | merkel | missing_metadata | source |
| merkel3.txt | merkel | missing_metadata | source |
| putin2022.txt | putin | missing_metadata | source |
| putin2022.txt | putin | truncated_start | text begins 'resident of Russia Vladimir Pu' |
| putin2023.txt | putin | missing_metadata | source |
| putin2023.txt | putin | speaker_label_prefix | 1 label(s), first: 'President of Russia Vladimir Putin' |
| putin2024.txt | putin | missing_metadata | source |
| putin2024.txt | putin | speaker_label_prefix | 1 label(s), first: 'President of Russia Vladimir Putin' |
| putin2025.txt | putin | missing_metadata | source |
| putin2025.txt | putin | speaker_label_prefix | 1 label(s), first: 'President of Russia Vladimir Putin' |
| trump1.txt | trump | missing_metadata | source |
| trump1.txt | trump | mixed_speech_types | trump has no dominant speech type: farewell_address×1, composite_excerpts×1, inaugural_address×1 |
| trump2.txt | trump | missing_metadata | speech_date, source |
| trump2.txt | trump | mixed_speech_types | trump has no dominant speech type: farewell_address×1, composite_excerpts×1, inaugural_address×1 |
| trump2.txt | trump | review:exclude_candidate | NOT a single speech: ~320 words stitched from several occasions (Gorsuch nomination Jan 2017, MS-13 remarks, a disaster-visit remark, space-policy lines). Kept  |
| trump2.txt | trump | very_short | 323 words < 400 |
| trump3.txt | trump | missing_metadata | source |
| trump3.txt | trump | mixed_speech_types | trump has no dominant speech type: farewell_address×1, composite_excerpts×1, inaugural_address×1 |

Flag counts: `missing_metadata`×20, `speaker_label_prefix`×3, `mixed_speech_types`×3, `third_person_narration`×1, `review:verify`×1, `speech_type_outlier`×1, `filename_year_vs_speech_date`×1, `truncated_start`×1, `very_short`×1, `review:exclude_candidate`×1

_Nothing was modified or removed. Flags are proposals for Phase 1 (preprocessing) and for the collector._

## 5. Proposed chunking

Parameters: min 80 · max 180 · target ≈130 tokens · no overlap · paragraph boundaries preferred, over-long paragraphs split at sentence ends, short orphans merged with a neighbour.

Estimates below run the *same* `chunk_paragraphs` function Phase 1 will use, with token counts from `hf_tokenizer:Qwen/Qwen3-Embedding-8B`.

| leader | filename | paragraph_count | token_count | estimated_chunk_count | short_chunks | mean_chunk_tokens |
|---|---|---|---|---|---|---|
| erdogan | erdogan1.txt | 25 | 1064 | 10 | 0 | 106.4 |
| erdogan | erdogan2022.txt | 52 | 1359 | 13 | 0 | 104.5 |
| erdogan | erdogan2023.txt | 50 | 1317 | 14 | 0 | 94.1 |
| erdogan | erdogan2024.txt | 41 | 1138 | 12 | 0 | 94.8 |
| erdogan | erdogan2025.txt | 48 | 1473 | 14 | 0 | 105.2 |
| macron | macron2022.txt | 55 | 3421 | 27 | 0 | 126.7 |
| macron | macron2023.txt | 37 | 2377 | 19 | 0 | 125.1 |
| macron | macron2024.txt | 44 | 1959 | 16 | 0 | 122.4 |
| macron | macron2025.txt | 20 | 1708 | 13 | 1 | 131.4 |
| merkel | merkel1.txt | 28 | 1149 | 10 | 0 | 114.9 |
| merkel | merkel2.txt | 27 | 1011 | 10 | 0 | 101.1 |
| merkel | merkel2020.txt | 17 | 1094 | 9 | 0 | 121.6 |
| merkel | merkel3.txt | 21 | 1004 | 9 | 0 | 111.6 |
| putin | putin2022.txt | 31 | 1337 | 11 | 0 | 121.5 |
| putin | putin2023.txt | 17 | 589 | 6 | 0 | 98.2 |
| putin | putin2024.txt | 12 | 536 | 5 | 0 | 107.2 |
| putin | putin2025.txt | 15 | 558 | 5 | 0 | 111.6 |
| trump | trump1.txt | 57 | 3269 | 28 | 0 | 116.8 |
| trump | trump2.txt | 7 | 409 | 3 | 0 | 136.3 |
| trump | trump3.txt | 84 | 1901 | 19 | 0 | 100.1 |

Chunks per leader: Erdoğan 63, Macron 75, Merkel 38, Putin 27, Trump 50

## 6. Metadata verification (`data/metadata.csv`)

| leader | filename | speech_date | date_confidence | speech_type | source | title | missing_metadata |
|---|---|---|---|---|---|---|---|
| erdogan | erdogan1.txt |  | unknown | symposium_speech | — | SETA symposium speech on the presidential system | speech_date;source |
| erdogan | erdogan2022.txt | 2022-12-31 | inferred_from_text | new_year_message | — | New Year message 2022/23 | source |
| erdogan | erdogan2023.txt | 2023-12-31 | inferred_from_text | new_year_message | — | New Year message 2023/24 | source |
| erdogan | erdogan2024.txt | 2024-12-31 | inferred_from_text | new_year_message | — | New Year message 2024/25 | source |
| erdogan | erdogan2025.txt | 2025-12-31 | inferred_from_text | new_year_message | — | New Year message 2025/26 | source |
| macron | macron2022.txt | 2022-12-31 | inferred_from_text | new_year_address | — | Vœux aux Français 2023 | source |
| macron | macron2023.txt | 2023-12-31 | inferred_from_text | new_year_address | — | Vœux aux Français 2024 | source |
| macron | macron2024.txt | 2024-12-31 | inferred_from_text | new_year_address | — | Vœux aux Français 2025 | source |
| macron | macron2025.txt | 2025-12-31 | inferred_from_text | new_year_address | — | Vœux aux Français 2026 | source |
| merkel | merkel1.txt | 2016-12-31 | inferred_from_text | new_year_address | — | Neujahrsansprache 2017 | source |
| merkel | merkel2.txt | 2017-12-31 | inferred_from_text | new_year_address | — | Neujahrsansprache 2018 | source |
| merkel | merkel2020.txt | 2019-12-31 | inferred_from_text | new_year_address | — | Neujahrsansprache 2020 | source |
| merkel | merkel3.txt | 2018-12-31 | inferred_from_text | new_year_address | — | Neujahrsansprache 2019 | source |
| putin | putin2022.txt | 2022-12-31 | inferred_from_text | new_year_address | — | New Year address 2023 | source |
| putin | putin2023.txt | 2023-12-31 | inferred_from_text | new_year_address | — | New Year address 2024 | source |
| putin | putin2024.txt | 2024-12-31 | inferred_from_text | new_year_address | — | New Year address 2025 | source |
| putin | putin2025.txt | 2025-12-31 | inferred_from_text | new_year_address | — | New Year address 2026 | source |
| trump | trump1.txt | 2021-01-19 | inferred_from_text | farewell_address | — | Farewell address | source |
| trump | trump2.txt |  | unknown | composite_excerpts | — | Compilation of short excerpts | speech_date;source |
| trump | trump3.txt | 2017-01-20 | inferred_from_text | inaugural_address | — | Inaugural address 2017 | source |

Date confidence: `inferred_from_text`×18, `unknown`×2

**20 of 20 files have no `source`.** Please add the URL/origin of each transcript; it is required for traceability in the video.

### Collector review items (from `metadata.csv`)

- **`erdogan1.txt`** — `verify`: Not a New Year message: a speech at a SETA symposium held 'on the eve of the historic decision' on the presidential system (likely early 2017). Source text looked like an automatic transcript; the translation smooths it. Confirm date/source.
- **`trump2.txt`** — `exclude_candidate`: NOT a single speech: ~320 words stitched from several occasions (Gorsuch nomination Jan 2017, MS-13 remarks, a disaster-visit remark, space-policy lines). Kept in the corpus at the collector's request; robustness check E reports its effect.

## 7. What Phase 1 (preprocessing) would clean — proposals only

- **speaker_label_prefix** → strip the leading speaker label (e.g. `President of Russia Vladimir Putin:`); log the removed text  
  files: `putin2023.txt`, `putin2024.txt`, `putin2025.txt`
- **truncated_start** → first word is truncated — sits inside the speaker label, so it disappears with it; otherwise fix the source file  
  files: `putin2022.txt`
- **third_person_narration** → review manually — news commentary around the transcript must be cut  
  files: `erdogan1.txt`

All removals will be written to `data/processed/preprocessing_report.md`; original files are never edited.

## 8. Readiness for Phase 1

**Decision needed — exclude candidates:** `trump2.txt`. If excluded, re-check the per-leader minimum above.

No hard blockers. Review the warnings and decisions above, then Phase 1 can run.

Corpus caveats to repeat in the video: speeches differ in year and format; leaders have unequal speech counts; Putin and Trump are English (Putin via official English transcript) while the others are in the original language. Every later result is a statement about *this* corpus.
