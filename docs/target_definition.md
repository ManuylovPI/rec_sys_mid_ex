# Which ground-truth definition Kaggle most likely uses

Written 2026-10-22, after the first two Kaggle submissions.

## Evidence

The competition page does not say how a user's "5 most preferred" programmes are defined. On validation
(history weeks 11-20, target weeks 21-30, 1,260 test users) we built the target in three ways: top-5 by total
watch seconds, by number of distinct days, and by number of airings watched. The same two methods were then
refit on weeks 11-30 and submitted.

| | popularity_v1 | repeat_v1 | ratio repeat / popularity |
|---|---:|---:|---:|
| Validation, target = watch seconds | 0.1799 | 0.2988 | 1.66 |
| Validation, target = distinct days | 0.3174 | 0.4142 | 1.31 |
| Validation, target = airings | 0.3100 | 0.4062 | 1.31 |
| Kaggle public | 0.255 | 0.332 | 1.30 |
| Kaggle private | 0.244 | 0.314 | 1.29 |

Sources: validation numbers from `docs/baselines_results.md` / `experiments.csv`; Kaggle scores as returned
for the files in `submissions/LOG.md`.

## Reasoning

Absolute MAP@5 levels are not comparable between validation and Kaggle (different window length, different
weeks, unknown thresholds). The ratio between two methods scored on the same ground truth is more stable. The
Kaggle ratio (1.29-1.30) matches the frequency-based targets (1.31) and not the time-based one (1.66).

## Decision

From this point, models are selected on the **mean MAP@5 of the n_days and n_airings targets on the 1,260 test
users**. The watch-seconds target is still reported for completeness.

## Caveats

This rests on one pair of submissions and a single ratio. It is strong evidence that the hidden target ranks by
how often a user watches a programme, not by how long, but it does not tell us the exact rule (days vs airings,
or any minimum watch threshold), and the two frequency targets cannot be told apart this way (both give 1.31).
