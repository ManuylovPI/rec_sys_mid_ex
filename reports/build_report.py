"""Build the exam report: fill reports/report_template.html from repository files, then print it to PDF.

Tables are generated from saved outputs only:
  TABLE I    docs/results_table.csv
  TABLE II   submissions/LOG.md (scores, Kaggle names) + validation numbers parsed from docs/target_definition.md,
             docs/hybrid_cov50_results.md, docs/hybrid_v4_results.md, docs/hybrid_v5_results.md
  TABLE III  docs/examples.md
  AI stats   the Claude Code transcript (counted at build time)
The commit shown is HEAD at build time (code and results); the report files are committed afterwards.

Usage (Windows venv): python -X utf8 reports/build_report.py [transcript.jsonl]
"""
import csv
import datetime as dt
import html
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
REPO = "https://github.com/ManuylovPI/rec_sys_mid_ex"
STEPS = {
    "popularity_v1.csv": "popularity baseline (watch seconds)",
    "repeat_v1.csv": "personal repeat, log seconds",
    "repeat_v2.csv": "loyalty repeat on any-overlap days",
    "repeat_cont50.csv": "&gt; 50% continuous watches (label test)",
    "hybrid_v2.csv": "LightGBM re-ranker on cov50 labels",
    "hybrid_v3_lr.csv": "top-50 candidates, more features, 3-fold refit",
    "hybrid_v3_ens.csv": "same, LambdaRank + binary ensemble",
    "hybrid_v3_lr_seeds.csv": "same, LambdaRank &times; 3 seeds",
    "hybrid_v4_recent.csv": "5 recency-weighted folds",
    "hybrid_v4_cov80.csv": "5 folds + cov80 labels (final)",
}


def text(p: str) -> str:
    return (ROOT / p).read_text(encoding="utf-8")


def f4(x) -> str:
    return "&ndash;" if x in (None, "") else f"{float(x):.4f}"


def methods_table() -> str:
    rows = list(csv.DictReader((ROOT / "docs/results_table.csv").open(encoding="utf-8")))
    out = ['<table><tr><th>Method</th><th>Configuration</th><th class="n">cov50</th><th class="n">cov80</th>'
           '<th class="n">n_days</th><th class="n">Temporal cov50</th><th class="n">Temporal cov80</th>'
           '<th class="n">Runtime, s</th></tr>']
    for r in rows:
        cls = ' class="best"' if r["method"].startswith("final") else ""
        out.append(f'<tr{cls}><td>{html.escape(r["method"])}</td><td>{html.escape(r["configuration"])}</td>'
                   f'<td class="n">{f4(r["main_cov50"])}</td><td class="n">{f4(r["main_cov80"])}</td>'
                   f'<td class="n">{f4(r["main_n_days"])}</td><td class="n">{f4(r["temporal_cov50"])}</td>'
                   f'<td class="n">{f4(r["temporal_cov80"])}</td><td class="n">{float(r["runtime_sec"]):.1f}</td></tr>')
    return "\n".join(out) + "</table>"


def validation_numbers() -> dict[str, tuple[str, str]]:
    v = {}
    row = next(ln for ln in text("docs/target_definition.md").splitlines() if ln.startswith("| cov50_airings_merged |"))
    vals = [c.strip() for c in row.split("|")[2:6]]
    for f, x in zip(["popularity_v1.csv", "repeat_v1.csv", "repeat_v2.csv", "repeat_cont50.csv"], vals):
        v[f] = (x, "")
    h2 = text("docs/hybrid_cov50_results.md")
    main = re.search(r"\(select (0\.\d+)\)", h2).group(1)
    temporal_rows = h2.split("## Temporal check")[1].splitlines()
    t = next(ln for ln in temporal_rows if "'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20" in ln)
    v["hybrid_v2.csv"] = (main, t.split("|")[3].strip())
    for ln in text("docs/hybrid_v4_results.md").split("## Submission files")[1].splitlines():
        m = re.match(r"\| (hybrid_v3_\w+) \| (0\.\d+) \| (0\.\d+) \|", ln)
        if m:
            v[m.group(1) + ".csv"] = (m.group(2), m.group(3))
    for ln in text("docs/hybrid_v5_results.md").splitlines():
        m = re.match(r"\| (hybrid_v4_\w+) \| \w+ \| (main|temporal) \| (0\.\d+) \|", ln)
        if m:
            main_t = v.get(m.group(1) + ".csv", ("", ""))
            v[m.group(1) + ".csv"] = (m.group(3), main_t[1]) if m.group(2) == "main" else (main_t[0], m.group(3))
    return v


def submissions_table(blob: str) -> str:
    val = validation_numbers()
    out = ['<table><tr><th>#</th><th>Kaggle name &rarr; repo file</th><th>What changed</th>'
           '<th class="n">Val. main</th><th class="n">Val. temporal</th><th class="n">Public</th>'
           '<th class="n">Private</th></tr>']
    i = 0
    for ln in text("submissions/LOG.md").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] not in STEPS or not re.fullmatch(r"0\.\d+", cells[3]):
            continue
        i += 1
        f, pub, prv, kag = cells[0], cells[3], cells[4], cells[5]
        main, temp = val[f]
        cls = ' class="best"' if f == "hybrid_v4_cov80.csv" else ""
        out.append(f'<tr{cls}><td>{i}</td><td>{html.escape(kag)} &rarr; <a href="{blob}/submissions/{f}">{f}</a></td>'
                   f'<td>{STEPS[f]}</td><td class="n">{f4(main)}</td><td class="n">{f4(temp)}</td>'
                   f'<td class="n">{pub}</td><td class="n">{prv}</td></tr>')
    assert i == 10, i
    return "\n".join(out) + "</table>"


def examples_table() -> str:
    md = text("docs/examples.md")
    sections = re.split(r"^## ", md, flags=re.M)[1:]
    out = ['<table class="ex"><tr><th style="width:9%">List</th>' + "".join(f"<th>{k}</th>" for k in range(1, 6)) + "</tr>"]
    for sec in sections:
        head = sec.splitlines()[0]
        info = sec.splitlines()[2]
        out.append(f'<tr><td colspan="6" style="background:#f6f6f6"><b>{html.escape(head)}</b> &mdash; '
                   f'{html.escape(info)}</td></tr>')
        truth = [ln for ln in sec.splitlines() if ln.startswith("| cov50 |")]
        cells = []
        for ln in truth:
            c = [x.strip() for x in ln.strip("|").split("|")]
            cells.append(cell(c[2], c[3], c[4], hit=True, fam=c[7] == "yes", fb=False))
        out.append("<tr><td><i>actual cov50 top-5</i></td>" + "".join(cells) + "</tr>")
        for block in re.split(r"^\*\*", sec.split("### Top-5 per method")[1], flags=re.M)[1:]:
            name = block.split("**")[0]
            rows = [ln for ln in block.splitlines() if re.match(r"\| \d \|", ln)]
            cs = []
            for ln in rows:
                c = [x.strip() for x in ln.strip("|").split("|")]
                cs.append(cell(c[1], c[2], c[3], hit=c[5] == "yes", fam=c[4] == "yes", fb=c[6] == "yes"))
            out.append(f"<tr><td>{html.escape(name)}</td>" + "".join(cs) + "</tr>")
    return "\n".join(out) + "</table>"


def cell(sid: str, title: str, cat: str, hit: bool, fam: bool, fb: bool) -> str:
    short = title if len(title) <= 30 else title[:28].rstrip()
    s = f"{sid} {html.escape(short)}{'&hellip;' if short != title else ''} [{html.escape(cat)}]"
    s += ("*" if fam else "") + ("&dagger;" if fb else "")
    return f"<td>{'<b>' + s + '</b>' if hit else s}</td>"


def ai_stats(transcript: Path) -> str:
    tools, ts, versions, models, prompts, queued = Counter(), [], set(), set(), 0, 0
    for line in transcript.open(encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "timestamp" in e:
            ts.append(e["timestamp"])
        if e.get("version"):
            versions.add(e["version"])
        att = e.get("attachment")
        if e.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command":
            queued += 1  # a message the user sent while the agent was working
        msg = e.get("message") or {}
        if e.get("type") == "assistant" and isinstance(msg, dict):
            if msg.get("model"):
                models.add(msg["model"])
            tools.update(c.get("name") for c in msg.get("content") or [] if isinstance(c, dict) and c.get("type") == "tool_use")
        if e.get("type") == "user" and isinstance(msg, dict) and not e.get("isMeta"):
            c = msg.get("content")
            if isinstance(c, str):
                prompts += not c.startswith("<") or c.lstrip().startswith("<pasted_content")
            elif isinstance(c, list) and not any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                first = next((x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"), "")
                prompts += bool(first) and (not first.lstrip().startswith("<") or first.lstrip().startswith("<pasted_content"))
    msk = dt.timedelta(hours=3)
    start = dt.datetime.fromisoformat(min(ts).replace("Z", "+00:00")) + msk
    end = dt.datetime.fromisoformat(max(ts).replace("Z", "+00:00")) + msk
    top = ", ".join(f"{n} {k}" for k, n in tools.most_common())
    return (f"Claude Code (Anthropic), versions {', '.join(sorted(versions))}, model {', '.join(sorted(models))} "
            f"(Claude Opus 5.5): one session from {start:%d %b %Y %H:%M} to {end:%d %b %Y %H:%M} MSK (with a break between "
            f"22 and 24 Oct), {prompts} prompts from me plus {queued} message sent while the agent was working, and "
            f"{sum(tools.values())} tool calls ({top}), counted from the transcript when this PDF was built; the "
            f"transcript continues with the final commit and push.")


def main() -> None:
    transcript = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    dirty = [ln for ln in status.splitlines() if not ln[3:].startswith("reports/")]
    if dirty:
        raise SystemExit(f"commit everything outside reports/ first: {dirty}")
    full = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    blob = f"{REPO}/blob/{full}"
    page = (REP / "report_template.html").read_text(encoding="utf-8")
    fills = {"{{TABLE_METHODS}}": methods_table(), "{{TABLE_SUBMISSIONS}}": submissions_table(blob),
             "{{TABLE_EXAMPLES}}": examples_table(), "{{COMMIT}}": full[:10], "{{REPO_BLOB}}": blob,
             "{{AI_STATS}}": ai_stats(transcript) if transcript else "[transcript statistics]"}
    for k, v in fills.items():
        assert k in page, k
        page = page.replace(k, v)
    out_html = REP / "manuilov_exam_report.html"
    out_html.write_text(page, encoding="utf-8")
    out_pdf = REP / "manuilov_exam_report.pdf"
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", "--virtual-time-budget=10000", out_html.as_uri()],
                   check=True, capture_output=True)
    print(f"built {out_pdf} from commit {full[:10]}")


if __name__ == "__main__":
    main()
