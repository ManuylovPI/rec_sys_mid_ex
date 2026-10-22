"""Check the bucketed join in build_interactions against a brute-force overlap join on a user sample.

Usage: python -m src.verify_join   ->  docs/join_verification.md
"""
import time

from src.data import PROCESSED, ROOT, SEED, connect
from src.report_utils import MdReport

OUT = ROOT / "docs" / "join_verification.md"


def main() -> None:
    t0 = time.time()
    con = connect()
    p = PROCESSED.as_posix()
    con.execute(f"""
        CREATE TABLE seg AS SELECT * FROM '{p}/view_segments.parquet'
        WHERE user_id IN (SELECT DISTINCT user_id FROM '{p}/view_segments.parquet'
                          USING SAMPLE reservoir(300 ROWS) REPEATABLE ({SEED}))""")
    con.execute(f"""
        CREATE TABLE brute AS
        SELECT seg.user_id, s.airing_id, seg.week,
               sum(epoch(least(seg.stop_time, s.end_time)) - epoch(greatest(seg.start_time, s.start_time)))::BIGINT AS ov
        FROM seg JOIN '{p}/schedule.parquet' s
          ON seg.channel_id = s.channel_id AND s.start_time < seg.stop_time AND s.end_time > seg.start_time
        GROUP BY ALL""")
    con.execute(f"""
        CREATE TABLE built AS
        SELECT user_id, airing_id, week, overlap_sec AS ov FROM '{p}/pairs_labelled.parquet'
        WHERE user_id IN (SELECT user_id FROM seg)
        UNION ALL
        SELECT user_id, airing_id, week, overlap_sec FROM '{p}/pairs_unlabelled.parquet'
        WHERE user_id IN (SELECT user_id FROM seg)""")
    r = MdReport("Join verification")
    r.text(f"Users: view-segment rows sampled with reservoir(300) seed {SEED}, then their distinct users. "
           "Brute force = plain channel + interval-overlap join, no hour buckets.")
    r.query(con, "Bucketed join vs brute force", """
        SELECT (SELECT count(DISTINCT user_id) FROM seg) AS users,
               (SELECT count(*) FROM brute) AS brute_pairs, (SELECT count(*) FROM built) AS built_pairs,
               (SELECT sum(ov) FROM brute) AS brute_overlap_sec, (SELECT sum(ov) FROM built) AS built_overlap_sec,
               (SELECT count(*) FROM brute FULL JOIN built USING (user_id, airing_id, week)
                WHERE brute.ov IS DISTINCT FROM built.ov) AS mismatched_pairs""")
    r.text(f"Runtime: {time.time() - t0:.1f} s.")
    r.save(OUT)


if __name__ == "__main__":
    main()
