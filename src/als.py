"""Implicit ALS on the user x show matrix of the history weeks.

Confidence input: decayed distinct viewing days per (user, show), no watch threshold,
d(w) = 0.5 ** ((last_hist_week - w) / 8) (the unit and decay that won for repeat). Optionally BM25-weighted.
All shows watched in history are in the matrix; recommendations are restricted to the candidate pool
(shows airing in the target window) and already-watched shows are NOT filtered. Shows never watched in
history have no item factor and cannot be recommended by ALS. Users outside the matrix get the shared fallback.

Usage: python -m src.als [--extend]   ->  experiments.csv rows, docs/als_results.md, docs/best_params.json
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")  # recommended by implicit; ALS itself is multithreaded

import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import implicit  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from implicit.nearest_neighbours import bm25_weight  # noqa: E402

from src.data import ROOT, SEED  # noqa: E402
from src.method_utils import RESULT_COLS, Context, load_best, results_table, save_best  # noqa: E402
from src.metrics import K  # noqa: E402

OUT_MD = ROOT / "docs" / "als_results.md"
HALF_LIFE = 8
WEIGHTINGS = ["raw", "bm25"]
FACTORS = [32, 64, 128]
REGS = [0.01, 0.1]
ALPHAS = [1.0, 10.0, 40.0]
ITERS = [15, 30]
BM25_K1, BM25_B = 100, 0.8
# --extend: the first grid peaked at its smallest factors and alpha, so it is extended in that direction
EXT_FACTORS = [8, 16, 32]
EXT_ALPHAS = [0.1, 0.3, 1.0]
EXT_ITERS = [15]


class AlsData:
    def __init__(self, st):
        u = st.user_week["none"]
        w = u["n_days"] * 0.5 ** ((st.hist_weeks[1] - u["week"]) / HALF_LIFE)
        df = u[["user_id", "tv_show_id"]].assign(w=w).groupby(["user_id", "tv_show_id"], as_index=False)["w"].sum()
        self.users = np.sort(df["user_id"].unique())
        self.items = np.sort(df["tv_show_id"].unique())
        ui = np.searchsorted(self.users, df["user_id"].to_numpy())
        ii = np.searchsorted(self.items, df["tv_show_id"].to_numpy())
        self.matrix = sp.csr_matrix((df["w"].to_numpy(np.float32), (ui, ii)), shape=(len(self.users), len(self.items)))
        in_pool = np.isin(self.items, st.pool.index.to_numpy())
        self.pool_cols = np.flatnonzero(in_pool)
        self.user_pos = {int(u): i for i, u in enumerate(self.users)}


def fit_predict(ad: AlsData, users: list[int], weighting: str, factors: int, reg: float, alpha: float,
                iters: int) -> dict[int, list[int]]:
    m = ad.matrix
    if weighting == "bm25":
        m = bm25_weight(m, K1=BM25_K1, B=BM25_B).tocsr().astype(np.float32)
    model = implicit.cpu.als.AlternatingLeastSquares(factors=factors, regularization=reg, alpha=alpha,
                                                     iterations=iters, random_state=SEED)
    model.fit(m, show_progress=False)
    known = [u for u in users if u in ad.user_pos]
    uf = model.user_factors[[ad.user_pos[u] for u in known]]
    scores = uf @ model.item_factors[ad.pool_cols].T
    top = np.argpartition(-scores, K, axis=1)[:, :K]
    out = {}
    for row, u in enumerate(known):
        cols = top[row][np.argsort(-scores[row, top[row]], kind="stable")]
        out[u] = [int(x) for x in ad.items[ad.pool_cols[cols]]]
    return out


def predict(ctx: Context, params: dict) -> dict[int, list[int]]:
    return fit_predict(AlsData(ctx.st), ctx.users, **{k: params[k] for k in
                                                      ("weighting", "factors", "reg", "alpha", "iters")})


def main() -> None:
    extend = "--extend" in sys.argv
    factors, alphas, iters = (EXT_FACTORS, EXT_ALPHAS, EXT_ITERS) if extend else (FACTORS, ALPHAS, ITERS)
    t_all = time.time()
    ctx = Context()
    ad = AlsData(ctx.st)
    print(f"matrix {ad.matrix.shape}, nnz {ad.matrix.nnz}, pool items with factors {len(ad.pool_cols)}", flush=True)
    for weighting, f, reg, a, it in itertools.product(WEIGHTINGS, factors, REGS, alphas, iters):
        t = time.time()
        p = {"weighting": weighting, "factors": f, "reg": reg, "alpha": a, "iters": it, "conf": f"n_days_hl{HALF_LIFE}"}
        if weighting == "bm25":
            p.update(bm25_k1=BM25_K1, bm25_b=BM25_B)
        ctx.run("als", p, fit_predict(ad, ctx.users, weighting, f, reg, a, it), t, "grid extension" if extend else "")
    best = ctx.best("als")
    out_md = OUT_MD.with_name("als_results_extension.md") if extend else OUT_MD
    if extend:
        prev = load_best().get("als_select")
        if prev is None or best["select"] > prev:
            save_best("als", best["params"])
            save_best("als_select", best["select"])
    else:
        save_best("als", best["params"])
        save_best("als_select", best["select"])
    lines = ["# Implicit ALS: validation results", "",
             f"Produced by `python -m src.als{' --extend' if extend else ''}` on {dt.datetime.now():%Y-%m-%d %H:%M}, implicit {implicit.__version__}, "
             f"random_state {SEED}. Matrix: {ad.matrix.shape[0]} users x {ad.matrix.shape[1]} shows (weeks 11-20), "
             f"{ad.matrix.nnz} non-zeros; {len(ad.pool_cols)} of {len(ctx.st.pool)} pool shows have item factors. "
             "Already-watched shows are not filtered. Same harness and selection as repeat_v2.", "",
             *results_table(ctx.rows, RESULT_COLS), "",
             f"Selected: `{best['params']}` (select {best['select']:.4f}).", "",
             f"Total runtime: {time.time() - t_all:.1f} s."]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
