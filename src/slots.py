"""Slot habits: how much of the target window is new content, and a (channel, day type, hour) slot model.

Measurement
  * share of the test users' true top-5 shows (n_days, weeks 21-30) without viewing history in weeks 11-20
  * share of pool airings (and prime-time airings, start 19:00-22:59) whose id has no viewing history,
    weeks 21-30 vs history 11-20 and weeks 31-42 vs history 11-30, by week

Slot model
  slot = (channel, day type, hour); day type = weekday/weekend ("we2") or day of week ("dow7").
  User affinity A(u, slot) = decayed seconds the user watched that channel in that hour (all airtime, id = 0
  included) / decayed seconds available in that slot over the history window -> share of the slot watched.
  Show weight W(slot, s) per target week from the target-window schedule (channel and airing times only):
    hours    airing hours of s in the slot
    airings  share of each airing that falls in the slot (sums to 1 per airing)
  slot score(u, s) = A(u, .) . W(., s)   (expected watch hours / expected airings watched)
Replacement
  Shows the user watched in history that do NOT air in the target window: R(u, slot) = sum over those shows of the
  user's decayed days per week x the show's share of its history airtime in that slot.
  replacement score(u, s) = R(u, .) . W_airings(., s)

Usage: python -m src.slots   ->  experiments.csv rows, docs/slots_results.md, docs/best_params.json ("slot")
"""
import datetime as dt
import itertools
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp

from src.data import PROCESSED, ROOT
from src.evaluation import window
from src.method_utils import RESULT_COLS, Context, results_table, save_best
from src.metrics import K

OUT_MD = ROOT / "docs" / "slots_results.md"
DAYTYPES = ["we2", "dow7"]
HALF_LIVES = [None, 8]
AGGS = ["hours", "airings"]
PRIME = (19, 23)


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


def _dt_expr(daytype: str, hb: str = "hb") -> str:
    dow = f"((({hb}) // 24 + 3) % 7 + 1)"  # ISO day of week of the hour bucket (epoch day 0 = Thursday)
    return f"(CASE WHEN {dow} >= 6 THEN 1 ELSE 0 END)" if daytype == "we2" else f"({dow} - 1)"


def _days_per_week(daytype: str) -> np.ndarray:
    return np.array([5, 2]) if daytype == "we2" else np.ones(7)


def _hour_cells(src: str, keys: str, daytype: str) -> str:
    """SQL: split [a, b) intervals of `src` into hour buckets -> keys, channel_id, dt, hour, sec, len_sec (+ week)."""
    return f"""
        WITH x AS (SELECT {keys}, channel_id, a, b, unnest(range(a // 3600, (b - 1) // 3600 + 1)) AS hb FROM ({src}))
        SELECT {keys}, channel_id, {_dt_expr(daytype)} AS dt, hb % 24 AS hour,
               least(b, (hb + 1) * 3600) - greatest(a, hb * 3600) AS sec, b - a AS len_sec
        FROM x"""


class SlotModel:
    """Slot affinities for one history window and show weights for one target window."""

    def __init__(self, con, hist_weeks, target_weeks, daytype: str, half_life):
        h0, h1 = hist_weeks
        t0, t1 = target_weeks
        decay = "1.0" if half_life is None else f"pow(0.5, ({h1} - week) / {half_life})"
        user = con.sql(_hour_cells(f"""
            SELECT user_id, week, channel_id, epoch(start_time)::BIGINT AS a, epoch(stop_time)::BIGINT AS b
            FROM '{pq('view_segments')}' WHERE week BETWEEN {h0} AND {h1}""", "user_id, week", daytype)
                       ).aggregate(f"user_id, channel_id, dt, hour, sum(sec * {decay}) AS wsec").df()
        dsum = sum(1.0 if half_life is None else 0.5 ** ((h1 - w) / half_life) for w in range(h0, h1 + 1))
        avail = dsum * _days_per_week(daytype)[user["dt"].to_numpy()] * 3600.0
        user["aff"] = user["wsec"] / avail
        tgt = con.sql(_hour_cells(f"""
            SELECT tv_show_id, channel_id, epoch(start_time)::BIGINT AS a, epoch(end_time)::BIGINT AS b
            FROM '{pq('schedule')}' WHERE tv_show_id <> 0 AND week BETWEEN {t0} AND {t1}""", "tv_show_id", daytype)
                      ).aggregate("tv_show_id, channel_id, dt, hour, sum(sec) / 3600.0 AS hours, "
                                  "sum(sec / len_sec) AS airings").df()
        n_t = t1 - t0 + 1
        tgt["hours"] /= n_t
        tgt["airings"] /= n_t
        hist_air = con.sql(_hour_cells(f"""
            SELECT tv_show_id, channel_id, epoch(start_time)::BIGINT AS a, epoch(end_time)::BIGINT AS b
            FROM '{pq('schedule')}' WHERE tv_show_id <> 0 AND week BETWEEN {h0} AND {h1}""", "tv_show_id", daytype)
                           ).aggregate("tv_show_id, channel_id, dt, hour, sum(sec) AS sec").df()
        hist_air["share"] = hist_air["sec"] / hist_air.groupby("tv_show_id")["sec"].transform("sum")

        def key(df):
            return df["channel_id"].to_numpy(np.int64) * 1000 + df["dt"].to_numpy(np.int64) * 24 + df["hour"].to_numpy(np.int64)

        slots = np.unique(np.concatenate([key(user), key(tgt), key(hist_air)]))
        self.users = np.sort(user["user_id"].unique())
        self.shows = np.sort(tgt["tv_show_id"].unique())
        self.hist_shows = np.sort(hist_air["tv_show_id"].unique())
        su = np.searchsorted(slots, key(user))
        self.A = sp.csr_matrix((user["aff"].to_numpy(), (np.searchsorted(self.users, user["user_id"].to_numpy()), su)),
                               shape=(len(self.users), len(slots)))
        st_ = np.searchsorted(slots, key(tgt))
        si = np.searchsorted(self.shows, tgt["tv_show_id"].to_numpy())
        self.W = {a: sp.csc_matrix((tgt[a].to_numpy(), (st_, si)), shape=(len(slots), len(self.shows))) for a in AGGS}
        self.H = sp.csr_matrix((hist_air["share"].to_numpy(),
                                (np.searchsorted(self.hist_shows, hist_air["tv_show_id"].to_numpy()),
                                 np.searchsorted(slots, key(hist_air)))), shape=(len(self.hist_shows), len(slots)))
        self.user_pos = {int(u): i for i, u in enumerate(self.users)}

    def scores(self, users: list[int], agg: str) -> tuple[list[int], np.ndarray]:
        known = [u for u in users if u in self.user_pos]
        return known, (self.A[[self.user_pos[u] for u in known]] @ self.W[agg]).toarray()

    def replacement(self, users: list[int], dropped: pd.DataFrame) -> tuple[list[int], np.ndarray]:
        """dropped: user_id, tv_show_id, weight for history shows that do not air in the target window."""
        d = dropped[dropped["user_id"].isin(users) & dropped["tv_show_id"].isin(self.hist_shows)]
        known = sorted(set(d["user_id"].tolist()))
        if not known:
            return [], np.zeros((0, len(self.shows)))
        upos = {u: i for i, u in enumerate(known)}
        L = sp.csr_matrix((d["weight"].to_numpy(), ([upos[int(u)] for u in d["user_id"]],
                                                    np.searchsorted(self.hist_shows, d["tv_show_id"].to_numpy()))),
                          shape=(len(known), len(self.hist_shows)))
        return known, (L @ self.H @ self.W["airings"]).toarray()


def dropped_shows(usw: pd.DataFrame, hist_weeks, target_airing: pd.Index, half_life=8) -> pd.DataFrame:
    """History shows of each user that do not air in the target window, weight = decayed days per week."""
    h = window(usw, hist_weeks)
    h1 = hist_weeks[1]
    dsum = sum(0.5 ** ((h1 - w) / half_life) for w in range(hist_weeks[0], h1 + 1))
    w = h["n_days"] * 0.5 ** ((h1 - h["week"]) / half_life) / dsum
    d = h[["user_id", "tv_show_id"]].assign(weight=w).groupby(["user_id", "tv_show_id"], as_index=False)["weight"].sum()
    return d[~d["tv_show_id"].isin(target_airing)]


def ranked_from_scores(known: list[int], scores: np.ndarray, items: np.ndarray, pool: pd.Index, k: int = K):
    cols = np.flatnonzero(np.isin(items, pool.to_numpy()))
    s = scores[:, cols]
    out = {}
    if len(known) == 0:
        return out
    top = np.argpartition(-s, k, axis=1)[:, :k]
    for r, u in enumerate(known):
        c = top[r][np.argsort(-s[r, top[r]], kind="stable")]
        c = c[s[r, c] > 0]
        out[u] = [int(x) for x in items[cols[c]]]
    return out


def measurement(ctx: Context) -> list[str]:
    con, usw = ctx.con, ctx.data.usw
    users = ctx.data.populations["test_users"]
    watched_hist = set(window(usw, (11, 20))["tv_show_id"].unique().tolist())
    hist_by_user = window(usw, (11, 20)).groupby("user_id")["tv_show_id"].agg(set).to_dict()
    aired_hist = set(con.sql(f"SELECT DISTINCT tv_show_id FROM '{pq('schedule')}' WHERE week BETWEEN 11 AND 20").df()["tv_show_id"])
    gt = ctx.data.gts["n_days"]
    items = [(u, s) for u in users for s in gt.get(u, [])]
    n = len(items)
    lines = ["## How much of the target is new content", "",
             f"Test users' true top-5 shows in weeks 21-30 (n_days): {n} (user, show) pairs.", "",
             "| share of true top-5 shows that ... | value |", "|---|---|",
             f"| nobody watched in weeks 11-20 | {sum(s not in watched_hist for _, s in items) / n:.4f} |",
             f"| did not air at all in weeks 11-20 | {sum(s not in aired_hist for _, s in items) / n:.4f} |",
             f"| this user did not watch in weeks 11-20 | {sum(s not in hist_by_user.get(u, set()) for u, s in items) / n:.4f} |",
             ""]
    for (tw, hw) in [((21, 30), (11, 20)), ((31, 42), (11, 30))]:
        watched = window(usw, hw)["tv_show_id"].unique()
        con.register("watched_df", pd.DataFrame({"tv_show_id": watched}))
        df = con.sql(f"""
            SELECT week, count(*) AS airings,
                   avg((w.tv_show_id IS NULL)::INT) AS share_no_history,
                   count(*) FILTER (WHERE hour(start_time) BETWEEN {PRIME[0]} AND {PRIME[1] - 1}) AS prime_airings,
                   avg((w.tv_show_id IS NULL)::INT) FILTER (WHERE hour(start_time) BETWEEN {PRIME[0]} AND {PRIME[1] - 1})
                       AS prime_share_no_history,
                   sum(duration * (w.tv_show_id IS NULL)::INT) FILTER (WHERE hour(start_time) BETWEEN {PRIME[0]} AND {PRIME[1] - 1})
                       / sum(duration) FILTER (WHERE hour(start_time) BETWEEN {PRIME[0]} AND {PRIME[1] - 1}) AS prime_airtime_share_no_history
            FROM '{pq('schedule')}' s LEFT JOIN watched_df w USING (tv_show_id)
            WHERE s.tv_show_id <> 0 AND week BETWEEN {tw[0]} AND {tw[1]} GROUP BY 1 ORDER BY 1""").df()
        tot = con.sql(f"""
            SELECT avg((w.tv_show_id IS NULL)::INT) AS a,
                   avg((w.tv_show_id IS NULL)::INT) FILTER (WHERE hour(start_time) BETWEEN {PRIME[0]} AND {PRIME[1] - 1}) AS p
            FROM '{pq('schedule')}' s LEFT JOIN watched_df w USING (tv_show_id)
            WHERE s.tv_show_id <> 0 AND week BETWEEN {tw[0]} AND {tw[1]}""").fetchall()[0]
        lines += [f"### Labelled airings in weeks {tw[0]}-{tw[1]} whose id nobody watched in weeks {hw[0]}-{hw[1]}", "",
                  f"All airings: {tot[0]:.4f}; prime time (start {PRIME[0]}:00-{PRIME[1] - 1}:59): {tot[1]:.4f}.", "",
                  "| week | airings | share no history | prime airings | prime share no history | prime airtime share no history |",
                  "|---|---|---|---|---|---|"]
        lines += [f"| {r.week} | {r.airings} | {r.share_no_history:.4f} | {r.prime_airings} | {r.prime_share_no_history:.4f} | "
                  f"{r.prime_airtime_share_no_history:.4f} |" for r in df.itertuples()]
        lines.append("")
    return lines


def main() -> None:
    t_all = time.time()
    ctx = Context()
    lines = measurement(ctx)
    pool = ctx.st.pool.index
    for daytype, hl in itertools.product(DAYTYPES, HALF_LIVES):
        t = time.time()
        sm = SlotModel(ctx.con, (11, 20), (21, 30), daytype, hl)
        build = time.time() - t
        known, sc = sm.scores(ctx.users, "hours")
        for agg in AGGS:
            t = time.time()
            if agg != "hours":
                known, sc = sm.scores(ctx.users, agg)
            p = {"model": "slot", "daytype": daytype, "half_life": hl, "agg": agg}
            ctx.run("slot", p, ranked_from_scores(known, sc, sm.shows, pool), t - build)
        if (daytype, hl) == ("we2", 8):
            t = time.time()
            drop = dropped_shows(ctx.data.usw, (11, 20), pd.Index(sm.shows))
            known, sc = sm.replacement(ctx.users, drop)
            ctx.run("slot", {"model": "replacement", "daytype": daytype, "half_life": hl, "agg": "airings"},
                    ranked_from_scores(known, sc, sm.shows, pool), t, "replacement score alone (diagnostic)")
    best = max((r for r in ctx.rows if r["params"]["model"] == "slot"), key=lambda r: r["select"])
    save_best("slot", best["params"])
    save_best("slot_select", best["select"])
    lines = ["# Slot habits", "",
             f"Produced by `python -m src.slots` on {dt.datetime.now():%Y-%m-%d %H:%M}. Same harness as all methods "
             "(history 11-20, target 21-30, 1,260 test users, shared popularity fallback); `select` = MAP@5 on n_days.", ""] \
        + lines + ["## Slot model and replacement score alone", "", *results_table(ctx.rows, RESULT_COLS), "",
                   f"Selected slot config: `{best['params']}` (select {best['select']:.4f}).", "",
                   f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
