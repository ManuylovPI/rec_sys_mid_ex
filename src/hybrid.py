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

Usage: python -m src.hybrid   ->  experiments.csv rows, docs/hybrid_results.md,
                                  docs/hybrid_feature_importance.md, docs/methods_results.md section,
                                  submissions/hybrid_v1.csv (only if it clearly beats repeat)
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import dataclasses  # noqa: E402
import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
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
from src.evaluation import (EXPERIMENTS, FINAL_HIST_WEEKS, HIST_WEEKS, TARGET_WEEKS, TEST_WEEKS, evaluate,  # noqa: E402
                            fill, ground_truth, log_results, selection_score, test_users, validation_data, window)
from src.metrics import K  # noqa: E402
from src.method_utils import load_best, save_best  # noqa: E402
from src.repeat_v2 import POP_N, Stats  # noqa: E402
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
CLEAR_MARGIN = 0.01  # "clearly beats repeat" on the selection score


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


class Window:
    """Candidates and features for one (history window, target window)."""

    def __init__(self, con, usw, hist_weeks, target_weeks, best):
        t0 = time.time()
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
        print(f"window {hist_weeks}->{target_weeks} built in {time.time() - t0:.1f} s", flush=True)

    # ------------------------------------------------------------------
    def candidates(self, users: list[int], n: int = N_CAND) -> pd.DataFrame:
        parts = []
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
        ch = self.chan[(self.chan["chan_rank"] <= n) & self.chan["user_id"].isin(users)]
        parts.append(ch[["user_id", "tv_show_id"]])
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
        return f

    def labels(self, usw: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
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


FEATURES = ["u_sec_pw", "u_days_frac", "u_n_shows",
            "h_d_days", "h_d_airings", "h_d_sec", "h_days_pw", "h_sec_pw", "h_weeks_since_last", "h_weeks_frac",
            "h_loyalty", "h_loyalty_score", "rep_rank", "als_score", "als_rank", "cbf_score", "ch_share",
            "chan_score", "chan_rank", "tod_fit",
            "s_t_days_pw", "s_t_airings_pw", "s_hist_air_days_pw", "s_aired_in_hist", "s_pop_sec_pw", "s_pop_users",
            "s_pop_days_pw", "pop_rank", "s_category"]


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
    cat = ["s_category"]
    if objective == "binary":
        model = lgb.LGBMClassifier(objective="binary", **common)
        fit_kw = {}
    else:
        model = lgb.LGBMRanker(objective="lambdarank", **common)
        fit_kw = {"group": tr.groupby("user_id", sort=False).size().to_numpy()}
    if n_estimators is None:
        fit_kw["eval_set"] = [(va[FEATURES], va[label])]
        fit_kw["callbacks"] = [lgb.early_stopping(100, verbose=False)]
        if objective != "binary":
            fit_kw["eval_group"] = [va.groupby("user_id", sort=False).size().to_numpy()]
            fit_kw["eval_at"] = [K]
    model.fit(tr[FEATURES], tr[label], categorical_feature=cat, **fit_kw)
    return model


def score(model, f: pd.DataFrame) -> np.ndarray:
    if isinstance(model, lgb.LGBMClassifier):
        return model.predict_proba(f[FEATURES])[:, 1]
    return model.predict(f[FEATURES])


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
    for name, method, params in [("popularity", "popularity", {"n_weeks": POP_N}), ("repeat", "repeat_v2", best["repeat"]),
                                 ("als", "als", best["als"]), ("cbf", "cbf", best["cbf"])]:
        sub = e[(e["method"] == method) & (e["params_json"] == json.dumps(params, sort_keys=True))]
        sub = sub.drop_duplicates("notes", keep="last")
        vals = {n.split(";")[0].removeprefix("target="): v for n, v in zip(sub["notes"], sub["val_map5"])}
        out[name] = {"n_days": vals["n_days"], "n_airings": vals["n_airings"], "watch_sec": vals["watch_sec"],
                     "select": (vals["n_days"] + vals["n_airings"]) / 2}
    return out


def main() -> None:
    t_all = time.time()
    from src.data import connect
    con = connect()
    best = load_best()
    data = validation_data()
    test = data.populations["test_users"]
    test_set = set(test)
    data_test = dataclasses.replace(data, populations={"test_users": test})

    val = Window(con, data.usw, HIST_WEEKS, TARGET_WEEKS, best)
    all_users = sorted(set(val.hist["user_id"].tolist()) | test_set)
    train_users = [u for u in all_users if u not in test_set]

    # ---- candidate recall on the days target (test users)
    gt = data.gts["n_days"]
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
        log_results("hybrid_lgbm", p, res, time.time() - t,
                    f"fallback=popularity_n_weeks={POP_N}; selection=mean(n_days,n_airings); trained on non-test users")
        rows.append({"params": p, "select": selection_score(res), **{d: v[1] for (_, d), v in res.items()}})
        models[json.dumps(p, sort_keys=True)] = model
        print(f"hybrid {p}: select={rows[-1]['select']:.4f}", flush=True)
    best_row = max(rows, key=lambda r: r["select"])
    best_model = models[json.dumps(best_row["params"], sort_keys=True)]

    # ---- temporal check: train on 11-15 -> 16-20, evaluate on the same validation
    early = Window(con, data.usw, *TEMPORAL_TRAIN, best)
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
        log_results("hybrid_lgbm", p, res, time.time() - t,
                    f"fallback=popularity_n_weeks={POP_N}; selection=mean(n_days,n_airings); temporal check")
        temporal_rows.append({"params": p, "select": selection_score(res), **{d: v[1] for (_, d), v in res.items()}})
        print(f"temporal {p}: select={temporal_rows[-1]['select']:.4f}", flush=True)

    # ---- feature importance
    imp = pd.DataFrame({"feature": FEATURES, "gain": best_model.booster_.feature_importance("gain"),
                        "splits": best_model.booster_.feature_importance("split")})
    imp["gain_share"] = imp["gain"] / imp["gain"].sum()
    imp = imp.sort_values("gain", ascending=False)
    IMP_MD.write_text("\n".join(
        ["# Hybrid re-ranker: feature importance", "",
         f"Produced by `python -m src.hybrid` on {dt.datetime.now():%Y-%m-%d %H:%M}. Model: `{best_row['params']}`.", "",
         "| feature | gain share | splits |", "|---|---|---|"]
        + [f"| {r.feature} | {r.gain_share:.4f} | {r.splits} |" for r in imp.itertuples()]) + "\n", encoding="utf-8")

    comp = component_rows()
    repeat_sel = comp["repeat"]["select"]
    best_temporal = max(temporal_rows, key=lambda r: r["select"])
    clear = best_row["select"] >= repeat_sel + CLEAR_MARGIN and best_temporal["select"] > repeat_sel
    save_best("hybrid", best_row["params"])
    save_best("hybrid_select", best_row["select"])

    # ---- final
    sub_note = "not written"
    if clear:
        users = test_users()
        fin = Window(con, data.usw, FINAL_HIST_WEEKS, TEST_WEEKS, best)
        cand_all = val.candidates(all_users)
        f_all = val.features(cand_all).merge(val.labels(data.usw, cand_all), on=["user_id", "tv_show_id"])
        p = best_row["params"]
        model = train(f_all, p["objective"], p["num_leaves"], p["min_child_samples"], n_estimators=p["n_trees"])
        f_fin = fin.features(fin.candidates(users))
        preds = fill(top5(f_fin, score(model, f_fin)), users, fin.st.fallback)
        write_submission(preds, users, SUB)
        problems = check_submission(SUB, set(int(x) for x in fin.pool))
        sub_note = f"{SUB.name}: format {'OK' if not problems else problems}"
        with open(ROOT / "submissions" / "LOG.md", "a", encoding="utf-8") as fh:
            fh.write(f"| {SUB.name} | hybrid LightGBM re-ranker {p}; trained weeks 11-20 -> 21-30 on all users with "
                     f"{p['n_trees']} trees; features weeks 11-30, pool = labelled shows airing weeks 31-42 | "
                     f"{dt.date.today().isoformat()} |  |  |  |\n")
        print(sub_note, flush=True)

    # ---- reports
    def fmt_row(name, r):
        return f"| {name} | {r['select']:.4f} | {r['n_days']:.4f} | {r['n_airings']:.4f} | {r['watch_sec']:.4f} |"

    lines = ["# Hybrid: candidate generation + LightGBM re-ranker", "",
             f"Produced by `python -m src.hybrid` on {dt.datetime.now():%Y-%m-%d %H:%M}. Validation on the "
             f"{len(test)} test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). "
             f"Re-ranker trained on {len(train_users)} non-test users ({len(f_tr)} candidate rows). "
             f"Candidates: top-{N_CAND} of repeat, popularity, ALS and channel lists ({len(f_test) / len(test):.1f} "
             "per test user).", "",
             "## Candidate recall (days target, test users)", "",
             "| top-N per source | candidates per user | recall of target top-5 |", "|---|---|---|"]
    lines += [f"| {n} | {c:.1f} | {r:.4f} |" for n, c, r in recall_rows]
    lines += ["", "## Re-ranker grid", "", "| params | select | n_days | n_airings | watch_sec |", "|---|---|---|---|---|"]
    lines += [f"| `{r['params']}` | {r['select']:.4f} | {r['n_days']:.4f} | {r['n_airings']:.4f} | {r['watch_sec']:.4f} |"
              for r in sorted(rows, key=lambda r: -r["select"])]
    lines += ["", "## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)", "",
              "| params | select | n_days | n_airings | watch_sec |", "|---|---|---|---|---|"]
    lines += [f"| `{r['params']}` | {r['select']:.4f} | {r['n_days']:.4f} | {r['n_airings']:.4f} | {r['watch_sec']:.4f} |"
              for r in temporal_rows]
    lines += ["", f"Selected: `{best_row['params']}` (select {best_row['select']:.4f}); repeat {repeat_sel:.4f}. "
              f"Clearly beats repeat (>= +{CLEAR_MARGIN} and temporal check above repeat): {clear}. Submission: {sub_note}.",
              "", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    section = ["## Hybrid vs components (test users)", "",
               f"Produced by `python -m src.hybrid`. Components from experiments.csv; hybrid = best re-ranker "
               "(trained on non-test users, weeks 11-20 -> 21-30) and its temporal check (trained on weeks 11-15 -> 16-20).", "",
               "| method | select | n_days | n_airings | watch_sec |", "|---|---|---|---|---|"]
    section += [fmt_row(k, v) for k, v in comp.items()]
    section += [fmt_row("hybrid (LightGBM re-ranker)", best_row), fmt_row("hybrid, temporal check", best_temporal)]
    text = METHODS_MD.read_text(encoding="utf-8")
    text = text.split("## Hybrid vs components")[0].rstrip() + "\n\n" + "\n".join(section) + "\n"
    METHODS_MD.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_MD}, {IMP_MD}, {METHODS_MD}; total {time.time() - t_all:.1f} s")


if __name__ == "__main__":
    main()
