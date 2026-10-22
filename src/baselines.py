"""Popularity baseline and personal-repeat baseline: validation grid, then refit and submission files.

popularity(N):  total watch seconds per show over the last N history weeks, pool only. The selected N
                is the cold-start / top-up fallback for every method.
repeat(h, transform, alpha):
                score(u, s) = sum_w x(u, s, w) * 0.5 ** ((last_hist_week - w) / h) * airtime(s) ** alpha
                x = watch_sec (raw) or log1p(watch_sec) (log, applied per user-show-week before the sum);
                h = None means no decay; airtime(s) = seconds the show airs in the target window (schedule only).
                Pool shows only; repeats allowed; topped up with the popularity fallback.

Usage: python -m src.baselines   ->  experiments.csv rows, docs/baselines_results.md,
                                     submissions/popularity_v1.csv, submissions/repeat_v1.csv
"""
import datetime as dt
import itertools
import time

import numpy as np
import pandas as pd

from src.data import ROOT
from src.evaluation import (FINAL_HIST_WEEKS, HIST_WEEKS, TARGET_DEFS, TEST_WEEKS, evaluate, fill, log_results,
                            pool_airtime, selection_score, test_users, top_k_lists, validation_data, window)
from src.metrics import K
from src.submission import check_submission, write_submission

OUT_MD = ROOT / "docs" / "baselines_results.md"
SUB_DIR = ROOT / "submissions"

POP_N = [1, 2, 4, 10]
HALF_LIVES = [1, 2, 4, 8, None]
TRANSFORMS = ["raw", "log"]
ALPHAS = [0.0, 0.5, 1.0]
FALLBACK_LEN = 50


def popularity_list(usw: pd.DataFrame, hist_weeks: tuple[int, int], n_weeks: int, pool: pd.DataFrame,
                    length: int = FALLBACK_LEN) -> list[int]:
    h = window(usw, (hist_weeks[1] - n_weeks + 1, hist_weeks[1]))
    s = h[h["tv_show_id"].isin(pool.index)].groupby("tv_show_id")["watch_sec"].sum()
    s = s.reset_index().sort_values(["watch_sec", "tv_show_id"], ascending=[False, True])
    return [int(x) for x in s["tv_show_id"].head(length)]


def repeat_ranked(usw: pd.DataFrame, hist_weeks: tuple[int, int], pool: pd.DataFrame,
                  half_life: float | None, transform: str, alpha: float) -> dict[int, list[int]]:
    h = window(usw, hist_weeks)
    h = h[h["tv_show_id"].isin(pool.index)]
    x = h["watch_sec"].astype(float)
    if transform == "log":
        x = np.log1p(x)
    if half_life is not None:
        x = x * 0.5 ** ((hist_weeks[1] - h["week"]) / half_life)
    df = h[["user_id", "tv_show_id"]].assign(score=x).groupby(["user_id", "tv_show_id"], as_index=False)["score"].sum()
    if alpha:
        df["score"] *= pool["airtime_sec"].reindex(df["tv_show_id"]).to_numpy(dtype=float) ** alpha
    return top_k_lists(df, ["score"])


def fallback_slots(ranked: dict[int, list[int]], users: list[int]) -> tuple[int, int]:
    """(users with no own items, total slots filled by the fallback) for these users."""
    own = [min(len(ranked.get(u, [])), K) for u in users]
    return sum(o == 0 for o in own), sum(K - o for o in own)


def main() -> None:
    t_all = time.time()
    data = validation_data()
    all_users = sorted(set(data.populations["test_users"]) | set(data.populations["active_both"]))
    rows = []

    def record(method, params, preds, runtime, notes=""):
        res = evaluate(preds, data)
        log_results(method, params, res, runtime, notes)
        rows.append({"method": method, "params": params, "select": selection_score(res),
                     **{f"{p}/{d}": v[1] for (p, d), v in res.items()}})
        print(f"{method} {params}: select={rows[-1]['select']:.4f}", flush=True)

    # --- popularity
    for n in POP_N:
        t = time.time()
        fb = popularity_list(data.usw, HIST_WEEKS, n, data.pool)
        record("popularity", {"n_weeks": n}, fill({}, all_users, fb), time.time() - t)
    pop_rows = [r for r in rows if r["method"] == "popularity"]
    best_n = max(pop_rows, key=lambda r: r["select"])["params"]["n_weeks"]
    fallback = popularity_list(data.usw, HIST_WEEKS, best_n, data.pool)

    # --- repeat
    for hl, tr, a in itertools.product(HALF_LIVES, TRANSFORMS, ALPHAS):
        t = time.time()
        params = {"half_life": hl, "transform": tr, "alpha": a}
        ranked = repeat_ranked(data.usw, HIST_WEEKS, data.pool, hl, tr, a)
        record("repeat", params, fill(ranked, all_users, fallback), time.time() - t,
               f"fallback=popularity_n_weeks={best_n}")
    rep_rows = [r for r in rows if r["method"] == "repeat"]
    best_rep = max(rep_rows, key=lambda r: r["select"])["params"]
    val_ranked = repeat_ranked(data.usw, HIST_WEEKS, data.pool, best_rep["half_life"], best_rep["transform"],
                               best_rep["alpha"])
    val_fb = fallback_slots(val_ranked, data.populations["test_users"])

    # --- refit on weeks 11-30, predict 31-42
    users = test_users()
    test_pool = pool_airtime(TEST_WEEKS)
    final_fb_list = popularity_list(data.usw, FINAL_HIST_WEEKS, best_n, test_pool)
    final_ranked = repeat_ranked(data.usw, FINAL_HIST_WEEKS, test_pool, best_rep["half_life"],
                                 best_rep["transform"], best_rep["alpha"])
    final_fb = fallback_slots(final_ranked, users)
    subs = {"popularity_v1.csv": (f"popularity, n_weeks={best_n} (weeks {FINAL_HIST_WEEKS[1] - best_n + 1}-"
                                  f"{FINAL_HIST_WEEKS[1]})", fill({}, users, final_fb_list)),
            "repeat_v1.csv": (f"repeat, {best_rep}, fallback popularity n_weeks={best_n}",
                              fill(final_ranked, users, final_fb_list))}
    checks = {}
    for name, (desc, preds) in subs.items():
        path = SUB_DIR / name
        write_submission(preds, users, path)
        checks[name] = check_submission(path, set(int(x) for x in test_pool.index))
        print(name, "format problems:", checks[name] or "none")
    log_md = SUB_DIR / "LOG.md"
    with open(log_md, "a", encoding="utf-8") as f:
        for name, (desc, _) in subs.items():
            f.write(f"| {name} | {desc}; fit weeks 11-30, pool = labelled shows airing weeks 31-42 | "
                    f"{dt.date.today().isoformat()} |  |  |  |\n")

    # --- results file
    cols = [f"{p}/{d}" for p in data.populations for d in TARGET_DEFS]
    lines = ["# Baselines: validation results", "",
             f"Produced by `python -m src.baselines` on {dt.datetime.now():%Y-%m-%d %H:%M}. History weeks "
             f"{HIST_WEEKS[0]}-{HIST_WEEKS[1]}, target weeks 21-30, pool = {len(data.pool)} labelled shows airing in "
             f"weeks 21-30. Populations: test_users = {len(data.populations['test_users'])}, active_both = "
             f"{len(data.populations['active_both'])} (labelled interactions in both windows). MAP@5; users with "
             "empty ground truth count as 0. `select` = mean over the three targets on test_users.", "",
             "Ground-truth users with a non-empty top-5 (any population): "
             + ", ".join(f"{d} {len(g)}" for d, g in data.gts.items())
             + f"; test users with empty ground truth: "
             f"{sum(u not in data.gts['watch_sec'] for u in data.populations['test_users'])}.", "",
             "| method | params | select | " + " | ".join(cols) + " |", "|---|---|---|" + "---|" * len(cols)]
    for r in sorted(rows, key=lambda r: (r["method"], -r["select"])):
        lines.append(f"| {r['method']} | `{r['params']}` | {r['select']:.4f} | "
                     + " | ".join(f"{r[c]:.4f}" for c in cols) + " |")
    lines += ["", f"Selected: popularity n_weeks={best_n}; repeat {best_rep}.", "",
              f"Fallback use for the selected repeat on test users: validation {val_fb[0]} users fully on fallback, "
              f"{val_fb[1]} of {K * len(users)} slots from fallback; final refit {final_fb[0]} users, "
              f"{final_fb[1]} slots.", "",
              f"Test pool (weeks 31-42): {len(test_pool)} labelled shows.", "",
              "Submission format checks: " + "; ".join(f"{k}: {'OK' if not v else v}" for k, v in checks.items()), "",
              f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
