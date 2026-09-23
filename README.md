# political-speech-geometry

A small, reproducible NLP experiment on the *content, semantic geometry and rhetorical style* of a
collected corpus of public speeches by five political leaders (Erdoğan, Macron, Merkel, Putin, Trump),
built for an explainer video.

**What this project is not.** It does not evaluate, rank, endorse or criticise anyone. Every number it
produces describes *the collected speech files*: their themes, how semantically close the corpora sit in
an embedding space, how concentrated each corpus is, and which measurable rhetorical and emotional
features their text shows. Style "rankings" are sorted descriptive measurements with confidence
intervals, never a judgement of quality. None of it measures ideology, personality, competence or
political similarity between people.

## Two runs

| | Run 1 (archived in `old_results/`) | Run 2 (current) |
|---|---|---|
| corpus | original languages (tr / fr / de / en) | **English**: the collector's translations saved over `data/original/`; originals at commit `d192094` |
| primary model | Qwen/Qwen3-Embedding-8B | **tencent/KaLM-Embedding-Gemma3-12B-2511** (top open model on MTEB multilingual v2 that runs in bf16 on a 32 GB GPU) |
| robustness model | BAAI/bge-m3 | Qwen/Qwen3-Embedding-8B (same model as run 1 → old-vs-new isolates the language effect) |
| style analysis | 2 framing scales | 7 rhetorical dimensions + emotional tone (28 GoEmotions labels, sentiment valence) + composite style similarity |
| plots | landscape | **square 1:1 and vertical 9:16** (Instagram) |

Headline of run 1: language dominated the geometry. Run 2 removes the language signal by translation
and adds the translator's voice instead; both facts are stated wherever it matters.

## Layout

```
config.yaml            every parameter, model id, theme / dimension definition (single source of truth)
requirements.txt       pinned versions from the working environment
data/original/<leader>/    the analysed texts (English) — never edited by any script
data/metadata.csv      per-file date / type / source / title / translation status
data/processed/        speeches_clean.csv, chunks.csv, chunks_noceremonial.csv, preprocessing_report.md
src/                   one module per pipeline step (see table below)
artifacts/             embeddings, cluster labels, bootstrap draws (regenerable; npy/parquet git-ignored)
outputs/tables/        CSV results          outputs/plots/  PNG (2×) + SVG, square and _9x16
outputs/*.md           phase0_report, robustness_report, clusters_report(s), video_insights, methodology_for_video, results_summary
old_results/           complete run 1 (see its README)
```

## Environment

Conda env `speechgeo` (Python 3.12, PyTorch CUDA 13.0 build for the RTX 5090). Conda is installed at
`C:\ProgramData\anaconda3` but not on PATH:

```powershell
& "C:\ProgramData\anaconda3\shell\condabin\conda-hook.ps1"; conda activate speechgeo
# or call the interpreter directly: $env:USERPROFILE\.conda\envs\speechgeo\python.exe
```

Recreate from scratch (torch **must** come from the PyTorch index; the PyPI wheel is CPU-only on Windows):

```powershell
$conda = "C:\ProgramData\anaconda3\Scripts\conda.exe"
& $conda create -n speechgeo python=3.12 -y
& $conda run -n speechgeo python -m pip install -r requirements.txt
```

Notes: no Windows wheels for flash-attention → `sdpa` attention. KaLM-12B loads through a plain
`AutoModel` + last-token-pooling path (`src/embed.py`, `LastTokenEmbedder`) because sentence-transformers
5/6 tries to fetch an image processor for the Gemma-3 config; the repo has no custom code, so the result
is identical. Peak VRAM ≈ 23 GB.

## How to run

All commands from the project root with the `speechgeo` interpreter. `{model}` is a key under
`embedding.models` (`kalm_embedding_gemma3_12b`, `qwen3_embedding_8b`, `bge_m3`); `{suffix}` is `""` or
`_noceremonial`.

| # | Step | Command | Output |
|---|------|---------|--------|
| 0 | Organize raw files | `python -m src.organize --dry-run` / `python -m src.organize` | files moved into `data/original/<leader>/` |
| 0 | **Inventory & validation** | `python -m src.inventory` | `outputs/phase0_report.md`, `corpus_inventory.csv`, `suspicious_files.csv` |
| 1 | Preprocessing | `python -m src.preprocess` | `speeches_clean.csv`, `preprocessing_report.md` |
| 1 | Chunking (+ robustness variant) | `python -m src.chunking` · `python -m src.chunking --strip-ceremonial` | `chunks.csv`, `chunks_noceremonial.csv` |
| 2 | Embeddings (GPU) | `python -m src.embed --model {model} --chunks chunks.csv` (and `chunks_noceremonial.csv`) | `artifacts/embeddings/{model}{suffix}_chunks.npy`, `_index.parquet`, `{model}_queries.*`, `_run.json` |
| 3 | Theme + rhetorical scoring | `python -m src.theme_scoring --model {model} --suffix {suffix}` | `theme_scores_chunks{tag}.csv`, `theme_method_agreement{tag}.csv` |
| 3b | Emotional tone | `python -m src.emotion --suffix {suffix}` | `emotion_scores_chunks{etag}.csv`, `emotion_profile_speech/leader{etag}.csv` |
| 4 | Aggregation + geometry | `python -m src.aggregate …` → `python -m src.geometry …` | `theme_profile_*`, `top_themes_by_leader`, `framing_*`, `leader_cosine_similarity`, `chunk_knn_*`, `semantic_dispersion` |
| 4c | Style profile & similarity | `python -m src.style --model {model} --suffix {suffix}` | `style_rankings`, `style_leader_profile`, `style_distance/similarity_leader`, `style_pairs`, `content_vs_style` |
| 5 | Topic discovery | `python -m src.clustering` · `python -m src.clustering --center-by-leader` | `clusters_summary{tag}.csv`, `cluster_passages{tag}.csv`, `outputs/clusters_report{tag}.md` |
| 6 | Plots (square + 9:16) | `python -m src.visualization [--formats square,vertical] [--only …]` | `outputs/plots/{name}.png`, `{name}_9x16.png`, SVGs |
| 7 | Bootstrap uncertainty | `python -m src.bootstrap --model {model} --suffix {suffix}` | `bootstrap_*_ci{tag}.csv`, `bootstrap_pair_rank_stability{tag}.csv` |
| 8 | Robustness | `python -m src.robustness` | `robustness_summary.csv`, `outputs/robustness_report.md`, `language_effect_*.csv`, `rhetoric_vs_emotion.csv` |
| 9 | Final report generation | `python -m src.generate_report` | `outputs/video_insights.md`, `methodology_for_video.md`, `results_summary.md` |
| all | Phases 1–9 | `python -m src.run_pipeline` (`--skip-embed`, `--from <step>`) | everything above |

Result tables for the primary model on the full chunk set carry the plain spec filenames; every other
combination carries a `__{model}{suffix}` tag. Emotion tables are model-independent and carry `""` or
`__noceremonial`.

### Robustness checks (`outputs/robustness_report.md`)

A primary vs robustness model · B/G original-language corpus (run 1, same Qwen3 model) vs English corpus
· C all content vs ceremonial openings/closings removed · D leader-centroid similarity vs chunk-level
cross-neighbour similarity · E with vs without `trump2` (a compilation of excerpts kept at the collector's
request) · F embedding vs NLI theme scoring · H rhetorical dimensions vs emotion classifier.

## Method summary

- **Unit**: paragraph-based chunks of ~80–180 tokens, no overlap; identical chunks for both models.
- **Aggregation**: chunk → speech (mean) → leader (mean of speeches); every speech weighs equally.
- **Geometry**: unit-normalised embeddings, normalised speech centroids, leader centroid = normalised mean of
  speech centroids; all similarities are cosine values in the original space; UMAP/PCA are visual only.
- **Themes / rhetorical dimensions**: cosine similarity between a chunk and a written description (same
  model), reported as corpus percentiles (0.5 = corpus average); multilingual NLI as a second opinion.
- **Emotional tone**: GoEmotions (28 labels, multi-label) grouped into families + sentiment valence.
- **Style similarity**: z-scored speech-level vectors (7 rhetorical dims, 3 emotion families, valence) →
  leader means → Euclidean distance / cosine; hierarchical clustering for the dendrogram.
- **Uncertainty**: speech-level bootstrap (2000 resamples) for every leader-level number.
- **Wording rule**: results describe the collected speech corpora, never the people. Translated leaders'
  style measurements also carry the translator's choices.
