"""Tiny helpers to write query results as Markdown, so every reported number lives in a saved file."""
import datetime as dt
import platform

import duckdb


def _fmt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.4g}" if abs(v) < 1e6 else f"{v:.0f}"
    return str(v).replace("|", "\\|").replace("\n", " ")


def md_table(con: duckdb.DuckDBPyConnection, sql: str) -> str:
    rel = con.sql(sql)
    cols = rel.columns
    rows = rel.fetchall()
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_fmt(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


class MdReport:
    def __init__(self, title: str):
        self.parts = [f"# {title}", "",
                      f"Generated {dt.datetime.now():%Y-%m-%d %H:%M:%S} on {platform.platform()}, "
                      f"Python {platform.python_version()}, duckdb {duckdb.__version__}.", ""]

    def text(self, s: str) -> None:
        self.parts += [s, ""]

    def query(self, con, title: str, sql: str, note: str | None = None) -> None:
        self.parts += [f"## {title}", ""]
        if note:
            self.parts += [note, ""]
        self.parts += [md_table(con, sql), ""]
        print(f"done: {title}", flush=True)

    def save(self, path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts), encoding="utf-8")
        print(f"wrote {path}")
