"""Write and check Kaggle submission files."""
from pathlib import Path

import pandas as pd

from src.data import SUBMISSION_CSV
from src.metrics import K


def write_submission(preds: dict[int, list[int]], users: list[int], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("user_id,tv_show_id\n")
        for u in users:
            f.write(f"{u},{' '.join(str(x) for x in preds[u])}\n")


def check_submission(path: Path, pool: set[int] | None = None) -> list[str]:
    """Return a list of format problems (empty list = OK)."""
    problems = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    template = pd.read_csv(SUBMISSION_CSV, dtype=str)
    if lines[0] != "user_id,tv_show_id":
        problems.append(f"bad header: {lines[0]!r}")
    rows = lines[1:]
    if len(rows) != len(template):
        problems.append(f"{len(rows)} rows, expected {len(template)}")
    users = [r.split(",", 1)[0] for r in rows]
    if users != template["user_id"].tolist():
        problems.append("user ids differ from submission.csv (set or order)")
    for r in rows:
        u, items = r.split(",", 1)
        ids = items.split(" ")
        if len(ids) != K or len(set(ids)) != K:
            problems.append(f"user {u}: not {K} distinct ids: {items!r}")
        elif not all(i.isdigit() for i in ids):
            problems.append(f"user {u}: non-integer id in {items!r}")
        elif "0" in ids:
            problems.append(f"user {u}: contains tv_show_id 0")
        elif pool is not None and not set(int(i) for i in ids) <= pool:
            problems.append(f"user {u}: id outside the test candidate pool")
    return problems
