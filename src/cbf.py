"""Content-based filtering on programme metadata.

Item vector per tv_show_id, built only from the fields the spec lists: tv_show_category, tv_show_genre_1..3,
year_of_production (as decade), director, actors. Tokens are unioned over a show's distinct metadata rows.
director / actors are split on ',', at most MAX_ACTORS actors per row, and names in fewer than `min_df` shows
are dropped (rare-name cap). Vectors: binary one-hot or TF-IDF (smooth idf), people columns scaled by
`people_weight`, rows L2-normalised.

Metadata comes from schedule weeks <= last target week (11-30 on validation); no viewing data from the
target window is used.

User profile = weighted mean of the vectors of the shows the user watched in the history window (all shows,
not only the pool), weights = decayed distinct days (half-life 8) or log1p of that. Score = cosine(profile,
item) over the candidate pool; already-watched shows are not filtered. Exact score ties (shows with identical
vectors) are broken by the shared popularity score, then tv_show_id.

Usage: python -m src.cbf [--extend]   ->  experiments.csv rows, docs/cbf_results.md, docs/best_params.json
"""
import datetime as dt
import itertools
import re
import sys
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from src.data import PROCESSED, ROOT
from src.evaluation import window
from src.method_utils import RESULT_COLS, Context, load_best, results_table, save_best
from src.metrics import K
from src.repeat_v2 import POP_N

OUT_MD = ROOT / "docs" / "cbf_results.md"
HALF_LIFE = 8
MAX_ACTORS = 5
REPS = ["onehot", "tfidf"]
MIN_DFS = [2, 5]
PEOPLE_WEIGHTS = [0.5, 1.0]
PROFILE_WEIGHTS = ["linear", "log"]
# --extend: the first grid peaked at the largest people_weight
EXT_GRID = {"reps": ["onehot", "tfidf"], "min_dfs": [2], "people_weights": [2.0, 4.0], "profiles": ["linear"]}
META_MAX_WEEK = 30  # validation: metadata from the training schedules only
YEAR = re.compile(r"(1[89]\d\d|20\d\d)")


def split_names(s, limit=None) -> list[str]:
    if not isinstance(s, str):
        return []
    names = [n.strip().lower() for n in s.split(",") if n.strip()]
    return names[:limit] if limit else names


def show_tokens(con, max_week: int) -> pd.DataFrame:
    meta = con.sql(f"""
        SELECT DISTINCT tv_show_id, tv_show_category, tv_show_genre_1, tv_show_genre_2, tv_show_genre_3,
               year_of_production, director, actors
        FROM '{(PROCESSED / 'schedule.parquet').as_posix()}' WHERE tv_show_id <> 0 AND week <= {max_week}""").df()
    rows = {}
    for r in meta.itertuples(index=False):
        t = rows.setdefault(r.tv_show_id, {"base": set(), "people": set()})
        if isinstance(r.tv_show_category, str):
            t["base"].add("cat:" + r.tv_show_category.lower())
        for g in (r.tv_show_genre_1, r.tv_show_genre_2, r.tv_show_genre_3):
            if isinstance(g, str) and g.strip():
                t["base"].add("genre:" + g.strip().lower())
        m = YEAR.search(r.year_of_production) if isinstance(r.year_of_production, str) else None
        if m:
            t["base"].add(f"decade:{int(m.group(1)) // 10 * 10}")
        t["people"].update("dir:" + n for n in split_names(r.director))
        t["people"].update("act:" + n for n in split_names(r.actors, MAX_ACTORS))
    return pd.DataFrame([(k, sorted(v["base"]), sorted(v["people"])) for k, v in rows.items()],
                        columns=["tv_show_id", "base", "people"]).sort_values("tv_show_id").reset_index(drop=True)


def item_matrix(tokens: pd.DataFrame, rep: str, min_df: int, people_weight: float) -> sp.csr_matrix:
    people_df = pd.Series([p for ps in tokens["people"] for p in ps]).value_counts()
    keep = set(people_df[people_df >= min_df].index)
    docs = [b + [p for p in ps if p in keep] for b, ps in zip(tokens["base"], tokens["people"])]
    vec = TfidfVectorizer(analyzer=lambda d: d, binary=True, use_idf=(rep == "tfidf"), norm=None, lowercase=False)
    x = vec.fit_transform(docs).tocsc().astype(np.float64)
    names = vec.get_feature_names_out()
    scale = np.array([people_weight if n.startswith(("dir:", "act:")) else 1.0 for n in names])
    return normalize(x @ sp.diags(scale), norm="l2").tocsr()


class CbfData:
    def __init__(self, ctx: Context):
        st = ctx.st
        self.tokens = show_tokens(ctx.con, max_week=META_MAX_WEEK)
        self.items = self.tokens["tv_show_id"].to_numpy()
        u = st.user_week["none"]
        w = u["n_days"] * 0.5 ** ((st.hist_weeks[1] - u["week"]) / HALF_LIFE)
        df = u[["user_id", "tv_show_id"]].assign(w=w).groupby(["user_id", "tv_show_id"], as_index=False)["w"].sum()
        df = df[df["tv_show_id"].isin(self.items)]
        self.users = np.sort(df["user_id"].unique())
        self.user_pos = {int(x): i for i, x in enumerate(self.users)}
        ui = np.searchsorted(self.users, df["user_id"].to_numpy())
        ii = np.searchsorted(self.items, df["tv_show_id"].to_numpy())
        self.weights = sp.csr_matrix((df["w"].to_numpy(), (ui, ii)), shape=(len(self.users), len(self.items)))
        pool = st.pool.index.to_numpy()
        self.pool_cols = np.flatnonzero(np.isin(self.items, pool))
        h = window(ctx.data.usw, (st.hist_weeks[1] - POP_N + 1, st.hist_weeks[1]))
        pop = h.groupby("tv_show_id")["watch_sec"].sum()
        p = pop.reindex(self.items[self.pool_cols]).fillna(0).to_numpy()
        self.pop_tiebreak = p / (p.max() + 1) * 1e-7  # < rounding step below: only breaks exact ties


def fit_predict(cd: CbfData, users: list[int], rep: str, min_df: int, people_weight: float,
                profile: str) -> dict[int, list[int]]:
    x = item_matrix(cd.tokens, rep, min_df, people_weight)
    w = cd.weights.copy()
    if profile == "log":
        w.data = np.log1p(w.data)
    known = [u for u in users if u in cd.user_pos]
    wu = w[[cd.user_pos[u] for u in known]]
    prof = normalize(sp.diags(1 / np.asarray(wu.sum(axis=1)).ravel()) @ wu @ x, norm="l2")
    scores = (prof @ x[cd.pool_cols].T).toarray()
    scores = np.round(scores, 6) + cd.pop_tiebreak
    top = np.argpartition(-scores, K, axis=1)[:, :K]
    out = {}
    for row, u in enumerate(known):
        cols = top[row][np.argsort(-scores[row, top[row]], kind="stable")]
        out[u] = [int(v) for v in cd.items[cd.pool_cols[cols]]]
    return out


def predict(ctx: Context, params: dict) -> dict[int, list[int]]:
    return fit_predict(CbfData(ctx), ctx.users, **{k: params[k] for k in ("rep", "min_df", "people_weight", "profile")})


def main() -> None:
    extend = "--extend" in sys.argv
    grid = (EXT_GRID["reps"], EXT_GRID["min_dfs"], EXT_GRID["people_weights"], EXT_GRID["profiles"]) if extend \
        else (REPS, MIN_DFS, PEOPLE_WEIGHTS, PROFILE_WEIGHTS)
    t_all = time.time()
    ctx = Context()
    cd = CbfData(ctx)
    print(f"{len(cd.items)} shows with metadata, {len(cd.pool_cols)} of {len(ctx.st.pool)} pool shows", flush=True)
    for rep, md, pw, prof in itertools.product(*grid):
        t = time.time()
        p = {"rep": rep, "min_df": md, "people_weight": pw, "profile": prof, "max_actors": MAX_ACTORS,
             "profile_unit": f"n_days_hl{HALF_LIFE}"}
        ctx.run("cbf", p, fit_predict(cd, ctx.users, rep, md, pw, prof), t, "grid extension" if extend else "")
    best = ctx.best("cbf")
    out_md = OUT_MD.with_name("cbf_results_extension.md") if extend else OUT_MD
    prev = load_best().get("cbf_select") if extend else None
    if prev is None or best["select"] > prev:
        save_best("cbf", best["params"])
        save_best("cbf_select", best["select"])
    lines = ["# Content-based filtering: validation results", "",
             f"Produced by `python -m src.cbf{' --extend' if extend else ''}` on {dt.datetime.now():%Y-%m-%d %H:%M}. {len(cd.items)} shows with "
             f"metadata (schedule weeks <= 30); {len(cd.pool_cols)} of {len(ctx.st.pool)} pool shows have a vector. "
             "Already-watched shows are not filtered. Same harness and selection as repeat_v2.", "",
             *results_table(ctx.rows, RESULT_COLS), "",
             f"Selected: `{best['params']}` (select {best['select']:.4f}).", "",
             f"Total runtime: {time.time() - t_all:.1f} s."]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
