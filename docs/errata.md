# Errata

## 1. Day counts shifted by the DuckDB session time zone (found and fixed 2026-10-22)

**What was wrong.** `src/build_interactions.py` converted the epoch seconds of each overlap start back to a
timestamp with `to_timestamp(x)::TIMESTAMP`. `to_timestamp` returns a TIMESTAMPTZ, and the cast to TIMESTAMP
uses the DuckDB session time zone, which defaulted to the Windows setting `Europe/Moscow` (UTC+3). All raw
timestamps are naive local wall-clock values, so `first_overlap_start` in `pairs_labelled.parquet` was 3 hours
late (its maximum was 2020-07-27 02:58 although the last view ends 2020-07-26 23:59:58). Found while building
the coverage table, where the same expression produced week-31 rows.

**What it affected.** Only quantities derived from the *date* of `first_overlap_start`: every distinct-day count
(`n_days` in `user_show_week.parquet` and in `repeat_v2.Stats`, `days_300s` / `days_50pct` in the target
study). Effectively a "day" started at 21:00 local time instead of midnight. Overlap seconds, airing counts,
week assignment, the join itself and the brute-force join check were not affected.

**Size.** 2.1% of the 2,159,681 (user, show, week) rows changed their `n_days` value (total day count 2,668,710
before vs 2,666,808 after). For the 1,260 test users, 1,042 keep the same `n_days` top-5 set in weeks 21-30 and
the item overlap of the old and new top-5 lists is 96.4%. All `n_days`-based numbers before the fix are
therefore slightly off; the `n_airings` and `watch_sec` targets are unchanged.

**Fix.** `make_timestamp(x * 1000000)` (naive, no time-zone conversion) in `build_interactions.py` and
`coverage.py`, and `src.data.connect()` now pins `SET TimeZone = 'UTC'`. Rows in `experiments.csv` logged after
the fix carry `data=tzfix` in `notes`; rows without that tag were computed on the shifted day counts.
Kaggle scores of submitted files are unaffected as returned values, but the models behind them used the shifted
day counts.

**Side note.** After the rebuild, `src.verify_join` sampled 280 users instead of 285, because `segment_id` is
assigned by `row_number() OVER ()` without an ORDER BY, so the seed-42 reservoir sample of segment rows is not
stable across rebuilds. The check again found 0 mismatched pairs.
