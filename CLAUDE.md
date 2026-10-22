# sweet.tv TV program recommender — final exam (RecSys course, HSE)

Individual exam. Deadline: 24 Oct 2026, 19:00 MSK. Full spec: `docs/exam_quiz_GSB.md`.
Read the spec before any work. If this file and the spec disagree, the spec wins; tell me about the conflict.

## Task in one paragraph
Join the view log to the TV schedule (same channel + view interval overlaps the show's airing interval)
to get user-program interactions, then predict 5 `tv_show_id`s per test user (1,260 users in
`submission.csv`) for test weeks 31-42. Metric: MAP@5, higher is better. Kaggle competition slug:
`sweettv-tv-program-recommender` (late submissions are scored).

## Hard rules (breaking any of these can fail the exam)
1. **K = 5 everywhere**: submission, validation, every reported number.
2. **No future leakage.** Never use views from test weeks 31-42 (there are none in the data, keep it that way).
   The 31-42 schedule may be used ONLY to know which shows air on which channel and when.
3. **`tv_show_id = 0` is unlabelled airtime, never an item.** It may be used as context (e.g. channel time), never recommended.
4. **Validation**: temporal. History = earlier training weeks, target = later training weeks
   (planned: history weeks 11-20, target weeks 21-30; if real week boundaries differ, ask me before changing).
   Models are fit on the history part only; validation is for selection, never for fitting.
   After selection, the final model is refit on all training weeks and predicts weeks 31-42.
5. **Candidate pool**: shows with `tv_show_id != 0` that air in the target window's schedule.
   Repeats of already-watched shows are ALLOWED. Same pool, same repeat policy, same cold-start
   fallback for EVERY method, including the baseline.
6. **Cold-start users** (no usable history): popularity fallback, identical across all methods.
   Every method must output exactly 5 distinct ids per user; if it can't fill 5, top up with the fallback.
7. **Required methods**: popularity baseline (reference, not counted) + at least two of:
   content-based, association rules, matrix factorization (implicit), personalized PageRank.
   Each method is evaluated individually on the same hold-out before any hybrid.
8. **Honesty**: never claim something was checked, verified or measured unless it was actually run in
   this session. No invented numbers, references or experiments. If unsure, say so.

## Experiment log
- Every evaluation run appends ONE row to `experiments.csv`:
  `timestamp, stage, method, params_json, seed, n_val_users, val_map5, runtime_sec, notes`.
- No number goes into the report unless it is in `experiments.csv` (or in a saved output file).
- Each submission file is logged in `submissions/LOG.md`: file name, method, date. I add the returned Kaggle scores myself.

## Engineering conventions
- Python, seed 42 everywhere (numpy, implicit, lightgbm, sampling).
- Code in `src/`, each step runnable from the command line (`python -m src.<module>`). Notebooks only for EDA/plots.
- Heavy joins with DuckDB; intermediate tables cached as parquet in `data/processed/` (gitignored).
- Raw data in `data/raw/` (gitignored). Never modify raw files.
- One shared MAP@5 implementation in `src/metrics.py` with a small unit test on a toy example.
- Record environment (OS, Python and package versions, CPU/RAM) and runtimes for the report.
- Commit after each finished stage with a clear message. Do not push unless I ask.

## Submission files
- I submit to Kaggle myself. Never run `kaggle competitions submit`.
- Your job is to write the file to `submissions/` and check its format: header, 1,260 rows, user ids match `submission.csv`, exactly 5 distinct ids per row, space-separated.

## Deliverables (end of the project)
- `submissions/final.csv` used for the designated final Kaggle score.
- `README.md` with reproduction steps.
- Report (PDF): GitHub link, screenshot of the Submissions page with the returned score, join rule and
  watch threshold with justification, handling of id=0, validation design, method comparison table,
  hybrid ablation, Top-5 of every method for the same two users (id, title, category) vs. their actual
  views, business/algorithmic analysis, limitations, AI-assistance disclosure.

## How we work
Stage by stage. At the end of each stage: short summary, key numbers, anything suspicious, then stop and wait for me.
