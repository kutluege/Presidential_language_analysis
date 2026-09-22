"""Phase 6 — plots (PNG 200 dpi + SVG) with identical scales for every leader.

Usage:
    python -m src.visualization [--model qwen3_embedding_8b] [--suffix ""]

Design rules applied everywhere: one fixed colour per leader (never re-assigned), thin marks,
hairline grid, corpus-average reference lines, the same axis range on every panel, values in
the original embedding space (UMAP/PCA panels are visual only and say so).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, seed_everything, theme_keys, theme_labels
from .vectors import load_embeddings

INK, INK2, MUTED, GRID, BASE, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
MARKERS = ["o", "s", "^", "D", "P"]


def setup_style() -> None:
    fam = ["Segoe UI", "DejaVu Sans", "Arial"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams.update({
        "font.family": [f for f in fam if f in available] or ["DejaVu Sans"],
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "semibold", "axes.labelsize": 11,
        "axes.edgecolor": BASE, "axes.linewidth": 0.8, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
        "savefig.facecolor": SURFACE, "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.labelcolor": INK2,
        "legend.frameon": False, "svg.fonttype": "none",
    })


def save(fig: plt.Figure, plots_dir: Path, name: str, tag: str) -> None:
    fig.savefig(plots_dir / f"{name}{tag}.png", dpi=200, bbox_inches="tight")
    fig.savefig(plots_dir / f"{name}{tag}.svg", bbox_inches="tight")
    plt.close(fig)


def footer(fig: plt.Figure, text: str) -> None:
    fig.text(0.01, 0.005, text, fontsize=8, color=MUTED, ha="left", va="bottom")


class Viz:
    def __init__(self, cfg: dict, model_key: str, suffix: str):
        self.cfg, self.model_key, self.suffix = cfg, model_key, suffix
        self.tag = result_tag(cfg, model_key, suffix)
        self.tables = path_for(cfg, "outputs_tables")
        self.plots = path_for(cfg, "outputs_plots")
        self.plots.mkdir(parents=True, exist_ok=True)
        self.leaders = leader_slugs(cfg)
        self.names = {L: cfg["leaders"][L]["short_name"] for L in self.leaders}
        vcfg = cfg.get("visualization", {})
        self.colors = vcfg.get("leader_colors", {})
        self.themes = theme_keys(cfg)
        self.tlabels = theme_labels(cfg)
        self.framings = framing_keys(cfg)
        self.model_name = cfg["embedding"]["models"][model_key]["hf_id"]
        self.note = f"Corpus: {cfg['project_name']} · model {self.model_name} · values describe the collected speeches only"
        self.radar_range = tuple(vcfg.get("radar_range", [0.2, 0.8]))

    def t(self, name: str) -> pd.DataFrame:
        return pd.read_csv(self.tables / f"{name}{self.tag}.csv")

    def t_opt(self, name: str) -> pd.DataFrame | None:
        p = self.tables / f"{name}{self.tag}.csv"
        return pd.read_csv(p) if p.exists() else None

    # ---------------------------------------------------------------- radar
    def _radar_axes(self, ax, values_by_leader: dict[str, np.ndarray], title: str, show_legend: bool):
        n = len(self.themes)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        lo, hi = self.radar_range
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(lo, hi)
        ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7])
        ax.set_yticklabels(["", "", "0.5 = corpus avg", "", ""], fontsize=7, color=MUTED)
        ax.yaxis.grid(True, color=GRID, linewidth=0.7)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.spines["polar"].set_color(BASE)
        ax.plot(np.r_[angles, angles[0]], [0.5] * (n + 1), color=MUTED, linewidth=1.0, linestyle="-")
        ax.set_xticks(angles)
        ax.set_xticklabels([self.tlabels[k].replace(" & ", " &\n") for k in self.themes], fontsize=8, color=INK2)
        for L, vals in values_by_leader.items():
            v = np.r_[vals, vals[0]]
            ax.plot(np.r_[angles, angles[0]], v, color=self.colors[L], linewidth=2, label=self.names[L])
            ax.fill(np.r_[angles, angles[0]], v, color=self.colors[L], alpha=0.10 if len(values_by_leader) > 1 else 0.18)
        ax.set_title(title, pad=18)
        if show_legend:
            ax.legend(loc="upper right", bbox_to_anchor=(1.32, 1.12), fontsize=9)

    def radars(self):
        prof = self.t("theme_profile_leader").set_index("leader")
        for L in self.leaders:
            if L not in prof.index:
                continue
            fig = plt.figure(figsize=(6.4, 6.4))
            ax = fig.add_subplot(111, polar=True)
            vals = prof.loc[L, [f"{k}_pct" for k in self.themes]].to_numpy(dtype=float)
            self._radar_axes(ax, {L: vals}, f"{self.cfg['leaders'][L]['display_name']} — theme profile of the collected speeches", False)
            footer(fig, f"Mean percentile of chunk–theme similarity (0.5 = corpus average); same scale for every leader · n={int(prof.loc[L,'n_speeches'])} speeches, {int(prof.loc[L,'n_chunks'])} chunks · {self.model_name}")
            save(fig, self.plots, f"radar_{L}", self.tag)
        fig = plt.figure(figsize=(8.2, 7.4))
        ax = fig.add_subplot(111, polar=True)
        self._radar_axes(ax, {L: prof.loc[L, [f"{k}_pct" for k in self.themes]].to_numpy(dtype=float) for L in self.leaders if L in prof.index},
                         "Theme profiles of the five collected speech corpora", True)
        footer(fig, f"Mean percentile of chunk–theme similarity, speech-weighted (0.5 = corpus average); identical scale for all leaders · {self.model_name}")
        save(fig, self.plots, "radar_all_leaders", self.tag)

    # ---------------------------------------------------------------- heatmap
    def heatmap(self):
        sim = self.t("leader_cosine_similarity").set_index(self.t("leader_cosine_similarity").columns[0])
        sim.index.name = None
        names = [self.names[L] for L in sim.index]
        M = sim.to_numpy(dtype=float)
        off = M[~np.eye(len(M), dtype=bool)]
        fig, ax = plt.subplots(figsize=(7.2, 6.2))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", SEQ_BLUE[:10])
        vmin, vmax = float(off.min()) - 0.02, float(off.max()) + 0.02
        im = ax.imshow(np.where(np.eye(len(M), dtype=bool), np.nan, M), cmap=cmap, vmin=vmin, vmax=vmax)
        for i in range(len(M)):
            for j in range(len(M)):
                if i == j:
                    ax.text(j, i, "—", ha="center", va="center", color=MUTED, fontsize=11)
                else:
                    lum = (M[i, j] - vmin) / max(vmax - vmin, 1e-9)
                    ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", color="white" if lum > 0.55 else INK, fontsize=11)
        ax.set_xticks(range(len(M)), names)
        ax.set_yticks(range(len(M)), names)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title("Cosine similarity between leader centroids (collected speech corpora)")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.outline.set_visible(False)
        cb.ax.tick_params(color=MUTED, labelcolor=MUTED)
        footer(fig, f"Leader centroid = normalised mean of speech centroids; computed in the full {self.model_name} space (no projection). Semantic similarity of the corpora, not of the people.")
        save(fig, self.plots, "leader_similarity_heatmap", self.tag)

    # ---------------------------------------------------------------- projections
    def _projection(self, coords: np.ndarray, index: pd.DataFrame, name: str, title: str, method_note: str):
        leader = index["leader"].astype(str).to_numpy()
        speech = index["speech_id"].astype(str).to_numpy()
        fig = plt.figure(figsize=(12, 10.5))
        gs = fig.add_gridspec(2, 5, height_ratios=[3.2, 1.15], hspace=0.28, wspace=0.12)
        ax = fig.add_subplot(gs[0, :])
        for i, L in enumerate(self.leaders):
            m = leader == L
            if not m.any():
                continue
            ax.scatter(coords[m, 0], coords[m, 1], s=34, c=self.colors[L], marker=MARKERS[i], alpha=0.85,
                       edgecolors=SURFACE, linewidths=0.8, label=f"{self.names[L]} ({m.sum()} chunks)")
            # speech centroids in the 2-D plane: hollow markers with a label
            for sid in dict.fromkeys(speech[m]):
                sm = speech == sid
                cx, cy = coords[sm, 0].mean(), coords[sm, 1].mean()
                ax.scatter(cx, cy, s=150, facecolors="none", edgecolors=self.colors[L], marker=MARKERS[i], linewidths=1.6)
                ax.annotate(sid, (cx, cy), textcoords="offset points", xytext=(6, 6), fontsize=7, color=INK2)
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(BASE)
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9, title="leader (marker shape = leader)", title_fontsize=9)
        ax.text(0.01, 0.01, "filled = chunk · hollow = speech centroid (2-D mean) · labels = speech_id", transform=ax.transAxes, fontsize=8, color=MUTED)
        for i, L in enumerate(self.leaders):
            axs = fig.add_subplot(gs[1, i])
            axs.scatter(coords[:, 0], coords[:, 1], s=8, c=GRID, marker="o")
            m = leader == L
            axs.scatter(coords[m, 0], coords[m, 1], s=12, c=self.colors[L], marker=MARKERS[i], alpha=0.9)
            axs.set_title(self.names[L], fontsize=10, pad=4)
            axs.set_xticks([])
            axs.set_yticks([])
            for s in axs.spines.values():
                s.set_color(GRID)
        footer(fig, f"{method_note} 2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space. · {self.model_name}")
        save(fig, self.plots, name, self.tag)

    def projections(self):
        emb, index = load_embeddings(self.cfg, self.model_key, self.suffix)
        seed = int(self.cfg["random_seed"])
        from sklearn.decomposition import PCA

        pca = PCA(n_components=2, random_state=seed)
        pc = pca.fit_transform(emb)
        ev = pca.explained_variance_ratio_
        self._projection(pc, index, "pca_chunks", "Chunk embeddings — PCA (first two components)",
                         f"PCA on unit-normalised chunk vectors; PC1 {ev[0]:.0%}, PC2 {ev[1]:.0%} of variance.")
        np.save(path_for(self.cfg, "artifacts_clusters") / f"{self.model_key}{self.suffix}_pca2d.npy", pc)
        try:
            import umap

            up = self.cfg["umap_parameters"]
            reducer = umap.UMAP(n_neighbors=int(up["n_neighbors"]), min_dist=float(up["min_dist"]), n_components=2,
                                metric=up.get("metric", "cosine"), random_state=seed)
            um = reducer.fit_transform(emb)
            np.save(path_for(self.cfg, "artifacts_clusters") / f"{self.model_key}{self.suffix}_umap2d.npy", um)
            self._projection(um, index, "umap_chunks", "Chunk embeddings — UMAP",
                             f"UMAP(n_neighbors={up['n_neighbors']}, min_dist={up['min_dist']}, {up.get('metric','cosine')}, seed {seed}).")
        except Exception as exc:  # pragma: no cover
            print(f"[visualization] UMAP skipped: {type(exc).__name__}: {exc}")

    # ---------------------------------------------------------------- bars with CIs
    def _ci_lookup(self, table: str, key_col: str, metric: str | None = None):
        ci = self.t_opt(table)
        if ci is None:
            return None
        if metric is not None and "metric" in ci:
            ci = ci[ci["metric"] == metric]
        return ci.set_index(["leader", key_col])

    def theme_comparison(self):
        prof = self.t("theme_profile_leader").set_index("leader")
        ci = self._ci_lookup("bootstrap_theme_profile_ci", "theme", "pct")
        fig, axes = plt.subplots(2, 4, figsize=(14, 7.2), sharex=True)
        lo, hi = self.radar_range
        for ax, k in zip(axes.ravel(), self.themes):
            y = np.arange(len(self.leaders))[::-1]
            for yi, L in zip(y, self.leaders):
                v = float(prof.loc[L, f"{k}_pct"])
                ax.barh(yi, v - 0.5, left=0.5, height=0.62, color=self.colors[L])
                if ci is not None and (L, k) in ci.index:
                    r = ci.loc[(L, k)]
                    ax.plot([r["ci_low"], r["ci_high"]], [yi, yi], color=INK2, linewidth=1.2, solid_capstyle="butt")
                ax.text(v + (0.012 if v >= 0.5 else -0.012), yi, f"{v:.2f}", va="center", ha="left" if v >= 0.5 else "right", fontsize=8, color=INK2)
            ax.axvline(0.5, color=MUTED, linewidth=1)
            ax.set_yticks(y, [self.names[L] for L in self.leaders], fontsize=9)
            ax.set_xlim(lo, hi)
            ax.set_title(self.tlabels[k], fontsize=11)
            ax.xaxis.grid(True)
            ax.set_axisbelow(True)
            for s in ("top", "right", "left"):
                ax.spines[s].set_visible(False)
        fig.suptitle("Theme emphasis by leader — mean percentile of chunk–theme similarity (0.5 = corpus average)", fontsize=13, fontweight="semibold")
        footer(fig, f"Bars: speech-weighted leader mean · whiskers: 95% speech-level bootstrap interval (2000 resamples) · identical scale on every panel · {self.model_name}")
        fig.tight_layout(rect=(0, 0.03, 1, 0.96))
        save(fig, self.plots, "theme_comparison", self.tag)

    def conflict_cooperation(self):
        lead = self.t("framing_leader").set_index("leader")
        sp = self.t("framing_speech")
        ci = self._ci_lookup("bootstrap_framing_ci", "framing", "pct")
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
        titles = {k: self.cfg["framing_definitions"][k]["label"] for k in self.framings}
        for ax, k in zip(axes, self.framings):
            y = np.arange(len(self.leaders))[::-1]
            for yi, L in zip(y, self.leaders):
                v = float(lead.loc[L, f"{k}_pct"])
                ax.barh(yi, v - 0.5, left=0.5, height=0.55, color=self.colors[L], alpha=0.9)
                pts = sp.loc[sp["leader"] == L, f"{k}_pct"]
                ax.scatter(pts, np.full(len(pts), yi), s=26, facecolors=SURFACE, edgecolors=INK2, linewidths=0.9, zorder=3)
                if ci is not None and (L, k) in ci.index:
                    r = ci.loc[(L, k)]
                    ax.plot([r["ci_low"], r["ci_high"]], [yi + 0.36, yi + 0.36], color=INK2, linewidth=1.2)
                ax.text(1.01, yi, f"{v:.2f}   rate {lead.loc[L, f'{k}_rate']:.0%}", va="center", fontsize=8.5, color=INK2,
                        transform=ax.get_yaxis_transform(), clip_on=False)
            ax.axvline(0.5, color=MUTED, linewidth=1)
            ax.set_yticks(y, [self.names[L] for L in self.leaders])
            ax.set_xlim(0.2, 0.9)
            ax.set_title(titles[k])
            ax.xaxis.grid(True)
            ax.set_axisbelow(True)
            for s in ("top", "right", "left"):
                ax.spines[s].set_visible(False)
        fig.suptitle("Conflict/threat vs cooperation/solidarity framing — descriptive measurements, no ranking", fontsize=13, fontweight="semibold")
        footer(fig, "Bar: leader mean percentile of chunk similarity to the framing description · hollow dots: individual speeches · whisker: 95% speech-level bootstrap CI · rate: share of chunks in the corpus top quartile")
        fig.tight_layout(rect=(0, 0.04, 0.97, 0.94), w_pad=6)
        save(fig, self.plots, "conflict_cooperation_comparison", self.tag)

    def dispersion(self):
        d = self.t("semantic_dispersion").set_index("leader")
        ci = self.t_opt("bootstrap_dispersion_ci")
        ci = ci.set_index("leader") if ci is not None else None
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
        specs = [("mean_dist_speech_to_leader", "Speech centroids → leader centroid\n(how far the speeches sit from their own corpus centre)"),
                 ("mean_dist_chunk_to_speech", "Chunks → their speech centroid\n(how much a speech ranges within itself)")]
        for ax, (col, title) in zip(axes, specs):
            y = np.arange(len(self.leaders))[::-1]
            for yi, L in zip(y, self.leaders):
                v = float(d.loc[L, col])
                ax.barh(yi, v, height=0.58, color=self.colors[L])
                if col == "mean_dist_speech_to_leader" and ci is not None and L in ci.index:
                    ax.plot([ci.loc[L, "ci_low"], ci.loc[L, "ci_high"]], [yi, yi], color=INK2, linewidth=1.2)
                ax.text(v + 0.004, yi, f"{v:.3f}", va="center", fontsize=8.5, color=INK2)
            ax.set_yticks(y, [self.names[L] for L in self.leaders])
            ax.set_xlim(0, max(d[col].max() * 1.35, 0.05))
            ax.set_xlabel("mean cosine distance (higher = more spread)")
            ax.set_title(title, fontsize=11)
            ax.xaxis.grid(True)
            ax.set_axisbelow(True)
            for s in ("top", "right", "left"):
                ax.spines[s].set_visible(False)
        fig.suptitle("Semantic concentration / spread of each collected corpus", fontsize=13, fontweight="semibold")
        footer(fig, f"Cosine distances in the original {self.model_name} space · whiskers: speech-level bootstrap range (biased downward: resampled duplicates can only shrink spread) · describes the corpus, not consistency of a person")
        fig.tight_layout(rect=(0, 0.04, 1, 0.93))
        save(fig, self.plots, "semantic_dispersion", self.tag)

    def top_themes(self):
        top = self.t("top_themes_by_leader")
        top = top[top["method"] == "embedding_pct"]
        stab = self.t_opt("bootstrap_top_theme_stability")
        fig, axes = plt.subplots(1, len(self.leaders), figsize=(15, 3.9), sharex=True)
        for ax, L in zip(axes, self.leaders):
            rows = top[top["leader"] == L].sort_values("rank")
            y = np.arange(len(rows))[::-1]
            ax.barh(y, rows["value"].to_numpy() - 0.5, left=0.5, height=0.6, color=self.colors[L])
            labels = []
            for r in rows.itertuples():
                s = ""
                if stab is not None:
                    q = stab[(stab["leader"] == L) & (stab["theme"] == r.theme)]
                    if len(q):
                        s = f"  (top-3 in {q['share_top3'].iloc[0]:.0%} of resamples)"
                labels.append(self.tlabels[r.theme].replace(" & ", " &\n") + s)
            for yi, r in zip(y, rows.itertuples()):
                right = r.value >= 0.5
                ax.text(r.value + (0.01 if right else -0.01), yi, f"{r.value:.2f}", va="center", ha="left" if right else "right", fontsize=9, color=INK2)
            ax.set_yticks(y, [self.tlabels[r.theme].replace(" & ", " &\n") for r in rows.itertuples()], fontsize=8.5)
            ax.axvline(0.5, color=MUTED, linewidth=1)
            ax.set_xlim(0.35, 0.85)
            ax.set_title(self.names[L])
            ax.xaxis.grid(True)
            ax.set_axisbelow(True)
            for s in ("top", "right", "left"):
                ax.spines[s].set_visible(False)
            if stab is not None:
                txt = []
                for r in rows.itertuples():
                    q = stab[(stab["leader"] == L) & (stab["theme"] == r.theme)]
                    if len(q):
                        txt.append(f"{q['share_top3'].iloc[0]:.0%}")
                ax.text(0.98, -0.16, "in top-3 across bootstrap: " + " / ".join(txt), transform=ax.transAxes, ha="right", fontsize=7.5, color=MUTED)
        fig.suptitle("The three most represented themes in each collected speech set (mean percentile, 0.5 = corpus average)", fontsize=13, fontweight="semibold")
        footer(fig, f"Speech-weighted leader means · stability = share of 2000 speech-level bootstrap resamples in which the theme stays in the leader's top three · {self.model_name}")
        fig.tight_layout(rect=(0, 0.05, 1, 0.92))
        save(fig, self.plots, "top_themes_by_leader", self.tag)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 6: plots.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--only", default=None, help="comma list: radars,heatmap,projections,theme_comparison,conflict_cooperation,dispersion,top_themes")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    cfg = load_config(args.config)
    seed_everything(int(cfg["random_seed"]))
    setup_style()
    viz = Viz(cfg, args.model or primary_model_key(cfg), args.suffix)
    steps = ["radars", "heatmap", "projections", "theme_comparison", "conflict_cooperation", "dispersion", "top_themes"]
    if args.only:
        steps = [s for s in args.only.split(",") if s in steps]
    for s in steps:
        getattr(viz, s)()
        print(f"[visualization] {s} done")
    print(f"[visualization] plots in {viz.plots} (tag '{viz.tag}')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
