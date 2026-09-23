# old_results — first full run on the ORIGINAL-LANGUAGE corpus (archived 2026-09-23)

This folder freezes the complete output of the first analysis, produced on 2026-09-22 at commit `d192094`:

- corpus: 20 speeches in their original languages (Erdoğan tr, Macron fr, Merkel de, Putin en transcript, Trump en)
- primary embedding model `Qwen/Qwen3-Embedding-8B`, robustness model `BAAI/bge-m3`
- theme scoring against language-matched descriptions; all plots in landscape format

Contents

| path | what |
|---|---|
| `outputs/plots/` | the 13 landscape figures (PNG + SVG) |
| `outputs/tables/` | every result table (leader similarity, kNN, themes, framing, bootstrap, robustness, clusters) |
| `outputs/*.md` | phase0_report, video_insights, methodology_for_video, results_summary, robustness_report, clusters_report(s) |
| `data_processed/` | speeches_clean.csv, chunks.csv, chunks_noceremonial.csv, preprocessing_report.md for the original-language texts |
| `artifacts/` | embeddings (`*.npy`/`*.parquet`, git-ignored but kept on disk), cluster labels, bootstrap draws, run JSONs |
| `config_original_language.yaml` | the exact configuration of that run |

Headline of that run: language dominated the geometry (69–100% of a chunk's nearest neighbours came from the same
leader, i.e. the same language), and the leader-pair ranking was not stable across embedding models.

The original-language speech texts themselves are no longer in `data/original/` (the user replaced them with
English translations on 2026-09-23). They remain in git history:

    git show d192094:data/original/erdogan/erdogan2022.txt

The current run (repository root) uses the English corpus, `tencent/KaLM-Embedding-Gemma3-12B-2511` as primary
model and `Qwen/Qwen3-Embedding-8B` as robustness model; its robustness report compares Qwen3 results here
(original languages) with Qwen3 results on the English corpus to quantify the language effect.
