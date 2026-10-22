"""Re-evaluate the selected components on the time-zone-fixed data (docs/errata.md) and re-select repeat.

repeat is re-selected on the n_days target with a compact loyalty grid around the previous optimum
(unit n_days / n_airings, beta 1 / 5 / 10 / 20, half-life 8 / none, no threshold, delta 1), plus the channel
fill for the best one. ALS, CBF, slot habits and popularity keep their selected parameters and are re-scored.

Usage: python -m src.refresh   ->  experiments.csv rows (data=tzfix), docs/refresh_after_tzfix.md, docs/best_params.json
"""
import datetime as dt
import itertools
import time

import pandas as pd

from src import als, cbf
from src.data import ROOT
from src.method_utils import Context, load_best, save_best
from src.repeat_v2 import POP_N, predict as repeat_predict
from src.slots import SlotModel, ranked_from_scores

OUT_MD = ROOT / "docs" / "refresh_after_tzfix.md"


def main() -> None:
    t_all = time.time()
    best = load_best()
    old = {k: best.get(f"{k}_select") for k in ("repeat", "als", "cbf", "slot")}
    ctx = Context()
    note = "refresh after tz fix"

    t = time.time()
    pop = ctx.run("popularity", {"n_weeks": POP_N}, {}, t, note)

    for unit, beta, hl in itertools.product(["n_days", "n_airings"], [1, 5, 10, 20], [8, None]):
        t = time.time()
        p = {"score": "loyalty", "unit": unit, "threshold": "none", "half_life": hl, "beta": beta, "delta": 1.0,
             "fill": "global"}
        ctx.run("repeat_v2", p, repeat_predict(ctx.st, p, ctx.users)[1], t, note)
    top = ctx.best("repeat_v2")
    t = time.time()
    p3 = {**top["params"], "fill": "channels_m3"}
    ctx.run("repeat_v2", p3, repeat_predict(ctx.st, p3, ctx.users)[1], t, note)
    rep = ctx.best("repeat_v2")
    save_best("repeat", rep["params"])
    save_best("repeat_select", rep["select"])

    t = time.time()
    a = ctx.run("als", best["als"], als.predict(ctx, best["als"]), t, note)
    save_best("als_select", a["select"])
    t = time.time()
    c = ctx.run("cbf", best["cbf"], cbf.predict(ctx, best["cbf"]), t, note)
    save_best("cbf_select", c["select"])
    t = time.time()
    sp_ = best["slot"]
    sm = SlotModel(ctx.con, (11, 20), (21, 30), sp_["daytype"], sp_["half_life"])
    known, sc = sm.scores(ctx.users, sp_["agg"])
    s = ctx.run("slot", sp_, ranked_from_scores(known, sc, sm.shows, ctx.st.pool.index), t, note)
    save_best("slot_select", s["select"])

    rows = [("popularity", 0.3174, pop), ("repeat", old["repeat"], rep), ("als", old["als"], a),
            ("cbf", old["cbf"], c), ("slot habits", old["slot"], s)]
    lines = ["# Components re-scored after the time-zone fix", "",
             f"Produced by `python -m src.refresh` on {dt.datetime.now():%Y-%m-%d %H:%M}. Test users, MAP@5 on n_days "
             "(selection target). `before` = value on the shifted day counts (docs/errata.md).", "",
             "| method | params after | n_days before | n_days after | n_airings after | watch_sec after |",
             "|---|---|---|---|---|---|"]
    for name, before, r in rows:
        lines.append(f"| {name} | `{r['params']}` | {before:.4f} | {r['test_users/n_days']:.4f} | "
                     f"{r['test_users/n_airings']:.4f} | {r['test_users/watch_sec']:.4f} |")
    grid = pd.DataFrame([{"params": str(r["params"]), "n_days": r["test_users/n_days"]} for r in ctx.rows
                         if r["method"] == "repeat_v2"]).sort_values("n_days", ascending=False)
    lines += ["", "## Repeat re-selection grid (n_days, test users)", "", "| params | n_days |", "|---|---|"]
    lines += [f"| `{r.params}` | {r.n_days:.4f} |" for r in grid.itertuples()]
    lines += ["", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
