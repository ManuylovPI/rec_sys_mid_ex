"""How many test-pool shows without history match a training show by title under a different id?

Three title levels:
  exact  raw tv_show_title string
  norm   lowercased, ё->е, punctuation removed, spaces collapsed
  base   first quoted part of the title ('...', "...", «...») if present, else text before the first '.' or ',';
         then normalised as above (drops 'Х/ф', 'Т/с' prefixes and season/episode suffixes)
"No history" is checked two ways: (a) the id never airs in weeks <= 30, (b) the id was never watched in weeks 11-30.

Usage: python -m src.title_match   ->  docs/title_match.md
"""
import re
import time

import pandas as pd

from src.data import PROCESSED, ROOT, connect

OUT = ROOT / "docs" / "title_match.md"
QUOTED = re.compile(r"['\"«](.+?)['\"»]")


def norm(t: str) -> str:
    t = t.lower().replace("ё", "е")
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def base(t: str) -> str:
    m = QUOTED.search(t)
    core = m.group(1) if m else re.split(r"[.,]", t, maxsplit=1)[0]
    return norm(core)


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v).replace("|", "/") for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main() -> None:
    t0 = time.time()
    con = connect()
    titles = con.sql(f"""
        SELECT tv_show_id, tv_show_title AS title, week >= 31 AS is_test, count(*) AS n_airings
        FROM '{(PROCESSED / 'schedule.parquet').as_posix()}' WHERE tv_show_id <> 0 GROUP BY ALL""").df()
    watched = set(pd.read_parquet(PROCESSED / "user_show_week.parquet", columns=["tv_show_id"])["tv_show_id"].unique())
    titles["norm"] = titles["title"].map(norm)
    titles["base"] = titles["title"].map(base)
    titles["exact"] = titles["title"]

    test = titles[titles["is_test"]]
    train = titles[~titles["is_test"]]
    test_ids = set(test["tv_show_id"])
    train_ids = set(train["tv_show_id"])
    test_airings = test.groupby("tv_show_id")["n_airings"].sum()

    defs = {"(a) id never airs in weeks <= 30": test_ids - train_ids,
            "(b) id never watched in weeks 11-30": test_ids - watched}
    lines = ["# Title matching for test-pool shows without history", "",
             "Produced by `python -m src.title_match`. Test pool = labelled shows airing in weeks 31-42 "
             f"({len(test_ids)} ids, {int(test_airings.sum())} airings).", ""]
    rows, examples = [], None
    for name, ids in defs.items():
        sub = test[test["tv_show_id"].isin(ids)]
        row = {"no-history definition": name, "ids": len(ids),
               "their airings in 31-42": int(test_airings.reindex(list(ids)).sum())}
        for level in ["exact", "norm", "base"]:
            tr = train[["tv_show_id", level]].rename(columns={"tv_show_id": "train_id"})
            m = sub[["tv_show_id", level, "title"]].merge(tr, on=level)
            m = m[m["tv_show_id"] != m["train_id"]]
            matched = set(m["tv_show_id"])
            matched_w = set(m.loc[m["train_id"].isin(watched), "tv_show_id"])
            row[f"{level}: matched"] = len(matched)
            row[f"{level}: matched to a watched id"] = len(matched_w)
            if level == "base" and name.startswith("(a)"):
                ex = m.drop_duplicates("tv_show_id").head(15).copy()
                ex["train_title"] = ex["train_id"].map(train.drop_duplicates("tv_show_id").set_index("tv_show_id")["title"])
                examples = ex[["tv_show_id", "title", "train_id", "train_title"]]
        rows.append(row)
    lines += ["## Matches", "", md(pd.DataFrame(rows)), ""]
    lines += ["## Examples of base-title matches, definition (a)", "", md(examples), ""]

    per_id = train.groupby("tv_show_id")["base"].nunique()
    per_base = train.groupby("base")["tv_show_id"].nunique()
    lines += ["## Context: how ids relate to titles in weeks <= 30", "",
              f"Ids with more than one distinct base title: {int((per_id > 1).sum())} of {len(per_id)}. "
              f"Base titles shared by more than one id: {int((per_base > 1).sum())} of {len(per_base)} "
              f"(max {int(per_base.max())} ids for one base title).", "",
              f"Runtime: {time.time() - t0:.1f} s."]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
