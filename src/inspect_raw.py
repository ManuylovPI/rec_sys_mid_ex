"""Raw-data inspection: counts, columns, time formats, week boundaries, channel ids, file hand-offs.

Usage: python -m src.inspect_raw   ->  docs/data_inspection.md
"""
import time

from src.data import ROOT, SCHEDULE_CSVS, SEED, connect, register_raw
from src.report_utils import MdReport

OUT = ROOT / "docs" / "data_inspection.md"
SCHED = {k: "raw_sched_" + k.replace("-", "_") for k in SCHEDULE_CSVS}


def main() -> None:
    t0 = time.time()
    con = connect()
    register_raw(con)
    r = MdReport("Raw data inspection")
    r.text("All numbers below are produced by `python -m src.inspect_raw` on the unmodified files in `data/raw/`.")

    # ---------------- files and rows
    parts = [f"SELECT 'dataset11-30.csv' AS file, count(*) AS n_rows FROM raw_views"]
    parts += [f"SELECT 'export_arh_{k}-final.csv', count(*) FROM {v}" for k, v in SCHED.items()]
    parts += ["SELECT 'submission.csv', count(*) FROM raw_submission"]
    r.query(con, "Row counts", " UNION ALL ".join(parts))
    r.query(con, "View log: columns", "DESCRIBE raw_views")
    r.query(con, "Schedule: columns (all three files share them)", f"DESCRIBE {SCHED['11-20']}")
    r.query(con, "View log: first rows (times are stored as 'YYYY-MM-DD HH:MM:SS' strings)",
            "SELECT * FROM raw_views LIMIT 5")
    r.query(con, "Schedule: first rows (times are stored as 'DD.MM.YYYY HH:MM:SS' strings, parsed here)",
            f"SELECT channel_id, channel_title, start_time, duration, tv_show_title, tv_show_id, tv_show_category "
            f"FROM {SCHED['11-20']} LIMIT 5")

    # ---------------- view log
    r.query(con, "View log: summary", """
        SELECT count(*) AS n, count(DISTINCT user_id) AS users, count(DISTINCT vsetv_id) AS channels,
               min(start_time) AS min_start, max(start_time) AS max_start, max(stop_time) AS max_stop,
               min(duraton) AS min_dur, median(duraton) AS median_dur, quantile_cont(duraton, 0.9) AS p90_dur,
               max(duraton) AS max_dur,
               sum((duraton <> epoch(stop_time) - epoch(start_time))::INT) AS dur_ne_stop_minus_start,
               sum((stop_time < start_time)::INT) AS negative_intervals
        FROM raw_views""")
    r.query(con, "View log: rows and users per ISO week (week = ISO week of start_time, Monday 00:00 start)", """
        SELECT isoyear(start_time) AS iso_year, week(start_time) AS week, min(start_time)::DATE AS first_day,
               max(start_time)::DATE AS last_day, count(*) AS n_views, count(DISTINCT user_id) AS users,
               round(count(*) / count(DISTINCT user_id), 1) AS views_per_user
        FROM raw_views GROUP BY ALL ORDER BY 1, 2""")
    r.query(con, "View log: share of views by start hour (%)", """
        SELECT hour(start_time) AS hour, round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct
        FROM raw_views GROUP BY 1 ORDER BY 1""")
    r.query(con, "View log: rows where the same user starts a view before their previous view ended", """
        SELECT count(*) AS n_overlapping FROM (
            SELECT start_time, lag(stop_time) OVER (PARTITION BY user_id ORDER BY start_time) AS prev_stop
            FROM raw_views) WHERE start_time < prev_stop""",
            note="Across all channels. The interaction build merges overlaps per (user, channel).")

    # ---------------- schedules
    for k, v in SCHED.items():
        r.query(con, f"Schedule {k}: summary", f"""
            SELECT count(*) AS n, sum((tv_show_id <> 0)::INT) AS labelled,
                   round(100 * avg((tv_show_id <> 0)::INT), 2) AS labelled_pct,
                   count(DISTINCT tv_show_id) FILTER (WHERE tv_show_id <> 0) AS programmes_excl_0,
                   count(DISTINCT tv_show_id) AS programmes_incl_0,
                   count(DISTINCT channel_id) AS channels, count(DISTINCT tv_show_category) AS categories,
                   min(start_time) AS min_start, max(start_time) AS max_start,
                   min(duration) AS min_duration, median(duration) AS median_duration, max(duration) AS max_duration
            FROM {v}""")
        r.query(con, f"Schedule {k}: rows per ISO week of start_time", f"""
            SELECT week(start_time) AS week, min(start_time)::DATE AS first_day, max(start_time)::DATE AS last_day,
                   count(*) AS n FROM {v} GROUP BY 1 ORDER BY 1""")
    r.query(con, "Schedule: duration units (duration vs gap to the next airing on the same channel, within file)",
            " UNION ALL ".join(f"""
            SELECT '{k}' AS file, count(*) AS n_pairs, round(avg((duration = gap)::INT), 4) AS share_equal_seconds,
                   round(avg((duration * 60 = gap)::INT), 4) AS share_equal_if_minutes,
                   round(avg((gap > duration)::INT), 4) AS share_gap_after, round(avg((gap < duration)::INT), 4) AS share_overlap
            FROM (SELECT duration, epoch(lead(start_time) OVER (PARTITION BY channel_id ORDER BY start_time))
                               - epoch(start_time) AS gap FROM {v}) WHERE gap IS NOT NULL""" for k, v in SCHED.items()))
    r.query(con, "Schedule: categories (11-20)",
            f"SELECT tv_show_category, count(*) AS n FROM {SCHED['11-20']} GROUP BY 1 ORDER BY 2 DESC")
    r.query(con, "Schedule: zero-length rows and duplicate (channel_id, start_time) keys", " UNION ALL ".join(f"""
            SELECT '{k}' AS file, sum((duration = 0)::INT) AS zero_duration,
                   count(*) - count(DISTINCT (channel_id, start_time)) AS duplicate_keys FROM {v}"""
                                                                                            for k, v in SCHED.items()))

    # ---------------- timezone / DST evidence
    r.query(con, "DST evidence: view starts per hour on 2020-03-29 00:00-06:00 (Kyiv clocks jumped 03:00 -> 04:00)", """
        SELECT hour(start_time) AS hour, count(*) AS n FROM raw_views
        WHERE start_time >= '2020-03-29 00:00' AND start_time < '2020-03-29 06:00' GROUP BY 1 ORDER BY 1""")
    r.query(con, "DST evidence: channel 3 grid on the same night (01:25 + 6000 s = 03:05, next airing 04:05)", f"""
        SELECT start_time, duration, tv_show_title FROM {SCHED['11-20']}
        WHERE channel_id = 3 AND start_time BETWEEN '2020-03-28 23:00' AND '2020-03-29 07:00' ORDER BY 1""")

    # ---------------- file hand-offs
    con.execute("""CREATE TEMP TABLE s AS SELECT row_number() OVER () AS rid, channel_id, start_time,
                   start_time + to_seconds(duration) AS end_time, source_file FROM raw_sched""")
    r.query(con, "File hand-off: rows starting after the file's last ISO week (overhang)", """
        SELECT source_file, count(*) AS n_overhang, max(start_time) AS last_start,
               sum((hour(start_time) >= 6)::INT) AS starting_at_or_after_06
        FROM s WHERE (source_file = '11-20' AND start_time >= '2020-05-18')
                  OR (source_file = '21-30' AND start_time >= '2020-07-27')
                  OR (source_file = '31-42' AND start_time >= '2020-10-19')
        GROUP BY 1 ORDER BY 1""")
    r.query(con, "File hand-off: overlaps between consecutive airings on a channel after gluing all files", """
        SELECT source_file, next_file, count(*) AS n_overlaps FROM (
            SELECT source_file, end_time, lead(start_time) OVER w AS next_start, lead(source_file) OVER w AS next_file
            FROM s WINDOW w AS (PARTITION BY channel_id ORDER BY start_time, rid))
        WHERE next_start < end_time GROUP BY ALL ORDER BY ALL""",
            note="Few overlaps and only one across files: the files hand off cleanly and can simply be unioned.")
    r.query(con, "Week-10 rows (2020-03-08) that run into week 11", """
        SELECT count(*) AS n_week10, sum((end_time > '2020-03-09')::INT) AS end_in_week11, max(end_time) AS max_end
        FROM s WHERE start_time < '2020-03-09'""")

    # ---------------- channel ids
    r.query(con, "Channels: view-log vsetv_id vs schedule channel_id", """
        WITH a AS (SELECT DISTINCT vsetv_id AS c FROM raw_views), b AS (SELECT DISTINCT channel_id AS c FROM raw_sched)
        SELECT (SELECT count(*) FROM a) AS view_channels, (SELECT count(*) FROM b) AS schedule_channels,
               (SELECT count(*) FROM a SEMI JOIN b USING (c)) AS in_both""")
    r.query(con, "Channels: top-10 viewed vsetv_id with the schedule's channel_title for that id", """
        WITH t AS (SELECT vsetv_id, count(*) AS n FROM raw_views GROUP BY 1 ORDER BY 2 DESC LIMIT 10),
             c AS (SELECT DISTINCT channel_id, channel_title FROM raw_sched_11_20)
        SELECT t.vsetv_id, t.n AS n_views, string_agg(DISTINCT c.channel_title, ' / ') AS schedule_title
        FROM t LEFT JOIN c ON c.channel_id = t.vsetv_id GROUP BY ALL ORDER BY n_views DESC""")
    r.query(con, "Channels: viewed channels absent from every schedule (views can never match)", """
        SELECT vsetv_id, count(*) AS n_views FROM raw_views
        ANTI JOIN (SELECT DISTINCT channel_id FROM raw_sched) s ON s.channel_id = raw_views.vsetv_id
        GROUP BY 1 ORDER BY 2 DESC""")
    r.query(con, f"Coverage: random sample of 100,000 views from weeks 21-30 (seed {SEED})", f"""
        WITH vv AS (SELECT * FROM (SELECT * FROM raw_views WHERE start_time >= '2020-05-18')
                    USING SAMPLE reservoir(100000 ROWS) REPEATABLE ({SEED}))
        SELECT count(*) AS n,
               round(100 * avg((EXISTS (SELECT 1 FROM raw_sched_21_30 x WHERE x.channel_id = vv.vsetv_id
                   AND x.start_time < vv.stop_time AND x.start_time + to_seconds(x.duration) > vv.start_time))::INT), 2)
                   AS pct_overlap_any_airing,
               round(100 * avg((EXISTS (SELECT 1 FROM raw_sched_21_30 x WHERE x.channel_id = vv.vsetv_id AND x.tv_show_id <> 0
                   AND x.start_time < vv.stop_time AND x.start_time + to_seconds(x.duration) > vv.start_time))::INT), 2)
                   AS pct_overlap_labelled_airing
        FROM vv""")
    r.query(con, "Labelled programmes airing in weeks 31-42 that also air in a training schedule", """
        WITH a AS (SELECT DISTINCT tv_show_id t FROM raw_sched_31_42 WHERE tv_show_id <> 0 AND start_time < '2020-10-19'),
             b AS (SELECT DISTINCT tv_show_id t FROM raw_sched WHERE tv_show_id <> 0 AND source_file <> '31-42')
        SELECT (SELECT count(*) FROM a) AS test_pool_weeks_31_42, (SELECT count(*) FROM a SEMI JOIN b USING (t)) AS also_in_training""")

    # ---------------- submission template
    r.query(con, "Submission template", """
        SELECT count(*) AS n_rows, count(DISTINCT user_id) AS users,
               (SELECT count(*) FROM raw_submission SEMI JOIN (SELECT DISTINCT user_id FROM raw_views) u USING (user_id)) AS in_view_log,
               (SELECT count(*) FROM raw_submission SEMI JOIN (SELECT DISTINCT user_id FROM raw_views WHERE start_time < '2020-05-18') u USING (user_id)) AS with_views_wk11_20,
               (SELECT count(*) FROM raw_submission SEMI JOIN (SELECT DISTINCT user_id FROM raw_views WHERE start_time >= '2020-05-18') u USING (user_id)) AS with_views_wk21_30,
               string_agg(DISTINCT tv_show_id, ', ') AS distinct_template_values
        FROM raw_submission""")

    r.text(f"Runtime: {time.time() - t0:.1f} s.")
    r.save(OUT)


if __name__ == "__main__":
    main()
