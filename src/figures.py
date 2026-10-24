"""Report figures (PNG) in reports/figures/.

  coverage_distribution.png  share of each airing covered by the user's best single continuous view, with the
                             30 / 50 / 80% cut-offs used for the coverage targets and features
  validation_map5.png        validation MAP@5 per method on cov50 and cov80 (docs/results_table.csv)
  leaderboard.png            public and private score of every Kaggle submission, in order (submissions/LOG.md)

Colours: reference categorical slots 1-2 (blue #2a78d6, orange #eb6834), validated for CVD separation and
contrast on the light surface. Every two-series chart has a legend and direct labels.

Usage: python -m src.figures
"""
import re

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.data import PROCESSED, ROOT  # noqa: E402

OUT = ROOT / "reports" / "figures"
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
STEPS = {  # what changed at each submission (submissions/LOG.md)
    "popularity_v1.csv": "popularity baseline",
    "repeat_v1.csv": "personal repeat (log seconds)",
    "repeat_v2.csv": "loyalty repeat, any-overlap days",
    "repeat_cont50.csv": "> 50% continuous watches (label fix)",
    "hybrid_v2.csv": "LightGBM re-ranker on cov50 labels",
    "hybrid_v3_lr.csv": "top-50 candidates, extra features, 3-fold refit",
    "hybrid_v3_ens.csv": "same, lambdarank + binary ensemble",
    "hybrid_v3_lr_seeds.csv": "same, lambdarank x 3 seeds",
    "hybrid_v4_recent.csv": "5 recency-weighted folds",
    "hybrid_v4_cov80.csv": "5 folds + cov80 labels (final)",
}


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def coverage_figure() -> None:
    frac = duckdb.connect().sql(
        f"SELECT cont_frac FROM '{(PROCESSED / 'coverage.parquet').as_posix()}'").df()["cont_frac"].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SURFACE)
    bins = np.linspace(0, 1, 41)
    w = np.full(len(frac), 100 / len(frac))
    ax.hist(frac, bins=bins, weights=w, color=BLUE, edgecolor=SURFACE, linewidth=1)
    top = ax.get_ylim()[1]
    for cut, height in ((0.3, 0.92), (0.5, 0.78), (0.8, 0.64)):  # staggered so the labels do not collide
        share = (frac > cut).mean() * 100
        ax.axvline(cut, color=INK, linewidth=1, linestyle=(0, (3, 3)))
        left = cut > 0.7  # the last label goes left of its line, clear of the 100% bar
        ax.text(cut - 0.01 if left else cut + 0.01, top * height, f"> {int(cut * 100)}%: {share:.1f}% of pairs",
                color=INK, fontsize=9, ha="right" if left else "left")
    style(ax)
    ax.set_xlabel("share of the airing covered by the best single continuous view", color=INK)
    ax.set_ylabel("% of (user, airing) pairs", color=INK)
    ax.set_title(f"Coverage of labelled airings by one continuous view ({len(frac):,} pairs, weeks 11-30)",
                 color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "coverage_distribution.png", dpi=180)
    plt.close(fig)


def validation_figure() -> None:
    t = pd.read_csv(ROOT / "docs" / "results_table.csv")
    t = t.iloc[::-1].reset_index(drop=True)  # best (final) at the top
    y = np.arange(len(t))
    h = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=SURFACE)
    ax.barh(y + h / 2, t["main_cov50"], height=h, color=BLUE, label="cov50 (> 50% watched)")
    ax.barh(y - h / 2, t["main_cov80"], height=h, color=ORANGE, label="cov80 (> 80% watched)")
    for yi, v in zip(y, t["main_cov50"]):
        ax.text(v + 0.004, yi + h / 2, f"{v:.3f}", va="center", fontsize=8, color=INK)
    ax.set_yticks(y, t["method"])
    style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("validation MAP@5 (1,260 test users, weeks 21-30)", color=INK)
    ax.set_title("Validation MAP@5 per method", color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_xlim(0, max(t["main_cov50"].max(), t["main_cov80"].max()) * 1.15)
    fig.tight_layout()
    fig.savefig(OUT / "validation_map5.png", dpi=180)
    plt.close(fig)


def leaderboard_figure() -> None:
    rows = []
    for ln in (ROOT / "submissions" / "LOG.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0] in STEPS and re.fullmatch(r"0\.\d+", cells[3] or ""):
            rows.append((cells[0], float(cells[3]), float(cells[4]), cells[5]))
    d = pd.DataFrame(rows, columns=["file", "public", "private", "kaggle"])
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURFACE)
    ax.plot(x, d["public"], color=BLUE, linewidth=2, marker="o", markersize=7, label="public")
    ax.plot(x, d["private"], color=ORANGE, linewidth=2, marker="s", markersize=7, label="private")
    for xi, pub, prv in zip(x, d["public"], d["private"]):
        ax.text(xi, pub + 0.008, f"{pub:.3f}", ha="center", fontsize=7.5, color=INK)
        ax.text(xi, prv - 0.017, f"{prv:.3f}", ha="center", fontsize=7.5, color=MUTED)
    ax.set_xticks(x, [f"{i + 1}. {STEPS[f]}" for i, f in enumerate(d["file"])], rotation=35, ha="right", fontsize=8)
    style(ax)
    ax.set_ylabel("MAP@5 on Kaggle", color=INK)
    ax.set_ylim(0.2, 0.5)
    ax.set_title("Leaderboard progression of all submissions (final = last point)", color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "leaderboard.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    coverage_figure()
    validation_figure()
    leaderboard_figure()
    print(f"wrote figures to {OUT}")


if __name__ == "__main__":
    main()
