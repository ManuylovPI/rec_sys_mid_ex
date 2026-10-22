"""Repeat re-tuned on the cov50 target, plus every component re-scored on that target.

score(u, s) = sum_w c(u, s, w) * d(w)                      (plain)
            = sum_w c d / (sum_w A(s, w) d + beta) * T(s)   (loyalty: share of the show's airings the user covered,
                                                             times its airings in the target window)
c = airings (or distinct days) where one view covers more than `cut` of the airing, from the merged continuous
intervals ("merged") or raw single views ("raw"); A, T = the show's airings (or airing days) per history week /
in the target window; d = 0.5 ** ((last week - w) / half_life) or 1. Optional filter: keep only shows with
c >= min_count. Ties: shared popularity score ("pop") or tv_show_id ("id"). Pool and fallback as everywhere.

Usage: python -m src.repeat_v3   ->  experiments.csv rows, docs/repeat_v3_results.md, docs/best_params.json
"""
import datetime as dt
import itertools
import time

import numpy as np
import pandas as pd

from src import als, cbf
from src.data import PROCESSED, ROOT
from src.evaluation import window
from src.method_utils import RESULT_COLS, Context, load_best, results_table, save_best
from src.metrics import K
from src.repeat_v2 import POP_N, predict as repeat_v2_predict
from src.repeat_cont import ranked as cont_ranked
from src.slots import SlotModel, ranked_from_scores
from src.evaluation import top_k_lists

OUT_MD = ROOT / "docs" / "repeat_v3_results.md"
SOURCES = {"merged": PROCESSED / "coverage.parquet", "raw": PROCESSED / "coverage_raw.parquet"}
CUTS = [0.3, 0.5, 0.8]
UNITS = ["airings", "days"]
HALF_LIVES = [None, 8, 4]
SCALES = ["plain", "loyalty5", "loyalty10"]


class CovCounts:
    """Per (user, show, week) coverage counts for one history window."""

    def __init__(self, con, usw, st, hist_weeks):
        self.st, self.hw = st, hist_weeks
        self.counts = {}
        for src, path in SOURCES.items():
            for cut in CUTS:
                self.counts[(src, cut)] = con.sql(f"""
                    SELECT user_id, tv_show_id, week, count(*) AS airings, count(DISTINCT day) AS days
                    FROM '{path.as_posix()}' WHERE week BETWEEN {hist_weeks[0]} AND {hist_weeks[1]} AND cont_frac > {cut}
                    GROUP BY ALL""").df()
        h = window(usw, (hist_weeks[1] - POP_N + 1, hist_weeks[1]))
        self.pop = h.groupby("tv_show_id")["watch_sec"].sum()

    def scores(self, p: dict) -> pd.DataFrame:
        c = self.counts[(p.get("source", "merged"), p["cut"])]
        c = c[c["tv_show_id"].isin(self.st.pool.index)]
        hl, h1 = p["half_life"], self.hw[1]
        d = 1.0 if hl is None else 0.5 ** ((h1 - c["week"]) / hl)
        df = c[["user_id", "tv_show_id"]].assign(w=c[p["unit"]] * d, raw=c[p["unit"]]) \
            .groupby(["user_id", "tv_show_id"], as_index=False)[["w", "raw"]].sum()
        if p["scale"].startswith("loyalty"):
            beta = float(p["scale"].removeprefix("loyalty"))
            sched_unit = "n_airings" if p["unit"] == "airings" else "n_days"
            sw = self.st.show_week
            sd = 1.0 if hl is None else 0.5 ** ((h1 - sw["week"]) / hl)
            a = sw[["tv_show_id"]].assign(a=sw[sched_unit] * sd).groupby("tv_show_id")["a"].sum()
            av = np.maximum(a.reindex(df["tv_show_id"]).fillna(0).to_numpy(), df["w"].to_numpy())
            t = self.st.target[sched_unit].reindex(df["tv_show_id"]).fillna(0).to_numpy()
            df["score"] = df["w"] / (av + beta) * t
        else:
            df["score"] = df["w"]
        if p.get("min_count", 1) > 1:
            df = df[df["raw"] >= p["min_count"]]
        return df

    def ranked(self, p: dict, k: int = K) -> dict[int, list[int]]:
        df = self.scores(p)
        if p.get("tie", "pop") == "pop":
            df = df.assign(pop=self.pop.reindex(df["tv_show_id"]).fillna(0).to_numpy())
            return top_k_lists(df, ["score", "pop"], k)
        return top_k_lists(df, ["score"], k)


def predict(cc: CovCounts, p: dict) -> dict[int, list[int]]:
    return cc.ranked(p)


def main() -> None:
    t_all = time.time()
    ctx = Context()
    best = load_best()
    note = "cov50 target"

    # ---- references on the new target
    t = time.time()
    ctx.run("popularity", {"n_weeks": POP_N}, {}, t, note)
    t = time.time()
    ctx.run("repeat_v2", best["repeat"], repeat_v2_predict(ctx.st, best["repeat"], ctx.users)[1], t, note)
    t = time.time()
    ctx.run("repeat_cont", {"cut": 0.5, "tie": "pop", "history": "whole window, no decay"},
            cont_ranked(ctx.con, ctx.data.usw, (11, 20), ctx.st.pool, 0.5, "pop"), t, note)
    t = time.time()
    a = ctx.run("als", best["als"], als.predict(ctx, best["als"]), t, note)
    t = time.time()
    c = ctx.run("cbf", best["cbf"], cbf.predict(ctx, best["cbf"]), t, note)
    t = time.time()
    sp_ = best["slot"]
    sm = SlotModel(ctx.con, (11, 20), (21, 30), sp_["daytype"], sp_["half_life"])
    known, sc = sm.scores(ctx.users, sp_["agg"])
    s = ctx.run("slot", sp_, ranked_from_scores(known, sc, sm.shows, ctx.st.pool.index), t, note)
    n_ref = len(ctx.rows)

    # ---- repeat grid on cov50
    cc = CovCounts(ctx.con, ctx.data.usw, ctx.st, (11, 20))
    for cut, unit, hl, scale in itertools.product(CUTS, UNITS, HALF_LIVES, SCALES):
        t = time.time()
        p = {"source": "merged", "cut": cut, "unit": unit, "half_life": hl, "scale": scale, "tie": "pop", "min_count": 1}
        ctx.run("repeat_cov", p, cc.ranked(p), t, note)
    top = ctx.best("repeat_cov")["params"]
    for var in ({"source": "raw"}, {"tie": "id"}, {"min_count": 2}, {"min_count": 3}):
        t = time.time()
        p = {**top, **var}
        ctx.run("repeat_cov", p, cc.ranked(p), t, f"{note}; variant of best")
    rep = ctx.best("repeat_cov")
    save_best("repeat_loyalty", best["repeat"])  # old loyalty config, still used for hybrid features
    save_best("repeat_cov", rep["params"])
    for key, r in (("repeat_cov", rep), ("als", a), ("cbf", c), ("slot", s)):
        save_best(f"{key}_select", r["select"])

    lines = ["# Repeat on the cov50 target", "",
             f"Produced by `python -m src.repeat_v3` on {dt.datetime.now():%Y-%m-%d %H:%M}. History 11-20, target 21-30, "
             "test users / active_both, shared popularity fallback. `select` = MAP@5 on cov50 (one merged continuous "
             "view covering > 50% of the airing, counted as airings) on the test users.", "",
             "## Components re-scored on cov50", "", *results_table(ctx.rows[:n_ref], RESULT_COLS), "",
             "## Repeat grid (cov50)", "", *results_table(ctx.rows[n_ref:], RESULT_COLS), "",
             f"Selected repeat: `{rep['params']}` (select {rep['select']:.4f}).", "",
             f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
