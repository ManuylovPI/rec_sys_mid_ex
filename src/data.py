"""Raw-data loaders shared by every step.

All timestamps in the raw files are naive local wall-clock strings (evidence points to
Kyiv time with DST, see docs/data_inspection.md). They are parsed as naive TIMESTAMPs and
never converted. Weeks are ISO weeks of 2020 (Monday 00:00 start), taken from start_time.
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

VIEWS_CSV = RAW / "dataset11-30.csv"
SCHEDULE_CSVS = {
    "11-20": RAW / "export_arh_11-20-final.csv",
    "21-30": RAW / "export_arh_21-30-final.csv",
    "31-42": RAW / "export_arh_31-42-final.csv",
}
SUBMISSION_CSV = RAW / "submission.csv"

# Week ranges: training views exist for 11-30, test window is 31-42.
FIRST_WEEK, LAST_TRAIN_WEEK, LAST_TEST_WEEK = 11, 30, 42
SEED = 42


def _p(path: Path) -> str:
    return path.as_posix()


def connect(memory_limit: str = "8GB") -> duckdb.DuckDBPyConnection:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET memory_limit = '{memory_limit}'")
    con.execute(f"SET temp_directory = '{_p(PROCESSED / 'duckdb_tmp')}'")
    # All timestamps are naive local wall-clock values. Pin the session to UTC so that no TIMESTAMPTZ
    # conversion can shift them (before 2026-10-22 the Windows default Europe/Moscow shifted epoch -> timestamp
    # conversions by +3 h; see docs/errata.md).
    con.execute("SET TimeZone = 'UTC'")
    return con


def register_raw(con: duckdb.DuckDBPyConnection) -> None:
    """Create views over the raw CSVs: raw_views, raw_sched_<file>, raw_sched (with source file), raw_submission."""
    con.execute(f"""
        CREATE OR REPLACE VIEW raw_views AS
        SELECT * FROM read_csv('{_p(VIEWS_CSV)}', header = true,
            columns = {{'user_id': 'UBIGINT', 'vsetv_id': 'INTEGER', 'start_time': 'TIMESTAMP',
                        'stop_time': 'TIMESTAMP', 'duraton': 'BIGINT'}})
    """)
    parts = []
    for name, path in SCHEDULE_CSVS.items():
        view = "raw_sched_" + name.replace("-", "_")
        con.execute(f"""
            CREATE OR REPLACE VIEW {view} AS
            SELECT * EXCLUDE (start_time),
                   strptime(start_time, '%d.%m.%Y %H:%M:%S') AS start_time
            FROM read_csv('{_p(path)}', header = true,
                types = {{'start_time': 'VARCHAR', 'tv_show_id': 'BIGINT',
                          'channel_id': 'INTEGER', 'duration': 'BIGINT'}})
        """)
        parts.append(f"SELECT *, '{name}' AS source_file FROM {view}")
    con.execute("CREATE OR REPLACE VIEW raw_sched AS " + " UNION ALL ".join(parts))
    con.execute(f"""
        CREATE OR REPLACE VIEW raw_submission AS
        SELECT * FROM read_csv('{_p(SUBMISSION_CSV)}', header = true,
            types = {{'user_id': 'UBIGINT', 'tv_show_id': 'VARCHAR'}})
    """)
