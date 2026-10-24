"""Rebuild the main results table from one data version and one label.

Every method is re-run with its selected configuration (docs/best_params.json) on the validation split:
features/history weeks 11-20, target weeks 21-30, the 1,260 test users, the shared popularity fallback.
Main target: cov50 (airings where one continuous view covers more than 50% of the airing); cov80 and n_days are
extra columns. Learned re-rankers also get the temporal check (trained only on labels before week 21); the other
methods have no label-trained parameters, so they have no temporal-check column.

Outputs: docs/results.md, docs/results_table.csv, data/processed/val_preds.parquet (validation top-5 per user
and method, with a flag for slots filled by the fallback), and the two hybrid submissions regenerated into
data/processed/regenerated/ and compared with the committed files (submission files are never overwritten).

Usage: python -m src.report_tables
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import dataclasses  # noqa: E402
import datetime as dt  # noqa: E402
import time  # noqa: E402

import pandas as pd  # noqa: E402

from src import als, cbf, hybrid as H, hybrid_v5 as V5  # noqa: E402
from src.data import PROCESSED, ROOT  # noqa: E402
from src.evaluation import (FINAL_HIST_WEEKS, HIST_WEEKS, TARGET_WEEKS, TEST_WEEKS, cov_ground_truth, evaluate,  # noqa: E402
                            fill, log_results, test_users)
from src.method_utils import Context, load_best  # noqa: E402
from src.metrics import K  # noqa: E402
from src.repeat_cont import ranked as cont_ranked  # noqa: E402
from src.repeat_v2 import POP_N  # noqa: E402
from src.repeat_v3 import CovCounts  # noqa: E402
from src.slots import SlotModel, ranked_from_scores  # noqa: E402
from src.submission import check_submission, write_submission  # noqa: E402

OUT_MD = ROOT / "docs" / "results.md"
OUT_CSV = ROOT / "docs" / "results_table.csv"
PREDS = PROCESSED / "val_preds.parquet"
REGEN = PROCESSED / "regenerated"
TARGETS = ("cov50", "cov80", "n_days")


class Report:
    def __init__(self):
        self.ctx = Context()
        d = self.ctx.data
        self.test = d.populations["test_users"]
        gts = {**d.gts, "cov80": cov_ground_truth(TARGET_WEEKS, d.pool.index, d.usw, 0.8)}
        self.data = dataclasses.replace(d, populations={"test_users": self.test}, gts=gts)
        self.rows, self.pred_rows = [], []

    def score(self, method: str, own: dict, params: dict) -> dict:
        preds = fill(own, self.test, self.ctx.st.fallback)
        res = evaluate(preds, self.data)
        log_results(method, params, res, 0.0, f"fallback=popularity_n_weeks={POP_N}; selection=cov50; report rebuild")
        for u in self.test:
            mine = own.get(u, [])[:K]
            for r, x in enumerate(preds[u]):
                self.pred_rows.append((method, u, r + 1, x, x in mine))
        return {d: v[1] for (_, d), v in res.items()}

    def add(self, method: str, config: str, own: dict, params: dict, t0: float, temporal: dict | None = None,
            preds: dict | None = None) -> None:
        main = self.score(method, preds if preds is not None else own, params)
        row = {"method": method, "configuration": config, **{f"main_{t}": main[t] for t in TARGETS},
               **{f"temporal_{t}": (temporal or {}).get(t) for t in ("cov50", "cov80")},
               "runtime_sec": time.time() - t0}
        self.rows.append(row)
        print(f"{method}: main cov50 {main['cov50']:.4f} cov80 {main['cov80']:.4f} "
              f"({row['runtime_sec']:.0f} s)", flush=True)


def hybrid_v2_setup(rep: Report, best: dict) -> tuple[dict, dict, str]:
    """The hybrid_v2 configuration: one fold, top-20 candidates, cov50 labels, lambdarank (src.hybrid --cov-target)."""
    H.set_version(True, True, True)
    con, usw = rep.ctx.con, rep.ctx.data.usw
    p = best["hybrid_cov50_final"]
    test_set = set(rep.test)
    val = H.Window(con, usw, HIST_WEEKS, TARGET_WEEKS, best, slots=True, coverage=True, cov_target=True)
    all_users = sorted(set(val.hist["user_id"].tolist()) | test_set)
    non_test = [u for u in all_users if u not in test_set]
    f_test = val.features(val.candidates(rep.test))

    def frame(w, users):
        cand = w.candidates(users)
        return w.features(cand).merge(w.labels(usw, cand), on=["user_id", "tv_show_id"])

    model = H.train(frame(val, non_test), p["objective"], p["num_leaves"], p["min_child_samples"])
    own = H.top5(f_test, H.score(model, f_test))
    early = H.Window(con, usw, (11, 15), (16, 20), best, slots=True, coverage=True, cov_target=True)
    early_users = [u for u in sorted(set(early.hist["user_id"].tolist())) if u not in test_set]
    m_t = H.train(frame(early, early_users), p["objective"], p["num_leaves"], p["min_child_samples"])
    preds_t = fill(H.top5(f_test, H.score(m_t, f_test)), rep.test, rep.ctx.st.fallback)
    temporal = {d: v[1] for (_, d), v in evaluate(preds_t, rep.data).items()}
    # regenerate the submission: all users, the validated number of trees, features weeks 11-30
    users = test_users()
    fin = H.Window(con, usw, FINAL_HIST_WEEKS, TEST_WEEKS, best, slots=True, coverage=True, cov_target=True)
    m_f = H.train(frame(val, all_users), p["objective"], p["num_leaves"], p["min_child_samples"], n_estimators=p["n_trees"])
    f_fin = fin.features(fin.candidates(users))
    path = REGEN / "hybrid_v2.csv"
    write_submission(fill(H.top5(f_fin, H.score(m_f, f_fin)), users, fin.st.fallback), users, path)
    return own, temporal, compare(path, "hybrid_v2.csv")


def compare(regenerated, committed_name: str) -> str:
    a = pd.read_csv(regenerated, dtype=str)
    b = pd.read_csv(ROOT / "submissions" / committed_name, dtype=str)
    same_rows = int((a["tv_show_id"] == b["tv_show_id"]).sum())
    sa = a["tv_show_id"].str.split().map(set)
    sb = b["tv_show_id"].str.split().map(set)
    overlap = sum(len(x & y) for x, y in zip(sa, sb)) / (K * len(a))
    problems = check_submission(regenerated)
    return (f"{committed_name}: regenerated file identical in {same_rows} of {len(a)} rows, item overlap {overlap:.4f}, "
            f"format {'OK' if not problems else problems}")


def main() -> None:
    t_all = time.time()
    REGEN.mkdir(parents=True, exist_ok=True)
    best = load_best()
    rep = Report()
    ctx = rep.ctx
    con, usw, pool = ctx.con, ctx.data.usw, ctx.st.pool

    t = time.time()
    rep.add("popularity", f"watch seconds, last {POP_N} history weeks", {}, {"n_weeks": POP_N}, t)
    t = time.time()
    rep.add("ALS", "implicit ALS, BM25, 8 factors, alpha 0.3", als.predict(ctx, best["als"]), best["als"], t)
    t = time.time()
    rep.add("CBF", "TF-IDF metadata, people weight 4", cbf.predict(ctx, best["cbf"]), best["cbf"], t)
    t = time.time()
    p_cont = {"cut": 0.5, "tie": "pop", "history": "whole window, no decay"}
    rep.add("repeat_cont50", "count of > 50% continuous watches (write-up Algorithm 1)",
            cont_ranked(con, usw, HIST_WEEKS, pool, 0.5, "pop"), p_cont, t)
    t = time.time()
    rc = best["repeat_cov"]
    cc = CovCounts(con, usw, ctx.st, HIST_WEEKS, cuts=[rc["cut"]])
    rep.add("repeat_cov", "> 30% watches, half-life 4, loyalty beta 10, min 3 watches", cc.ranked(rc), rc, t)
    t = time.time()
    sp_ = best["slot"]
    sm = SlotModel(con, HIST_WEEKS, TARGET_WEEKS, sp_["daytype"], sp_["half_life"])
    known, sc = sm.scores(ctx.users, sp_["agg"])
    rep.add("slot habits", "channel x weekday/weekend x hour affinity", ranked_from_scores(known, sc, sm.shows, pool.index),
            sp_, t)

    t = time.time()
    own_v2, temporal_v2, note_v2 = hybrid_v2_setup(rep, best)
    rep.add("hybrid_v2 setup", "LightGBM lambdarank, 1 fold, top-20 candidates, cov50 labels", own_v2,
            best["hybrid_cov50_final"], t, temporal_v2)

    t = time.time()
    fd = V5.Folds(con, ctx.data, best)
    res = V5.run(fd, "cov80", "cov80", V5.MEMBERS, V5.SEEDS)
    fin = V5.WindowV4(con, usw, FINAL_HIST_WEEKS, TEST_WEEKS, best)
    final_frame = fin.features(fin.candidates(test_users()))
    final_frame[V5.FEATS] = final_frame[V5.FEATS].astype("float32")
    V5.write_final(fd, res, "cov80", "hybrid_v4_cov80", final_frame, fin, out_dir=REGEN, log_md=False)
    note_final = compare(REGEN / "hybrid_v4_cov80.csv", "hybrid_v4_cov80.csv")
    rep.add("final (hybrid_v4_cov80)", "LightGBM lambdarank + binary x 3 seeds, 5 recency-weighted folds, cov80 labels",
            res["main"]["preds"], res["main"]["params"], t, res["temporal"], preds=res["main"]["preds"])

    table = pd.DataFrame(rep.rows)
    table.to_csv(OUT_CSV, index=False)
    pd.DataFrame(rep.pred_rows, columns=["method", "user_id", "rank", "tv_show_id", "own"]) \
        .astype({"user_id": "uint64"}).to_parquet(PREDS, index=False)

    def f(v):
        return "–" if v is None or pd.isna(v) else f"{v:.4f}"

    lines = ["# Results (one data version, one label)", "",
             f"Produced by `python -m src.report_tables` on {dt.datetime.now():%Y-%m-%d %H:%M}. Data after the time-zone "
             "fix (docs/errata.md). Validation: history weeks 11-20, target weeks 21-30, the 1,260 test users, pool = "
             f"{len(pool)} labelled shows airing in weeks 21-30, repeats allowed, shared popularity fallback. MAP@5. "
             "Main target cov50 (airings where one continuous view covers > 50% of the airing); cov80 (> 80%) and n_days "
             "(the earlier any-overlap target) for comparison. Temporal check = the same re-ranker trained only on labels "
             "before week 21; methods without label-trained parameters have none. Runtime = wall-clock seconds for "
             "fitting and scoring on this machine (docs/environment.md); for the two hybrids it includes the temporal "
             "check and the regeneration of the submission file.", "",
             "| method | configuration | cov50 | cov80 | n_days | temporal cov50 | temporal cov80 | runtime (s) |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rep.rows:
        lines.append(f"| {r['method']} | {r['configuration']} | {f(r['main_cov50'])} | {f(r['main_cov80'])} | "
                     f"{f(r['main_n_days'])} | {f(r['temporal_cov50'])} | {f(r['temporal_cov80'])} | {r['runtime_sec']:.0f} |")
    lines += ["", "## Reproducibility of the submitted hybrids", "", f"- {note_v2}", f"- {note_final}", "",
              f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}; total {time.time() - t_all:.1f} s", flush=True)


if __name__ == "__main__":
    main()
