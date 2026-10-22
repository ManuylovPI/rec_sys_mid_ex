"""Continuous-view coverage of labelled airings.

For every (user, labelled airing) the share of the airing covered by the single best continuous view on that
channel: the merged view intervals of src.build_interactions (overlapping/touching views of one user on one
channel merged) with the Monday 00:00 week cuts joined back together, so one interval = one continuous stretch
on one channel. Separate views are NOT summed (that is what pairs_labelled.frac_watched does).

Output data/processed/coverage.parquet:
  user_id, airing_id, tv_show_id, channel_id, air_duration, cont_frac (best single interval / duration),
  cont_start (start of the overlap of that best interval), week and day of cont_start.

Usage: python -m src.coverage   ->  data/processed/coverage.parquet, docs/coverage_summary.md
"""
import time

from src.data import PROCESSED, ROOT, connect
from src.report_utils import MdReport

OUT = PROCESSED / "coverage.parquet"
OUT_MD = ROOT / "docs" / "coverage_summary.md"
B = 3600


def pq(name: str) -> str:
    return (PROCESSED / f"{name}.parquet").as_posix()


def build(con) -> float:
    t = time.time()
    con.execute(f"""
        CREATE OR REPLACE TABLE cont AS
        WITH s AS (SELECT user_id, channel_id, start_time, stop_time FROM '{pq('view_segments')}'),
        o AS (SELECT *, max(stop_time) OVER (PARTITION BY user_id, channel_id ORDER BY start_time, stop_time
                                             ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max FROM s),
        g AS (SELECT *, sum(CASE WHEN prev_max IS NULL OR start_time > prev_max THEN 1 ELSE 0 END)
                        OVER (PARTITION BY user_id, channel_id ORDER BY start_time, stop_time ROWS UNBOUNDED PRECEDING) AS grp
              FROM o)
        SELECT row_number() OVER () AS cid, user_id, channel_id,
               epoch(min(start_time))::BIGINT AS v0, epoch(max(stop_time))::BIGINT AS v1
        FROM g GROUP BY user_id, channel_id, grp""")
    con.execute(f"""
        CREATE OR REPLACE TABLE cov AS
        WITH sb AS (
            SELECT airing_id, channel_id, tv_show_id, duration, epoch(start_time)::BIGINT AS a0, epoch(end_time)::BIGINT AS a1,
                   unnest(range(epoch(start_time)::BIGINT // {B}, (epoch(end_time)::BIGINT - 1) // {B} + 1)) AS bucket
            FROM '{pq('schedule')}' WHERE tv_show_id <> 0),
        vb AS (SELECT cid, user_id, channel_id, v0, v1, unnest(range(v0 // {B}, (v1 - 1) // {B} + 1)) AS bucket FROM cont),
        p AS (
            SELECT vb.user_id, sb.airing_id, sb.tv_show_id, sb.channel_id, sb.duration,
                   least(vb.v1, sb.a1) - greatest(vb.v0, sb.a0) AS ov, greatest(vb.v0, sb.a0) AS ov_start
            FROM vb JOIN sb ON vb.channel_id = sb.channel_id AND vb.bucket = sb.bucket
            WHERE sb.a0 < vb.v1 AND sb.a1 > vb.v0 AND vb.bucket = greatest(vb.v0, sb.a0) // {B})
        SELECT user_id, airing_id, any_value(tv_show_id) AS tv_show_id, any_value(channel_id) AS channel_id,
               any_value(duration) AS air_duration, max(ov) / any_value(duration) AS cont_frac,
               make_timestamp(arg_max(ov_start, ov) * 1000000) AS cont_start
        FROM p GROUP BY user_id, airing_id""")
    con.execute(f"""COPY (SELECT *, week(cont_start) AS week, cont_start::DATE AS day FROM cov)
                    TO '{OUT.as_posix()}' (FORMAT parquet)""")
    return time.time() - t


def main() -> None:
    con = connect()
    runtime = build(con)
    r = MdReport("Continuous-view coverage of labelled airings")
    r.text(f"Produced by `python -m src.coverage`. Build time {runtime:.1f} s.")
    r.query(con, "Counts", f"""
        SELECT (SELECT count(*) FROM cont) AS continuous_intervals, count(*) AS user_airing_pairs,
               max(cont_frac) AS max_cont_frac, min(week) AS min_week, max(week) AS max_week FROM '{OUT.as_posix()}'""")
    r.query(con, "Pairs reaching each coverage threshold (single continuous view vs summed views)", f"""
        WITH c AS (SELECT * FROM '{OUT.as_posix()}'),
             s AS (SELECT user_id, airing_id, sum(frac_watched) AS frac_sum FROM '{pq('pairs_labelled')}' GROUP BY ALL)
        SELECT t AS threshold, sum((c.cont_frac >= t)::INT) AS continuous, sum((s.frac_sum >= t)::INT) AS summed
        FROM c JOIN s USING (user_id, airing_id), (VALUES (0.3), (0.5), (0.7), (0.8), (0.9)) v(t)
        GROUP BY 1 ORDER BY 1""")
    r.save(OUT_MD)


if __name__ == "__main__":
    main()
