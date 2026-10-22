"""Side-by-side comparison of the selected config of every method on the validation harness.

Re-runs popularity, repeat (best of repeat_v2 + beta extension), ALS and CBF with the parameters stored in
docs/best_params.json (deterministic, seed 42) and checks that the selection scores match the logged grid runs.
Extra diagnostics on the 1,260 test users:
  already_watched  share of recommended ids the user watched in the history window (any labelled overlap)
  no_history       share of recommended ids nobody watched in the history window
  gt_hit           share of ground-truth target shows that appear in the method's top-5
  gt_hit_not_rep   share of ground-truth target shows in the method's top-5 but NOT in repeat's top-5
  gt_hit_union     share of ground-truth target shows in the union of the method's and repeat's top-5

Usage: python -m src.compare_methods   ->  docs/methods_results.md
"""
import datetime as dt
import time

import numpy as np

from src import als, cbf
from src.data import ROOT
from src.evaluation import evaluate, fill, selection_score, window
from src.method_utils import Context, load_best
from src.repeat_v2 import POP_N, predict as repeat_predict

OUT_MD = ROOT / "docs" / "methods_results.md"


def main() -> None:
    t_all = time.time()
    ctx = Context()
    best = load_best()
    users = ctx.data.populations["test_users"]
    raw = {
        "popularity": ({"n_weeks": POP_N}, {}),
        "repeat": (best["repeat"], repeat_predict(ctx.st, best["repeat"], ctx.users)[1]),
        "als": (best["als"], als.predict(ctx, best["als"])),
        "cbf": (best["cbf"], cbf.predict(ctx, best["cbf"])),
    }
    preds = {m: fill(r, ctx.users, ctx.st.fallback) for m, (_, r) in raw.items()}

    hist = window(ctx.data.usw, ctx.st.hist_weeks)
    user_hist = hist.groupby("user_id")["tv_show_id"].agg(set).to_dict()
    watched_any = set(hist["tv_show_id"].unique().tolist())

    rows = []
    for m, (params, _) in raw.items():
        res = evaluate(preds[m], ctx.data)
        sel = selection_score(res)
        if f"{m}_select" in best:
            # logged scores are rounded to 6 decimals in experiments.csv
            assert abs(sel - best[f"{m}_select"]) < 1e-6, f"{m}: {sel} != logged {best[f'{m}_select']}"
        recs = [preds[m][u] for u in users]
        rep = [set(preds["repeat"][u]) for u in users]
        flat = [x for r in recs for x in r]
        row = {"method": m, "params": params, "select": sel,
               **{f"{p}/{d}": v[1] for (p, d), v in res.items()},
               "already_watched": np.mean([x in user_hist.get(u, set()) for u, r in zip(users, recs) for x in r]),
               "no_history": np.mean([x not in watched_any for x in flat]),
               "users_with_no_history_rec": np.mean([any(x not in watched_any for x in r) for r in recs])}
        for d in ("n_days", "n_airings"):
            gt = [set(ctx.data.gts[d].get(u, [])) for u in users]
            n_gt = sum(len(g) for g in gt)
            row[f"gt_hit/{d}"] = sum(len(g & set(r)) for g, r in zip(gt, recs)) / n_gt
            row[f"gt_hit_not_rep/{d}"] = sum(len(g & (set(r) - rp)) for g, r, rp in zip(gt, recs, rep)) / n_gt
            row[f"gt_hit_union/{d}"] = sum(len(g & (set(r) | rp)) for g, r, rp in zip(gt, recs, rep)) / n_gt
        rows.append(row)
        print(m, f"select={sel:.4f}", flush=True)

    def f(v):
        return f"{v:.4f}"

    lines = ["# Method comparison (validation)", "",
             f"Produced by `python -m src.compare_methods` on {dt.datetime.now():%Y-%m-%d %H:%M}. History weeks "
             f"{ctx.st.hist_weeks[0]}-{ctx.st.hist_weeks[1]}, target weeks 21-30, pool = {len(ctx.st.pool)} labelled "
             "shows airing in weeks 21-30, repeats allowed, shared fallback = popularity (watch seconds, last "
             f"{POP_N} history weeks). MAP@5; `select` = mean of n_days and n_airings targets on the "
             f"{len(users)} test users. Selection scores were checked against the logged grid runs.", "",
             "## Accuracy", "",
             "| method | select | test: n_days | test: n_airings | test: watch_sec | active_both: n_days | "
             "active_both: n_airings | already watched | no-history ids | users with a no-history id |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['method']} | {f(r['select'])} | {f(r['test_users/n_days'])} | {f(r['test_users/n_airings'])} | "
                     f"{f(r['test_users/watch_sec'])} | {f(r['active_both/n_days'])} | {f(r['active_both/n_airings'])} | "
                     f"{f(r['already_watched'])} | {f(r['no_history'])} | {f(r['users_with_no_history_rec'])} |")
    lines += ["", "`already watched` and `no-history ids` are shares of all recommended ids (5 per test user); "
              "the last column is the share of test users with at least one no-history id in their top-5.", "",
              "## Complementarity with repeat (test users)", "",
              "| method | target | GT shows hit | hit and not in repeat top-5 | hit by method or repeat |",
              "|---|---|---|---|---|"]
    for r in rows:
        for d in ("n_days", "n_airings"):
            lines.append(f"| {r['method']} | {d} | {f(r[f'gt_hit/{d}'])} | {f(r[f'gt_hit_not_rep/{d}'])} | "
                         f"{f(r[f'gt_hit_union/{d}'])} |")
    lines += ["", "Shares are over all ground-truth target shows of the test users (up to 5 per user).", "",
              "## Selected parameters", ""]
    lines += [f"- {r['method']}: `{r['params']}`" for r in rows]
    lines += ["", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
