"""Repeat v2: frequency and loyalty scoring of the user's own shows, plus a personalised channel fill.

History counts per (user, show, week) come from pairs_labelled after an optional per-airing threshold
(none / overlap >= 300 s / >= 10% of the airing):  W_w = watched airings or distinct watched days.
Decay d(w) = 0.5 ** ((last_hist_week - w) / half_life), or 1 without decay.

freq     score = sum_w W_w d(w)
loyalty  L = sum_w W_w d(w) / (sum_w A_w d(w) + beta),  A_w = the show's airings (or airing days) in week w
         score = L * T ** delta,  T = the show's airings (or airing days) in the target window (schedule only)

Fill order for every config: own top-5, then (optional) the user's channel fill, then the shared global
popularity fallback (watch seconds, last 10 history weeks, as selected in stage 2).
Channel fill: user's top-m channels by viewing seconds in the history window (all airtime, id = 0 included as
context); candidates = labelled shows airing on those channels in the target window, score = channel share x
global popularity of the show; shows with zero popularity are skipped.

Usage: python -m src.repeat_v2   ->  experiments.csv rows, docs/repeat_v2_results.md, submissions/repeat_v2.csv
"""
import datetime as dt
import itertools
import time

import pandas as pd

from src.baselines import popularity_list, repeat_ranked
from src.data import PROCESSED, ROOT, connect
from src.evaluation import (FINAL_HIST_WEEKS, HIST_WEEKS, SELECT_DEFS, TARGET_WEEKS, TEST_WEEKS, evaluate, fill,
                            log_results, pool_airtime, selection_score, test_users, top_k_lists, validation_data,
                            window)
from src.metrics import K
from src.submission import check_submission, write_submission

OUT_MD = ROOT / "docs" / "repeat_v2_results.md"
SUB = ROOT / "submissions" / "repeat_v2.csv"
POP_N = 10  # selected in stage 2 (also best under the frequency criterion, see experiments.csv)

THRESHOLDS = {"none": "TRUE", "sec300": "overlap_sec >= 300", "frac10": "frac_watched >= 0.10"}
UNITS = ["n_days", "n_airings"]
FREQ_HALF_LIVES = [4, 8, None]
LOY_HALF_LIVES = [8, None]
BETAS = [0, 1, 5]
DELTAS = [0.5, 1.0]
CHANNEL_M = [1, 3, 5]


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


class Stats:
    """Everything the scorers need for one (history window, target window)."""

    def __init__(self, con, usw, hist_weeks, target_weeks):
        self.hist_weeks = hist_weeks
        self.pool = pool_airtime(target_weeks)
        h0, h1 = hist_weeks
        t0, t1 = target_weeks
        self.user_week = {
            name: con.sql(f"""
                SELECT user_id, tv_show_id, week, count(*) AS n_airings,
                       count(DISTINCT first_overlap_start::DATE) AS n_days
                FROM '{pq('pairs_labelled')}' WHERE week BETWEEN {h0} AND {h1} AND {cond} GROUP BY ALL""").df()
            for name, cond in THRESHOLDS.items()}
        self.show_week = con.sql(f"""
            SELECT tv_show_id, week, count(*) AS n_airings, count(DISTINCT start_time::DATE) AS n_days
            FROM '{pq('schedule')}' WHERE tv_show_id <> 0 AND week BETWEEN {h0} AND {h1} GROUP BY ALL""").df()
        self.target = con.sql(f"""
            SELECT tv_show_id, count(*) AS n_airings, count(DISTINCT start_time::DATE) AS n_days
            FROM '{pq('schedule')}' WHERE tv_show_id <> 0 AND week BETWEEN {t0} AND {t1} GROUP BY 1""").df() \
            .set_index("tv_show_id")
        self.fallback = popularity_list(usw, hist_weeks, POP_N, self.pool)
        h = window(usw, (h1 - POP_N + 1, h1))
        pop = h[h["tv_show_id"].isin(self.pool.index)].groupby("tv_show_id", as_index=False)["watch_sec"].sum()
        con.register("pop_df", pop)
        self.channel_rows = con.sql(f"""
            WITH uc AS (
                SELECT user_id, channel_id, sum(epoch(stop_time) - epoch(start_time)) AS sec
                FROM '{pq('view_segments')}' WHERE week BETWEEN {h0} AND {h1} GROUP BY ALL),
            ranked AS (
                SELECT *, sec / sum(sec) OVER (PARTITION BY user_id) AS share,
                       row_number() OVER (PARTITION BY user_id ORDER BY sec DESC, channel_id) AS ch_rank
                FROM uc),
            sc AS (
                SELECT DISTINCT channel_id, tv_show_id FROM '{pq('schedule')}'
                WHERE tv_show_id <> 0 AND week BETWEEN {t0} AND {t1})
            SELECT r.user_id, r.ch_rank, sc.tv_show_id, r.share * p.watch_sec AS score
            FROM ranked r JOIN sc USING (channel_id) JOIN pop_df p USING (tv_show_id)
            WHERE r.ch_rank <= {max(CHANNEL_M)} AND p.watch_sec > 0""").df()

    def decay(self, week: pd.Series, half_life):
        return 1.0 if half_life is None else 0.5 ** ((self.hist_weeks[1] - week) / half_life)

    def user_counts(self, unit, threshold, half_life) -> pd.DataFrame:
        u = self.user_week[threshold]
        u = u[u["tv_show_id"].isin(self.pool.index)]
        return u[["user_id", "tv_show_id"]].assign(w=u[unit] * self.decay(u["week"], half_life)) \
            .groupby(["user_id", "tv_show_id"], as_index=False)["w"].sum()

    def freq(self, unit, threshold, half_life) -> dict[int, list[int]]:
        return top_k_lists(self.user_counts(unit, threshold, half_life).rename(columns={"w": "score"}), ["score"])

    def loyalty(self, unit, threshold, half_life, beta, delta) -> dict[int, list[int]]:
        df = self.user_counts(unit, threshold, half_life)
        s = self.show_week
        a = s[["tv_show_id"]].assign(a=s[unit] * self.decay(s["week"], half_life)).groupby("tv_show_id")["a"].sum()
        df["a"] = a.reindex(df["tv_show_id"]).fillna(0).to_numpy()
        df["a"] = df[["a", "w"]].max(axis=1)  # a pair can come from an airing that started before the window
        t = self.target[unit].reindex(df["tv_show_id"]).fillna(0).to_numpy()
        df["score"] = df["w"] / (df["a"] + beta) * t ** delta
        return top_k_lists(df, ["score"])

    def channel_fill(self, m) -> dict[int, list[int]]:
        c = self.channel_rows[self.channel_rows["ch_rank"] <= m]
        c = c.groupby(["user_id", "tv_show_id"], as_index=False)["score"].max()
        return top_k_lists(c, ["score"], k=2 * K)


def combine(own: dict, extra: dict | None, users: list[int]) -> dict[int, list[int]]:
    if extra is None:
        return own
    return {u: list(dict.fromkeys(own.get(u, [])[:K] + extra.get(u, []))) for u in users}


def predict(st: Stats, params: dict, users: list[int]) -> tuple[dict, dict]:
    """(own ranking, own + channel fill) for a repeat_v2 params dict; the caller applies the shared fallback."""
    kw = {k: params[k] for k in ("unit", "threshold", "half_life")}
    own = st.freq(**kw) if params["score"] == "freq" else st.loyalty(**kw, beta=params["beta"], delta=params["delta"])
    extra = None if params["fill"] == "global" else st.channel_fill(int(params["fill"].removeprefix("channels_m")))
    return own, combine(own, extra, users)


def main() -> None:
    t_all = time.time()
    con = connect()
    data = validation_data()
    users_all = sorted(set(data.populations["test_users"]) | set(data.populations["active_both"]))
    st = Stats(con, data.usw, HIST_WEEKS, TARGET_WEEKS)
    print(f"stats ready in {time.time() - t_all:.1f} s", flush=True)
    rows = []

    def record(method, params, own, extra=None, notes=""):
        t = time.time()
        preds = fill(combine(own, extra, users_all), users_all, st.fallback)
        res = evaluate(preds, data)
        log_results(method, params, res, time.time() - t, f"fallback=popularity_n_weeks={POP_N}; selection=mean(n_days,n_airings)" + (f"; {notes}" if notes else ""))
        rows.append({"method": method, "params": params, "select": selection_score(res),
                     **{f"{p}/{d}": v[1] for (p, d), v in res.items()}})
        print(f"{method} {params}: select={rows[-1]['select']:.4f}", flush=True)

    # references on the same harness
    record("popularity", {"n_weeks": POP_N}, {}, notes="reference")
    record("repeat", {"half_life": 8, "transform": "log", "alpha": 0.0},
           repeat_ranked(data.usw, HIST_WEEKS, data.pool, 8, "log", 0.0), notes="reference: repeat_v1 config")

    cache = {}
    for unit, thr, hl in itertools.product(UNITS, THRESHOLDS, FREQ_HALF_LIVES):
        p = {"score": "freq", "unit": unit, "threshold": thr, "half_life": hl, "fill": "global"}
        cache[str(p)] = own = st.freq(unit, thr, hl)
        record("repeat_v2", p, own)
    for unit, thr, hl, beta, delta in itertools.product(UNITS, THRESHOLDS, LOY_HALF_LIVES, BETAS, DELTAS):
        p = {"score": "loyalty", "unit": unit, "threshold": thr, "half_life": hl, "beta": beta, "delta": delta,
             "fill": "global"}
        cache[str(p)] = own = st.loyalty(unit, thr, hl, beta, delta)
        record("repeat_v2", p, own)

    top3 = sorted([r for r in rows if r["method"] == "repeat_v2"], key=lambda r: -r["select"])[:3]
    for r, m in itertools.product(top3, CHANNEL_M):
        p = {**r["params"], "fill": f"channels_m{m}"}
        record("repeat_v2", p, cache[str(r["params"])], st.channel_fill(m))

    best = max([r for r in rows if r["method"] == "repeat_v2"], key=lambda r: r["select"])["params"]

    # --- refit on weeks 11-30, predict 31-42
    users = test_users()
    fin = Stats(con, data.usw, FINAL_HIST_WEEKS, TEST_WEEKS)
    own, combined = predict(fin, best, users)
    preds = fill(combined, users, fin.fallback)
    write_submission(preds, users, SUB)
    problems = check_submission(SUB, set(int(x) for x in fin.pool.index))
    print(SUB.name, "format problems:", problems or "none")
    n_own = [min(len(own.get(u, [])), K) for u in users]
    n_comb = [min(len(combined.get(u, [])), K) for u in users]
    with open(ROOT / "submissions" / "LOG.md", "a", encoding="utf-8") as f:
        f.write(f"| {SUB.name} | repeat_v2, {best}, fallback popularity n_weeks={POP_N}; fit weeks 11-30, "
                f"pool = labelled shows airing weeks 31-42 | {dt.date.today().isoformat()} |  |  |  |\n")

    # --- results file
    cols = [f"{p}/{d}" for p in data.populations for d in ("n_days", "n_airings", "watch_sec")]
    lines = ["# Repeat v2: validation results", "",
             f"Produced by `python -m src.repeat_v2` on {dt.datetime.now():%Y-%m-%d %H:%M}. Same harness as stage 2: "
             f"history weeks {HIST_WEEKS[0]}-{HIST_WEEKS[1]}, target weeks 21-30, pool {len(data.pool)} shows, "
             f"populations test_users {len(data.populations['test_users'])} / active_both "
             f"{len(data.populations['active_both'])}. `select` = mean MAP@5 of {', '.join(SELECT_DEFS)} on test_users "
             "(see docs/target_definition.md).", "",
             "| method | params | select | " + " | ".join(cols) + " |", "|---|---|---|" + "---|" * len(cols)]
    for r in sorted(rows, key=lambda r: -r["select"]):
        lines.append(f"| {r['method']} | `{r['params']}` | {r['select']:.4f} | "
                     + " | ".join(f"{r[c]:.4f}" for c in cols) + " |")
    lines += ["", f"Selected: {best}.", "",
              f"Final refit (weeks 11-30 -> 31-42), test users: {sum(n == 0 for n in n_own)} with no own items, "
              f"{K * len(users) - sum(n_own)} of {K * len(users)} slots not filled by own items; "
              f"after channel fill {K * len(users) - sum(n_comb)} slots left for global popularity.", "",
              f"Submission format check {SUB.name}: {'OK' if not problems else problems}.", "",
              f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
