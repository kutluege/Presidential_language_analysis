# political-speech-geometry

A small, reproducible NLP experiment on the *content and semantic geometry* of a collected corpus of
public speeches by five political leaders (Erdoğan, Macron, Merkel, Putin, Trump), built for an
explainer video.

**What this project is not.** It does not evaluate, rank, endorse or criticise anyone. Every number it
produces describes *the collected speech files*: their themes, how semantically close the corpora sit in
an embedding space, and how concentrated each corpus is. None of that measures ideology, personality,
competence or political similarity between people. Speeches differ in year and format, and the corpus is
mixed-language (tr / fr / de / en), so all findings are corpus-level statements with stated uncertainty.

## Layout

```
config.yaml            every parameter, model id, theme definition (single source of truth)
requirements.txt       pinned versions from the working environment
data/original/<leader>/    raw speech files — never edited by any script
data/translated_en/<leader>/  optional English translations (robustness check; may stay empty)
data/metadata.csv      per-file date / type / source / title (+ how confident the date is)
data/processed/        speeches_clean.csv, chunks.csv, preprocessing_report.md   (Phase 1)
src/                   one module per pipeline step
artifacts/             embeddings, cluster models, bootstrap draws (regenerable, git-ignored)
outputs/tables/        CSV results          outputs/plots/  PNG + SVG
outputs/phase0_report.md, video_insights.md, methodology_for_video.md
notebooks/exploratory_analysis.ipynb
```

## Environment

Conda env `speechgeo` (Python 3.12, CUDA 13.0 build of PyTorch for the RTX 5090). On this machine
conda is installed at `C:\ProgramData\anaconda3` but is not on PATH, so either activate it once:

```powershell
& "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1"; conda activate speechgeo
```

or prefix every command with the interpreter directly:

```powershell
$py = "$env:USERPROFILE\.conda\envs\speechgeo\python.exe"
```

Recreate from scratch (torch **must** come from the PyTorch index; the PyPI wheel is CPU-only on Windows):

```powershell
$conda = "C:\ProgramData\anaconda3\Scripts\conda.exe"
& $conda create -n speechgeo python=3.12 -y
& $conda run -n speechgeo python -m pip install -r requirements.txt
& $conda run -n speechgeo python -m ipykernel install --user --name speechgeo --display-name "Python (speechgeo)"
```

Notes: `flash_attention_2` has no Windows wheels, so Qwen3-Embedding runs with `sdpa` attention in bf16
(~16 GB VRAM). All commands below are run from the project root with the `speechgeo` interpreter.

## How to run

| # | Step | Command | Output |
|---|------|---------|--------|
| 0 | Organize raw files (root → `data/original/<leader>/`) | `python -m src.organize --dry-run` then `python -m src.organize` | files moved, nothing edited |
| 0 | **Inventory & validation** (review before Phase 1) | `python -m src.inventory` | `outputs/phase0_report.md`, `outputs/tables/corpus_inventory.csv`, `suspicious_files.csv` |
| 1 | Preprocessing | `python -m src.preprocess` | `data/processed/speeches_clean.csv`, `preprocessing_report.md` |
| 1 | Chunking (+ robustness variant) | `python -m src.chunking` and `python -m src.chunking --strip-ceremonial` | `data/processed/chunks.csv`, `chunks_noceremonial.csv` |
| 2 | Embeddings (GPU) | `python -m src.embed --model qwen3_embedding_8b` (repeat with `--chunks chunks_noceremonial.csv`, and `--model bge_m3`) | `artifacts/embeddings/{model}[_suffix]_chunks.npy`, `_index.parquet`, `{model}_queries.*` |
| 3 | Theme scoring (embedding + NLI + keyword diagnostic) | `python -m src.theme_scoring --model qwen3_embedding_8b [--suffix _noceremonial]` | `outputs/tables/theme_scores_chunks{tag}.csv`, `theme_method_agreement{tag}.csv` |
| 4 | Aggregation + geometry | `python -m src.aggregate --model …` → `python -m src.geometry --model …` | `theme_profile_*`, `top_themes_by_leader`, `framing_*`, `leader_cosine_similarity`, `chunk_knn_*`, `semantic_dispersion` |
| 5 | Topic discovery (PCA → HDBSCAN) | `python -m src.clustering` and `python -m src.clustering --center-by-leader` | `clusters_summary{tag}.csv`, `cluster_passages{tag}.csv`, `outputs/clusters_report{tag}.md` |
| 6 | Plots | `python -m src.visualization` | `outputs/plots/*.png` + `.svg` |
| 7 | Bootstrap uncertainty | `python -m src.bootstrap --model … [--suffix …]` | `bootstrap_*_ci{tag}.csv`, `bootstrap_pair_rank_stability{tag}.csv` |
| 8 | Robustness (BGE-M3, ceremonial-stripped, centroid vs kNN, without trump2, method agreement, translated_en if present) | `python -m src.robustness` | `robustness_summary.csv`, `outputs/robustness_report.md` |
| 9 | Final report generation | `python -m src.generate_report` | `outputs/video_insights.md`, `methodology_for_video.md`, `results_summary.md` |
| all | Phases 1–9 in one go | `python -m src.run_pipeline` (`--skip-embed` reuses cached embeddings; `--from <step>` resumes) | everything above |

Every step reads `config.yaml`; the embedding model is chosen with `--model` and artifacts are written
per model so embeddings from different models are never mixed. Result tables for the primary model on
the full chunk set carry the plain names from the spec; every other combination carries a
`__{model}{suffix}` tag (e.g. `leader_cosine_similarity__bge_m3.csv`).

### English-normalised robustness run (Check B)

Drop translated files into `data/translated_en/<leader>/` with the **same filenames** as the originals,
then run `python -m src.run_pipeline --variant translated_en` followed by `python -m src.robustness`.
Until then the robustness report marks Check B as skipped.

### Key results (primary model, this corpus)

See `outputs/results_summary.md` for the tables, `outputs/video_insights.md` for eleven video-ready
findings with cautions, `outputs/robustness_report.md` for what changes with the second model, and
`outputs/methodology_for_video.md` (Turkish) for the explanations. The headline caveat: leader and
language are confounded in this corpus, and the leader-pair ranking is not stable across embedding models.

### Phase 0 outputs

- `outputs/tables/corpus_inventory.csv` — one row per file: leader, language (expected / detected),
  word / paragraph / token counts, estimated chunk count, metadata fields, flags.
- `outputs/tables/suspicious_files.csv` — one row per flag with a human-readable detail.
- `outputs/phase0_report.md` — the report to review before Phase 1.

The inventory never modifies files. Flags (`empty`, `very_short`, `near_duplicate`,
`possible_fragment_of`, `speaker_label_prefix`, `truncated_start`, `excess_whitespace`, `html_remnants`,
`timestamps`, `stage_directions`, `interviewer_pattern`, `third_person_narration`, `repeated_lines`,
`language_mismatch`, `filename_year_vs_speech_date`, `speech_type_outlier`, `mixed_speech_types`,
`below_min_speeches`, `missing_metadata`, `review:<status>`) are proposals for Phase 1 and for the
collector. `review:<status>` mirrors the `review_status` column of `data/metadata.csv` (`ok`, `verify`,
`exclude_candidate`), which is where facts that only a human reader can establish are recorded.

## Method summary (kept identical across phases)

- **Unit of analysis**: paragraph-based chunks of ~80–180 tokens, no overlap (`src/chunking.py`).
- **Aggregation**: chunk → speech (mean) → leader (mean of speeches). Every speech weighs equally, so
  longer speeches or more speeches do not inflate a leader.
- **Geometry**: unit-normalised embeddings; speech centroids re-normalised; leader centroid = normalised
  mean of speech centroids. All similarities are cosine values in the original embedding space.
  2D projections (UMAP / PCA) are for visualization only.
- **Uncertainty**: speech-level bootstrap (the speech, not the chunk, is the resampling unit).
- **Wording rule**: results are "semantic similarity between the collected speech corpora", never
  similarity between people, ideologies or political quality.
