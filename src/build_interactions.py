"""Join the view log to the schedule and cache interaction tables as parquet.

Steps
1. schedule: union of the three schedule files, end = start + duration (seconds), week = ISO week of
   start_time. Rows of week 43 (test-file overhang past week 42) and zero-duration rows are dropped.
   Week-10 rows (2020-03-08) are kept because some run into week 11; they are never candidates.
2. view segments: overlapping/touching views of the same user on the same channel are merged into one
   interval (so parallel devices do not double count), then cut at ISO-week boundaries (Monday 00:00),
   so each segment belongs to exactly one week.
3. join: segment.channel = airing.channel and the intervals overlap; overlap seconds per (segment, airing).
   Implemented as an equi-join on (channel, hour bucket); each pair is kept only in the bucket where its
   overlap starts, so it is counted once.
4. outputs (data/processed/):
   schedule.parquet            one row per airing (airing_id), all schedule attributes
   view_segments.parquet       merged, week-split view intervals
   pairs_labelled.parquet      (user, airing, week) with overlap seconds, tv_show_id != 0
   pairs_unlabelled.parquet    same for tv_show_id = 0 (context only, never items)
   user_show_week.parquet      (user, tv_show_id, week) aggregates, labelled only
No watch threshold is applied here.

Usage: python -m src.build_interactions   ->  data/processed/*.parquet, docs/join_summary.md
"""
import time

from src.data import FIRST_WEEK, LAST_TEST_WEEK, PROCESSED, ROOT, connect, register_raw
from src.report_utils import MdReport

OUT_MD = ROOT / "docs" / "join_summary.md"
BUCKET_SEC = 3600


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


def build(con) -> dict:
    timings = {}

    t = time.time()
    con.execute(f"""
        CREATE TABLE schedule AS
        SELECT row_number() OVER (ORDER BY channel_id, start_time, source_file) AS airing_id,
               channel_id, channel_title, start_time,
               start_time + to_seconds(duration) AS end_time, duration,
               week(start_time) AS week, tv_show_id, tv_show_title, tv_show_category,
               tv_show_genre_1, tv_show_genre_2, tv_show_genre_3, year_of_production, director, actors,
               source_file
        FROM raw_sched
        WHERE week(start_time) <= {LAST_TEST_WEEK} AND duration > 0
    """)
    con.execute(f"COPY schedule TO '{pq('schedule')}' (FORMAT parquet)")
    timings["schedule"] = time.time() - t

    t = time.time()
    # Gaps-and-islands merge per (user, channel); touching intervals (start == previous max stop) merge too.
    con.execute("""
        CREATE TABLE view_merged AS
        WITH o AS (
            SELECT user_id, vsetv_id AS channel_id, start_time AS s, stop_time AS e,
                   max(stop_time) OVER (PARTITION BY user_id, vsetv_id ORDER BY start_time, stop_time
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max
            FROM raw_views),
        g AS (
            SELECT *, sum(CASE WHEN prev_max IS NULL OR s > prev_max THEN 1 ELSE 0 END)
                      OVER (PARTITION BY user_id, channel_id ORDER BY s, e ROWS UNBOUNDED PRECEDING) AS grp
            FROM o)
        SELECT user_id, channel_id, min(s) AS start_time, max(e) AS stop_time, count(*) AS n_raw_views
        FROM g GROUP BY user_id, channel_id, grp
    """)
    con.execute("""
        CREATE TABLE view_segments AS
        WITH w AS (
            SELECT *, unnest(generate_series(date_trunc('week', start_time),
                                             date_trunc('week', stop_time - INTERVAL 1 SECOND),
                                             INTERVAL 7 DAY)) AS wk_start
            FROM view_merged)
        SELECT row_number() OVER () AS segment_id, user_id, channel_id,
               greatest(start_time, wk_start) AS start_time,
               least(stop_time, wk_start + INTERVAL 7 DAY) AS stop_time,
               week(wk_start) AS week, n_raw_views
        FROM w
        WHERE least(stop_time, wk_start + INTERVAL 7 DAY) > greatest(start_time, wk_start)
    """)
    con.execute(f"COPY view_segments TO '{pq('view_segments')}' (FORMAT parquet)")
    timings["merge_views"] = time.time() - t

    t = time.time()
    b = BUCKET_SEC
    con.execute(f"""
        CREATE TABLE seg_pairs AS
        WITH sb AS (
            SELECT airing_id, channel_id, tv_show_id, epoch(start_time)::BIGINT AS a0, epoch(end_time)::BIGINT AS a1,
                   unnest(range(epoch(start_time)::BIGINT // {b}, (epoch(end_time)::BIGINT - 1) // {b} + 1)) AS bucket
            FROM schedule),
        vb AS (
            SELECT segment_id, user_id, channel_id, week, epoch(start_time)::BIGINT AS v0, epoch(stop_time)::BIGINT AS v1,
                   unnest(range(epoch(start_time)::BIGINT // {b}, (epoch(stop_time)::BIGINT - 1) // {b} + 1)) AS bucket
            FROM view_segments)
        SELECT vb.segment_id, vb.user_id, vb.channel_id, vb.week, sb.airing_id, sb.tv_show_id,
               greatest(vb.v0, sb.a0) AS ov_start, least(vb.v1, sb.a1) - greatest(vb.v0, sb.a0) AS overlap_sec
        FROM vb JOIN sb ON vb.channel_id = sb.channel_id AND vb.bucket = sb.bucket
        WHERE sb.a0 < vb.v1 AND sb.a1 > vb.v0
          AND vb.bucket = greatest(vb.v0, sb.a0) // {b}
    """)
    timings["join"] = time.time() - t

    t = time.time()
    # (user, airing, week) pairs. Merged segments of one user on one channel are disjoint, so the
    # summed overlap can never exceed the airing's duration.
    pair_sql = """
        SELECT p.user_id, p.airing_id, p.week, s.channel_id, s.tv_show_id, s.start_time AS air_start,
               s.duration AS air_duration, sum(p.overlap_sec)::BIGINT AS overlap_sec,
               sum(p.overlap_sec) / max(s.duration) AS frac_watched, count(*) AS n_segments,
               to_timestamp(min(p.ov_start))::TIMESTAMP AS first_overlap_start
        FROM seg_pairs p JOIN schedule s USING (airing_id)
        WHERE {cond}
        GROUP BY ALL
    """
    con.execute("CREATE TABLE pairs_labelled AS " + pair_sql.format(cond="p.tv_show_id <> 0"))
    con.execute("CREATE TABLE pairs_unlabelled AS " + pair_sql.format(cond="p.tv_show_id = 0"))
    con.execute(f"COPY pairs_labelled TO '{pq('pairs_labelled')}' (FORMAT parquet)")
    con.execute(f"COPY pairs_unlabelled TO '{pq('pairs_unlabelled')}' (FORMAT parquet)")

    con.execute("""
        CREATE TABLE user_show_week AS
        SELECT user_id, tv_show_id, week,
               sum(overlap_sec)::BIGINT AS watch_sec,
               count(DISTINCT airing_id) AS n_airings,
               count(DISTINCT first_overlap_start::DATE) AS n_days,
               sum(air_duration)::BIGINT AS airtime_sec,
               sum(overlap_sec) / sum(air_duration) AS frac_total,
               max(frac_watched) AS frac_max
        FROM pairs_labelled GROUP BY ALL
    """)
    con.execute(f"COPY user_show_week TO '{pq('user_show_week')}' (FORMAT parquet)")
    timings["aggregate_and_write"] = time.time() - t
    return timings


def report(con, timings: dict, total: float) -> None:
    r = MdReport("View-schedule join summary")
    r.text("Produced by `python -m src.build_interactions`. No watch threshold is applied in the cached tables. "
           "`frac_watched` = overlap seconds / airing duration for one airing; in `user_show_week`, "
           "`frac_max` is the best single-airing fraction that week, `frac_total` = watch_sec / summed duration "
           "of the airings touched.")
    r.text("Timings (s): " + ", ".join(f"{k} {v:.1f}" for k, v in timings.items()) + f"; total {total:.1f}.")

    r.query(con, "Row counts", """
        SELECT 'raw views' AS step, (SELECT count(*) FROM raw_views) AS n_rows UNION ALL
        SELECT 'merged views (user, channel)', count(*) FROM view_merged UNION ALL
        SELECT 'view segments (after week split)', count(*) FROM view_segments UNION ALL
        SELECT 'schedule airings kept', count(*) FROM schedule UNION ALL
        SELECT 'segment-airing overlaps', count(*) FROM seg_pairs UNION ALL
        SELECT 'pairs_labelled (user, airing, week)', count(*) FROM pairs_labelled UNION ALL
        SELECT 'pairs_unlabelled (user, airing, week)', count(*) FROM pairs_unlabelled UNION ALL
        SELECT 'user_show_week', count(*) FROM user_show_week""")
    r.query(con, "Schedule airings kept by week range", f"""
        SELECT CASE WHEN week < {FIRST_WEEK} THEN '10 (join only)' WHEN week <= 20 THEN '11-20'
                    WHEN week <= 30 THEN '21-30' ELSE '31-42' END AS weeks,
               count(*) AS airings, sum((tv_show_id <> 0)::INT) AS labelled,
               count(DISTINCT tv_show_id) FILTER (WHERE tv_show_id <> 0) AS programmes
        FROM schedule GROUP BY 1 ORDER BY 1""")
    r.query(con, "Merge effect: viewing seconds before and after merging overlapping views", """
        SELECT (SELECT sum(epoch(stop_time) - epoch(start_time)) FROM raw_views)::BIGINT AS raw_sec,
               (SELECT sum(epoch(stop_time) - epoch(start_time)) FROM view_merged)::BIGINT AS merged_sec,
               (SELECT sum(epoch(stop_time) - epoch(start_time)) FROM view_segments)::BIGINT AS segments_sec,
               (SELECT count(*) FROM view_merged WHERE n_raw_views > 1) AS merged_intervals_from_2plus_views""")
    r.query(con, "Where viewing time goes (merged segments, seconds)", """
        WITH tot AS (SELECT sum(epoch(stop_time) - epoch(start_time)) AS t FROM view_segments)
        SELECT round(100 * (SELECT sum(overlap_sec) FROM pairs_labelled) / t, 2) AS pct_on_labelled_airings,
               round(100 * (SELECT sum(overlap_sec) FROM pairs_unlabelled) / t, 2) AS pct_on_unlabelled_airings,
               round(100 - 100 * ((SELECT sum(overlap_sec) FROM pairs_labelled)
                                  + (SELECT sum(overlap_sec) FROM pairs_unlabelled)) / t, 2) AS pct_unmatched
        FROM tot""")
    r.query(con, "Sanity: overlap never exceeds airing duration; weeks of interactions", """
        SELECT max(frac_watched) AS max_frac, min(overlap_sec) AS min_overlap_sec,
               min(week) AS min_week, max(week) AS max_week FROM pairs_labelled""")

    q = "0.1, 0.25, 0.5, 0.75, 0.9, 0.99"
    r.query(con, "Distribution: overlap seconds per (user, airing, week), labelled", f"""
        SELECT count(*) AS n, round(avg(overlap_sec), 1) AS mean,
               quantile_disc(overlap_sec, [{q}]) AS "quantiles p10/p25/p50/p75/p90/p99", max(overlap_sec) AS max
        FROM pairs_labelled""")
    r.query(con, "Distribution: fraction of the airing watched per (user, airing, week), labelled", f"""
        SELECT count(*) AS n, round(avg(frac_watched), 4) AS mean,
               list_transform(quantile_cont(frac_watched, [{q}]), lambda x: round(x, 4)) AS "quantiles p10/p25/p50/p75/p90/p99",
               round(avg((frac_watched >= 0.999)::INT), 4) AS share_full
        FROM pairs_labelled""")
    r.query(con, "Histogram: overlap seconds per (user, airing, week), labelled", """
        SELECT bin, count(*) AS n, round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct FROM (
            SELECT CASE WHEN overlap_sec < 10 THEN '01: <10 s' WHEN overlap_sec < 60 THEN '02: 10-59 s'
                        WHEN overlap_sec < 300 THEN '03: 1-5 min' WHEN overlap_sec < 900 THEN '04: 5-15 min'
                        WHEN overlap_sec < 1800 THEN '05: 15-30 min' WHEN overlap_sec < 3600 THEN '06: 30-60 min'
                        ELSE '07: >=60 min' END AS bin FROM pairs_labelled) GROUP BY 1 ORDER BY 1""")
    r.query(con, "Histogram: fraction of the airing watched per (user, airing, week), labelled", """
        SELECT bin, count(*) AS n, round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct FROM (
            SELECT CASE WHEN frac_watched < 0.05 THEN '01: <5%' WHEN frac_watched < 0.10 THEN '02: 5-10%'
                        WHEN frac_watched < 0.25 THEN '03: 10-25%' WHEN frac_watched < 0.50 THEN '04: 25-50%'
                        WHEN frac_watched < 0.75 THEN '05: 50-75%' WHEN frac_watched < 0.999 THEN '06: 75-<100%'
                        ELSE '07: 100%' END AS bin FROM pairs_labelled) GROUP BY 1 ORDER BY 1""")
    r.query(con, "Airing duration of labelled airings that were watched (seconds)", f"""
        SELECT quantile_disc(air_duration, [{q}]) AS "quantiles p10/p25/p50/p75/p90/p99", max(air_duration) AS max
        FROM pairs_labelled""")
    r.query(con, "Distribution: user_show_week watch_sec, frac_max, n_airings, n_days", f"""
        SELECT count(*) AS n,
               quantile_disc(watch_sec, [0.25, 0.5, 0.75, 0.9]) AS "watch_sec p25/p50/p75/p90",
               list_transform(quantile_cont(frac_max, [0.25, 0.5, 0.75, 0.9]), lambda x: round(x, 3)) AS "frac_max p25/p50/p75/p90",
               quantile_disc(n_airings, [0.5, 0.9, 0.99]) AS "n_airings p50/p90/p99",
               quantile_disc(n_days, [0.5, 0.9, 0.99]) AS "n_days p50/p90/p99"
        FROM user_show_week""")

    # (user, show) pairs per window, aggregated over the window's weeks
    con.execute("""
        CREATE TEMP TABLE us AS
        SELECT CASE WHEN week <= 20 THEN '11-20' ELSE '21-30' END AS win, user_id, tv_show_id,
               sum(watch_sec) AS watch_sec, max(frac_max) AS frac_max
        FROM user_show_week GROUP BY ALL
        UNION ALL
        SELECT '11-30', user_id, tv_show_id, sum(watch_sec), max(frac_max) FROM user_show_week GROUP BY ALL
    """)
    r.query(con, "(user, show) pairs surviving candidate thresholds, per window", """
        SELECT win, count(*) AS any_overlap,
               sum((watch_sec >= 60)::INT) AS "sec>=60", sum((watch_sec >= 300)::INT) AS "sec>=300",
               sum((frac_max >= 0.10)::INT) AS "frac>=10%", sum((frac_max >= 0.25)::INT) AS "frac>=25%",
               count(DISTINCT user_id) AS users_any, count(DISTINCT tv_show_id) AS shows_any
        FROM us GROUP BY 1 ORDER BY 1""",
            note="watch_sec = total seconds over all airings and weeks in the window; frac = best single-airing "
                 "fraction in the window (frac_max). Thresholds are illustrations only; none is applied.")
    r.query(con, "Test users (1,260 in submission.csv) with ZERO labelled (user, show) pairs at each threshold", """
        WITH u AS (SELECT DISTINCT user_id FROM raw_submission),
             w AS (SELECT * FROM (VALUES ('11-20'), ('21-30'), ('11-30')) t(win))
        SELECT w.win,
               sum((NOT EXISTS (SELECT 1 FROM us WHERE us.win = w.win AND us.user_id = u.user_id))::INT) AS any_overlap,
               sum((NOT EXISTS (SELECT 1 FROM us WHERE us.win = w.win AND us.user_id = u.user_id AND watch_sec >= 60))::INT) AS "sec>=60",
               sum((NOT EXISTS (SELECT 1 FROM us WHERE us.win = w.win AND us.user_id = u.user_id AND watch_sec >= 300))::INT) AS "sec>=300",
               sum((NOT EXISTS (SELECT 1 FROM us WHERE us.win = w.win AND us.user_id = u.user_id AND frac_max >= 0.10))::INT) AS "frac>=10%",
               sum((NOT EXISTS (SELECT 1 FROM us WHERE us.win = w.win AND us.user_id = u.user_id AND frac_max >= 0.25))::INT) AS "frac>=25%"
        FROM w CROSS JOIN u GROUP BY 1 ORDER BY 1""")
    r.save(OUT_MD)


def main() -> None:
    t0 = time.time()
    con = connect()
    register_raw(con)
    timings = build(con)
    total = time.time() - t0
    for k, v in timings.items():
        print(f"{k}: {v:.1f} s", flush=True)
    report(con, timings, total)


if __name__ == "__main__":
    main()
