"""Which target definition matches the Kaggle leaderboard?

Builds alternative ground truths for the validation target window (weeks 21-30) and scores exactly the three
submitted configs (popularity_v1, repeat_v1, repeat_v2) on the 1,260 test users. Compares val with the returned
Kaggle scores: stability of the LB/val ratio across the three configs and the gaps between them.

Definitions (top-5 per user, pool shows only, ties by overlap seconds then tv_show_id):
  start_views     raw views whose start_time falls inside a labelled airing on the view's channel, counted
  start_days      distinct days with such a view
  airings_300s    airings with >= 300 s overlap          days_300s   distinct days with such an airing
  airings_50pct   airings with >= 50% of the airing watched;  days_50pct  distinct days
  n_days, n_airings, watch_sec   current definitions (any overlap)
  cont{70,80,90}_airings / _days  airings where ONE continuous view on the channel (src.coverage) covers
                  >= 70/80/90% of the airing, counted / distinct days (hypothesis from docs/external_sources.md #1)
Start-time join: DuckDB ASOF join (latest airing on the channel with airing.start <= view.start), kept only if
view.start < airing.end. Raw views, not merged ones (the organisers would not have merged devices). Cached as
data/processed/view_starts.parquet for all training weeks.

Usage: python -m src.target_study   ->  data/processed/view_starts.parquet, experiments.csv rows,
                                        docs/target_definition.md (study section)
"""
import datetime as dt
import time

import numpy as np
import pandas as pd

from src.baselines import popularity_list, repeat_ranked
from src.data import PROCESSED, ROOT, connect, register_raw
from src.evaluation import HIST_WEEKS, TARGET_WEEKS, fill, log_results, top_k_lists, validation_data, window
from src.metrics import mapk
from src.repeat_v2 import POP_N, Stats, predict as repeat_predict

OUT_MD = ROOT / "docs" / "target_definition.md"
MARKER = "## Study: alternative target definitions"
VIEW_STARTS = PROCESSED / "view_starts.parquet"

# Returned Kaggle scores (submissions/LOG.md)
LB = {"popularity_v1": (0.255, 0.244), "repeat_v1": (0.332, 0.314), "repeat_v2": (0.36752, 0.348)}
CONFIGS = {
    "popularity_v1": ("popularity", {"n_weeks": POP_N}),
    "repeat_v1": ("repeat", {"half_life": 8, "transform": "log", "alpha": 0.0}),
    "repeat_v2": ("repeat_v2", {"score": "loyalty", "unit": "n_days", "threshold": "none", "half_life": 8, "beta": 5,
                                "delta": 1.0, "fill": "channels_m3"}),
}


def build_view_starts(con) -> None:
    register_raw(con)
    con.execute(f"""
        COPY (
            SELECT v.user_id, v.vsetv_id AS channel_id, v.start_time, v.duraton AS view_sec, week(v.start_time) AS week,
                   s.airing_id, s.tv_show_id, s.start_time AS air_start
            FROM raw_views v
            ASOF JOIN '{(PROCESSED / 'schedule.parquet').as_posix()}' s
              ON v.vsetv_id = s.channel_id AND v.start_time >= s.start_time
            WHERE v.start_time < s.end_time
        ) TO '{VIEW_STARTS.as_posix()}' (FORMAT parquet)""")


def target_tables(con, usw: pd.DataFrame, weeks, pool: pd.Index) -> dict[str, pd.DataFrame]:
    """Per (user, show) metric tables for every definition, pool shows only, with watch_sec for ties."""
    w0, w1 = weeks
    sec = window(usw, weeks).groupby(["user_id", "tv_show_id"], as_index=False)["watch_sec"].sum()
    out = {}
    st = con.sql(f"""
        SELECT user_id, tv_show_id, count(*) AS start_views, count(DISTINCT start_time::DATE) AS start_days
        FROM '{VIEW_STARTS.as_posix()}' WHERE tv_show_id <> 0 AND week BETWEEN {w0} AND {w1} GROUP BY ALL""").df()
    for c in ("start_views", "start_days"):
        out[c] = st[["user_id", "tv_show_id", c]]
    for name, cond in [("300s", "overlap_sec >= 300"), ("50pct", "frac_watched >= 0.5")]:
        t = con.sql(f"""
            SELECT user_id, tv_show_id, count(*) AS airings, count(DISTINCT first_overlap_start::DATE) AS days
            FROM '{(PROCESSED / 'pairs_labelled.parquet').as_posix()}'
            WHERE week BETWEEN {w0} AND {w1} AND {cond} GROUP BY ALL""").df()
        out[f"airings_{name}"] = t[["user_id", "tv_show_id", "airings"]].rename(columns={"airings": f"airings_{name}"})
        out[f"days_{name}"] = t[["user_id", "tv_show_id", "days"]].rename(columns={"days": f"days_{name}"})
    for pct in (70, 80, 90):
        t = con.sql(f"""
            SELECT user_id, tv_show_id, count(*) AS a, count(DISTINCT day) AS d
            FROM '{(PROCESSED / 'coverage.parquet').as_posix()}'
            WHERE week BETWEEN {w0} AND {w1} AND cont_frac >= {pct / 100} GROUP BY ALL""").df()
        out[f"cont{pct}_airings"] = t[["user_id", "tv_show_id", "a"]].rename(columns={"a": f"cont{pct}_airings"})
        out[f"cont{pct}_days"] = t[["user_id", "tv_show_id", "d"]].rename(columns={"d": f"cont{pct}_days"})
    cur = window(usw, weeks).groupby(["user_id", "tv_show_id"], as_index=False)[["n_days", "n_airings", "watch_sec"]].sum()
    for c in ("n_days", "n_airings"):
        out[c] = cur[["user_id", "tv_show_id", c]]
    out["watch_sec"] = cur[["user_id", "tv_show_id", "watch_sec"]].rename(columns={"watch_sec": "watch_sec_"})
    res = {}
    for name, t in out.items():
        t = t[t["tv_show_id"].isin(pool)].merge(sec, on=["user_id", "tv_show_id"], how="left").fillna({"watch_sec": 0})
        res[name] = t
    return res


def gt_lists(t: pd.DataFrame, metric: str) -> dict[int, list[int]]:
    return top_k_lists(t, [metric, "watch_sec"])


def main() -> None:
    t_all = time.time()
    con = connect()
    if not VIEW_STARTS.exists():
        t = time.time()
        build_view_starts(con)
        print(f"view_starts built in {time.time() - t:.1f} s", flush=True)
    data = validation_data()
    users = data.populations["test_users"]
    st = Stats(con, data.usw, HIST_WEEKS, TARGET_WEEKS)
    fb = st.fallback
    preds = {
        "popularity_v1": fill({}, users, fb),
        "repeat_v1": fill(repeat_ranked(data.usw, HIST_WEEKS, data.pool, 8, "log", 0.0), users, fb),
        "repeat_v2": fill(repeat_predict(st, CONFIGS["repeat_v2"][1], users)[1], users, fb),
    }
    tables = target_tables(con, data.usw, TARGET_WEEKS, data.pool.index)
    defs = list(tables)
    gts = {d: gt_lists(tables[d], d if d != "watch_sec" else "watch_sec_") for d in defs}

    scores = {}
    for d in defs:
        for c, (method, params) in CONFIGS.items():
            t = time.time()
            s = mapk([gts[d].get(u, []) for u in users], [preds[c][u] for u in users])
            scores[(d, c)] = s
            log_results(method, params, {("test_users", d): (len(users), s)}, time.time() - t,
                        f"target study: config {c}", stage="target_study")

    vs = con.sql(f"""SELECT count(*) AS n, count(*) FILTER (WHERE tv_show_id <> 0) AS labelled,
                     count(DISTINCT user_id) AS users FROM '{VIEW_STARTS.as_posix()}'""").fetchall()[0]
    names = list(CONFIGS)
    rows = []
    for d in defs:
        val = np.array([scores[(d, c)] for c in names])
        r = {"def": d, **{c: v for c, v in zip(names, val)}, "users_with_gt": sum(1 for u in users if gts[d].get(u))}
        for k, lb_i in (("pub", 0), ("priv", 1)):
            lb = np.array([LB[c][lb_i] for c in names])
            ratio = lb / val
            scale = (lb @ val) / (val @ val)  # least-squares LB ~ scale * val
            r[f"ratio_{k}"] = ratio
            r[f"cv_{k}"] = ratio.std() / ratio.mean()
            r[f"relerr_{k}"] = np.max(np.abs(scale * val - lb) / lb)
        r["gap_v1_pop"] = val[1] / val[0]
        r["gap_v2_pop"] = val[2] / val[0]
        r["gap_v2_v1"] = val[2] / val[1]
        rows.append(r)
    rows.sort(key=lambda r: r["cv_pub"])
    lb_pub = [LB[c][0] for c in names]

    lines = [MARKER, "",
             f"Produced by `python -m src.target_study` on {dt.datetime.now():%Y-%m-%d %H:%M}. Validation weeks "
             f"11-20 -> 21-30, {len(users)} test users, pool {len(data.pool)} shows, exactly the three submitted "
             "configs. Start-time join over raw views: "
             f"{vs[0]} views matched to an airing, {vs[1]} of them to a labelled airing ({vs[2]} users).", "",
             "Leaderboard (public / private): " + ", ".join(f"{c} {LB[c][0]} / {LB[c][1]}" for c in names)
             + f". LB gaps (public): repeat_v1/pop {lb_pub[1] / lb_pub[0]:.3f}, repeat_v2/pop {lb_pub[2] / lb_pub[0]:.3f}, "
             f"repeat_v2/repeat_v1 {lb_pub[2] / lb_pub[1]:.3f}.", "",
             "### Validation MAP@5 of the submitted configs per target definition", "",
             "`cv` = coefficient of variation of the three LB/val ratios (lower = more stable); `max rel err` = largest "
             "relative error when LB is fitted as one scale factor times val. Sorted by public cv.", "",
             "| definition | pop_v1 | repeat_v1 | repeat_v2 | LB/val ratios (public) | cv public | max rel err public | "
             "cv private | max rel err private | val gap v1/pop | val gap v2/pop | val gap v2/v1 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['def']} | {r['popularity_v1']:.4f} | {r['repeat_v1']:.4f} | {r['repeat_v2']:.4f} | "
                     + " / ".join(f"{x:.3f}" for x in r["ratio_pub"])
                     + f" | {r['cv_pub']:.4f} | {r['relerr_pub']:.4f} | {r['cv_priv']:.4f} | {r['relerr_priv']:.4f} | "
                     f"{r['gap_v1_pop']:.3f} | {r['gap_v2_pop']:.3f} | {r['gap_v2_v1']:.3f} |")
    lines += ["", f"Test users with a non-empty ground truth: "
              + ", ".join(f"{r['def']} {r['users_with_gt']}" for r in rows) + ".", "",
              f"Runtime: {time.time() - t_all:.1f} s.", ""]
    text = OUT_MD.read_text(encoding="utf-8")
    text = text.split(MARKER)[0].rstrip() + "\n\n" + "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8")
    for r in rows:
        print(f"{r['def']:>14}: val {r['popularity_v1']:.4f} {r['repeat_v1']:.4f} {r['repeat_v2']:.4f} "
              f"cv_pub {r['cv_pub']:.4f} cv_priv {r['cv_priv']:.4f} gaps {r['gap_v1_pop']:.3f} {r['gap_v2_pop']:.3f} {r['gap_v2_v1']:.3f}")


if __name__ == "__main__":
    main()
