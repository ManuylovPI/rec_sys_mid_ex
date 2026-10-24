"""Run the whole current pipeline, from raw CSVs in data/raw/ to the report tables, examples and figures.

Stages (each is also runnable on its own with `python -m src.<module>`):
  inspect_raw         raw-file checks                         -> docs/data_inspection.md
  build_interactions  schedule + merged views + overlap join   -> data/processed/*.parquet, docs/join_summary.md
  verify_join         brute-force check of the join            -> docs/join_verification.md
  coverage            single-continuous-view coverage          -> data/processed/coverage*.parquet
  target_study4       target definitions vs four LB points     -> docs/target_definition.md (four-point section)
  report_tables       every method on cov50 / cov80, regenerated hybrid submissions
                                                               -> docs/results.md, docs/results_table.csv
  examples            two example users                        -> docs/examples.md
  figures             report figures                           -> reports/figures/*.png
Wall-clock time per stage -> docs/runtimes.md. Submission files in submissions/ are never overwritten here;
the hybrids are regenerated into data/processed/regenerated/ and compared with the committed files.

Usage: python -m src.run_all
"""
import datetime as dt
import importlib
import platform
import time

from src.data import ROOT

STAGES = ["inspect_raw", "build_interactions", "verify_join", "coverage", "target_study4", "report_tables",
          "examples", "figures"]


def main() -> None:
    times = []
    for stage in STAGES:
        t = time.time()
        print(f"=== {stage}", flush=True)
        importlib.import_module(f"src.{stage}").main()
        times.append((stage, time.time() - t))
    lines = ["# Runtimes", "", f"`python -m src.run_all` on {dt.datetime.now():%Y-%m-%d %H:%M}, {platform.platform()}, "
             f"Python {platform.python_version()} (hardware in docs/environment.md).", "",
             "| stage | seconds |", "|---|---|"] + [f"| {s} | {t:.0f} |" for s, t in times] + \
            [f"| **total** | {sum(t for _, t in times):.0f} |"]
    (ROOT / "docs" / "runtimes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
