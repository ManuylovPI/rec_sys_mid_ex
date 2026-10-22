"""Glue shared by the per-method grid scripts: one validation context, run+log, best-params store."""
import json
import time

from src.data import ROOT, connect
from src.evaluation import HIST_WEEKS, SELECT_DEFS, TARGET_WEEKS, evaluate, fill, log_results, selection_score, validation_data
from src.repeat_v2 import POP_N, Stats

BEST_PARAMS = ROOT / "docs" / "best_params.json"


class Context:
    """Validation data + repeat_v2 stats (which also hold the shared popularity fallback)."""

    def __init__(self):
        self.con = connect()
        self.data = validation_data()
        self.users = sorted(set(self.data.populations["test_users"]) | set(self.data.populations["active_both"]))
        self.st = Stats(self.con, self.data.usw, HIST_WEEKS, TARGET_WEEKS)
        self.rows = []

    def run(self, method: str, params: dict, ranked: dict, t_start: float, notes: str = "") -> dict:
        """Fill with the shared fallback, evaluate, log one row per (population, target), remember the result."""
        preds = fill(ranked, self.users, self.st.fallback)
        res = evaluate(preds, self.data)
        log_results(method, params, res, time.time() - t_start,
                    f"fallback=popularity_n_weeks={POP_N}; selection={'+'.join(SELECT_DEFS)}" + (f"; {notes}" if notes else ""))
        row = {"method": method, "params": params, "select": selection_score(res),
               **{f"{p}/{d}": v[1] for (p, d), v in res.items()}}
        self.rows.append(row)
        print(f"{method} {params}: select={row['select']:.4f}", flush=True)
        return row

    def best(self, method: str) -> dict:
        return max((r for r in self.rows if r["method"] == method), key=lambda r: r["select"])


def save_best(method: str, params: dict) -> None:
    best = json.loads(BEST_PARAMS.read_text(encoding="utf-8")) if BEST_PARAMS.exists() else {}
    best[method] = params
    BEST_PARAMS.write_text(json.dumps(best, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_best() -> dict:
    return json.loads(BEST_PARAMS.read_text(encoding="utf-8"))


def results_table(rows: list[dict], cols: list[str]) -> list[str]:
    out = ["| method | params | select | " + " | ".join(cols) + " |", "|---|---|---|" + "---|" * len(cols)]
    for r in sorted(rows, key=lambda r: -r["select"]):
        out.append(f"| {r['method']} | `{r['params']}` | {r['select']:.4f} | " + " | ".join(f"{r[c]:.4f}" for c in cols) + " |")
    return out


RESULT_COLS = [f"{p}/{d}" for p in ("test_users", "active_both") for d in ("n_days", "n_airings", "watch_sec")]
