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

| # | Step | Command | Status |
|---|------|---------|--------|
| 0 | Organize raw files (root → `data/original/<leader>/`) | `python -m src.organize --dry-run` then `python -m src.organize` | ready |
| 0 | **Inventory & validation** | `python -m src.inventory` | ready |
| 1 | Preprocessing + chunking | `python -m src.preprocess` → `python -m src.chunking` | Phase 1 — pending |
| 2 | Embeddings (primary) | `python -m src.embed --model qwen3_embedding_8b` | Phase 2 — pending |
| 3 | Theme scoring | `python -m src.theme_scoring --model qwen3_embedding_8b` | Phase 3 — pending |
| 4 | Geometry (centroids, kNN, dispersion) | `python -m src.aggregate` → `python -m src.geometry` | Phase 4 — pending |
| 5 | Topic discovery (PCA → HDBSCAN) | `python -m src.clustering` | Phase 5 — pending |
| 6 | Plots | `python -m src.visualization` | Phase 6 — pending |
| 7 | Bootstrap uncertainty | `python -m src.bootstrap` | Phase 7 — pending |
| 8 | Robustness (BGE-M3, translated, ceremonial-stripped, centroid vs kNN) | `python -m src.robustness` | Phase 8 — pending |
| 9 | Final report generation | `python -m src.generate_report` | Phase 9 — pending |

Every step reads `config.yaml`; the embedding model is chosen with `--model` and artifacts are written
per model so embeddings from different models are never mixed.

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
