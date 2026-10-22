"""Target-definition study with all four leaderboard points (adds repeat_cont50, the discriminating submission).

Candidate targets for weeks 21-30 (top-5 per user, pool only, ties by overlap seconds then id):
  n_days, n_airings                       any overlap (previous selection target and its sibling)
  cov{30,50,80}_{airings,days}_{merged,raw}
      airings (or distinct days) where ONE view covers MORE than 30/50/80% of the airing; "merged" = our merged
      continuous intervals per user and channel (src.coverage), "raw" = each raw view row on its own
Each target is scored with the four submitted configs on the 1,260 test users and compared with the returned
Kaggle scores: cv of the LB/val ratio over all four, and a leave-one-out test that fits the scale on the three
any-overlap submissions and predicts repeat_cont50 (actual public 0.417, private 0.400).

Usage: python -m src.target_study4   ->  experiments.csv rows, docs/target_definition.md (four-point section)
"""
import datetime as dt
import time

import numpy as np
import pandas as pd

from src.baselines import popularity_list, repeat_ranked
from src.data import PROCESSED, ROOT, connect
from src.evaluation import HIST_WEEKS, TARGET_WEEKS, fill, log_results, top_k_lists, validation_data, window
from src.metrics import mapk
from src.repeat_cont import ranked as cont_ranked
from src.repeat_v2 import POP_N, Stats, predict as repeat_predict

OUT_MD = ROOT / "docs" / "target_definition.md"
MARKER = "## Study with four leaderboard points"
SOURCES = {"merged": PROCESSED / "coverage.parquet", "raw": PROCESSED / "coverage_raw.parquet"}
LB = {"popularity_v1": (0.255, 0.244), "repeat_v1": (0.332, 0.314), "repeat_v2": (0.36752, 0.348),
      "repeat_cont50": (0.417, 0.400)}
CONFIGS = {
    "popularity_v1": ("popularity", {"n_weeks": POP_N}),
    "repeat_v1": ("repeat", {"half_life": 8, "transform": "log", "alpha": 0.0}),
    "repeat_v2": ("repeat_v2", {"score": "loyalty", "unit": "n_days", "threshold": "none", "half_life": 8, "beta": 5,
                                "delta": 1.0, "fill": "channels_m3"}),
    "repeat_cont50": ("repeat_cont", {"cut": 0.5, "tie": "pop", "history": "whole window, no decay"}),
}


def coverage_targets(con, usw, weeks, pool: pd.Index) -> dict[str, dict[int, list[int]]]:
    sec = window(usw, weeks).groupby(["user_id", "tv_show_id"], as_index=False)["watch_sec"].sum()
    out = {}
    for src, path in SOURCES.items():
        for cut in (30, 50, 80):
            t = con.sql(f"""
                SELECT user_id, tv_show_id, count(*) AS airings, count(DISTINCT day) AS days FROM '{path.as_posix()}'
                WHERE week BETWEEN {weeks[0]} AND {weeks[1]} AND cont_frac > {cut / 100} GROUP BY ALL""").df()
            t = t[t["tv_show_id"].isin(pool)].merge(sec, on=["user_id", "tv_show_id"], how="left").fillna({"watch_sec": 0})
            for unit in ("airings", "days"):
                out[f"cov{cut}_{unit}_{src}"] = top_k_lists(t, [unit, "watch_sec"])
    return out


def main() -> None:
    t_all = time.time()
    con = connect()
    data = validation_data()
    users = data.populations["test_users"]
    st = Stats(con, data.usw, HIST_WEEKS, TARGET_WEEKS)
    fb = st.fallback
    preds = {
        "popularity_v1": fill({}, users, fb),
        "repeat_v1": fill(repeat_ranked(data.usw, HIST_WEEKS, data.pool, 8, "log", 0.0), users, fb),
        "repeat_v2": fill(repeat_predict(st, CONFIGS["repeat_v2"][1], users)[1], users, fb),
        "repeat_cont50": fill(cont_ranked(con, data.usw, HIST_WEEKS, data.pool, 0.5, "pop"), users, fb),
    }
    gts = {"n_days": data.gts["n_days"], "n_airings": data.gts["n_airings"],
           **coverage_targets(con, data.usw, TARGET_WEEKS, data.pool.index)}
    names = list(CONFIGS)
    rows = []
    for d, gt in gts.items():
        val = []
        for c in names:
            t = time.time()
            s = mapk([gt.get(u, []) for u in users], [preds[c][u] for u in users])
            val.append(s)
            method, params = CONFIGS[c]
            log_results(method, params, {("test_users", d): (len(users), s)}, time.time() - t,
                        f"target study 4 points: config {c}", stage="target_study")
        val = np.array(val)
        r = {"def": d, "val": val}
        for k, i in (("pub", 0), ("priv", 1)):
            lb = np.array([LB[c][i] for c in names])
            ratio = lb / val
            r[f"cv_{k}"] = ratio.std() / ratio.mean()
            s3 = lb[:3] @ val[:3] / (val[:3] @ val[:3])  # scale from the three any-overlap submissions
            r[f"loo_{k}"] = s3 * val[3]
            r[f"ratio_{k}"] = ratio
        rows.append(r)
    rows.sort(key=lambda r: r["cv_pub"] + r["cv_priv"])

    lines = [MARKER, "",
             f"Produced by `python -m src.target_study4` on {dt.datetime.now():%Y-%m-%d %H:%M} (data after the time-zone "
             f"fix). Validation weeks 11-20 -> 21-30, {len(users)} test users, the four submitted configs. "
             "`cov{cut}_{unit}_{source}`: airings (or distinct days) where one view covers more than cut% of the airing; "
             "merged = our merged continuous intervals per user and channel, raw = each raw view row on its own. "
             "`cv` = coefficient of variation of the four LB/val ratios; `LOO pred` = repeat_cont50's leaderboard score "
             "predicted from a scale fitted on the other three submissions (actual 0.417 public / 0.400 private). "
             "Sorted by cv public + cv private.", "",
             "| target | pop_v1 | repeat_v1 | repeat_v2 | repeat_cont50 | LB/val ratios public | cv public | cv private | "
             "LOO pred public | LOO pred private |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['def']} | " + " | ".join(f"{v:.4f}" for v in r["val"]) + " | "
                     + " / ".join(f"{x:.3f}" for x in r["ratio_pub"])
                     + f" | {r['cv_pub']:.4f} | {r['cv_priv']:.4f} | {r['loo_pub']:.3f} | {r['loo_priv']:.3f} |")
    lines += ["", f"Runtime: {time.time() - t_all:.1f} s.", ""]
    text = OUT_MD.read_text(encoding="utf-8")
    text = text.split(MARKER)[0].rstrip() + "\n\n" + "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8")
    for r in rows[:8]:
        print(f"{r['def']:>22}: cv {r['cv_pub']:.4f}/{r['cv_priv']:.4f} loo {r['loo_pub']:.3f}/{r['loo_priv']:.3f} "
              f"val {np.round(r['val'], 4)}")
    print("...", rows[-1]["def"], round(rows[-1]["cv_pub"], 4))


if __name__ == "__main__":
    main()
