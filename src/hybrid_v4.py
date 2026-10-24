"""Hybrid v4 on the cov50 target: wider repeat, more candidates, stacked folds, extra features, ensembles.

Steps (each logged to experiments.csv, every model with its temporal check):
  0. repeat_cov grid widened around the previous optimum (cut 0.2-0.3, half-life 2-4, beta 10-40, min_count 3-5).
  1. Candidates: top-N (N = 50) of repeat_cov, repeat_cov without the min-count filter, the >30% coverage ranking,
     the old loyalty repeat, popularity, ALS and slot habits; `n_sources` = how many sources proposed the pair.
  2. Extra features: show cov50 reach (share of users with a > 50% watch) and cov50 watches per week, user cov50
     watches per week and number of shows, weeks since the user's last > 50% watch of the show, and
     cov_expect = user's > 50% watches of the show / the show's history airings x its airings per target week.
  3. Training folds (features from the history part, labels = cov50 target of the fold's target weeks):
       single  : B = 11-20 -> 21-30 (non-test users)
       stacked : A = 11-15 -> 16-20 (all users) + B (non-test users)
     Temporal check: the same model trained only on folds whose labels end before week 21:
       single  : A;  stacked: A + C = 11-17 -> 18-20 (all users).
     Test users' labels from weeks 16-20 are history relative to the validation target, so folds A and C may
     include them. Validation is always the 1,260 test users on B features against the 21-30 cov50 target.
  4. Small LightGBM search, then rank-average ensembles (lambdarank + binary, several seeds).
Final refit for a chosen model: folds A + B + E (11-25 -> 26-30), all users, the validated number of trees,
applied to features from weeks 11-30 for weeks 31-42.

Usage: python -m src.hybrid_v4   ->  experiments.csv rows, docs/hybrid_v4_results.md, submissions/hybrid_v3*.csv
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import dataclasses  # noqa: E402
import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402

import lightgbm as lgb  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import hybrid as H  # noqa: E402
from src.data import PROCESSED, ROOT, SEED, connect  # noqa: E402
from src.evaluation import (FINAL_HIST_WEEKS, TEST_WEEKS, evaluate, fill, log_results, selection_score,  # noqa: E402
                            test_users, validation_data)
from src.method_utils import Context, load_best, save_best  # noqa: E402
from src.metrics import K  # noqa: E402
from src.repeat_v2 import POP_N  # noqa: E402
from src.repeat_v3 import CovCounts  # noqa: E402
from src.submission import check_submission, write_submission  # noqa: E402

OUT_MD = ROOT / "docs" / "hybrid_v4_results.md"
N_CAND = 50
FOLD_A, FOLD_B, FOLD_C, FOLD_E = ((11, 15), (16, 20)), ((11, 20), (21, 30)), ((11, 17), (18, 20)), ((11, 25), (26, 30))
EXTRA = ["s_cov50_users", "s_cov50_pw", "u_cov50_pw", "u_cov50_shows", "h_weeks_since_full", "cov_expect", "n_sources"]
FEATS = H.FEATURES + H.SLOT_FEATURES + H.COV_FEATURES + H.COV50_FEATURES + EXTRA
CAT = [c for c in H.CATEGORICAL if c in FEATS]
LOG = []  # rows for the results file


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


class WindowV4(H.Window):
    def __init__(self, con, usw, hist_weeks, target_weeks, best):
        super().__init__(con, usw, hist_weeks, target_weeks, best, slots=True, coverage=True, cov_target=True)
        h0, h1 = hist_weeks
        c = con.sql(f"""
            SELECT user_id, tv_show_id, week, count(*) AS c50 FROM '{pq('coverage')}'
            WHERE week BETWEEN {h0} AND {h1} AND cont_frac > 0.5 GROUP BY ALL""").df()
        n_users = max(len(self.users_df), 1)
        sh = c.groupby("tv_show_id").agg(users=("user_id", "nunique"), tot=("c50", "sum"))
        self.shows["s_cov50_users"] = sh["users"].reindex(self.pool).fillna(0).to_numpy() / n_users
        self.shows["s_cov50_pw"] = sh["tot"].reindex(self.pool).fillna(0).to_numpy() / self.n_hist
        us = c.groupby("user_id").agg(tot=("c50", "sum"), shows=("tv_show_id", "nunique"))
        self.users_df["u_cov50_pw"] = us["tot"].reindex(self.users_df.index).fillna(0).to_numpy() / self.n_hist
        self.users_df["u_cov50_shows"] = us["shows"].reindex(self.users_df.index).fillna(0).to_numpy()
        pair = c.groupby(["user_id", "tv_show_id"]).agg(c50=("c50", "sum"), last=("week", "max")).reset_index()
        hist_air = self.st.show_week.groupby("tv_show_id")["n_airings"].sum()
        t_air = self.shows["s_t_airings_pw"]
        pair["h_weeks_since_full"] = h1 - pair["last"]
        pair["cov_expect"] = (pair["c50"] / hist_air.reindex(pair["tv_show_id"]).fillna(0).clip(lower=1).to_numpy()
                              * t_air.reindex(pair["tv_show_id"]).fillna(0).to_numpy())
        self.extra_pair = pair[["user_id", "tv_show_id", "h_weeks_since_full", "cov_expect"]]
        self._rc_all = {}

    def candidates(self, users: list[int], n: int = N_CAND) -> pd.DataFrame:
        parts = [super().candidates(users, n).assign(src="base")]
        if n not in self._rc_all:
            self._rc_all[n] = self.cc.ranked({**self.rc_params, "min_count": 1}, k=n)
        lists = self._rc_all[n]
        parts.append(pd.DataFrame([(u, x) for u in users for x in lists.get(u, [])],
                                  columns=["user_id", "tv_show_id"]).astype({"user_id": "uint64"}).assign(src="rc_all"))
        cv = self.cov[self.cov["tv_show_id"].isin(self.pool) & self.cov["user_id"].isin(users)]
        cv = cv[cv.groupby("user_id")["cov30"].rank(ascending=False, method="first") <= n]
        parts.append(cv[["user_id", "tv_show_id"]].assign(src="cov30"))
        rep = self.hist[(self.hist["rep_rank"] <= n) & self.hist["user_id"].isin(users)]
        parts.append(rep[["user_id", "tv_show_id"]].assign(src="loyalty"))
        c = pd.concat(parts)
        c["user_id"] = c["user_id"].astype("uint64")
        c["tv_show_id"] = c["tv_show_id"].astype("int64")
        # base sources are already de-duplicated inside super(); count how many lists proposed each pair
        return c.groupby(["user_id", "tv_show_id"], as_index=False).size().rename(columns={"size": "n_sources"})

    def features(self, cand: pd.DataFrame) -> pd.DataFrame:
        f = super().features(cand)
        return f.merge(self.extra_pair, on=["user_id", "tv_show_id"], how="left")


def fold_frame(w: WindowV4, usw, users: list[int], k: int) -> pd.DataFrame:
    cand = w.candidates(users)
    lab = w.labels(usw, cand[["user_id", "tv_show_id"]]).drop(columns=["cov"], errors="ignore")
    f = w.features(cand).merge(lab, on=["user_id", "tv_show_id"])
    f["qid"] = f["user_id"].astype(str) + f"_{k}"
    return f


def train(df: pd.DataFrame, objective: str, num_leaves: int, min_child: int, seed: int = SEED,
          n_estimators: int | None = None, lr: float = 0.05):
    label = "y_binary" if objective == "binary" else "y_log"
    df = df.sort_values(["qid", "tv_show_id"]).reset_index(drop=True)
    if objective != "binary":
        df = df[df.groupby("qid")[label].transform("max") > 0].reset_index(drop=True)
    common = dict(learning_rate=lr, num_leaves=num_leaves, min_child_samples=min_child, subsample=0.8, subsample_freq=1,
                  colsample_bytree=0.8, random_state=seed, deterministic=True, force_row_wise=True, verbose=-1,
                  n_estimators=n_estimators or 3000)
    users = df["user_id"].unique()
    hold = set(np.random.default_rng(seed).choice(users, size=len(users) // 10, replace=False).tolist()) \
        if n_estimators is None else set()
    is_hold = df["user_id"].isin(hold).to_numpy()
    tr, va = df[~is_hold], df[is_hold]
    if objective == "binary":
        model, kw = lgb.LGBMClassifier(objective="binary", **common), {}
    else:
        model = lgb.LGBMRanker(objective="lambdarank", **common)
        kw = {"group": tr.groupby("qid", sort=False).size().to_numpy()}
    if n_estimators is None:
        kw["eval_set"] = [(va[FEATS], va[label])]
        kw["callbacks"] = [lgb.early_stopping(100, verbose=False)]
        if objective != "binary":
            kw["eval_group"] = [va.groupby("qid", sort=False).size().to_numpy()]
            kw["eval_at"] = [K]
    model.fit(tr[FEATS], tr[label], categorical_feature=CAT, **kw)
    return model


def score(model, f: pd.DataFrame) -> np.ndarray:
    if isinstance(model, lgb.LGBMClassifier):
        return model.predict_proba(f[FEATS])[:, 1]
    return model.predict(f[FEATS])


def rank_avg(f: pd.DataFrame, scores: list[np.ndarray]) -> np.ndarray:
    """Average of per-user percentile ranks of several models' scores."""
    out = np.zeros(len(f))
    for s in scores:
        out += pd.Series(s, index=f.index).groupby(f["user_id"].to_numpy()).rank(pct=True).to_numpy()
    return out / len(scores)


class Runner:
    def __init__(self, con, data, best):
        self.con, self.data, self.best = con, data, best
        self.test = data.populations["test_users"]
        self.test_set = set(self.test)
        self.data_test = dataclasses.replace(data, populations={"test_users": self.test})
        t = time.time()
        self.w = {name: WindowV4(con, data.usw, *fold, best) for name, fold in
                  (("A", FOLD_A), ("B", FOLD_B), ("C", FOLD_C))}
        self.all_users = sorted(set(self.w["B"].hist["user_id"].tolist()) | self.test_set)
        self.non_test = [u for u in self.all_users if u not in self.test_set]
        self.f_test = self.w["B"].features(self.w["B"].candidates(self.test))
        frames = {"A": fold_frame(self.w["A"], data.usw, self.all_users, 0),
                  "B": fold_frame(self.w["B"], data.usw, self.non_test, 1),
                  "C": fold_frame(self.w["C"], data.usw, self.all_users, 2)}
        self.train_sets = {"single": (frames["B"], frames["A"]),
                           "stacked": (pd.concat([frames["A"], frames["B"]]), pd.concat([frames["A"], frames["C"]]))}
        print(f"windows and frames in {time.time() - t:.1f} s; test candidates {len(self.f_test)}; "
              + ", ".join(f"{k} {len(v)}" for k, v in frames.items()), flush=True)

    def evaluate_scores(self, s: np.ndarray, method: str, params: dict, t0: float, note: str) -> dict:
        preds = fill(H.top5(self.f_test, s), self.test, self.w["B"].st.fallback)
        res = evaluate(preds, self.data_test)
        log_results(method, params, res, time.time() - t0, f"fallback=popularity_n_weeks={POP_N}; selection=cov50; {note}")
        return {d: v[1] for (_, d), v in res.items()}

    def run_model(self, setup: str, objective: str, nl: int, mc: int, seeds=(SEED,), reuse: dict | None = None) -> dict:
        """Train (main + temporal) for one config, averaging several seeds by rank; log and return both results.
        `reuse`: a run of the same config whose seed-42 models are reused instead of retrained."""
        out = {}
        for kind, idx in (("main", 0), ("temporal", 1)):
            t0 = time.time()
            models = [reuse[kind]["models"][0] if (reuse is not None and s == SEED) else
                      train(self.train_sets[setup][idx], objective, nl, mc, seed=s) for s in seeds]
            s = rank_avg(self.f_test, [score(m, self.f_test) for m in models]) if len(models) > 1 else score(models[0], self.f_test)
            p = {"setup": setup, "objective": objective, "num_leaves": nl, "min_child_samples": mc, "seeds": list(seeds),
                 "n_trees": [int(m.best_iteration_ or m.n_estimators) for m in models], "n_cand": N_CAND}
            out[kind] = {"params": p, **self.evaluate_scores(s, "hybrid_v4", p, t0, f"{kind}; v4")}
            out[kind]["models"] = models
        LOG.append(("model", out["main"]["params"], out["main"], out["temporal"]))
        print(f"{setup} {objective} nl{nl} mc{mc} seeds{list(seeds)}: main {out['main']['cov50']:.4f} "
              f"temporal {out['temporal']['cov50']:.4f}", flush=True)
        return out

    def run_ensemble(self, members: list[dict], name: str) -> dict:
        out = {}
        for kind in ("main", "temporal"):
            t0 = time.time()
            s = rank_avg(self.f_test, [score(m, self.f_test) for mem in members for m in mem[kind]["models"]])
            p = {"ensemble": name, "members": [mem["main"]["params"] for mem in members]}
            out[kind] = {"params": p, **self.evaluate_scores(s, "hybrid_v4_ensemble", p, t0, f"{kind}; v4 ensemble")}
        LOG.append(("ensemble", out["main"]["params"], out["main"], out["temporal"]))
        print(f"ensemble {name}: main {out['main']['cov50']:.4f} temporal {out['temporal']['cov50']:.4f}", flush=True)
        return out


def widen_repeat(best: dict) -> dict:
    """Step 0: widen the repeat_cov grid; returns the best params (old best included as reference)."""
    ctx = Context()
    cuts = [0.2, 0.25, 0.3]
    cc = CovCounts(ctx.con, ctx.data.usw, ctx.st, (11, 20), cuts=cuts)
    old = best["repeat_cov"]
    t = time.time()
    ctx.run("repeat_cov", old, cc.ranked(old), t, "cov50 target; reference (previous best)")
    for cut, hl, beta, mc in itertools.product(cuts, [2, 3, 4], [10, 20, 40], [3, 4, 5]):
        t = time.time()
        p = {**old, "cut": cut, "half_life": hl, "scale": f"loyalty{beta}", "min_count": mc}
        if p == old:
            continue
        ctx.run("repeat_cov", p, cc.ranked(p), t, "cov50 target; widened grid")
    top = ctx.best("repeat_cov")
    LOG.append(("repeat", top["params"], {"cov50": top["select"]}, None))
    print(f"repeat_cov widened: {top['params']} {top['select']:.4f} (previous {ctx.rows[0]['select']:.4f})", flush=True)
    if top["select"] > ctx.rows[0]["select"]:
        save_best("repeat_cov", top["params"])
        save_best("repeat_cov_select", top["select"])
    return {"previous": ctx.rows[0]["select"], "best": top["select"], "params": top["params"]}


FINAL = {}


def write_final(con, data, best, members: list[dict], name: str) -> str:
    """Retrain every member on folds A + B + E with all users and its validated trees; predict 31-42.
    Windows, training frame and trained models are cached across calls."""
    users = test_users()
    if not FINAL:
        wA, wB, wE = (WindowV4(con, data.usw, *f, best) for f in (FOLD_A, FOLD_B, FOLD_E))
        all_users = sorted(set(wE.hist["user_id"].tolist()) | set(users) | set(wB.hist["user_id"].tolist()))
        FINAL["df"] = pd.concat([fold_frame(w, data.usw, all_users, k) for k, w in enumerate((wA, wB, wE))])
        FINAL["fin"] = fin = WindowV4(con, data.usw, FINAL_HIST_WEEKS, TEST_WEEKS, best)
        FINAL["f_fin"] = fin.features(fin.candidates(users))
        FINAL["models"] = {}
    df, fin, f_fin = FINAL["df"], FINAL["fin"], FINAL["f_fin"]
    scores = []
    for mem in members:
        p = mem["main"]["params"]
        for seed, n_trees in zip(p["seeds"], p["n_trees"]):
            key = (p["objective"], p["num_leaves"], p["min_child_samples"], seed, n_trees)
            if key not in FINAL["models"]:
                FINAL["models"][key] = score(train(df, p["objective"], p["num_leaves"], p["min_child_samples"],
                                                   seed=seed, n_estimators=n_trees), f_fin)
            scores.append(FINAL["models"][key])
    s = rank_avg(f_fin, scores) if len(scores) > 1 else scores[0]
    preds = fill(H.top5(f_fin, s), users, fin.st.fallback)
    path = ROOT / "submissions" / f"{name}.csv"
    write_submission(preds, users, path)
    problems = check_submission(path, set(int(x) for x in fin.pool))
    log = ROOT / "submissions" / "LOG.md"
    kept = [ln for ln in log.read_text(encoding="utf-8").splitlines() if not ln.startswith(f"| {path.name} |")]
    desc = "; ".join(f"{m['main']['params']['objective']} nl{m['main']['params']['num_leaves']} "
                     f"mc{m['main']['params']['min_child_samples']} seeds {m['main']['params']['seeds']}" for m in members)
    kept.append(f"| {path.name} | hybrid v4 on cov50 labels ({desc}); top-{N_CAND} candidates from 7 sources, extra cov50 "
                f"features, trained on folds 11-15->16-20, 11-20->21-30, 11-25->26-30 with all users; features weeks "
                f"11-30, pool = labelled shows airing weeks 31-42 | {dt.date.today().isoformat()} |  |  |  |")
    log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return f"{path.name}: format {'OK' if not problems else problems}"


def main() -> None:
    t_all = time.time()
    best = load_best()
    rep = widen_repeat(best)
    best = load_best()
    con = connect()
    data = validation_data()
    r = Runner(con, data, best)

    # recall of the larger candidate set (cov50 target, test users)
    gt = data.gts["cov50"]
    n_gt = sum(len(gt.get(u, [])) for u in r.test)
    recall = []
    for n in (20, 50, 100):
        c = r.w["B"].candidates(r.test, n)
        cs = c.groupby("user_id")["tv_show_id"].agg(set).to_dict()
        recall.append((n, len(c) / len(r.test), sum(len(set(gt.get(u, [])) & cs.get(u, set())) for u in r.test) / n_gt))
    print("recall", recall, flush=True)

    res = {}
    res["single"] = r.run_model("single", "lambdarank_log", 15, 20)
    res["stacked"] = r.run_model("stacked", "lambdarank_log", 15, 20)
    setup = "stacked" if res["stacked"]["main"]["cov50"] >= res["single"]["main"]["cov50"] else "single"
    grid = {}
    for obj, nl, mc in itertools.product(["lambdarank_log", "binary"], [15, 63], [20, 100]):
        if (setup, obj, nl, mc) == (setup, "lambdarank_log", 15, 20):
            grid[(obj, nl, mc)] = res[setup]
            continue
        grid[(obj, nl, mc)] = r.run_model(setup, obj, nl, mc)
    best_lr = max((v for k, v in grid.items() if k[0] == "lambdarank_log"), key=lambda v: v["main"]["cov50"])
    best_bin = max((v for k, v in grid.items() if k[0] == "binary"), key=lambda v: v["main"]["cov50"])
    seeds = (SEED, SEED + 1, SEED + 2)
    lp = best_lr["main"]["params"]
    bp = best_bin["main"]["params"]
    lr3 = r.run_model(setup, "lambdarank_log", lp["num_leaves"], lp["min_child_samples"], seeds, reuse=best_lr)
    bin3 = r.run_model(setup, "binary", bp["num_leaves"], bp["min_child_samples"], seeds, reuse=best_bin)
    ens = r.run_ensemble([lr3, bin3], "lambdarank x3 seeds + binary x3 seeds")
    ens1 = r.run_ensemble([best_lr, best_bin], "lambdarank + binary, 1 seed")

    # rank candidates for submission by main validation; keep up to three distinct ones
    options = [("hybrid_v3_lr_seeds", [lr3], lr3), ("hybrid_v3_ens", [lr3, bin3], ens),
               ("hybrid_v3_lr", [best_lr], best_lr), ("hybrid_v3_ens1", [best_lr, best_bin], ens1)]
    options.sort(key=lambda o: -o[2]["main"]["cov50"])
    chosen = options[:3]
    notes = []
    for name, members, out in chosen:
        notes.append((name, out["main"]["cov50"], out["temporal"]["cov50"], write_final(con, data, best, members, name)))
        print(notes[-1], flush=True)
    save_best("hybrid_v4_options", [{"file": n, "main": m, "temporal": t} for n, m, t, _ in notes])

    lines = ["# Hybrid v4 (cov50 target)", "",
             f"Produced by `python -m src.hybrid_v4` on {dt.datetime.now():%Y-%m-%d %H:%M}. Validation: 1,260 test users, "
             "features weeks 11-20, cov50 target weeks 21-30; temporal check = same model trained only on folds with "
             "labels before week 21. Previous final hybrid_v2: main 0.4271, temporal 0.4161 (docs/hybrid_cov50_results.md).", "",
             f"## Step 0: repeat_cov widened", "", f"Previous best {rep['previous']:.4f}, widened best {rep['best']:.4f}: "
             f"`{rep['params']}`.", "",
             f"## Candidate recall (cov50, test users, 7 sources)", "", "| top-N per source | candidates per user | recall |",
             "|---|---|---|"] + [f"| {n} | {c:.1f} | {x:.4f} |" for n, c, x in recall] + \
            ["", "## Models (main = trained on folds incl. 11-20 -> 21-30 of non-test users; temporal = earlier folds only)", "",
             "| kind | params | main cov50 | main n_days | temporal cov50 | temporal n_days |", "|---|---|---|---|---|---|"]
    for kind, p, m, t in LOG:
        if kind == "repeat":
            continue
        lines.append(f"| {kind} | `{p}` | {m['cov50']:.4f} | {m['n_days']:.4f} | {t['cov50']:.4f} | {t['n_days']:.4f} |")
    lines += ["", "## Submission files (ranked by main validation)", "", "| file | main cov50 | temporal cov50 | check |",
              "|---|---|---|---|"] + [f"| {n} | {m:.4f} | {t:.4f} | {c} |" for n, m, t, c in notes]
    lines += ["", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}; total {time.time() - t_all:.1f} s")


if __name__ == "__main__":
    main()
