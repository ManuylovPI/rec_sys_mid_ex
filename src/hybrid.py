"""Hybrid: candidate generation + LightGBM re-ranker.

Candidates per user (all within the target-window pool): union of the top-N of
  repeat   own watched shows ranked by the loyalty score of the selected repeat config
  pop      global popularity (watch seconds, last 10 history weeks)
  als      the selected ALS config, refit on the history window
  chan     popular shows airing on the user's top-5 channels (score = channel share x popularity)

Features (count features are per week of their window, decayed sums are divided by the sum of the decay
weights, so windows of different length are comparable):
  user   viewing seconds per week, share of history days with any viewing, number of labelled shows watched
  pair   decayed days / airings / seconds, plain days and seconds per week, weeks since last watched, share of
         history weeks with the show, loyalty ratio and loyalty score (repeat), repeat rank, ALS score and rank,
         CBF cosine, user's share of time on the show's target-window channels, channel-candidate score and rank,
         time-of-day fit = sum_h P_user(h) * P_show_airtime_in_target(h)
  show   airing days and airings per week in the target window, airing days per week in history, aired in history
         (0/1), popularity (seconds per week, share of users, days per week), popularity rank, category
CBF and category use metadata from schedule weeks <= end of the history window only (strict reading of the spec;
for the submission that is weeks <= 30, so test-only shows have no metadata).

Training (validation): features from weeks 11-20, labels from weeks 21-30, users NOT in the 1,260 test users;
10% of those users (seed 42) are held out for early stopping. Evaluated on the test users exactly like the
other methods. Labels: binary = show in the user's days top-5; lambdarank graded by target days
(log2 buckets) or by top-5 rank.
Temporal check: the same model trained on weeks 11-15 -> 16-20 (non-test users) and evaluated on the same
validation, so no label from weeks 21-30 is used in training at all.
Final: model trained on weeks 11-20 -> 21-30 with all users and the validated number of trees, applied to
features from weeks 11-30 for the target weeks 31-42.

Usage: python -m src.hybrid [--final-only]   ->  experiments.csv rows, docs/hybrid_results.md,
                                  docs/hybrid_feature_importance.md, docs/methods_results.md section,
                                  submissions/hybrid_v1.csv (only if it clearly beats repeat)
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import dataclasses  # noqa: E402
import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import implicit  # noqa: E402
import lightgbm as lgb  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from implicit.nearest_neighbours import bm25_weight  # noqa: E402
from sklearn.preprocessing import normalize  # noqa: E402

from src.als import AlsData  # noqa: E402
from src.cbf import item_matrix, show_tokens  # noqa: E402
from src.data import PROCESSED, ROOT, SEED  # noqa: E402
from src.evaluation import (EXPERIMENTS, SELECT_DEFS, cov_ground_truth, FINAL_HIST_WEEKS, HIST_WEEKS, TARGET_WEEKS, TEST_WEEKS, evaluate,  # noqa: E402
                            fill, ground_truth, log_results, selection_score, test_users, validation_data, window)
from src.metrics import K  # noqa: E402
from src.method_utils import load_best, save_best  # noqa: E402
from src.repeat_v2 import POP_N, Stats  # noqa: E402
from src.slots import SlotModel, dropped_shows  # noqa: E402
from src.submission import check_submission, write_submission  # noqa: E402

OUT_MD = ROOT / "docs" / "hybrid_results.md"
IMP_MD = ROOT / "docs" / "hybrid_feature_importance.md"
METHODS_MD = ROOT / "docs" / "methods_results.md"
SUB = ROOT / "submissions" / "hybrid_v1.csv"
HL = 8
N_CAND = 20
RECALL_NS = [5, 10, 20, 50]
TEMPORAL_TRAIN = ((11, 15), (16, 20))
OBJECTIVES = ["binary", "lambdarank_log", "lambdarank_top5"]
NUM_LEAVES = [15, 63]
MIN_CHILD = [20, 100]
CLEAR_MARGIN = 0.01  # "clearly beats" margin on the selection score
SLOT_FEATURES = ["slot_score", "slot_rank", "slot_hours", "repl_score", "s_no_view_hist"]
COV_FEATURES = ["cov30", "cov50", "cov80", "cov80_rank", "cov80_share", "s_sched_ratio_airings", "s_sched_ratio_days",
                "s_channel"]
CATEGORICAL = ["s_category", "s_channel"]
COV50_FEATURES = ["cov30_rank", "cov50_rank", "rc_score", "rc_rank"]


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


class Window:
    """Candidates and features for one (history window, target window)."""

    def __init__(self, con, usw, hist_weeks, target_weeks, best, slots: bool = False, coverage: bool = False,
                 cov_target: bool = False):
        t0 = time.time()
        self.slots = slots
        self.coverage = coverage or cov_target
        self.cov_target = cov_target
        self.usw = usw
        self.hw, self.tw = hist_weeks, target_weeks
        h0, h1 = hist_weeks
        t_0, t_1 = target_weeks
        self.n_hist, self.n_target = h1 - h0 + 1, t_1 - t_0 + 1
        self.st = st = Stats(con, usw, hist_weeks, target_weeks)
        self.pool = st.pool.index.to_numpy()
        rep = best["repeat"]

        # ---- user x show history
        d_w = 0.5 ** ((h1 - np.arange(h0, h1 + 1)) / HL)
        dnorm = d_w.sum()
        uw = st.user_week["none"]
        sec = window(usw, hist_weeks)[["user_id", "tv_show_id", "week", "watch_sec"]]
        h = uw.merge(sec, on=["user_id", "tv_show_id", "week"], how="outer").fillna(0)
        h["d"] = 0.5 ** ((h1 - h["week"]) / HL)
        g = h.assign(dd=h["n_days"] * h["d"], da=h["n_airings"] * h["d"], ds=h["watch_sec"] * h["d"]) \
            .groupby(["user_id", "tv_show_id"]).agg(dd=("dd", "sum"), da=("da", "sum"), ds=("ds", "sum"),
                                                     days=("n_days", "sum"), sec=("watch_sec", "sum"),
                                                     last_week=("week", "max"), weeks=("week", "nunique")).reset_index()
        sw = st.show_week
        a_days = sw.assign(a=sw["n_days"] * 0.5 ** ((h1 - sw["week"]) / HL)).groupby("tv_show_id")["a"].sum()
        a = a_days.reindex(g["tv_show_id"]).fillna(0).to_numpy()
        t_days = st.target["n_days"]
        hist = pd.DataFrame({
            "user_id": g["user_id"], "tv_show_id": g["tv_show_id"],
            "h_d_days": g["dd"] / dnorm, "h_d_airings": g["da"] / dnorm, "h_d_sec": g["ds"] / dnorm,
            "h_days_pw": g["days"] / self.n_hist, "h_sec_pw": g["sec"] / self.n_hist,
            "h_weeks_since_last": h1 - g["last_week"], "h_weeks_frac": g["weeks"] / self.n_hist,
        })
        hist["h_loyalty"] = g["dd"] / (np.maximum(a, g["dd"]) + rep["beta"])
        hist["h_loyalty_score"] = hist["h_loyalty"] * (
            t_days.reindex(g["tv_show_id"]).fillna(0).to_numpy() / self.n_target) ** rep["delta"]
        hist = hist[hist["tv_show_id"].isin(self.pool)].copy()
        hist["rep_rank"] = hist.groupby("user_id")["h_loyalty_score"].rank(ascending=False, method="first")
        self.hist = hist

        # ---- shows
        pop_weeks = min(POP_N, self.n_hist)
        ph = window(usw, (h1 - pop_weeks + 1, h1))
        all_hist = window(usw, hist_weeks)
        n_users = all_hist["user_id"].nunique()
        shows = pd.DataFrame(index=pd.Index(self.pool, name="tv_show_id"))
        shows["s_t_days_pw"] = st.target["n_days"].reindex(self.pool).fillna(0).to_numpy() / self.n_target
        shows["s_t_airings_pw"] = st.target["n_airings"].reindex(self.pool).fillna(0).to_numpy() / self.n_target
        hist_air = sw.groupby("tv_show_id")["n_days"].sum()
        shows["s_hist_air_days_pw"] = hist_air.reindex(self.pool).fillna(0).to_numpy() / self.n_hist
        shows["s_aired_in_hist"] = (shows["s_hist_air_days_pw"] > 0).astype(int)
        shows["s_pop_sec_pw"] = ph.groupby("tv_show_id")["watch_sec"].sum().reindex(self.pool).fillna(0).to_numpy() / pop_weeks
        shows["s_pop_users"] = all_hist.groupby("tv_show_id")["user_id"].nunique().reindex(self.pool).fillna(0).to_numpy() / n_users
        shows["s_pop_days_pw"] = all_hist.groupby("tv_show_id")["n_days"].sum().reindex(self.pool).fillna(0).to_numpy() / self.n_hist
        shows["pop_rank"] = shows["s_pop_sec_pw"].rank(ascending=False, method="first")
        hist_airings = sw.groupby("tv_show_id")["n_airings"].sum().reindex(self.pool).fillna(0).to_numpy() / self.n_hist
        shows["s_sched_ratio_airings"] = (shows["s_t_airings_pw"] + 0.1) / (hist_airings + 0.1)
        shows["s_sched_ratio_days"] = (shows["s_t_days_pw"] + 0.1) / (shows["s_hist_air_days_pw"] + 0.1)
        main_ch = con.sql(f"""
            SELECT tv_show_id, mode(channel_id) AS ch FROM '{pq('schedule')}'
            WHERE tv_show_id <> 0 AND week BETWEEN {t_0} AND {t_1} GROUP BY 1""").df().set_index("tv_show_id")["ch"]
        shows["s_channel"] = main_ch.reindex(self.pool).to_numpy()
        meta = con.sql(f"""
            SELECT tv_show_id, mode(tv_show_category) AS cat FROM '{pq('schedule')}'
            WHERE tv_show_id <> 0 AND week <= {h1} GROUP BY 1""").df().set_index("tv_show_id")["cat"]
        cats = sorted(con.sql(f"SELECT DISTINCT tv_show_category FROM '{pq('schedule')}' WHERE week <= 30 "
                              "AND tv_show_category IS NOT NULL").df()["tv_show_category"])
        shows["s_category"] = meta.reindex(self.pool).map({c: i for i, c in enumerate(cats)}).to_numpy()
        self.shows = shows
        self.pop_list = shows.sort_values(["s_pop_sec_pw"], ascending=False).index.to_numpy()

        # ---- users
        self.users_df = con.sql(f"""
            SELECT user_id, sum(epoch(stop_time) - epoch(start_time)) / {self.n_hist} AS u_sec_pw,
                   count(DISTINCT start_time::DATE) / {7 * self.n_hist} AS u_days_frac
            FROM '{pq('view_segments')}' WHERE week BETWEEN {h0} AND {h1} GROUP BY 1""").df().set_index("user_id")
        self.users_df["u_n_shows"] = g.groupby("user_id")["tv_show_id"].nunique().reindex(self.users_df.index).fillna(0)

        # ---- ALS
        ap = best["als"]
        self.ad = ad = AlsData(st)
        m = ad.matrix
        if ap["weighting"] == "bm25":
            m = bm25_weight(m, K1=ap["bm25_k1"], B=ap["bm25_b"]).tocsr().astype(np.float32)
        model = implicit.cpu.als.AlternatingLeastSquares(factors=ap["factors"], regularization=ap["reg"],
                                                         alpha=ap["alpha"], iterations=ap["iters"], random_state=SEED)
        model.fit(m, show_progress=False)
        self.als_scores = model.user_factors @ model.item_factors[ad.pool_cols].T  # users x pool items with factors
        self.als_items = ad.items[ad.pool_cols]
        self.als_rank = (-self.als_scores).argsort(axis=1).argsort(axis=1) + 1

        # ---- CBF (metadata from weeks <= end of history)
        cp = best["cbf"]
        tokens = show_tokens(con, max_week=h1)
        x = item_matrix(tokens, cp["rep"], cp["min_df"], cp["people_weight"])
        self.cbf_items = tokens["tv_show_id"].to_numpy()
        hw_ = g[g["tv_show_id"].isin(self.cbf_items)]
        cu = np.sort(hw_["user_id"].unique())
        wmat = sp.csr_matrix((hw_["dd"].to_numpy(), (np.searchsorted(cu, hw_["user_id"].to_numpy()),
                                                      np.searchsorted(self.cbf_items, hw_["tv_show_id"].to_numpy()))),
                             shape=(len(cu), len(self.cbf_items)))
        self.cbf_users, self.cbf_x = cu, x
        self.cbf_prof = normalize(wmat @ x, norm="l2").tocsr()

        # ---- channels and time of day
        self.user_channel = con.sql(f"""
            SELECT user_id, channel_id, sum(epoch(stop_time) - epoch(start_time)) AS sec
            FROM '{pq('view_segments')}' WHERE week BETWEEN {h0} AND {h1} GROUP BY ALL""").df()
        self.user_channel["share"] = self.user_channel["sec"] / self.user_channel.groupby("user_id")["sec"].transform("sum")
        self.show_channels = con.sql(f"""
            SELECT DISTINCT tv_show_id, channel_id FROM '{pq('schedule')}'
            WHERE tv_show_id <> 0 AND week BETWEEN {t_0} AND {t_1}""").df()
        hod_sql = """
            WITH x AS (SELECT {key}, a, b, unnest(range(a // 3600, (b - 1) // 3600 + 1)) AS hb FROM ({src}))
            SELECT {key}, hb % 24 AS hod, sum(least(b, (hb + 1) * 3600) - greatest(a, hb * 3600)) AS sec
            FROM x GROUP BY ALL"""
        uh = con.sql(hod_sql.format(key="user_id", src=f"""
            SELECT user_id, epoch(start_time)::BIGINT AS a, epoch(stop_time)::BIGINT AS b FROM '{pq('view_segments')}'
            WHERE week BETWEEN {h0} AND {h1}""")).df()
        sh = con.sql(hod_sql.format(key="tv_show_id", src=f"""
            SELECT tv_show_id, epoch(start_time)::BIGINT AS a, epoch(end_time)::BIGINT AS b FROM '{pq('schedule')}'
            WHERE tv_show_id <> 0 AND week BETWEEN {t_0} AND {t_1}""")).df()
        self.user_hod = uh.pivot_table(index="user_id", columns="hod", values="sec", fill_value=0).reindex(columns=range(24), fill_value=0)
        self.user_hod = self.user_hod.div(self.user_hod.sum(axis=1), axis=0)
        self.show_hod = sh.pivot_table(index="tv_show_id", columns="hod", values="sec", fill_value=0).reindex(columns=range(24), fill_value=0)
        self.show_hod = self.show_hod.div(self.show_hod.sum(axis=1), axis=0)
        cr = st.channel_rows.groupby(["user_id", "tv_show_id"], as_index=False)["score"].max()
        cr["chan_rank"] = cr.groupby("user_id")["score"].rank(ascending=False, method="first")
        self.chan = cr.rename(columns={"score": "chan_score"})
        watched = set(window(usw, hist_weeks)["tv_show_id"].unique().tolist())
        self.shows["s_no_view_hist"] = (~self.shows.index.isin(list(watched))).astype(int)

        # ---- continuous-view coverage counts (coverage version)
        if self.coverage:
            op = ">" if cov_target else ">="  # cov50 version: strict, as in the target definition
            c = con.sql(f"""
                SELECT user_id, tv_show_id, week,
                       count(*) FILTER (WHERE cont_frac {op} 0.3) AS c30, count(*) FILTER (WHERE cont_frac {op} 0.5) AS c50,
                       count(*) FILTER (WHERE cont_frac {op} 0.8) AS c80
                FROM '{pq('coverage')}' WHERE week BETWEEN {h0} AND {h1} GROUP BY ALL""").df()
            dw = 0.5 ** ((h1 - c["week"]) / HL) / dnorm
            cov = c[["user_id", "tv_show_id"]].assign(cov30=c["c30"] * dw, cov50=c["c50"] * dw, cov80=c["c80"] * dw) \
                .groupby(["user_id", "tv_show_id"], as_index=False)[["cov30", "cov50", "cov80"]].sum()
            for k in (30, 50, 80):
                cov[f"cov{k}_rank"] = cov.groupby("user_id")[f"cov{k}"].rank(ascending=False, method="first")
            self.cov = cov

        # ---- repeat on the cov50 target (cov_target version): candidates, score and rank
        if cov_target:
            from src.repeat_v3 import CovCounts
            self.cc = CovCounts(con, usw, st, hist_weeks, cuts=sorted({0.3, 0.5, 0.8, best["repeat_cov"]["cut"]}))
            self.rc_params = best["repeat_cov"]
            rc = self.cc.scores({**self.rc_params, "min_count": 1})[["user_id", "tv_show_id", "score"]]
            rc["rc_rank"] = rc.groupby("user_id")["score"].rank(ascending=False, method="first")
            self.rc = rc.rename(columns={"score": "rc_score"})
            self._rc_lists = {}

        # ---- slot habits (v2)
        if slots:
            sp_ = best["slot"]
            sm = SlotModel(con, hist_weeks, target_weeks, sp_["daytype"], sp_["half_life"])
            su = [int(u) for u in sm.users]
            cols = np.flatnonzero(np.isin(sm.shows, self.pool))
            self.slot_items = sm.shows[cols]
            self.slot_pos = {u: i for i, u in enumerate(su)}
            self.slot_air = sm.scores(su, "airings")[1][:, cols].astype(np.float32)
            self.slot_hours = sm.scores(su, "hours")[1][:, cols].astype(np.float32)
            self.slot_rank = ((-self.slot_air).argsort(axis=1).argsort(axis=1) + 1).astype(np.int32)
            ru, rs = sm.replacement(su, dropped_shows(usw, hist_weeks, pd.Index(sm.shows)))
            self.repl_pos = {int(u): i for i, u in enumerate(ru)}
            self.repl = rs[:, cols].astype(np.float32)
        print(f"window {hist_weeks}->{target_weeks} built in {time.time() - t0:.1f} s", flush=True)

    # ------------------------------------------------------------------
    def candidates(self, users: list[int], n: int = N_CAND) -> pd.DataFrame:
        parts = []
        if self.cov_target:  # candidates: repeat_cov, popularity, ALS, slots
            if n not in self._rc_lists:
                self._rc_lists[n] = self.cc.ranked(self.rc_params, k=n)
            lists = self._rc_lists[n]
            pairs = [(u, x) for u in users for x in lists.get(u, [])]
            parts.append(pd.DataFrame(pairs, columns=["user_id", "tv_show_id"]).astype({"user_id": "uint64"}))
        else:
            rep = self.hist[self.hist["rep_rank"] <= n]
            parts.append(rep[rep["user_id"].isin(users)][["user_id", "tv_show_id"]])
        top_pop = self.pop_list[:n]
        uarr = np.array(users, dtype=np.uint64)
        parts.append(pd.DataFrame({"user_id": np.repeat(uarr, len(top_pop)), "tv_show_id": np.tile(top_pop, len(users))}))
        known = [u for u in users if u in self.ad.user_pos]
        rows = [self.ad.user_pos[u] for u in known]
        if rows:
            top = np.argpartition(-self.als_scores[rows], n, axis=1)[:, :n]
            parts.append(pd.DataFrame({"user_id": np.repeat(np.array(known, dtype=np.uint64), n),
                                       "tv_show_id": self.als_items[top].ravel()}))
        if not self.cov_target:
            ch = self.chan[(self.chan["chan_rank"] <= n) & self.chan["user_id"].isin(users)]
            parts.append(ch[["user_id", "tv_show_id"]])
        if self.slots:
            sk = [u for u in users if u in self.slot_pos]
            if sk:
                top = np.argpartition(-self.slot_air[[self.slot_pos[u] for u in sk]], n, axis=1)[:, :n]
                parts.append(pd.DataFrame({"user_id": np.repeat(np.array(sk, dtype=np.uint64), n),
                                           "tv_show_id": self.slot_items[top].ravel()}))
        c = pd.concat(parts).drop_duplicates()
        c["user_id"] = c["user_id"].astype("uint64")
        c["tv_show_id"] = c["tv_show_id"].astype("int64")
        return c.reset_index(drop=True)

    def features(self, cand: pd.DataFrame) -> pd.DataFrame:
        f = cand.merge(self.hist, on=["user_id", "tv_show_id"], how="left")
        f = f.merge(self.shows, left_on="tv_show_id", right_index=True, how="left")
        f = f.merge(self.users_df, left_on="user_id", right_index=True, how="left")
        f = f.merge(self.chan[["user_id", "tv_show_id", "chan_score", "chan_rank"]], on=["user_id", "tv_show_id"], how="left")
        # ALS
        ui = np.array([self.ad.user_pos.get(int(u), -1) for u in f["user_id"]])
        col = pd.Series(np.arange(len(self.als_items)), index=self.als_items)
        ii = col.reindex(f["tv_show_id"]).fillna(-1).astype(int).to_numpy()
        ok = (ui >= 0) & (ii >= 0)
        f["als_score"] = np.where(ok, self.als_scores[np.maximum(ui, 0), np.maximum(ii, 0)], np.nan)
        f["als_rank"] = np.where(ok, self.als_rank[np.maximum(ui, 0), np.maximum(ii, 0)], np.nan)
        # CBF
        cu = pd.Series(np.arange(len(self.cbf_users)), index=self.cbf_users).reindex(f["user_id"]).fillna(-1).astype(int).to_numpy()
        ci = pd.Series(np.arange(len(self.cbf_items)), index=self.cbf_items).reindex(f["tv_show_id"]).fillna(-1).astype(int).to_numpy()
        ok = (cu >= 0) & (ci >= 0)
        vals = np.full(len(f), np.nan)
        if ok.any():
            vals[ok] = np.asarray(self.cbf_prof[cu[ok]].multiply(self.cbf_x[ci[ok]]).sum(axis=1)).ravel()
        f["cbf_score"] = vals
        # channel share of the show's target channels
        sc = self.show_channels.merge(self.user_channel[["user_id", "channel_id", "share"]], on="channel_id")
        sc = sc.merge(cand, on=["user_id", "tv_show_id"]).groupby(["user_id", "tv_show_id"], as_index=False)["share"].max()
        f = f.merge(sc.rename(columns={"share": "ch_share"}), on=["user_id", "tv_show_id"], how="left")
        f["ch_share"] = f["ch_share"].fillna(0)
        # time of day fit
        uh = self.user_hod.reindex(f["user_id"].to_numpy()).to_numpy()
        shh = self.show_hod.reindex(f["tv_show_id"].to_numpy()).to_numpy()
        f["tod_fit"] = np.nansum(uh * shh, axis=1)
        if self.cov_target:
            f = f.merge(self.rc, on=["user_id", "tv_show_id"], how="left")
        if self.coverage:
            f = f.merge(self.cov, on=["user_id", "tv_show_id"], how="left")
            f[["cov30", "cov50", "cov80"]] = f[["cov30", "cov50", "cov80"]].fillna(0)
            f["cov80_share"] = np.where(f["h_d_airings"] > 0, f["cov80"] / f["h_d_airings"], np.nan)
        if self.slots:
            si = pd.Series(np.arange(len(self.slot_items)), index=self.slot_items).reindex(f["tv_show_id"]).fillna(-1).astype(int).to_numpy()
            su = np.array([self.slot_pos.get(int(u), -1) for u in f["user_id"]])
            ok = (su >= 0) & (si >= 0)
            a, b = np.maximum(su, 0), np.maximum(si, 0)
            f["slot_score"] = np.where(ok, self.slot_air[a, b], np.nan)
            f["slot_hours"] = np.where(ok, self.slot_hours[a, b], np.nan)
            f["slot_rank"] = np.where(ok, self.slot_rank[a, b], np.nan)
            ru = np.array([self.repl_pos.get(int(u), -1) for u in f["user_id"]])
            okr = (ru >= 0) & (si >= 0)
            f["repl_score"] = np.where(okr, self.repl[np.maximum(ru, 0), b], 0.0) if len(self.repl) else 0.0
        return f

    def labels(self, usw: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
        if self.cov_target:
            return self.labels_cov(usw, cand)
        t = window(usw, self.tw)
        t = t[t["tv_show_id"].isin(self.pool)].groupby(["user_id", "tv_show_id"], as_index=False)["n_days"].sum()
        lab = cand.merge(t, on=["user_id", "tv_show_id"], how="left").fillna({"n_days": 0})
        gt = ground_truth(usw, self.tw, pd.Index(self.pool), "n_days")
        rank = {(u, s): i for u, lst in gt.items() for i, s in enumerate(lst)}
        r = np.array([rank.get((int(u), int(s)), -1) for u, s in zip(lab["user_id"], lab["tv_show_id"])])
        lab["y_binary"] = (r >= 0).astype(int)
        lab["y_top5"] = np.where(r >= 0, K - r, 0)
        d = lab["n_days"].to_numpy()
        lab["y_log"] = np.where(d > 0, np.minimum(1 + np.floor(np.log2(np.maximum(d, 1))), 5), 0).astype(int)
        return lab


    def labels_cov(self, usw: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
        """Labels from the cov50 target: airings with one continuous view covering > 50% in the target window."""
        from src.data import connect
        t = connect().sql(f"""
            SELECT user_id, tv_show_id, count(*) AS cov FROM '{pq('coverage')}'
            WHERE week BETWEEN {self.tw[0]} AND {self.tw[1]} AND cont_frac > 0.5 GROUP BY ALL""").df()
        lab = cand.merge(t, on=["user_id", "tv_show_id"], how="left").fillna({"cov": 0})
        gt = cov_ground_truth(self.tw, pd.Index(self.pool), usw)
        rank = {(u, s): i for u, lst in gt.items() for i, s in enumerate(lst)}
        r = np.array([rank.get((int(u), int(s)), -1) for u, s in zip(lab["user_id"], lab["tv_show_id"])])
        lab["y_binary"] = (r >= 0).astype(int)
        lab["y_top5"] = np.where(r >= 0, K - r, 0)
        d = lab["cov"].to_numpy()
        lab["y_log"] = np.where(d > 0, np.minimum(1 + np.floor(np.log2(np.maximum(d, 1))), 5), 0).astype(int)
        return lab


FEATURES = ["u_sec_pw", "u_days_frac", "u_n_shows",
            "h_d_days", "h_d_airings", "h_d_sec", "h_days_pw", "h_sec_pw", "h_weeks_since_last", "h_weeks_frac",
            "h_loyalty", "h_loyalty_score", "rep_rank", "als_score", "als_rank", "cbf_score", "ch_share",
            "chan_score", "chan_rank", "tod_fit",
            "s_t_days_pw", "s_t_airings_pw", "s_hist_air_days_pw", "s_aired_in_hist", "s_pop_sec_pw", "s_pop_users",
            "s_pop_days_pw", "pop_rank", "s_category"]


CFG = {"slots": False, "coverage": False, "cov_target": False, "method": "hybrid_lgbm", "out_md": OUT_MD, "imp_md": IMP_MD, "sub": SUB, "key": "hybrid",
       "features": FEATURES}


def set_version(slots: bool, coverage: bool = False, cov_target: bool = False) -> None:
    """v1 = original hybrid; v2 (--slots) = slot-habit candidates and features; --slots --coverage adds the
    continuous-coverage counts, schedule-change ratios and channel (written to hybrid_v2.csv if clearly better)."""
    if cov_target:
        CFG.update(slots=True, coverage=True, cov_target=True, method="hybrid_lgbm_cov50",
                   out_md=ROOT / "docs" / "hybrid_cov50_results.md",
                   imp_md=ROOT / "docs" / "hybrid_cov50_feature_importance.md", sub=ROOT / "submissions" / "hybrid_v2.csv",
                   key="hybrid_cov50", features=FEATURES + SLOT_FEATURES + COV_FEATURES + COV50_FEATURES)
    elif coverage:
        CFG.update(slots=True, coverage=True, method="hybrid_lgbm_cov", out_md=ROOT / "docs" / "hybrid_cov_results.md",
                   imp_md=ROOT / "docs" / "hybrid_cov_feature_importance.md", sub=ROOT / "submissions" / "hybrid_v2.csv",
                   key="hybrid_cov", features=FEATURES + SLOT_FEATURES + COV_FEATURES)
    elif slots:
        CFG.update(slots=True, method="hybrid_lgbm_slots", out_md=ROOT / "docs" / "hybrid_v2_results.md",
                   imp_md=ROOT / "docs" / "hybrid_v2_feature_importance.md", sub=ROOT / "submissions" / "hybrid_v2.csv",
                   key="hybrid_v2", features=FEATURES + SLOT_FEATURES)


def v1_reference() -> tuple[float, float]:
    """Best n_days MAP@5 of hybrid v1 on test users: (main grid, temporal check), from experiments.csv."""
    e = pd.read_csv(EXPERIMENTS)
    e = e[(e["method"] == "hybrid_lgbm") & e["notes"].str.contains("target=n_days; population=test_users", regex=False)]
    temporal = e["notes"].str.contains("temporal check", regex=False)
    return float(e.loc[~temporal, "val_map5"].max()), float(e.loc[temporal, "val_map5"].max())


def train(df: pd.DataFrame, objective: str, num_leaves: int, min_child: int, n_estimators: int | None = None):
    """Fit one model. With n_estimators=None, 10% of the users are held out for early stopping."""
    label = {"binary": "y_binary", "lambdarank_log": "y_log", "lambdarank_top5": "y_top5"}[objective]
    df = df.sort_values(["user_id", "tv_show_id"]).reset_index(drop=True)
    if objective != "binary":  # groups without any positive carry no ranking signal
        pos = df.groupby("user_id")[label].transform("max") > 0
        df = df[pos].reset_index(drop=True)
    common = dict(learning_rate=0.05, num_leaves=num_leaves, min_child_samples=min_child, subsample=0.8,
                  subsample_freq=1, colsample_bytree=0.8, random_state=SEED, deterministic=True, force_row_wise=True,
                  verbose=-1, n_estimators=n_estimators or 3000)
    users = df["user_id"].unique()
    rng = np.random.default_rng(SEED)
    hold = set(rng.choice(users, size=len(users) // 10, replace=False).tolist()) if n_estimators is None else set()
    is_hold = df["user_id"].isin(hold).to_numpy()
    tr, va = df[~is_hold], df[is_hold]
    cat = [c for c in CATEGORICAL if c in CFG["features"]]
    if objective == "binary":
        model = lgb.LGBMClassifier(objective="binary", **common)
        fit_kw = {}
    else:
        model = lgb.LGBMRanker(objective="lambdarank", **common)
        fit_kw = {"group": tr.groupby("user_id", sort=False).size().to_numpy()}
    if n_estimators is None:
        fit_kw["eval_set"] = [(va[CFG["features"]], va[label])]
        fit_kw["callbacks"] = [lgb.early_stopping(100, verbose=False)]
        if objective != "binary":
            fit_kw["eval_group"] = [va.groupby("user_id", sort=False).size().to_numpy()]
            fit_kw["eval_at"] = [K]
    model.fit(tr[CFG["features"]], tr[label], categorical_feature=cat, **fit_kw)
    return model


def score(model, f: pd.DataFrame) -> np.ndarray:
    if isinstance(model, lgb.LGBMClassifier):
        return model.predict_proba(f[CFG["features"]])[:, 1]
    return model.predict(f[CFG["features"]])


def top5(f: pd.DataFrame, s: np.ndarray) -> dict[int, list[int]]:
    d = f[["user_id", "tv_show_id"]].assign(score=s).sort_values(["user_id", "score", "tv_show_id"],
                                                                  ascending=[True, False, True])
    d = d.groupby("user_id", sort=False).head(K)
    return {int(u): [int(x) for x in g] for u, g in d.groupby("user_id", sort=False)["tv_show_id"]}


def component_rows() -> dict[str, dict]:
    """Test-user MAP@5 of the selected component configs, read from experiments.csv."""
    best = load_best()
    e = pd.read_csv(EXPERIMENTS)
    e = e[e["notes"].str.contains("population=test_users", regex=False)]
    out = {}
    comps = [("popularity", "popularity", {"n_weeks": POP_N}), ("repeat (loyalty, tuned on n_days)", "repeat_v2", best["repeat"]),
             ("als", "als", best["als"]), ("cbf", "cbf", best["cbf"])]
    if "slot" in best:
        comps.append(("slot habits", "slot", best["slot"]))
    if "repeat_cov" in best:
        comps += [("repeat_cont50 (write-up Algorithm 1)", "repeat_cont",
                   {"cut": 0.5, "tie": "pop", "history": "whole window, no decay"}),
                  ("repeat_cov (re-tuned on cov50)", "repeat_cov", best["repeat_cov"])]
    for name, method, params in comps:
        sub = e[(e["method"] == method) & (e["params_json"] == json.dumps(params, sort_keys=True))]
        if sub["notes"].str.contains("data=tzfix", regex=False).any():  # prefer rows on the fixed data
            sub = sub[sub["notes"].str.contains("data=tzfix", regex=False)]
        sub = sub.assign(target=sub["notes"].str.split(";").str[0]).drop_duplicates("target", keep="last")
        vals = {n.split(";")[0].removeprefix("target="): v for n, v in zip(sub["notes"], sub["val_map5"])}
        out[name] = {"cov50": vals.get("cov50", float("nan")), "n_days": vals["n_days"], "n_airings": vals["n_airings"],
                     "watch_sec": vals["watch_sec"],
                     "select": sum(vals.get(d, float("nan")) for d in SELECT_DEFS) / len(SELECT_DEFS)}
    return out


def best_logged(method: str, temporal: bool, post_fix: bool = True) -> dict:
    """Test-user scores of the logged config of `method` with the best n_days score (main grid or temporal check),
    from rows logged after (post_fix) or before the time-zone fix (docs/errata.md)."""
    e = pd.read_csv(EXPERIMENTS)
    e = e[(e["method"] == method) & e["notes"].str.contains("population=test_users", regex=False)]
    e = e[e["notes"].str.contains("data=tzfix", regex=False) == post_fix]
    e = e[e["notes"].str.contains("temporal check", regex=False) == temporal]
    e = e.assign(target=e["notes"].str.split(";").str[0].str.removeprefix("target="))
    wide = e.drop_duplicates(["params_json", "target"], keep="last").pivot(index="params_json", columns="target", values="val_map5")
    r = wide.sort_values("n_days", ascending=False).iloc[0]
    return {"select": sum(r[d] for d in SELECT_DEFS) / len(SELECT_DEFS), "n_days": r["n_days"],
            "n_airings": r["n_airings"], "watch_sec": r["watch_sec"]}


def write_final(con, data, best, p: dict, val: "Window", all_users: list[int]) -> str:
    """Train on weeks 11-20 -> 21-30 with all users and p['n_trees'] trees, predict weeks 31-42, write + check."""
    users = test_users()
    fin = Window(con, data.usw, FINAL_HIST_WEEKS, TEST_WEEKS, best, slots=CFG["slots"], coverage=CFG["coverage"],
                 cov_target=CFG["cov_target"])
    cand_all = val.candidates(all_users)
    f_all = val.features(cand_all).merge(val.labels(data.usw, cand_all), on=["user_id", "tv_show_id"])
    model = train(f_all, p["objective"], p["num_leaves"], p["min_child_samples"], n_estimators=p["n_trees"])
    f_fin = fin.features(fin.candidates(users))
    preds = fill(top5(f_fin, score(model, f_fin)), users, fin.st.fallback)
    sub = CFG["sub"]
    write_submission(preds, users, sub)
    problems = check_submission(sub, set(int(x) for x in fin.pool))
    log = ROOT / "submissions" / "LOG.md"
    kept = [ln for ln in log.read_text(encoding="utf-8").splitlines() if not ln.startswith(f"| {sub.name} |")]
    kept.append(f"| {sub.name} | hybrid LightGBM re-ranker{' on cov50 labels (repeat_cov, ALS, popularity, slot candidates)' if CFG['cov_target'] else ' with slot features' if CFG['slots'] else ''} {p}; trained weeks 11-20 -> 21-30 on all users with "
                f"{p['n_trees']} trees; features weeks 11-30, pool = labelled shows airing weeks 31-42 | "
                f"{dt.date.today().isoformat()} |  |  |  |")
    log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    note = f"{sub.name}: format {'OK' if not problems else problems}"
    print(note, flush=True)
    return note


def final_only() -> None:
    """Regenerate the submission from the stored final config without re-running the grid."""
    from src.data import connect
    con = connect()
    best = load_best()
    data = validation_data()
    val = Window(con, data.usw, HIST_WEEKS, TARGET_WEEKS, best, slots=CFG["slots"], coverage=CFG["coverage"],
                 cov_target=CFG["cov_target"])
    all_users = sorted(set(val.hist["user_id"].tolist()) | set(data.populations["test_users"]))
    note = write_final(con, data, best, best[CFG["key"] + "_final"], val, all_users)
    with open(CFG["out_md"], "a", encoding="utf-8") as fh:
        fh.write(f"\nRegenerated {dt.datetime.now():%Y-%m-%d %H:%M} with `python -m src.hybrid --final-only` using "
                 f"`{best[CFG['key'] + '_final']}` (objective with the best temporal check): {note}.\n")


def main() -> None:
    set_version("--slots" in sys.argv or "--coverage" in sys.argv, "--coverage" in sys.argv, "--cov-target" in sys.argv)
    if "--final-only" in sys.argv:
        final_only()
        return
    t_all = time.time()
    from src.data import connect
    con = connect()
    best = load_best()
    data = validation_data()
    test = data.populations["test_users"]
    test_set = set(test)
    data_test = dataclasses.replace(data, populations={"test_users": test})

    val = Window(con, data.usw, HIST_WEEKS, TARGET_WEEKS, best, slots=CFG["slots"], coverage=CFG["coverage"],
                 cov_target=CFG["cov_target"])
    all_users = sorted(set(val.hist["user_id"].tolist()) | test_set)
    train_users = [u for u in all_users if u not in test_set]

    # ---- candidate recall on the days target (test users)
    gt = data.gts[SELECT_DEFS[0]]
    n_gt = sum(len(gt.get(u, [])) for u in test)
    recall_rows = []
    for n in RECALL_NS:
        c = val.candidates(test, n)
        cs = c.groupby("user_id")["tv_show_id"].agg(set).to_dict()
        hits = sum(len(set(gt.get(u, [])) & cs.get(u, set())) for u in test)
        recall_rows.append((n, len(c) / len(test), hits / n_gt))
    print("recall", recall_rows, flush=True)

    cand_test = val.candidates(test)
    f_test = val.features(cand_test)
    cand_tr = val.candidates(train_users)
    f_tr = val.features(cand_tr).merge(val.labels(data.usw, cand_tr), on=["user_id", "tv_show_id"])
    print(f"train rows {len(f_tr)} ({len(train_users)} users), test rows {len(f_test)}", flush=True)

    rows, models = [], {}
    for obj, nl, mc in itertools.product(OBJECTIVES, NUM_LEAVES, MIN_CHILD):
        t = time.time()
        model = train(f_tr, obj, nl, mc)
        preds = fill(top5(f_test, score(model, f_test)), test, val.st.fallback)
        res = evaluate(preds, data_test)
        p = {"objective": obj, "num_leaves": nl, "min_child_samples": mc, "n_trees": int(model.best_iteration_ or model.n_estimators),
             "n_cand": N_CAND, "train": "weeks 11-20 -> 21-30, non-test users"}
        log_results(CFG["method"], p, res, time.time() - t,
                    f"fallback=popularity_n_weeks={POP_N}; selection={'+'.join(SELECT_DEFS)}; trained on non-test users")
        rows.append({"params": p, "select": selection_score(res), **{d: v[1] for (_, d), v in res.items()}})
        models[json.dumps(p, sort_keys=True)] = model
        print(f"hybrid {p}: select={rows[-1]['select']:.4f}", flush=True)
    best_row = max(rows, key=lambda r: r["select"])
    best_model = models[json.dumps(best_row["params"], sort_keys=True)]

    # ---- temporal check: train on 11-15 -> 16-20, evaluate on the same validation
    early = Window(con, data.usw, *TEMPORAL_TRAIN, best, slots=CFG["slots"], coverage=CFG["coverage"],
                 cov_target=CFG["cov_target"])
    early_users = [u for u in sorted(set(early.hist["user_id"].tolist())) if u not in test_set]
    cand_e = early.candidates(early_users)
    f_e = early.features(cand_e).merge(early.labels(data.usw, cand_e), on=["user_id", "tv_show_id"])
    temporal_rows = []
    for obj in OBJECTIVES:
        r = max((x for x in rows if x["params"]["objective"] == obj), key=lambda x: x["select"])
        t = time.time()
        model = train(f_e, obj, r["params"]["num_leaves"], r["params"]["min_child_samples"])
        preds = fill(top5(f_test, score(model, f_test)), test, val.st.fallback)
        res = evaluate(preds, data_test)
        p = {**r["params"], "n_trees": int(model.best_iteration_ or model.n_estimators),
             "train": "weeks 11-15 -> 16-20, non-test users"}
        log_results(CFG["method"], p, res, time.time() - t,
                    f"fallback=popularity_n_weeks={POP_N}; selection={'+'.join(SELECT_DEFS)}; temporal check")
        temporal_rows.append({"params": p, "select": selection_score(res), **{d: v[1] for (_, d), v in res.items()}})
        print(f"temporal {p}: select={temporal_rows[-1]['select']:.4f}", flush=True)

    # ---- feature importance
    imp = pd.DataFrame({"feature": CFG["features"], "gain": best_model.booster_.feature_importance("gain"),
                        "splits": best_model.booster_.feature_importance("split")})
    imp["gain_share"] = imp["gain"] / imp["gain"].sum()
    imp = imp.sort_values("gain", ascending=False)
    CFG["imp_md"].write_text("\n".join(
        ["# Hybrid re-ranker: feature importance", "",
         f"Produced by `python -m src.hybrid{' --cov-target' if CFG['cov_target'] else ' --coverage' if CFG['coverage'] else ' --slots' if CFG['slots'] else ''}` on {dt.datetime.now():%Y-%m-%d %H:%M}. Model: `{best_row['params']}`.", "",
         "| feature | gain share | splits |", "|---|---|---|"]
        + [f"| {r.feature} | {r.gain_share:.4f} | {r.splits} |" for r in imp.itertuples()]) + "\n", encoding="utf-8")

    comp = component_rows()
    repeat_sel = comp["repeat"]["select"]
    best_temporal = max(temporal_rows, key=lambda r: r["select"])
    if CFG["cov_target"]:  # must beat the best repeat on cov50 by the margin (main) and in the temporal check
        ref = best["repeat_cov_select"]
        clear = best_row["select"] >= ref + CLEAR_MARGIN and best_temporal["select"] > ref
        clear_rule = f">= best repeat on cov50 + {CLEAR_MARGIN} and temporal check above it (repeat {ref:.4f})"
    elif CFG["coverage"]:  # must beat hybrid v2 re-run on the fixed data by the margin in both runs
        r_main, r_temp = best_logged("hybrid_lgbm_slots", False), best_logged("hybrid_lgbm_slots", True)
        ref_main, ref_temporal = r_main["n_days"], r_temp["n_days"]
        clear = best_row["select"] >= ref_main + CLEAR_MARGIN and best_temporal["select"] >= ref_temporal + CLEAR_MARGIN
        clear_rule = (f">= hybrid v2 (fixed data) + {CLEAR_MARGIN} on n_days in both runs (v2 main {ref_main:.4f}, "
                      f"v2 temporal {ref_temporal:.4f})")
    elif CFG["slots"]:  # must beat hybrid v1 by the margin in both the main run and the temporal check
        ref_main, ref_temporal = v1_reference()
        clear = best_row["select"] >= ref_main + CLEAR_MARGIN and best_temporal["select"] >= ref_temporal + CLEAR_MARGIN
        clear_rule = (f">= v1 + {CLEAR_MARGIN} on n_days in both runs (v1 main {ref_main:.4f}, v1 temporal "
                      f"{ref_temporal:.4f})")
    else:
        clear = best_row["select"] >= repeat_sel + CLEAR_MARGIN and best_temporal["select"] > repeat_sel
        clear_rule = f">= repeat + {CLEAR_MARGIN} and temporal check above repeat"
    save_best(CFG["key"], best_row["params"])
    save_best(CFG["key"] + "_select", best_row["select"])

    # ---- final: the main-grid config of the objective whose temporal check scored best
    final_obj = best_temporal["params"]["objective"]
    final_params = max((r for r in rows if r["params"]["objective"] == final_obj), key=lambda r: r["select"])["params"]
    save_best(CFG["key"] + "_final", final_params)
    if "--no-submission" in sys.argv:
        sub_note = "not written (--no-submission)"
    else:
        sub_note = write_final(con, data, best, final_params, val, all_users) if clear else "not written"

    # ---- reports
    def fmt_row(name, r):
        return (f"| {name} | {r['select']:.4f} | {r.get('cov50', float('nan')):.4f} | {r['n_days']:.4f} | "
                f"{r['n_airings']:.4f} | {r['watch_sec']:.4f} |")

    lines = [f"# Hybrid{' on cov50 labels' if CFG['cov_target'] else ' v3 (slot habits + coverage)' if CFG['coverage'] else ' v2 (slot habits)' if CFG['slots'] else ''}: candidate generation + LightGBM re-ranker", "",
             f"Produced by `python -m src.hybrid{' --cov-target' if CFG['cov_target'] else ' --coverage' if CFG['coverage'] else ' --slots' if CFG['slots'] else ''}` on {dt.datetime.now():%Y-%m-%d %H:%M}. Validation on the "
             f"{len(test)} test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). "
             f"Re-ranker trained on {len(train_users)} non-test users ({len(f_tr)} candidate rows). "
             f"Candidates: top-{N_CAND} of " + ("repeat_cov, popularity, ALS, slot" if CFG['cov_target'] else
             f"repeat, popularity, ALS, channel{', slot' if CFG['slots'] else ''}") + " lists "
             f"({len(f_test) / len(test):.1f} "
             "per test user).", "",
             f"## Candidate recall ({SELECT_DEFS[0]} target, test users)", "",
             "| top-N per source | candidates per user | recall of target top-5 |", "|---|---|---|"]
    lines += [f"| {n} | {c:.1f} | {r:.4f} |" for n, c, r in recall_rows]
    lines += ["", "## Re-ranker grid", "", "| params | select | cov50 | n_days | n_airings | watch_sec |", "|---|---|---|---|---|---|"]
    lines += [f"| `{r['params']}` | {r['select']:.4f} | {r.get('cov50', float('nan')):.4f} | {r['n_days']:.4f} | "
              f"{r['n_airings']:.4f} | {r['watch_sec']:.4f} |" for r in sorted(rows, key=lambda r: -r["select"])]
    lines += ["", "## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)", "",
              "| params | select | cov50 | n_days | n_airings | watch_sec |", "|---|---|---|---|---|---|"]
    lines += [f"| `{r['params']}` | {r['select']:.4f} | {r.get('cov50', float('nan')):.4f} | {r['n_days']:.4f} | "
              f"{r['n_airings']:.4f} | {r['watch_sec']:.4f} |" for r in temporal_rows]
    lines += ["", f"Selected: `{best_row['params']}` (select {best_row['select']:.4f}); repeat {repeat_sel:.4f}. "
              f"Clearly better ({clear_rule}): {clear}. Final config "
              f"(objective with the best temporal check): `{final_params}`. Submission: {sub_note}.",
              "", f"Total runtime: {time.time() - t_all:.1f} s."]
    CFG["out_md"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    section = ["## Hybrid vs components (test users)", "",
               f"Produced by `python -m src.hybrid{' --cov-target' if CFG['cov_target'] else ' --coverage' if CFG['coverage'] else ' --slots' if CFG['slots'] else ''}`. Components from experiments.csv (rows on the fixed data where available, docs/errata.md); hybrid = best re-ranker "
               "(trained on non-test users, weeks 11-20 -> 21-30) and its temporal check (trained on weeks 11-15 -> 16-20).", "",
               "| method | select | cov50 | n_days | n_airings | watch_sec |", "|---|---|---|---|---|---|"]
    section += [fmt_row(k, v) for k, v in comp.items()]
    if CFG["cov_target"]:
        section += [fmt_row("hybrid on cov50 labels (re-ranker)", best_row),
                    fmt_row("hybrid on cov50 labels, temporal check", best_temporal)]
    elif CFG["coverage"]:
        section += [fmt_row("hybrid v2 (+ slot habits), before tz fix", best_logged("hybrid_lgbm_slots", False, False)),
                    fmt_row("hybrid v2, temporal check, before tz fix", best_logged("hybrid_lgbm_slots", True, False)),
                    fmt_row("hybrid v2 (+ slot habits), fixed data", best_logged("hybrid_lgbm_slots", False)),
                    fmt_row("hybrid v2, temporal check, fixed data", best_logged("hybrid_lgbm_slots", True)),
                    fmt_row("hybrid v3 (+ coverage, schedule change, channel)", best_row),
                    fmt_row("hybrid v3, temporal check", best_temporal)]
    elif CFG["slots"]:
        section += [fmt_row("hybrid v1", best_logged("hybrid_lgbm", False, False)),
                    fmt_row("hybrid v1, temporal check", best_logged("hybrid_lgbm", True, False)),
                    fmt_row("hybrid v2 (+ slot habits)", best_row), fmt_row("hybrid v2, temporal check", best_temporal)]
    else:
        section += [fmt_row("hybrid (LightGBM re-ranker)", best_row), fmt_row("hybrid, temporal check", best_temporal)]
    text = METHODS_MD.read_text(encoding="utf-8")
    text = text.split("## Hybrid vs components")[0].rstrip() + "\n\n" + "\n".join(section) + "\n"
    METHODS_MD.write_text(text, encoding="utf-8")
    print(f"wrote {CFG['out_md']}, {CFG['imp_md']}, {METHODS_MD}; total {time.time() - t_all:.1f} s")


if __name__ == "__main__":
    main()
