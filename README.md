# sweet.tv TV program recommender (RecSys final exam)

Predict the five TV programmes each of 1,260 test users will watch in weeks 31-42 of 2020, from a view log
(weeks 11-30) and the broadcast schedule. Kaggle competition `sweettv-tv-program-recommender`, metric MAP@5.

**Designated final submission: [`submissions/final.csv`](submissions/final.csv)**, identical to
`submissions/hybrid_v4_cov80.csv` (Kaggle "submission (10).csv": public 0.46071, private 0.44493). Kaggle disables
submission selection after the deadline, so the final file is designated here and in the report. All submissions
and their scores: [`submissions/LOG.md`](submissions/LOG.md); screenshot: `reports/figures/kaggle_submissions.png`.

## Approach in short

1. **Join** the view log to the schedule: same channel, overlapping intervals. Overlapping views of one user on one
   channel are merged first, so parallel devices do not double count. `tv_show_id = 0` airtime is kept only as
   context (channel and time-slot habits) and is never recommended.
2. **Label.** A show counts as watched when one continuous view covers more than 50% of an airing (`cov50`).
   The way we found this (an any-overlap label first, then a diagnostic submission) is documented in
   [`docs/target_definition.md`](docs/target_definition.md).
3. **Validation.** History weeks 11-20, target weeks 21-30, evaluated on the 1,260 test users. Candidate pool =
   labelled shows airing in the target window, repeats allowed, the same popularity fallback for every method.
   Every learned re-ranker also gets a temporal check: the same model trained only on labels before week 21.
4. **Methods.** Popularity, implicit ALS, content-based (metadata TF-IDF), repeat models on coverage counts, slot
   habits (channel × weekday/weekend × hour), and a LightGBM re-ranker over candidates from these sources.
   Results: [`docs/results.md`](docs/results.md).

## Reproduce

Windows PowerShell, from the repository root.

```powershell
# 1. Environment (Python 3.11; uv or pip)
uv venv .venv --python 3.11
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\activate

# 2. Data (needs a Kaggle API token in %USERPROFILE%\.kaggle\access_token and the competition rules accepted)
kaggle competitions download sweettv-tv-program-recommender -p data/raw
Expand-Archive data/raw/sweettv-tv-program-recommender.zip -DestinationPath data/raw

# 3. Everything from raw data to the results tables, examples and figures
python -X utf8 -m src.run_all

# 4. Rebuild the final submission (overwrites submissions/hybrid_v4_cov80.csv and hybrid_v4_recent.csv;
#    existing LOG.md rows are kept). The committed final.csv is the file that was scored on Kaggle; a re-run can
#    differ from it slightly (see "Known limit of reproducibility" below).
python -X utf8 -m src.hybrid_v5
Copy-Item submissions/hybrid_v4_cov80.csv submissions/final.csv

# Unit test of the MAP@5 implementation
python -m unittest tests.test_metrics
```

`src.run_all` never overwrites the submission files. It regenerates the two submitted hybrids into
`data/processed/regenerated/` and reports how closely they match the committed files (`docs/results.md`, section
"Reproducibility"). `src.hybrid_v5` also re-runs the label probe and logs its validation numbers to
`experiments.csv`.

## Environment, seeds, runtimes

- Windows 11, Intel i7-11370H (4 cores / 8 threads), 15.7 GB RAM, Python 3.11.9. Pinned packages in
  `requirements.txt`, summary in [`docs/environment.md`](docs/environment.md).
- Seed 42 everywhere (numpy, implicit ALS `random_state`, LightGBM `random_state` with `deterministic=True`, early-
  stopping holdouts, DuckDB reservoir samples). Ensembles add seeds 43 and 44.
- DuckDB sessions are pinned to UTC; all timestamps are naive local times (see [`docs/errata.md`](docs/errata.md)).
- Runtimes per stage: [`docs/runtimes.md`](docs/runtimes.md), written by `src.run_all`; the full run took 1,397 s (about 23 min) on this machine, almost all of it the final hybrid ensemble.
- Known limit of reproducibility: DuckDB returns aggregation results in no fixed row order. LightGBM models can
  therefore differ slightly between runs even with fixed seeds (validation about +-0.001; a regenerated final.csv
  shares about 97% of its ids with the scored one). Details and the likely cause: [`docs/errata.md`](docs/errata.md) #2.
  All single methods reproduce exactly.

## Repository map

| path | content |
|---|---|
| `src/data.py`, `src/evaluation.py`, `src/metrics.py`, `src/submission.py` | loaders, validation harness, MAP@5 (Kaggle-style), submission writer and format check |
| `src/inspect_raw.py`, `src/build_interactions.py`, `src/verify_join.py`, `src/coverage.py` | data checks, the view-schedule join, its brute-force check, continuous-view coverage |
| `src/repeat_cont.py`, `src/repeat_v3.py`, `src/slots.py`, `src/als.py`, `src/cbf.py`, `src/baselines.py` | single methods |
| `src/hybrid.py`, `src/hybrid_v4.py`, `src/hybrid_v5.py` | candidate generation and LightGBM re-rankers (v5 produced the final file) |
| `src/target_study4.py`, `src/report_tables.py`, `src/examples.py`, `src/figures.py`, `src/run_all.py` | target study, report tables, examples, figures, the full pipeline |
| `src/repeat_v2.py`, `src/repeat_beta.py`, `src/refresh.py`, `src/target_study.py`, `src/compare_methods.py`, `src/title_match.py` | earlier stages selected on the any-overlap `n_days` target (superseded, kept as the record of the work) |
| `docs/` | results, target-definition study, errata, examples, external sources, per-stage outputs (outputs selected on `n_days` are marked "Superseded") |
| `experiments.csv` | one row per evaluation run (rows after the time-zone fix carry `data=tzfix` in `notes`) |
| `submissions/` | every submitted file, `LOG.md` with Kaggle scores, `final.csv` |
| `reports/figures/` | figures for the report and the Kaggle screenshot |

External sources: [`docs/external_sources.md`](docs/external_sources.md). No code was taken from them.
