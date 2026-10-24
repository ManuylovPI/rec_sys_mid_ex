"""Hybrid v5: recency-weighted sliding folds, and labels from the 80% coverage definition.

Two submission files, each testing one idea against hybrid_v3_ens. Candidates, features and the ensemble are those
of src.hybrid_v4 (lambdarank_log 15 leaves / min_child 20 and binary 63 leaves / min_child 100, seeds 42-44,
rank-averaged):
  hybrid_v4_recent.csv  five sliding folds with recency sample weights, cov50 labels
  hybrid_v4_cov80.csv   the same folds and weights, labels from the cov80 definition

Folds (history -> target): A 11-15 -> 16-20, C 11-17 -> 18-20, B 11-20 -> 21-30, D 11-22 -> 23-30,
E 11-25 -> 26-30, G 11-27 -> 28-30. Within a set of folds, weight = 0.5 ** ((latest start - start) / 4), where
start is the first target week, so the most recent fold of the set weighs 1 (constant within each user's query).
Validation: the 1,260 test users, features weeks 11-20, cov50 and cov80 targets in weeks 21-30.
  main      folds C, B, D, E, G; test users are dropped from every fold whose target overlaps weeks 21-30
  temporal  only folds with labels before week 21 (A, C)
Final: folds C, B, D, E, G with all users and the validated number of trees; features weeks 11-30 -> 31-42.

Labels: cov50  y_binary = in the cov50 top-5, y_log = log2 bucket (max 5) of the cov50 count (as in hybrid_v4)
        cov80  the same with the cov80 count (one continuous view covering more than 80% of the airing)
        combo  y_binary = in the cov80 top-5, y_log = bucket(cov50) + bucket(cov80)
For the cov80 file, cov80 and combo are compared with one lambdarank model; the one with the higher temporal-check
cov80 score is used for the full ensemble.

Usage: python -m src.hybrid_v5   ->  experiments.csv rows, docs/hybrid_v5_results.md,
                                     submissions/hybrid_v4_recent.csv, submissions/hybrid_v4_cov80.csv
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import dataclasses  # noqa: E402
import datetime as dt  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import hybrid as H  # noqa: E402
from src.data import PROCESSED, ROOT, SEED, connect  # noqa: E402
from src.evaluation import (FINAL_HIST_WEEKS, TARGET_WEEKS, TEST_WEEKS, cov_ground_truth, evaluate, fill,  # noqa: E402
                            log_results, test_users, validation_data)
from src.hybrid_v4 import FEATS, WindowV4, rank_avg, score, train  # noqa: E402
from src.method_utils import load_best  # noqa: E402
from src.repeat_v2 import POP_N  # noqa: E402
from src.submission import check_submission, write_submission  # noqa: E402

OUT_MD = ROOT / "docs" / "hybrid_v5_results.md"
FOLDS = {"A": ((11, 15), (16, 20)), "C": ((11, 17), (18, 20)), "B": ((11, 20), (21, 30)),
         "D": ((11, 22), (23, 30)), "E": ((11, 25), (26, 30)), "G": ((11, 27), (28, 30))}
MAIN, TEMPORAL = ["C", "B", "D", "E", "G"], ["A", "C"]
HALF_LIFE = 4
MEMBERS = [("lambdarank_log", 15, 20), ("binary", 63, 100)]
SEEDS = (SEED, SEED + 1, SEED + 2)
TARGETS = ("cov50", "cov80", "n_days")


def fold_weights(folds: list[str]) -> dict[str, float]:
    latest = max(FOLDS[f][1][0] for f in folds)
    return {f: 0.5 ** ((latest - FOLDS[f][1][0]) / HALF_LIFE) for f in folds}


def bucket(x: np.ndarray) -> np.ndarray:
    return np.where(x > 0, np.minimum(1 + np.floor(np.log2(np.maximum(x, 1))), 5), 0).astype(int)


def make_labels(con, frame: pd.DataFrame, w: WindowV4, usw) -> dict[str, pd.DataFrame]:
    """y_binary / y_log for every label mode, aligned with `frame`."""
    counts = con.sql(f"""
        SELECT user_id, tv_show_id, count(*) FILTER (WHERE cont_frac > 0.5) AS c50,
               count(*) FILTER (WHERE cont_frac > 0.8) AS c80
        FROM '{(PROCESSED / 'coverage.parquet').as_posix()}'
        WHERE week BETWEEN {w.tw[0]} AND {w.tw[1]} GROUP BY ALL""").df()
    c = frame[["user_id", "tv_show_id"]].merge(counts, on=["user_id", "tv_show_id"], how="left").fillna(0)
    keys = list(zip(c["user_id"].astype("uint64").tolist(), c["tv_show_id"].tolist()))
    top = {}
    for cut in (0.5, 0.8):
        gt = cov_ground_truth(w.tw, pd.Index(w.pool), usw, cut)
        members = {(u, s) for u, lst in gt.items() for s in lst}
        top[cut] = np.array([k in members for k in keys], dtype=int)
    b50, b80 = bucket(c["c50"].to_numpy()), bucket(c["c80"].to_numpy())
    idx = frame.index
    return {"cov50": pd.DataFrame({"y_binary": top[0.5], "y_log": b50}, index=idx),
            "cov80": pd.DataFrame({"y_binary": top[0.8], "y_log": b80}, index=idx),
            "combo": pd.DataFrame({"y_binary": top[0.8], "y_log": b50 + b80}, index=idx)}


class Folds:
    """Features (all users) and labels for every fold window, plus the test-user validation frame."""

    def __init__(self, con, data, best):
        self.con, self.data, self.best = con, data, best
        self.test = data.populations["test_users"]
        self.test_set = set(self.test)
        self.frames, self.labels, self.windows = {}, {}, {}
        for name, fold in FOLDS.items():
            t = time.time()
            w = WindowV4(con, data.usw, *fold, best)
            users = sorted(set(w.hist["user_id"].tolist()) | self.test_set)
            f = w.features(w.candidates(users))
            f[FEATS] = f[FEATS].astype("float32")
            self.windows[name], self.frames[name] = w, f
            self.labels[name] = make_labels(con, f, w, data.usw)
            print(f"fold {name} {fold}: {len(f)} rows in {time.time() - t:.1f} s", flush=True)
        b = self.frames["B"]
        self.f_test = b[b["user_id"].isin(self.test)].reset_index(drop=True)
        self.fallback = self.windows["B"].st.fallback
        gts = {**data.gts, "cov80": cov_ground_truth(TARGET_WEEKS, data.pool.index, data.usw, 0.8)}
        self.data_test = dataclasses.replace(data, populations={"test_users": self.test}, gts=gts)

    def training_set(self, folds: list[str], mode: str, validation: bool) -> pd.DataFrame:
        weights = fold_weights(folds)
        parts = []
        for name in folds:
            f = pd.concat([self.frames[name], self.labels[name][mode]], axis=1)
            if validation and FOLDS[name][1][1] >= TARGET_WEEKS[0]:  # target overlaps the validation window
                f = f[~f["user_id"].isin(self.test_set)]
            parts.append(f.assign(w=weights[name], qid=f["user_id"].astype(str) + "_" + name))
        return pd.concat(parts, ignore_index=True)

    def evaluate(self, s: np.ndarray, params: dict, kind: str, t0: float) -> dict:
        preds = fill(H.top5(self.f_test, s), self.test, self.fallback)
        res = evaluate(preds, self.data_test)
        log_results("hybrid_v5", params, res, time.time() - t0,
                    f"fallback=popularity_n_weeks={POP_N}; selection=cov50; {kind}; v5")
        return {d: v[1] for (_, d), v in res.items()}


def run(fd: Folds, idea: str, mode: str, members, seeds) -> dict:
    """Main and temporal-check results of a rank-averaged ensemble; keeps the trees of the main models."""
    out = {}
    for kind, folds in (("main", MAIN), ("temporal", TEMPORAL)):
        t0 = time.time()
        df = fd.training_set(folds, mode, validation=True)
        models = [(m, s, train(df, m[0], m[1], m[2], seed=s)) for m in members for s in seeds]
        sc = [score(model, fd.f_test) for _, _, model in models]
        params = {"idea": idea, "label": mode, "members": [list(m) for m in members], "seeds": list(seeds),
                  "folds": folds, "fold_half_life": HALF_LIFE,
                  "n_trees": [int(model.best_iteration_ or model.n_estimators) for _, _, model in models]}
        out[kind] = {"params": params, "trees": [(m, s, n) for (m, s, _), n in zip(models, params["n_trees"])],
                     **fd.evaluate(rank_avg(fd.f_test, sc) if len(sc) > 1 else sc[0], params, kind, t0)}
        print(f"{idea} {mode} {kind}: " + ", ".join(f"{t} {out[kind][t]:.4f}" for t in TARGETS), flush=True)
    return out


def write_final(fd: Folds, result: dict, mode: str, name: str, final_frame: pd.DataFrame, fin: WindowV4) -> str:
    users = test_users()
    df = fd.training_set(MAIN, mode, validation=False)
    sc = [score(train(df, m[0], m[1], m[2], seed=s, n_estimators=n), final_frame) for m, s, n in result["main"]["trees"]]
    preds = fill(H.top5(final_frame, rank_avg(final_frame, sc)), users, fin.st.fallback)
    path = ROOT / "submissions" / f"{name}.csv"
    write_submission(preds, users, path)
    problems = check_submission(path, set(int(x) for x in fin.pool))
    log = ROOT / "submissions" / "LOG.md"
    kept = [ln for ln in log.read_text(encoding="utf-8").splitlines() if not ln.startswith(f"| {path.name} |")]
    kept.append(f"| {path.name} | hybrid v5 ({result['main']['params']['idea']}, {mode} labels): hybrid_v3_ens ensemble "
                f"(lambdarank + binary, 3 seeds each) trained on folds {', '.join(MAIN)} (11-17->18-20 ... 11-27->28-30) "
                f"with recency weights (half-life {HALF_LIFE} weeks) and all users; features weeks 11-30, pool = labelled "
                f"shows airing weeks 31-42 | {dt.date.today().isoformat()} |  |  |  |")
    log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return f"{path.name}: format {'OK' if not problems else problems}"


def main() -> None:
    t_all = time.time()
    con = connect()
    best = load_best()
    data = validation_data()
    fd = Folds(con, data, best)

    recent = run(fd, "recent", "cov50", MEMBERS, SEEDS)
    probe = {mode: run(fd, "label probe", mode, MEMBERS[:1], (SEED,)) for mode in ("cov80", "combo")}
    label = max(probe, key=lambda m: probe[m]["temporal"]["cov80"])
    cov80 = run(fd, "cov80", label, MEMBERS, SEEDS)

    fin = WindowV4(con, data.usw, FINAL_HIST_WEEKS, TEST_WEEKS, best)
    final_frame = fin.features(fin.candidates(test_users()))
    final_frame[FEATS] = final_frame[FEATS].astype("float32")
    notes = [write_final(fd, recent, "cov50", "hybrid_v4_recent", final_frame, fin),
             write_final(fd, cov80, label, "hybrid_v4_cov80", final_frame, fin)]
    print(notes, flush=True)

    rows = [("hybrid_v4_recent", "cov50", recent)] + [(f"label probe (1 lambdarank)", m, r) for m, r in probe.items()] \
        + [("hybrid_v4_cov80", label, cov80)]
    lines = ["# Hybrid v5: recency-weighted folds and cov80 labels", "",
             f"Produced by `python -m src.hybrid_v5` on {dt.datetime.now():%Y-%m-%d %H:%M}. Validation: 1,260 test users, "
             "features weeks 11-20, targets in weeks 21-30. main = folds C, B, D, E, G (test users removed from folds "
             "whose target overlaps weeks 21-30); temporal = folds A, C only. Fold weights (half-life 4 weeks on the "
             f"first target week): main {fold_weights(MAIN)}, temporal {fold_weights(TEMPORAL)}.", "",
             "Reference: hybrid_v3_ens (one fold per run, cov50 labels) main cov50 0.4272, temporal cov50 0.4228; "
             "leaderboard 0.457 public / 0.442 private.", "",
             "| model | label | run | cov50 | cov80 | n_days |", "|---|---|---|---|---|---|"]
    for name, mode, r in rows:
        for kind in ("main", "temporal"):
            lines.append(f"| {name} | {mode} | {kind} | " + " | ".join(f"{r[kind][t]:.4f}" for t in TARGETS) + " |")
    lines += ["", f"Label used for hybrid_v4_cov80: {label} (higher temporal-check cov80 score of the probe).", "",
              "Submission files: " + "; ".join(notes) + ".", "", f"Total runtime: {time.time() - t_all:.1f} s."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}; total {time.time() - t_all:.1f} s", flush=True)


if __name__ == "__main__":
    main()
