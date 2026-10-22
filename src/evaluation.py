"""Shared evaluation harness: windows, candidate pools, ground truths, populations, fallback fill, logging.

Every method goes through the same pool, the same fallback top-up and the same metric.
"""
import csv
import datetime as dt
import json
from dataclasses import dataclass

import pandas as pd

from src.data import PROCESSED, ROOT, SEED, SUBMISSION_CSV, connect
from src.metrics import K, mapk

HIST_WEEKS = (11, 20)        # validation history
TARGET_WEEKS = (21, 30)      # validation target
FINAL_HIST_WEEKS = (11, 30)  # refit for the submission
TEST_WEEKS = (31, 42)        # submission target

TARGET_DEFS = ("watch_sec", "n_days", "n_airings")
EXPERIMENTS = ROOT / "experiments.csv"
# Rows logged before the time-zone fix carry no data tag; see docs/errata.md.
DATA_VERSION = "tzfix"
EXP_HEADER = ["timestamp", "stage", "method", "params_json", "seed", "n_val_users", "val_map5", "runtime_sec", "notes"]


def load_usw() -> pd.DataFrame:
    """user_show_week (labelled only), user_id as Python-int-compatible uint64."""
    return pd.read_parquet(PROCESSED / "user_show_week.parquet",
                           columns=["user_id", "tv_show_id", "week", "watch_sec", "n_airings", "n_days"])


def window(df: pd.DataFrame, weeks: tuple[int, int]) -> pd.DataFrame:
    return df[(df["week"] >= weeks[0]) & (df["week"] <= weeks[1])]


def pool_airtime(weeks: tuple[int, int]) -> pd.DataFrame:
    """Candidate pool: labelled shows with an airing starting in `weeks`, with their airtime there.

    Uses only the schedule (allowed for the test window)."""
    con = connect()
    return con.sql(f"""
        SELECT tv_show_id, sum(duration)::BIGINT AS airtime_sec, count(*) AS n_airings_sched
        FROM '{(PROCESSED / 'schedule.parquet').as_posix()}'
        WHERE tv_show_id <> 0 AND week BETWEEN {weeks[0]} AND {weeks[1]}
        GROUP BY 1 ORDER BY 1
    """).df().set_index("tv_show_id")


def test_users() -> list[int]:
    """User ids of submission.csv, in file order."""
    return [int(u) for u in pd.read_csv(SUBMISSION_CSV, dtype=str)["user_id"]]


def ground_truth(usw: pd.DataFrame, weeks: tuple[int, int], pool: pd.Index, by: str) -> dict[int, list[int]]:
    """Top-K shows per user in `weeks`, ranked by `by` (ties: watch_sec desc, tv_show_id asc), pool only.

    n_days per (user, show, week) counts distinct dates inside one week, so summing over weeks gives
    distinct days. No watch threshold is applied."""
    t = window(usw, weeks)
    t = t[t["tv_show_id"].isin(pool)]
    agg = t.groupby(["user_id", "tv_show_id"], as_index=False)[["watch_sec", "n_days", "n_airings"]].sum()
    return top_k_lists(agg, [by, "watch_sec"])


def cov_ground_truth(weeks: tuple[int, int], pool: pd.Index, usw: pd.DataFrame, cut: float = 0.5) -> dict[int, list[int]]:
    """cov50-style target: top-K shows by number of airings with ONE merged continuous view covering more than
    `cut` of the airing (src.coverage), ties by overlap seconds then tv_show_id."""
    t = connect().sql(f"""
        SELECT user_id, tv_show_id, count(*) AS cov FROM '{(PROCESSED / 'coverage.parquet').as_posix()}'
        WHERE week BETWEEN {weeks[0]} AND {weeks[1]} AND cont_frac > {cut} GROUP BY ALL""").df()
    t = t[t["tv_show_id"].isin(pool)]
    sec = window(usw, weeks).groupby(["user_id", "tv_show_id"], as_index=False)["watch_sec"].sum()
    t = t.merge(sec, on=["user_id", "tv_show_id"], how="left").fillna({"watch_sec": 0})
    return top_k_lists(t, ["cov", "watch_sec"])


def top_k_lists(df: pd.DataFrame, score_cols: list[str], k: int = K) -> dict[int, list[int]]:
    """Per user, the k highest-scoring tv_show_ids (score desc, tv_show_id asc for ties)."""
    s = df.sort_values(["user_id", *score_cols, "tv_show_id"],
                       ascending=[True, *[False] * len(score_cols), True])
    s = s.groupby("user_id", sort=False).head(k)
    return {int(u): [int(x) for x in g] for u, g in s.groupby("user_id", sort=False)["tv_show_id"]}


def fill(ranked: dict[int, list[int]], users: list[int], fallback: list[int], k: int = K) -> dict[int, list[int]]:
    """Exactly k distinct ids per user: own ranking first, topped up from the fallback list."""
    out = {}
    for u in users:
        lst = list(dict.fromkeys(ranked.get(u, [])))[:k]
        for f in fallback:
            if len(lst) == k:
                break
            if f not in lst:
                lst.append(f)
        if len(lst) != k:
            raise RuntimeError(f"could not fill {k} items for user {u}")
        out[u] = lst
    return out


@dataclass
class ValData:
    usw: pd.DataFrame
    pool: pd.DataFrame
    gts: dict[str, dict[int, list[int]]]
    populations: dict[str, list[int]]


def validation_data() -> ValData:
    usw = load_usw()
    pool = pool_airtime(TARGET_WEEKS)
    gts = {"cov50": cov_ground_truth(TARGET_WEEKS, pool.index, usw),
           **{d: ground_truth(usw, TARGET_WEEKS, pool.index, d) for d in TARGET_DEFS}}
    hist_users = set(window(usw, HIST_WEEKS)["user_id"].tolist())
    both = sorted(u for u in gts["watch_sec"] if u in hist_users)
    return ValData(usw, pool, gts, {"test_users": test_users(), "active_both": both})


def evaluate(preds: dict[int, list[int]], data: ValData) -> dict[tuple[str, str], tuple[int, float]]:
    """MAP@5 for every (population, target definition). Users without ground truth count as 0."""
    res = {}
    for pop, users in data.populations.items():
        for d, gt in data.gts.items():
            res[(pop, d)] = (len(users), mapk([gt.get(u, []) for u in users], [preds[u] for u in users]))
    return res


def log_results(method: str, params: dict, res: dict, runtime: float, extra_notes: str = "", stage: str = "val") -> None:
    new = not EXPERIMENTS.exists() or EXPERIMENTS.stat().st_size == 0
    ts = dt.datetime.now().isoformat(timespec="seconds")
    with open(EXPERIMENTS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(EXP_HEADER)
        for (pop, d), (n, score) in res.items():
            notes = f"target={d}; population={pop}" + (f"; {extra_notes}" if extra_notes else "") + f"; data={DATA_VERSION}"
            w.writerow([ts, stage, method, json.dumps(params, sort_keys=True), SEED, n, f"{score:.6f}",
                        f"{runtime:.2f}", notes])


SELECT_DEFS = ("cov50",)


def selection_score(res: dict) -> float:
    """Model selection criterion: MAP@5 of the cov50 target on the test users.

    History: stage 2 used the mean over all three any-overlap targets, stages 3-5 the mean of n_days and n_airings,
    stages 7-9 n_days, and cov50 (one continuous view covering > 50% of the airing, counted as airings) from
    stage 10 on, after the four-point target study (docs/target_definition.md)."""
    return sum(res[("test_users", d)][1] for d in SELECT_DEFS) / len(SELECT_DEFS)
