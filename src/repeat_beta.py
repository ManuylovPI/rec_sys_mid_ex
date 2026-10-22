"""Extend the loyalty smoothing grid (beta in 10, 20, 50) and store the best repeat config as the repeat baseline.

Usage: python -m src.repeat_beta   ->  experiments.csv rows, docs/repeat_beta_results.md, docs/best_params.json
"""
import datetime as dt
import itertools
import time

from src.data import ROOT
from src.method_utils import RESULT_COLS, Context, results_table, save_best
from src.repeat_v2 import DELTAS, LOY_HALF_LIVES, THRESHOLDS, UNITS, predict

OUT_MD = ROOT / "docs" / "repeat_beta_results.md"
BETAS_EXT = [10, 20, 50]
V2_SUBMITTED = {"score": "loyalty", "unit": "n_days", "threshold": "none", "half_life": 8, "beta": 5, "delta": 1.0,
                "fill": "channels_m3"}


def main() -> None:
    t_all = time.time()
    ctx = Context()
    t = time.time()
    ctx.run("repeat_v2", V2_SUBMITTED, predict(ctx.st, V2_SUBMITTED, ctx.users)[1], t, "reference: repeat_v2 submitted")
    for unit, thr, hl, beta, delta in itertools.product(UNITS, THRESHOLDS, LOY_HALF_LIVES, BETAS_EXT, DELTAS):
        t = time.time()
        p = {"score": "loyalty", "unit": unit, "threshold": thr, "half_life": hl, "beta": beta, "delta": delta,
             "fill": "global"}
        ctx.run("repeat_v2", p, predict(ctx.st, p, ctx.users)[1], t, "beta extension")
    top = max((r for r in ctx.rows[1:]), key=lambda r: r["select"])
    t = time.time()
    p3 = {**top["params"], "fill": "channels_m3"}
    ctx.run("repeat_v2", p3, predict(ctx.st, p3, ctx.users)[1], t, "beta extension, channel fill")
    best = ctx.best("repeat_v2")
    save_best("repeat", best["params"])

    lines = ["# Repeat v2: beta extension", "",
             f"Produced by `python -m src.repeat_beta` on {dt.datetime.now():%Y-%m-%d %H:%M}. Same harness and selection "
             "as docs/repeat_v2_results.md (beta 0/1/5 results are there). First row is the submitted repeat_v2 "
             "config re-evaluated as reference.", "",
             *results_table(ctx.rows, RESULT_COLS), "",
             f"Selected as the repeat baseline: `{best['params']}` (select {best['select']:.4f}).", "",
             f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
