"""repeat_cont: re-implementation of the write-up's "Algorithm 1" from its description (docs/external_sources.md #1).

A "watch" = one continuous view on the channel (merged segments, src.coverage) covering MORE than `cut` of the
airing's full length. Score = number of such watches of the show over the whole history window (no decay).
Top-5 within the target pool (shows airing in the target window), repeats allowed, topped up with the shared
popularity fallback. The description gives no tie-break; ties are broken by the shared popularity score
("pop", used for the submission) or by tv_show_id ("id", logged for comparison).

Validation targets: n_days (current selection target), cont50 and cont80 = number of target-window airings with
one continuous view covering more than 50% / 80% of the airing (top-5 per user, ties by overlap seconds).

Usage: python -m src.repeat_cont   ->  experiments.csv rows, docs/repeat_cont_results.md,
                                       submissions/repeat_cont50.csv (always written, cut 0.5, pop tie-break)
"""
import dataclasses
import datetime as dt
import time

import pandas as pd

from src.baselines import popularity_list
from src.data import PROCESSED, ROOT, connect
from src.evaluation import (FINAL_HIST_WEEKS, HIST_WEEKS, TARGET_WEEKS, TEST_WEEKS, evaluate, fill, log_results,
                            pool_airtime, test_users, top_k_lists, validation_data, window)
from src.repeat_v2 import POP_N
from src.submission import check_submission, write_submission

COV = (PROCESSED / "coverage.parquet").as_posix()
OUT_MD = ROOT / "docs" / "repeat_cont_results.md"
SUB = ROOT / "submissions" / "repeat_cont50.csv"
CUTS = [0.3, 0.5, 0.8]
TIES = ["pop", "id"]


def watch_counts(con, weeks, cut: float) -> pd.DataFrame:
    return con.sql(f"""
        SELECT user_id, tv_show_id, count(*) AS watches FROM '{COV}'
        WHERE week BETWEEN {weeks[0]} AND {weeks[1]} AND cont_frac > {cut} GROUP BY ALL""").df()


def ranked(con, usw, hist_weeks, pool: pd.DataFrame, cut: float, tie: str) -> dict[int, list[int]]:
    c = watch_counts(con, hist_weeks, cut)
    c = c[c["tv_show_id"].isin(pool.index)]
    if tie == "pop":
        h = window(usw, (hist_weeks[1] - POP_N + 1, hist_weeks[1]))
        pop = h.groupby("tv_show_id")["watch_sec"].sum()
        c = c.assign(pop=pop.reindex(c["tv_show_id"]).fillna(0).to_numpy())
        return top_k_lists(c, ["watches", "pop"])
    return top_k_lists(c, ["watches"])


def cont_target(con, usw, weeks, pool: pd.Index, cut: float) -> dict[int, list[int]]:
    t = watch_counts(con, weeks, cut)
    t = t[t["tv_show_id"].isin(pool)]
    sec = window(usw, weeks).groupby(["user_id", "tv_show_id"], as_index=False)["watch_sec"].sum()
    t = t.merge(sec, on=["user_id", "tv_show_id"], how="left").fillna({"watch_sec": 0})
    return top_k_lists(t, ["watches", "watch_sec"])


def main() -> None:
    t_all = time.time()
    con = connect()
    data = validation_data()
    pool = data.pool
    gts = {"n_days": data.gts["n_days"],
           "cont50": cont_target(con, data.usw, TARGET_WEEKS, pool.index, 0.5),
           "cont80": cont_target(con, data.usw, TARGET_WEEKS, pool.index, 0.8)}
    vdata = dataclasses.replace(data, gts=gts)
    users = sorted(set(data.populations["test_users"]) | set(data.populations["active_both"]))
    fb = popularity_list(data.usw, HIST_WEEKS, POP_N, pool)

    from src.baselines import repeat_ranked
    from src.repeat_v2 import Stats, predict as repeat_predict
    from src.method_utils import load_best
    st = Stats(con, data.usw, HIST_WEEKS, TARGET_WEEKS)
    refs = {"popularity": ({"n_weeks": POP_N}, {}),
            "repeat_v1": ({"half_life": 8, "transform": "log", "alpha": 0.0},
                          repeat_ranked(data.usw, HIST_WEEKS, pool, 8, "log", 0.0)),
            "repeat_v2": (load_best()["repeat"], repeat_predict(st, load_best()["repeat"], users)[1])}
    rows = []
    for name, (params, r) in refs.items():
        t = time.time()
        res = evaluate(fill(r, users, fb), vdata)
        log_results(name if name != "repeat_v2" else "repeat_v2", params, res, time.time() - t,
                    f"fallback=popularity_n_weeks={POP_N}; reference on cont targets")
        rows.append((name, params, res))
    for cut in CUTS:
        for tie in TIES:
            t = time.time()
            params = {"cut": cut, "tie": tie, "history": "whole window, no decay"}
            res = evaluate(fill(ranked(con, data.usw, HIST_WEEKS, pool, cut, tie), users, fb), vdata)
            log_results("repeat_cont", params, res, time.time() - t, f"fallback=popularity_n_weeks={POP_N}")
            rows.append((f"repeat_cont{int(cut * 100)}", params, res))
            print(f"repeat_cont cut {cut} tie {tie}: n_days {res[('test_users', 'n_days')][1]:.4f} "
                  f"cont50 {res[('test_users', 'cont50')][1]:.4f} cont80 {res[('test_users', 'cont80')][1]:.4f}", flush=True)

    # ---- refit on weeks 11-30 -> 31-42, always written
    test = test_users()
    tpool = pool_airtime(TEST_WEEKS)
    preds = fill(ranked(con, data.usw, FINAL_HIST_WEEKS, tpool, 0.5, "pop"), test,
                 popularity_list(data.usw, FINAL_HIST_WEEKS, POP_N, tpool))
    write_submission(preds, test, SUB)
    problems = check_submission(SUB, set(int(x) for x in tpool.index))
    own = ranked(con, data.usw, FINAL_HIST_WEEKS, tpool, 0.5, "pop")
    n_fb = sum(5 - min(len(own.get(u, [])), 5) for u in test)
    log = ROOT / "submissions" / "LOG.md"
    kept = [ln for ln in log.read_text(encoding="utf-8").splitlines() if not ln.startswith(f"| {SUB.name} |")]
    kept.append(f"| {SUB.name} | repeat_cont: top-5 by number of airings with one continuous view covering > 50%, "
                f"weeks 11-30, no decay, ties by popularity, fallback popularity n_weeks={POP_N}; pool = labelled shows "
                f"airing weeks 31-42 (re-implementation of the write-up's Algorithm 1 from its description) | "
                f"{dt.date.today().isoformat()} |  |  |  |")
    log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(SUB.name, "format problems:", problems or "none")

    cols = [(p, d) for p in ("test_users", "active_both") for d in ("n_days", "cont50", "cont80")]
    lines = ["# repeat_cont (write-up's Algorithm 1, re-implemented)", "",
             f"Produced by `python -m src.repeat_cont` on {dt.datetime.now():%Y-%m-%d %H:%M}. History weeks 11-20, "
             f"target weeks 21-30, pool {len(pool)} shows, shared popularity fallback. MAP@5. Targets: n_days, and "
             "cont50 / cont80 = top-5 by number of target airings with one continuous view covering > 50% / > 80%.", "",
             f"Test users with a non-empty ground truth: " + ", ".join(
                 f"{d} {sum(1 for u in data.populations['test_users'] if g.get(u))}" for d, g in gts.items()) + ".", "",
             "| method | params | " + " | ".join(f"{p}: {d}" for p, d in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for name, params, res in rows:
        lines.append(f"| {name} | `{params}` | " + " | ".join(f"{res[c][1]:.4f}" for c in cols) + " |")
    lines += ["", f"Submission {SUB.name} (cut 0.5, pop tie-break, refit on weeks 11-30): format "
              f"{'OK' if not problems else problems}; {n_fb} of {5 * len(test)} slots filled by the popularity fallback.",
              "", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
