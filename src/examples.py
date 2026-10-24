"""Recommendation examples for two test users (validation split: history weeks 11-20, target weeks 21-30).

Users are chosen by a fixed rule, among test users with a non-empty cov50 target:
  heavy viewer  the user closest to the 90th percentile of history viewing time (a typical heavy viewer rather than
                the most extreme one)
  light viewer  among users with 1-20 distinct labelled shows touched in weeks 11-20 (any overlap; the median test
                user touches about 200 because zapping counts), the one with the most
                cov50 target shows (so there is something to compare against); ties by viewing time, then user id
For each method the validation top-5 (data/processed/val_preds.parquet, written by src.report_tables) is listed with
id, title and category; "familiar" = the user watched the show in weeks 11-20 (any overlap), "hit" = the show is in
the user's cov50 top-5 for weeks 21-30, "fallback" = the slot was filled by the shared popularity fallback.

Usage: python -m src.examples   ->  docs/examples.md
"""
import duckdb
import numpy as np
import pandas as pd

from src.data import PROCESSED, ROOT
from src.evaluation import HIST_WEEKS, TARGET_WEEKS, cov_ground_truth, load_usw, pool_airtime, test_users, window

OUT = ROOT / "docs" / "examples.md"
METHODS = ["popularity", "ALS", "CBF", "repeat_cov", "final (hybrid_v4_cov80)"]


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


def main() -> None:
    con = duckdb.connect()
    con.execute("SET TimeZone = 'UTC'")
    usw = load_usw()
    users = test_users()
    pool = pool_airtime(TARGET_WEEKS).index
    gt50 = cov_ground_truth(TARGET_WEEKS, pool, usw, 0.5)
    gt80 = cov_ground_truth(TARGET_WEEKS, pool, usw, 0.8)
    counts = con.sql(f"""
        SELECT user_id, tv_show_id, count(*) FILTER (WHERE cont_frac > 0.5) AS c50,
               count(*) FILTER (WHERE cont_frac > 0.8) AS c80
        FROM '{pq('coverage')}' WHERE week BETWEEN {TARGET_WEEKS[0]} AND {TARGET_WEEKS[1]} GROUP BY ALL""").df()
    counts = counts.set_index(["user_id", "tv_show_id"])
    sec = con.sql(f"""
        SELECT user_id, sum(epoch(stop_time) - epoch(start_time)) / 3600 AS hours FROM '{pq('view_segments')}'
        WHERE week BETWEEN {HIST_WEEKS[0]} AND {HIST_WEEKS[1]} GROUP BY 1""").df().set_index("user_id")["hours"]
    hist = window(usw, HIST_WEEKS)
    hist_shows = hist.groupby("user_id")["tv_show_id"].agg(set).to_dict()
    meta = con.sql(f"""
        SELECT tv_show_id, mode(tv_show_title) AS title, mode(tv_show_category) AS category FROM '{pq('schedule')}'
        WHERE tv_show_id <> 0 AND week <= 30 GROUP BY 1""").df().set_index("tv_show_id")

    cand = pd.DataFrame({"user_id": users})
    cand["hours"] = cand["user_id"].map(sec).fillna(0)
    cand["n_hist_shows"] = cand["user_id"].map(lambda u: len(hist_shows.get(u, ())))
    cand["n_gt"] = cand["user_id"].map(lambda u: len(gt50.get(u, [])))
    cand = cand[cand["n_gt"] > 0]
    p90 = np.quantile(cand["hours"], 0.9)
    heavy = int(cand["user_id"].iloc[(cand["hours"] - p90).abs().argsort().iloc[0]])  # column, not row: keeps uint64
    thin = cand[cand["n_hist_shows"].between(1, 20)].sort_values(["n_gt", "hours", "user_id"],
                                                               ascending=[False, True, True])
    light = int(thin["user_id"].iloc[0])

    preds = pd.read_parquet(PROCESSED / "val_preds.parquet")
    preds = preds[preds["method"].isin(METHODS)]

    def label(s: int) -> str:
        if s in meta.index:
            return f"{meta.at[s, 'title']} | {meta.at[s, 'category']}"
        return "(no metadata) | -"

    lines = ["# Recommendation examples", "",
             "Produced by `python -m src.examples` from the validation predictions of `python -m src.report_tables` "
             "(history weeks 11-20, target weeks 21-30). Users chosen by the fixed rule in the module docstring: a heavy "
             "viewer (closest to the 90th percentile of history viewing time among test users with a non-empty cov50 "
             "target) and a light viewer with a thin history (1-20 distinct labelled shows touched in weeks 11-20, against a median of about 200; the one "
             "with the most cov50 target shows). Titles and categories are the most frequent values in the schedule.", "",
             "Columns: **familiar** = watched by this user in weeks 11-20 (any overlap); **hit** = in the user's cov50 "
             "top-5 for weeks 21-30; **fallback** = slot filled by the shared popularity fallback.", ""]
    for name, u in (("Heavy viewer", heavy), ("Light viewer (thin history)", light)):
        row = cand[cand["user_id"] == u].iloc[0]  # numeric fields only below
        own_hist = hist_shows.get(u, set())
        g50, g80 = gt50.get(u, []), gt80.get(u, [])
        lines += [f"## {name}: user {u}", "",
                  f"History weeks 11-20: {row['hours']:.1f} viewing hours, {int(row['n_hist_shows'])} distinct labelled "
                  f"shows watched. Target weeks 21-30: {len(g50)} shows in the cov50 top-5, {len(g80)} in the cov80 top-5.", "",
                  "### What the user actually watched (weeks 21-30)", "",
                  "| target | rank | id | title | category | > 50% watches | > 80% watches | familiar |", "|---|---|---|---|---|---|---|---|"]
        for tname, g in (("cov50", g50), ("cov80", g80)):
            for r, s in enumerate(g, 1):
                c50, c80 = counts.loc[(u, s)] if (u, s) in counts.index else (0, 0)
                t, cat = label(s).split(" | ")
                lines.append(f"| {tname} | {r} | {s} | {t} | {cat} | {int(c50)} | {int(c80)} | "
                             f"{'yes' if s in own_hist else 'no'} |")
        lines += ["", "### Top-5 per method", ""]
        summary = []
        for m in METHODS:
            pm = preds[(preds["method"] == m) & (preds["user_id"] == u)].sort_values("rank")
            lines += [f"**{m}**", "", "| rank | id | title | category | familiar | hit | fallback |", "|---|---|---|---|---|---|---|"]
            for r in pm.itertuples():
                t, cat = label(int(r.tv_show_id)).split(" | ")
                lines.append(f"| {r.rank} | {r.tv_show_id} | {t} | {cat} | {'yes' if r.tv_show_id in own_hist else 'no'} | "
                             f"{'yes' if r.tv_show_id in g50 else ''} | {'–' if m == 'popularity' else ('' if r.own else 'yes')} |")
            fam = sum(int(x) in own_hist for x in pm["tv_show_id"])
            hits = sum(int(x) in g50 for x in pm["tv_show_id"])
            fb = "it is the fallback list" if m == "popularity" else f"{int((~pm['own']).sum())} fallback slots"
            summary.append(f"{m}: {fam} familiar / {5 - fam} new, {hits} hits, {fb}")
            lines.append("")
        lines += ["Summary: " + "; ".join(summary) + ".", ""]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} (heavy {heavy}, light {light})")


if __name__ == "__main__":
    main()
