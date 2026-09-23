"""Phase 6 — Instagram-format figures (square 1:1 and vertical 9:16), PNG at 2× + SVG.

Usage:
    python -m src.visualization [--model kalm_embedding_gemma3_12b] [--suffix ""] [--formats square,vertical] [--only radars,heatmap,...]

Rules applied everywhere: one fixed colour per leader (never re-assigned), identical scales on every
panel and for every leader, corpus-average reference lines, hairline grid, phone-readable type, values
from the original embedding space (projections say they are visual only). Square files keep the spec's
names (`radar_erdogan.png`, ...); vertical files carry the `_9x16` suffix.
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
from matplotlib.gridspec import GridSpec

from .config import framing_keys, leader_slugs, load_config, path_for, primary_model_key, result_tag, seed_everything, theme_keys, theme_labels
from .emotion import etag_for
from .vectors import load_embeddings

INK, INK2, MUTED, GRID, BASE, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab"]
MARKERS = ["o", "s", "^", "D", "P"]
DPI = 150  # figure dpi: pixels = inches * DPI; exported at export_scale × DPI


def px2pt(px: float) -> float:
    return px * 72.0 / DPI


class Fmt:
    def __init__(self, name: str, spec: dict, base_font_px: int):
        self.name, self.suffix = name, spec.get("suffix", "")
        self.w_in, self.h_in = spec["width_px"] / DPI, spec["height_px"] / DPI
        self.vertical = spec["height_px"] > spec["width_px"] * 1.2
        self.base = px2pt(base_font_px)          # smallest text
        self.small = self.base * 0.85
        self.label = self.base * 1.05
        self.title = self.base * 1.45
        self.big = self.base * 2.2

    def fig(self, h_scale: float = 1.0) -> plt.Figure:
        return plt.figure(figsize=(self.w_in, self.h_in * h_scale), dpi=DPI)


def setup_style(base_pt: float) -> None:
    fam = ["Segoe UI", "DejaVu Sans", "Arial"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams.update({
        "font.family": [f for f in fam if f in available] or ["DejaVu Sans"], "font.size": base_pt,
        "axes.titlesize": base_pt * 1.2, "axes.titleweight": "bold", "axes.labelsize": base_pt,
        "axes.edgecolor": BASE, "axes.linewidth": 0.8, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
        "savefig.facecolor": SURFACE, "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": base_pt * 0.9, "ytick.labelsize": base_pt * 0.9,
        "text.color": INK, "axes.labelcolor": INK2, "legend.frameon": False, "legend.fontsize": base_pt * 0.9, "svg.fonttype": "none",
    })


def strip_axes(ax, keep=("bottom",)):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)
    ax.set_axisbelow(True)


class Viz:
    def __init__(self, cfg: dict, model_key: str, suffix: str, formats: list[str]):
        self.cfg, self.model_key, self.suffix = cfg, model_key, suffix
        self.tag = result_tag(cfg, model_key, suffix)
        self.etag = etag_for(suffix)
        self.tables = path_for(cfg, "outputs_tables")
        self.plots = path_for(cfg, "outputs_plots")
        self.plots.mkdir(parents=True, exist_ok=True)
        self.leaders = leader_slugs(cfg)
        self.names = {L: cfg["leaders"][L]["short_name"] for L in self.leaders}
        vcfg = cfg.get("visualization", {})
        self.colors = vcfg.get("leader_colors", {})
        self.themes, self.tlabels = theme_keys(cfg), theme_labels(cfg)
        self.framings = framing_keys(cfg)
        self.flabels = {k: cfg["framing_definitions"][k]["label"] for k in self.framings}
        self.model_name = cfg["embedding"]["models"][model_key]["hf_id"].split("/")[-1]
        self.radar_range = tuple(vcfg.get("radar_range", [0.2, 0.8]))
        self.export_scale = int(vcfg.get("export_scale", 2))
        base_px = int(vcfg.get("base_font_px", 22))
        self.formats = [Fmt(n, vcfg["formats"][n], base_px) for n in formats if n in vcfg.get("formats", {})]
        self.translated = [self.names[L] for L in self.leaders if cfg["leaders"][L].get("text_is_translation")]

    # ------------------------------------------------------------------ helpers
    def t(self, name: str, tag: str | None = None) -> pd.DataFrame:
        return pd.read_csv(self.tables / f"{name}{self.tag if tag is None else tag}.csv")

    def t_opt(self, name: str, tag: str | None = None) -> pd.DataFrame | None:
        p = self.tables / f"{name}{self.tag if tag is None else tag}.csv"
        return pd.read_csv(p) if p.exists() else None

    def save(self, fig: plt.Figure, name: str, f: Fmt) -> None:
        fig.savefig(self.plots / f"{name}{self.tag}{f.suffix}.png", dpi=DPI * self.export_scale)
        fig.savefig(self.plots / f"{name}{self.tag}{f.suffix}.svg")
        plt.close(fig)

    def header(self, fig: plt.Figure, f: Fmt, title: str, subtitle: str = "", y: float = 0.985) -> None:
        fig.text(0.05, y, title, fontsize=f.title, fontweight="bold", va="top", ha="left", wrap=True)
        if subtitle:
            fig.text(0.05, y - (0.035 if f.vertical else 0.06), subtitle, fontsize=f.small, color=INK2, va="top", ha="left", wrap=True)

    def footer(self, fig: plt.Figure, f: Fmt, text: str) -> None:
        fig.text(0.05, 0.012, text, fontsize=f.small * 0.85, color=MUTED, va="bottom", ha="left", wrap=True)

    def caveat(self, extra: str = "") -> str:
        base = f"Collected speeches only · {self.model_name}"
        if self.translated:
            base += f" · English text ({', '.join(self.translated)} translated/transcribed)"
        return base + (" · " + extra if extra else "")

    def ci_lookup(self, table: str, key_col: str, metric: str | None = None):
        ci = self.t_opt(table)
        if ci is None:
            return None
        if metric is not None and "metric" in ci:
            ci = ci[ci["metric"] == metric]
        return ci.set_index(["leader", key_col])

    # ------------------------------------------------------------------ radar core
    def _radar(self, ax, keys, labels, values_by_leader, f: Fmt, rng=None, ref=0.5, legend=True):
        n = len(keys)
        lo, hi = rng or self.radar_range
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(lo, hi)
        ticks = [t for t in np.arange(0.3, 0.8, 0.1) if lo < t < hi]
        ax.set_yticks(ticks)
        ax.set_yticklabels([("corpus avg" if abs(t - ref) < 1e-9 else "") for t in ticks], fontsize=f.small * 0.8, color=MUTED)
        ax.yaxis.grid(True, color=GRID, linewidth=0.7)
        ax.xaxis.grid(True, color=GRID, linewidth=0.7)
        ax.spines["polar"].set_color(BASE)
        ax.plot(np.r_[angles, angles[0]], [ref] * (n + 1), color=MUTED, linewidth=1.0)
        ax.set_xticks(angles)
        ax.set_xticklabels([labels[k].replace(" & ", " &\n").replace(" / ", " /\n").replace("-versus-", "-vs-\n") for k in keys], fontsize=f.small, color=INK2)
        ax.tick_params(axis="x", pad=f.small * 0.9)
        for L, vals in values_by_leader.items():
            v = np.r_[vals, vals[0]]
            ax.plot(np.r_[angles, angles[0]], v, color=self.colors[L], linewidth=2.4, label=self.names[L])
            ax.fill(np.r_[angles, angles[0]], v, color=self.colors[L], alpha=0.10 if len(values_by_leader) > 1 else 0.20)
        if legend and len(values_by_leader) > 1:
            if f.vertical:
                ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=min(5, len(values_by_leader)), fontsize=f.small, handlelength=1.4)
            else:  # square: figure-level legend between subtitle and radar, clear of axis labels and footer
                h, l = ax.get_legend_handles_labels()
                ax.figure.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 0.865), ncol=min(5, len(values_by_leader)), fontsize=f.small, handlelength=1.4)

    def _radar_figure(self, f: Fmt, keys, labels, values_by_leader, title, subtitle, name, extra_rows=None, rng=None):
        fig = f.fig()
        if f.vertical:
            gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 0.55], top=0.86, bottom=0.05, left=0.17, right=0.83, hspace=0.05)
            ax = fig.add_subplot(gs[0], polar=True)
            axt = fig.add_subplot(gs[1])
        else:
            ax = fig.add_axes([0.18, 0.13, 0.64, 0.56], polar=True)
            axt = None
        self._radar(ax, keys, labels, values_by_leader, f, rng=rng)
        self.header(fig, f, title, subtitle)
        if axt is not None and extra_rows:
            axt.axis("off")
            y = 0.95
            for text, color, size in extra_rows:
                axt.text(0.0, y, text, fontsize=size, color=color, va="top", ha="left", transform=axt.transAxes, wrap=True)
                y -= 0.13 if size > f.base else 0.10
        self.footer(fig, f, self.caveat("mean percentile of chunk–description similarity; 0.5 = corpus average; same scale for every leader"))
        self.save(fig, name, f)

    # ------------------------------------------------------------------ figures
    def radars(self):
        prof = self.t("theme_profile_leader").set_index("leader")
        stab = self.t_opt("bootstrap_top_theme_stability")
        for f in self.formats:
            for L in self.leaders:
                if L not in prof.index:
                    continue
                vals = prof.loc[L, [f"{k}_pct" for k in self.themes]].to_numpy(float)
                order = np.argsort(-vals)[:3]
                rows = [(f"Most represented themes in the {self.names[L]} speeches", INK, f.label)]
                for i in order:
                    s = ""
                    if stab is not None:
                        q = stab[(stab["leader"] == L) & (stab["theme"] == self.themes[i])]
                        if len(q):
                            s = f"   · top-3 in {q['share_top3'].iloc[0]:.0%} of resamples"
                    rows.append((f"{self.tlabels[self.themes[i]]}  {vals[i]:.2f}{s}", self.colors[L], f.base))
                rows.append((f"{int(prof.loc[L, 'n_speeches'])} speeches · {int(prof.loc[L, 'n_chunks'])} chunks", MUTED, f.small))
                self._radar_figure(f, self.themes, self.tlabels, {L: vals}, f"{self.cfg['leaders'][L]['display_name']}",
                                   "Theme profile of the collected speeches", f"radar_{L}", extra_rows=rows)
            allv = {L: prof.loc[L, [f"{k}_pct" for k in self.themes]].to_numpy(float) for L in self.leaders if L in prof.index}
            rows = [("Top theme per speech set", INK, f.label)] + [
                (f"{self.names[L]}: {self.tlabels[self.themes[int(np.argmax(v))]]} ({v.max():.2f})", self.colors[L], f.base) for L, v in allv.items()]
            self._radar_figure(f, self.themes, self.tlabels, allv, "Theme profiles of five speech sets", "Eight fixed themes, identical scale", "radar_all_leaders", extra_rows=rows)

    def rhetorical_radars(self):
        fl = self.t("framing_leader").set_index("leader")
        for f in self.formats:
            allv = {L: fl.loc[L, [f"{k}_pct" for k in self.framings]].to_numpy(float) for L in self.leaders if L in fl.index}
            rows = [("Highest-scoring leader per dimension", INK, f.label)]
            for j, k in enumerate(self.framings):
                L = max(allv, key=lambda x: allv[x][j])
                rows.append((f"{self.flabels[k]}: {self.names[L]} ({allv[L][j]:.2f})", self.colors[L], f.small))
            self._radar_figure(f, self.framings, self.flabels, allv, "Rhetorical profile of five speech sets",
                               "Seven descriptive dimensions · sorted measurements, no ranking of people", "rhetorical_radar_all_leaders", extra_rows=rows)
            for L in allv:
                rows = [(f"{self.names[L]}: strongest dimensions", INK, f.label)] + [
                    (f"{self.flabels[self.framings[i]]}  {allv[L][i]:.2f}", self.colors[L], f.base) for i in np.argsort(-allv[L])[:3]]
                self._radar_figure(f, self.framings, self.flabels, {L: allv[L]}, self.cfg["leaders"][L]["display_name"],
                                   "Rhetorical profile of the collected speeches", f"rhetorical_radar_{L}", extra_rows=rows)

    def _heat(self, ax, M, names, f: Fmt, cmap, vmin, vmax, fmt="{:.3f}", diag="—"):
        im = ax.imshow(np.where(np.eye(len(M), dtype=bool), np.nan, M), cmap=cmap, vmin=vmin, vmax=vmax)
        for i in range(len(M)):
            for j in range(len(M)):
                if i == j:
                    ax.text(j, i, diag, ha="center", va="center", color=MUTED, fontsize=f.base)
                else:
                    lum = (M[i, j] - vmin) / max(vmax - vmin, 1e-9)
                    ax.text(j, i, fmt.format(M[i, j]), ha="center", va="center", color="white" if lum > 0.55 else INK, fontsize=f.base)
        ax.set_xticks(range(len(M)), names, fontsize=f.small)
        ax.set_yticks(range(len(M)), names, fontsize=f.small)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        return im

    def _pair_bars(self, ax, pairs: pd.DataFrame, value_col: str, f: Fmt, lo_col="ci_low", hi_col="ci_high", xlabel="", higher_is_closer=True):
        pairs = pairs.sort_values(value_col, ascending=not higher_is_closer).reset_index(drop=True)
        y = np.arange(len(pairs))[::-1]
        for yi, r in zip(y, pairs.itertuples()):
            ax.barh(yi, getattr(r, value_col), height=0.6, color=GRID)
            ax.scatter([getattr(r, value_col)], [yi], s=60, color=INK, zorder=3)
            if lo_col in pairs.columns:
                ax.plot([getattr(r, lo_col), getattr(r, hi_col)], [yi, yi], color=INK2, linewidth=1.5)
            ax.text(getattr(r, value_col), yi + 0.36, f"{getattr(r, value_col):.3f}", fontsize=f.small * 0.85, color=INK2, ha="center", va="bottom")
        ax.set_yticks(y, [f"{self.names[r.leader_a]} – {self.names[r.leader_b]}" for r in pairs.itertuples()], fontsize=f.small)
        ax.set_xlabel(xlabel, fontsize=f.small)
        ax.xaxis.grid(True)
        strip_axes(ax)
        lo = float(pairs[lo_col].min()) if lo_col in pairs.columns else float(pairs[value_col].min())
        hi = float(pairs[hi_col].max()) if hi_col in pairs.columns else float(pairs[value_col].max())
        pad = (hi - lo) * 0.15 or 0.01
        ax.set_xlim(lo - pad, hi + pad)

    def heatmap(self):
        raw = self.t("leader_cosine_similarity")
        sim = raw.set_index(raw.columns[0])
        names = [self.names[L] for L in sim.index]
        M = sim.to_numpy(float)
        off = M[~np.eye(len(M), dtype=bool)]
        ci = self.t_opt("bootstrap_leader_similarity_ci")
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", SEQ_BLUE)
        for f in self.formats:
            fig = f.fig()
            if f.vertical and ci is not None:
                gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 0.95], top=0.86, bottom=0.06, left=0.20, right=0.95, hspace=0.35)
                ax = fig.add_subplot(gs[0])
                ax2 = fig.add_subplot(gs[1])
            else:
                ax = fig.add_axes([0.20, 0.14, 0.72, 0.62])
                ax2 = None
            self._heat(ax, M, names, f, cmap, float(off.min()) - 0.02, float(off.max()) + 0.02)
            ax.set_title("cosine similarity of leader centroids", fontsize=f.small, color=INK2, pad=8)
            if ax2 is not None:
                self._pair_bars(ax2, ci, "cosine_similarity", f, xlabel="cosine similarity with 95% speech-level bootstrap interval")
                ax2.set_title("the ten pairs, closest first", fontsize=f.small, color=INK2, loc="left")
            self.header(fig, f, "Semantic proximity of the speech sets", "Leader centroid = normalised mean of speech centroids · full embedding space, no projection")
            self.footer(fig, f, self.caveat("similarity of the collected corpora, not of the people"))
            self.save(fig, "leader_similarity_heatmap", f)

    def projections(self):
        emb, index = load_embeddings(self.cfg, self.model_key, self.suffix)
        seed = int(self.cfg["random_seed"])
        from sklearn.decomposition import PCA

        pca = PCA(n_components=2, random_state=seed)
        pc = pca.fit_transform(emb)
        ev = pca.explained_variance_ratio_
        cl_dir = path_for(self.cfg, "artifacts_clusters")
        cl_dir.mkdir(parents=True, exist_ok=True)
        np.save(cl_dir / f"{self.model_key}{self.suffix}_pca2d.npy", pc)
        coords = {"pca_chunks": (pc, "PCA — first two components", f"PCA on unit-normalised chunk vectors; PC1 {ev[0]:.0%}, PC2 {ev[1]:.0%} of variance")}
        try:
            import umap

            up = self.cfg["umap_parameters"]
            um = umap.UMAP(n_neighbors=int(up["n_neighbors"]), min_dist=float(up["min_dist"]), n_components=2,
                           metric=up.get("metric", "cosine"), random_state=seed).fit_transform(emb)
            np.save(cl_dir / f"{self.model_key}{self.suffix}_umap2d.npy", um)
            coords["umap_chunks"] = (um, "UMAP of chunk embeddings", f"UMAP(n_neighbors={up['n_neighbors']}, min_dist={up['min_dist']}, {up.get('metric', 'cosine')}, seed {seed})")
        except Exception as exc:  # pragma: no cover
            print(f"[visualization] UMAP skipped: {type(exc).__name__}: {exc}")
        leader = index["leader"].astype(str).to_numpy()
        speech = index["speech_id"].astype(str).to_numpy()
        for name, (xy, title, note) in coords.items():
            for f in self.formats:
                fig = f.fig()
                if f.vertical:
                    gs = GridSpec(3, 5, figure=fig, height_ratios=[1.0, 0.36, 0.36], top=0.87, bottom=0.05, left=0.05, right=0.95, hspace=0.25, wspace=0.08)
                    ax = fig.add_subplot(gs[0, :])
                    # five facets in two rows (3 + 2) under the main panel
                    facet_axes = [fig.add_subplot(gs[1, 0:2]), fig.add_subplot(gs[1, 2:4]), fig.add_subplot(gs[1, 4:5]),
                                  fig.add_subplot(gs[2, 0:2]), fig.add_subplot(gs[2, 2:4])]
                else:
                    gs = GridSpec(2, 5, figure=fig, height_ratios=[1.0, 0.42], top=0.84, bottom=0.07, left=0.05, right=0.95, hspace=0.18, wspace=0.08)
                    ax = fig.add_subplot(gs[0, :])
                    facet_axes = [fig.add_subplot(gs[1, i]) for i in range(5)]
                for i, L in enumerate(self.leaders):
                    m = leader == L
                    if not m.any():
                        continue
                    ax.scatter(xy[m, 0], xy[m, 1], s=42, c=self.colors[L], marker=MARKERS[i], alpha=0.85, edgecolors=SURFACE, linewidths=0.8,
                               label=f"{self.names[L]} ({m.sum()})")
                    for sid in dict.fromkeys(speech[m]):
                        sm = speech == sid
                        ax.scatter(xy[sm, 0].mean(), xy[sm, 1].mean(), s=190, facecolors="none", edgecolors=self.colors[L], marker=MARKERS[i], linewidths=1.8)
                ax.set_xticks([])
                ax.set_yticks([])
                for s in ax.spines.values():
                    s.set_color(BASE)
                ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=5 if not f.vertical else 3, fontsize=f.small, markerscale=1.2, handletextpad=0.3, columnspacing=1.0)
                ax.text(0.01, 0.02, "filled = chunk · hollow = speech centre (2-D mean)", transform=ax.transAxes, fontsize=f.small * 0.8, color=MUTED)
                for i, (L, axs) in enumerate(zip(self.leaders, facet_axes)):
                    axs.scatter(xy[:, 0], xy[:, 1], s=8, c=GRID)
                    m = leader == L
                    axs.scatter(xy[m, 0], xy[m, 1], s=14, c=self.colors[L], marker=MARKERS[i])
                    axs.set_title(self.names[L], fontsize=f.small, pad=3, color=INK2)
                    axs.set_xticks([])
                    axs.set_yticks([])
                    for s in axs.spines.values():
                        s.set_color(GRID)
                self.header(fig, f, title, "Each point is one chunk · colour and marker = leader · one facet per leader")
                self.footer(fig, f, note + ". " + self.cfg["methodology_notes"]["projection_note"] + f" · {self.model_name}")
                self.save(fig, name, f)

    def _ranked_panels(self, f: Fmt, name: str, panels: list[dict], title: str, subtitle: str, footer: str, xlim, ref=0.5, ncols_square=2):
        """panels: [{title, rows:[(leader, value, lo, hi)]}] drawn as horizontal bars from `ref`, sorted by value."""
        n = len(panels)
        fig = f.fig()
        if f.vertical:
            nrows, ncols = n, 1
            gs = GridSpec(nrows, ncols, figure=fig, top=0.885, bottom=0.05, left=0.24, right=0.95, hspace=0.75)
        else:
            ncols = ncols_square
            nrows = int(np.ceil(n / ncols))
            gs = GridSpec(nrows, ncols, figure=fig, top=0.84, bottom=0.07, left=0.16, right=0.97, hspace=0.9, wspace=0.55)
        for p_i, p in enumerate(panels):
            ax = fig.add_subplot(gs[p_i // ncols, p_i % ncols])
            rows = sorted(p["rows"], key=lambda r: r[1], reverse=True)
            y = np.arange(len(rows))[::-1]
            for yi, (L, v, lo, hi) in zip(y, rows):
                ax.barh(yi, v - ref, left=ref, height=0.62, color=self.colors[L])
                if lo is not None:
                    ax.plot([lo, hi], [yi, yi], color=INK2, linewidth=1.4)
                ax.text(v, yi + 0.34, f"{v:.2f}", va="bottom", ha="center", fontsize=f.small * 0.8, color=INK2)
            ax.axvline(ref, color=MUTED, linewidth=1)
            ax.set_yticks(y, [self.names[L] for L, *_ in rows], fontsize=f.small)
            ax.set_xlim(*xlim)
            ax.set_title(p["title"], fontsize=f.label, loc="left", pad=6)
            ax.xaxis.grid(True)
            strip_axes(ax)
            ax.tick_params(axis="x", labelsize=f.small * 0.8)
        self.header(fig, f, title, subtitle)
        self.footer(fig, f, footer)
        self.save(fig, name, f)

    def theme_comparison(self):
        prof = self.t("theme_profile_leader").set_index("leader")
        ci = self.ci_lookup("bootstrap_theme_profile_ci", "theme", "pct")
        panels = []
        for k in self.themes:
            rows = []
            for L in self.leaders:
                if L not in prof.index:
                    continue
                lo = hi = None
                if ci is not None and (L, k) in ci.index:
                    lo, hi = float(ci.loc[(L, k), "ci_low"]), float(ci.loc[(L, k), "ci_high"])
                rows.append((L, float(prof.loc[L, f"{k}_pct"]), lo, hi))
            panels.append({"title": self.tlabels[k], "rows": rows})
        for f in self.formats:
            self._ranked_panels(f, "theme_comparison", panels, "Theme emphasis, leader by leader",
                                "Mean percentile of chunk–theme similarity · 0.5 = corpus average · whiskers: 95% speech-level bootstrap",
                                self.caveat("identical scale on every panel; sorted within each theme"), self.radar_range)

    def rhetorical_rankings(self):
        rk = self.t("style_rankings")
        rk = rk[rk["kind"] == "rhetorical"]
        panels = []
        for k in self.framings:
            sub = rk[rk["dimension"] == k]
            panels.append({"title": self.flabels[k], "rows": [(r.leader, float(r.value), float(r.ci_low), float(r.ci_high)) for r in sub.itertuples()]})
        for f in self.formats:
            self._ranked_panels(f, "style_rankings", panels, "Rhetorical dimensions, ranked by measured value",
                                "Mean percentile of chunk similarity to each description · whiskers: 95% speech-level bootstrap",
                                self.caveat("descriptive measurements; overlapping intervals mean no reliable difference"), (0.2, 0.85))
            two = [p for p in panels if p["title"] in (self.flabels["conflict_threat_framing"], self.flabels["cooperation_solidarity_framing"])]
            self._ranked_panels(f, "conflict_cooperation_comparison", two, "Conflict/threat vs cooperation/solidarity framing",
                                "Two descriptive scales · 0.5 = corpus average · whiskers: 95% speech-level bootstrap",
                                self.caveat("no 'hardest' or 'softest' label is implied"), (0.2, 0.85), ncols_square=1)

    def emotion_profile(self):
        rk = self.t("style_rankings")
        rk = rk[rk["kind"] == "emotion"]
        panels = []
        for dim in dict.fromkeys(rk["dimension"]):
            sub = rk[rk["dimension"] == dim]
            panels.append({"title": sub["dimension_label"].iloc[0], "rows": [(r.leader, float(r.value), float(r.ci_low), float(r.ci_high)) for r in sub.itertuples()],
                           "ref": float(sub["corpus_mean"].iloc[0])})
        for f in self.formats:
            n = len(panels)
            fig = f.fig()
            if f.vertical:
                gs = GridSpec(n, 1, figure=fig, top=0.885, bottom=0.06, left=0.24, right=0.95, hspace=0.75)
            else:
                gs = GridSpec(int(np.ceil(n / 2)), 2, figure=fig, top=0.84, bottom=0.10, left=0.16, right=0.97, hspace=0.9, wspace=0.55)
            for i, p in enumerate(panels):
                ax = fig.add_subplot(gs[i] if f.vertical else gs[i // 2, i % 2])
                rows = sorted(p["rows"], key=lambda r: r[1], reverse=True)
                y = np.arange(len(rows))[::-1]
                ref = p["ref"]
                for yi, (L, v, lo, hi) in zip(y, rows):
                    ax.barh(yi, v - ref, left=ref, height=0.62, color=self.colors[L])
                    ax.plot([lo, hi], [yi, yi], color=INK2, linewidth=1.4)
                    ax.text(v, yi + 0.34, f"{v:.2f}", va="bottom", ha="center", fontsize=f.small * 0.8, color=INK2)
                ax.axvline(ref, color=MUTED, linewidth=1)
                ax.set_yticks(y, [self.names[L] for L, *_ in rows], fontsize=f.small)
                title = p["title"].replace("(positive − negative)", "(pos − neg)")
                ax.set_title(f"{title}\ncorpus mean {ref:.2f}", fontsize=f.label * 0.95, loc="left", pad=6)
                ax.xaxis.grid(True)
                strip_axes(ax)
                ax.tick_params(axis="x", labelsize=f.small * 0.8)
            self.header(fig, f, "Emotional tone of the speech sets", "Classifier probabilities (GoEmotions families + sentiment valence) · line = corpus mean · whiskers: 95% bootstrap")
            self.footer(fig, f, self.caveat("classifiers trained on Reddit/Twitter text; translated leaders scored on the English translation"))
            self.save(fig, "emotion_profile", f)

    def style_similarity(self):
        raw = self.t("style_similarity_leader")
        S = raw.set_index(raw.columns[0])
        names = [self.names[L] for L in S.index]
        M = S.to_numpy(float)
        off = M[~np.eye(len(M), dtype=bool)]
        pairs = self.t("style_pairs")
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", SEQ_BLUE)
        for f in self.formats:
            fig = f.fig()
            if f.vertical:
                gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 0.95], top=0.86, bottom=0.06, left=0.20, right=0.95, hspace=0.35)
                ax, ax2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
            else:
                ax, ax2 = fig.add_axes([0.20, 0.14, 0.72, 0.62]), None
            self._heat(ax, M, names, f, cmap, float(off.min()) - 0.05, float(off.max()) + 0.05, fmt="{:.2f}")
            ax.set_title("cosine similarity of standardised style profiles", fontsize=f.small, color=INK2, pad=8)
            if ax2 is not None:
                self._pair_bars(ax2, pairs, "style_distance", f, xlabel="style distance (z-scored dimensions) · 95% speech-level bootstrap", higher_is_closer=False)
                ax2.set_title("the ten pairs, most alike first", fontsize=f.small, color=INK2, loc="left")
            self.header(fig, f, "Style similarity between the speech sets", "Seven rhetorical dimensions + emotion families + valence, z-scored across speeches")
            self.footer(fig, f, self.caveat("style of the collected texts; translated leaders carry the translator's choices"))
            self.save(fig, "style_similarity_heatmap", f)
        # dendrogram
        from scipy.cluster.hierarchy import dendrogram

        Zl = np.load(path_for(self.cfg, "artifacts_bootstrap") / f"{self.model_key}{self.suffix}_style_linkage.npy")
        for f in self.formats:
            fig = f.fig(0.6 if f.vertical else 1.0)
            ax = fig.add_axes([0.10, 0.18, 0.85, 0.60])
            d = dendrogram(Zl, labels=names, ax=ax, color_threshold=0, above_threshold_color=INK2, leaf_font_size=f.base)
            for lbl in ax.get_xticklabels():
                L = next(k for k, v in self.names.items() if v == lbl.get_text())
                lbl.set_color(self.colors[L])
                lbl.set_fontweight("bold")
            ax.set_ylabel("style distance (average linkage)", fontsize=f.small)
            strip_axes(ax, keep=("left",))
            ax.yaxis.grid(True)
            self.header(fig, f, "Which speech sets sound alike?", "Hierarchical clustering of the style profiles · lower joins = more alike")
            self.footer(fig, f, self.caveat("descriptive grouping of the collected texts"))
            self.save(fig, "style_dendrogram", f)

    def content_vs_style(self):
        cvs = self.t("content_vs_style")
        rho = float(cvs["spearman_content_vs_style_cosine"].iloc[0])
        for f in self.formats:
            fig = f.fig(0.75 if f.vertical else 1.0)
            ax = fig.add_axes([0.14, 0.16, 0.80, 0.62])
            ax.scatter(cvs["content_similarity"], cvs["style_cosine"], s=110, color=INK2, zorder=3)
            x_hi = float(cvs["content_similarity"].max())
            x_lo = float(cvs["content_similarity"].min())
            ax.set_xlim(x_lo - 0.05 * (x_hi - x_lo) - 0.005, x_hi + 0.30 * (x_hi - x_lo))
            for r in cvs.itertuples():
                a, b = r.pair.split("–")
                near_right = r.content_similarity > x_hi - 0.15 * (x_hi - x_lo)
                ax.annotate(f"{self.names[a]}–{self.names[b]}", (r.content_similarity, r.style_cosine), textcoords="offset points",
                            xytext=(-8, 6) if near_right else (8, 6), ha="right" if near_right else "left", fontsize=f.small * 0.85, color=INK2)
            ax.set_xlabel("content similarity (leader-centroid cosine, embedding space)", fontsize=f.small)
            ax.set_ylabel("style similarity (cosine of style profiles)", fontsize=f.small)
            ax.grid(True)
            strip_axes(ax, keep=("left", "bottom"))
            self.header(fig, f, "Do sets that say similar things also sound alike?", f"Ten leader pairs · Spearman rank correlation = {rho:.2f}")
            self.footer(fig, f, self.caveat("content and style are measured independently"))
            self.save(fig, "content_vs_style_scatter", f)

    def dispersion(self):
        d = self.t("semantic_dispersion").set_index("leader")
        ci = self.t_opt("bootstrap_dispersion_ci")
        ci = ci.set_index("leader") if ci is not None else None
        specs = [("mean_dist_speech_to_leader", "Speech centres → leader centre"), ("mean_dist_chunk_to_speech", "Chunks → their speech centre")]
        for f in self.formats:
            fig = f.fig(0.85 if f.vertical else 1.0)
            gs = GridSpec(2, 1, figure=fig, top=0.84, bottom=0.08, left=0.22, right=0.95, hspace=0.6)
            for i, (col, title) in enumerate(specs):
                ax = fig.add_subplot(gs[i])
                order = sorted(self.leaders, key=lambda L: d.loc[L, col])
                y = np.arange(len(order))[::-1]
                for yi, L in zip(y, order):
                    v = float(d.loc[L, col])
                    ax.barh(yi, v, height=0.6, color=self.colors[L])
                    if i == 0 and ci is not None and L in ci.index:
                        ax.plot([ci.loc[L, "ci_low"], ci.loc[L, "ci_high"]], [yi, yi], color=INK2, linewidth=1.4)
                    ax.text(v + d[col].max() * 0.02, yi, f"{v:.3f}", va="center", fontsize=f.small * 0.9, color=INK2)
                ax.set_yticks(y, [self.names[L] for L in order], fontsize=f.small)
                ax.set_xlim(0, d[col].max() * 1.3)
                ax.set_title(title, fontsize=f.label, loc="left")
                ax.set_xlabel("mean cosine distance (higher = more spread)", fontsize=f.small * 0.85)
                ax.xaxis.grid(True)
                strip_axes(ax)
            self.header(fig, f, "How concentrated is each speech set?", "Semantic spread in the original embedding space · sorted, most concentrated first")
            self.footer(fig, f, self.caveat("bootstrap range biased downward; describes the corpus, not consistency of a person"))
            self.save(fig, "semantic_dispersion", f)

    def top_themes(self):
        top = self.t("top_themes_by_leader")
        top = top[top["method"] == "embedding_pct"]
        stab = self.t_opt("bootstrap_top_theme_stability")
        for f in self.formats:
            fig = f.fig()
            gs = GridSpec(len(self.leaders), 1, figure=fig, top=0.86 if f.vertical else 0.82, bottom=0.06, left=0.36, right=0.93, hspace=0.9 if not f.vertical else 0.7)
            for i, L in enumerate(self.leaders):
                ax = fig.add_subplot(gs[i])
                rows = top[top["leader"] == L].sort_values("rank")
                y = np.arange(len(rows))[::-1]
                for yi, r in zip(y, rows.itertuples()):
                    ax.barh(yi, r.value - 0.5, left=0.5, height=0.62, color=self.colors[L])
                    s = ""
                    if stab is not None:
                        q = stab[(stab["leader"] == L) & (stab["theme"] == r.theme)]
                        if len(q):
                            s = f"  ({q['share_top3'].iloc[0]:.0%} stable)"
                    ax.text(max(r.value, 0.5) + 0.01, yi, f"{r.value:.2f}{s}", va="center", fontsize=f.small * 0.85, color=INK2)
                ax.set_yticks(y, [self.tlabels[r.theme] for r in rows.itertuples()], fontsize=f.small)
                ax.axvline(0.5, color=MUTED, linewidth=1)
                ax.set_xlim(0.35, 0.95)
                ax.set_title(self.names[L], fontsize=f.label, loc="left", color=self.colors[L])
                ax.xaxis.grid(True)
                strip_axes(ax)
                ax.tick_params(axis="x", labelsize=f.small * 0.8)
            self.header(fig, f, "Three most represented themes per speech set", "Mean percentile (0.5 = corpus average) · 'stable' = share of bootstrap resamples keeping the theme in the top three")
            self.footer(fig, f, self.caveat("themes are measured, reasons are not inferred"))
            self.save(fig, "top_themes_by_leader", f)

    def language_effect(self):
        le = self.t_opt("language_effect_pairs", "")
        kn = self.t_opt("language_effect_knn", "")
        if le is None or kn is None:
            print("[visualization] language_effect skipped (tables missing — run robustness first)")
            return
        for f in self.formats:
            fig = f.fig()
            if f.vertical:
                gs = GridSpec(2, 1, figure=fig, height_ratios=[1.35, 1.0], top=0.86, bottom=0.06, left=0.12, right=0.88, hspace=0.35)
            else:
                gs = GridSpec(1, 2, figure=fig, width_ratios=[1.3, 1.0], top=0.80, bottom=0.10, left=0.10, right=0.92, wspace=0.55)
            ax = fig.add_subplot(gs[0])

            def spread(values: np.ndarray, min_gap: float) -> np.ndarray:
                """Nudge label positions apart so close values do not overprint (order preserved)."""
                order = np.argsort(values)
                out = values.astype(float).copy()
                for prev, cur in zip(order[:-1], order[1:]):
                    if out[cur] - out[prev] < min_gap:
                        out[cur] = out[prev] + min_gap
                return out

            span = float(le[["old_similarity", "new_similarity"]].max().max() - le[["old_similarity", "new_similarity"]].min().min())
            gap = span * (0.045 if f.vertical else 0.06)
            y_old = spread(le["old_similarity"].to_numpy(), gap)
            y_new = spread(le["new_similarity"].to_numpy(), gap)
            for i, r in enumerate(le.itertuples()):
                a, b = r.pair.split("–")
                col = self.colors["erdogan"] if "erdogan" in (a, b) else GRID
                lw = 2.6 if "erdogan" in (a, b) else 1.6
                ax.plot([0, 1], [r.old_similarity, r.new_similarity], color=col, linewidth=lw, zorder=3 if col != GRID else 2)
                ax.scatter([0, 1], [r.old_similarity, r.new_similarity], color=col, s=40, zorder=4)
                ax.text(-0.04, y_old[i], f"{self.names[a]}–{self.names[b]} {r.old_similarity:.2f}", ha="right", va="center", fontsize=f.small * 0.75, color=INK2)
                ax.text(1.04, y_new[i], f"{r.new_similarity:.2f}  {self.names[a]}–{self.names[b]}", ha="left", va="center", fontsize=f.small * 0.7, color=INK2)
            ax.set_xticks([0, 1], ["original languages\n(archived run)", "English\n(this run)"], fontsize=f.small)
            ax.set_xlim(-0.75, 1.75)
            ax.set_yticks([])
            strip_axes(ax, keep=())
            ax.set_title("leader-pair similarity, same model (Qwen3-Embedding-8B)", fontsize=f.small, color=INK2, loc="left")
            ax2 = fig.add_subplot(gs[1])
            y = np.arange(len(kn))[::-1]
            for yi, r in zip(y, kn.itertuples()):
                ax2.plot([r.old_same_leader_share, r.new_same_leader_share], [yi, yi], color=self.colors[r.leader], linewidth=2.4)
                ax2.scatter([r.old_same_leader_share], [yi], s=70, facecolors=SURFACE, edgecolors=self.colors[r.leader], linewidths=2, zorder=3)
                ax2.scatter([r.new_same_leader_share], [yi], s=70, color=self.colors[r.leader], zorder=3)
                ax2.text(max(r.old_same_leader_share, r.new_same_leader_share) + 0.02, yi, f"{r.old_same_leader_share:.0%} → {r.new_same_leader_share:.0%}", va="center", fontsize=f.small * 0.8, color=INK2)
            ax2.set_yticks(y, [self.names[r.leader] for r in kn.itertuples()], fontsize=f.small)
            ax2.set_xlim(0, 1.25)
            ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "25%", "50%", "75%", "100%"], fontsize=f.small * 0.8)
            ax2.xaxis.grid(True)
            strip_axes(ax2)
            ax2.set_title("share of a chunk's 10 nearest neighbours from the same leader (hollow = original, filled = English)", fontsize=f.small * 0.85, color=INK2, loc="left", wrap=True)
            self.header(fig, f, "What changed when everything became English?", "Same embedding model on both corpora · Erdoğan pairs highlighted")
            self.footer(fig, f, "Original-language results from old_results/ (2026-09-22). Translation removes the language signal but adds the translator's voice.")
            self.save(fig, "language_effect", f)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phase 6: Instagram-format plots.")
    ap.add_argument("--config", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--formats", default=None, help="comma list of format names from config (default: all)")
    ap.add_argument("--only", default=None, help="comma list of figure groups")
    args = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    cfg = load_config(args.config)
    seed_everything(int(cfg["random_seed"]))
    formats = args.formats.split(",") if args.formats else list(cfg["visualization"]["formats"].keys())
    setup_style(px2pt(int(cfg["visualization"].get("base_font_px", 22))))
    viz = Viz(cfg, args.model or primary_model_key(cfg), args.suffix, formats)
    steps = ["radars", "rhetorical_radars", "heatmap", "projections", "theme_comparison", "rhetorical_rankings", "emotion_profile",
             "style_similarity", "content_vs_style", "dispersion", "top_themes", "language_effect"]
    if args.only:
        steps = [s for s in args.only.split(",") if s in steps]
    for s in steps:
        try:
            getattr(viz, s)()
            print(f"[visualization] {s} done")
        except FileNotFoundError as exc:
            print(f"[visualization] {s} skipped (missing input: {Path(str(exc)).name})")
    print(f"[visualization] plots in {viz.plots} (tag '{viz.tag}', formats {formats})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
