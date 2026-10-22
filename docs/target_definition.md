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

## Study: alternative target definitions

Produced by `python -m src.target_study` on 2026-10-22 17:02. Validation weeks 11-20 -> 21-30, 1260 test users, pool 6376 shows, exactly the three submitted configs. Start-time join over raw views: 5408469 views matched to an airing, 2776875 of them to a labelled airing (4912 users).

Leaderboard (public / private): popularity_v1 0.255 / 0.244, repeat_v1 0.332 / 0.314, repeat_v2 0.36752 / 0.348. LB gaps (public): repeat_v1/pop 1.302, repeat_v2/pop 1.441, repeat_v2/repeat_v1 1.107.

### Validation MAP@5 of the submitted configs per target definition

`cv` = coefficient of variation of the three LB/val ratios (lower = more stable); `max rel err` = largest relative error when LB is fitted as one scale factor times val. Sorted by public cv.

| definition | pop_v1 | repeat_v1 | repeat_v2 | LB/val ratios (public) | cv public | max rel err public | cv private | max rel err private | val gap v1/pop | val gap v2/pop | val gap v2/v1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| n_days | 0.3174 | 0.4142 | 0.4558 | 0.803 / 0.802 / 0.806 | 0.0024 | 0.0031 | 0.0057 | 0.0080 | 1.305 | 1.436 | 1.100 |
| n_airings | 0.3100 | 0.4062 | 0.4424 | 0.823 / 0.817 / 0.831 | 0.0067 | 0.0084 | 0.0084 | 0.0114 | 1.311 | 1.427 | 1.089 |
| start_days | 0.2806 | 0.3750 | 0.4043 | 0.909 / 0.885 / 0.909 | 0.0123 | 0.0168 | 0.0158 | 0.0198 | 1.336 | 1.441 | 1.078 |
| days_50pct | 0.2768 | 0.3463 | 0.3743 | 0.921 / 0.959 / 0.982 | 0.0262 | 0.0419 | 0.0217 | 0.0329 | 1.251 | 1.352 | 1.081 |
| days_300s | 0.2858 | 0.3973 | 0.4209 | 0.892 / 0.836 / 0.873 | 0.0271 | 0.0331 | 0.0315 | 0.0415 | 1.390 | 1.473 | 1.060 |
| airings_300s | 0.2788 | 0.3893 | 0.4094 | 0.915 / 0.853 / 0.898 | 0.0293 | 0.0364 | 0.0336 | 0.0420 | 1.396 | 1.468 | 1.052 |
| airings_50pct | 0.2710 | 0.3373 | 0.3620 | 0.941 / 0.984 / 1.015 | 0.0312 | 0.0492 | 0.0268 | 0.0402 | 1.244 | 1.335 | 1.073 |
| start_views | 0.2271 | 0.3369 | 0.3491 | 1.123 / 0.986 / 1.053 | 0.0532 | 0.0747 | 0.0581 | 0.0829 | 1.483 | 1.537 | 1.036 |
| watch_sec | 0.1799 | 0.2988 | 0.2953 | 1.417 / 1.111 / 1.245 | 0.0996 | 0.1432 | 0.1047 | 0.1509 | 1.661 | 1.641 | 0.988 |

Test users with a non-empty ground truth: n_days 1246, n_airings 1246, start_days 1246, days_50pct 1244, days_300s 1246, airings_300s 1246, airings_50pct 1244, start_views 1246, watch_sec 1246.

Runtime: 8.4 s.
### Conclusion (written by hand from the table above)

- The current **n_days** definition (distinct days with any overlap of a labelled airing) matches the
  leaderboard best: LB/val ratios 0.803 / 0.802 / 0.806 (public), cv 0.0024, and its validation gaps
  (1.305, 1.436, 1.100) reproduce the public LB gaps (1.302, 1.441, 1.107) within about 0.7%. The private LB
  gives the same ordering (cv 0.0057, best of all definitions).
- **n_airings** is second (cv 0.0067). The start-time hypothesis is not supported: **start_views** ranks 8th of 9
  (cv 0.053) and over-states the gap between repeat_v1 and popularity (1.483 vs 1.302); **start_days** ranks 3rd
  (cv 0.0123). Thresholded definitions (300 s, 50%) fit worse than the unthresholded ones.
- Consequence: the counts and labels are not rebuilt on start-time logic. n_days is the best available
  proxy for the hidden target.
- Caveats: three configs give only two independent gap ratios, so this ranks the candidate definitions; it does
  not identify the organisers' exact rule. The three configs are related (two are repeat variants), which
  limits how different their behaviour under the definitions can be. All validation numbers come from the
  same 1,260 test users and weeks 21-30.
- Note: the first run of `src.target_study` crashed after logging its 27 rows to experiments.csv (a DuckDB API
  change in the report step); the rerun logged the same 27 deterministic values again.
