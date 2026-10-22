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

Produced by `python -m src.target_study` on 2026-10-22 17:16. Validation weeks 11-20 -> 21-30, 1260 test users, pool 6376 shows, exactly the three submitted configs. Start-time join over raw views: 5408469 views matched to an airing, 2776875 of them to a labelled airing (4912 users).

Leaderboard (public / private): popularity_v1 0.255 / 0.244, repeat_v1 0.332 / 0.314, repeat_v2 0.36752 / 0.348. LB gaps (public): repeat_v1/pop 1.302, repeat_v2/pop 1.441, repeat_v2/repeat_v1 1.107.

### Validation MAP@5 of the submitted configs per target definition

`cv` = coefficient of variation of the three LB/val ratios (lower = more stable); `max rel err` = largest relative error when LB is fitted as one scale factor times val. Sorted by public cv.

| definition | pop_v1 | repeat_v1 | repeat_v2 | LB/val ratios (public) | cv public | max rel err public | cv private | max rel err private | val gap v1/pop | val gap v2/pop | val gap v2/v1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| n_days | 0.3167 | 0.4108 | 0.4512 | 0.805 / 0.808 / 0.815 | 0.0048 | 0.0064 | 0.0040 | 0.0056 | 1.297 | 1.425 | 1.098 |
| n_airings | 0.3100 | 0.4062 | 0.4395 | 0.823 / 0.817 / 0.836 | 0.0096 | 0.0116 | 0.0102 | 0.0142 | 1.311 | 1.418 | 1.082 |
| start_days | 0.2806 | 0.3750 | 0.4023 | 0.909 / 0.885 / 0.914 | 0.0137 | 0.0190 | 0.0166 | 0.0220 | 1.336 | 1.433 | 1.073 |
| days_50pct | 0.2758 | 0.3462 | 0.3738 | 0.925 / 0.959 / 0.983 | 0.0251 | 0.0395 | 0.0208 | 0.0306 | 1.256 | 1.356 | 1.080 |
| days_300s | 0.2809 | 0.3928 | 0.4158 | 0.908 / 0.845 / 0.884 | 0.0292 | 0.0372 | 0.0338 | 0.0457 | 1.398 | 1.480 | 1.059 |
| airings_300s | 0.2788 | 0.3893 | 0.4077 | 0.915 / 0.853 / 0.901 | 0.0299 | 0.0382 | 0.0339 | 0.0412 | 1.396 | 1.462 | 1.047 |
| airings_50pct | 0.2710 | 0.3373 | 0.3600 | 0.941 / 0.984 / 1.021 | 0.0333 | 0.0514 | 0.0291 | 0.0424 | 1.244 | 1.328 | 1.068 |
| cont70_days | 0.2680 | 0.3215 | 0.3445 | 0.952 / 1.033 / 1.067 | 0.0475 | 0.0788 | 0.0429 | 0.0697 | 1.200 | 1.286 | 1.071 |
| cont70_airings | 0.2644 | 0.3138 | 0.3360 | 0.965 / 1.058 / 1.094 | 0.0525 | 0.0877 | 0.0478 | 0.0785 | 1.187 | 1.271 | 1.070 |
| start_views | 0.2271 | 0.3369 | 0.3483 | 1.123 / 0.986 / 1.055 | 0.0531 | 0.0739 | 0.0580 | 0.0821 | 1.483 | 1.534 | 1.034 |
| cont80_days | 0.2646 | 0.3108 | 0.3343 | 0.964 / 1.068 / 1.099 | 0.0557 | 0.0943 | 0.0509 | 0.0851 | 1.174 | 1.263 | 1.076 |
| cont80_airings | 0.2601 | 0.3018 | 0.3233 | 0.981 / 1.100 / 1.137 | 0.0621 | 0.1053 | 0.0574 | 0.0960 | 1.161 | 1.243 | 1.071 |
| cont90_days | 0.2637 | 0.3035 | 0.3273 | 0.967 / 1.094 / 1.123 | 0.0638 | 0.1092 | 0.0590 | 0.0999 | 1.151 | 1.241 | 1.078 |
| cont90_airings | 0.2580 | 0.2943 | 0.3155 | 0.988 / 1.128 / 1.165 | 0.0695 | 0.1188 | 0.0648 | 0.1094 | 1.141 | 1.223 | 1.072 |
| watch_sec | 0.1799 | 0.2988 | 0.2942 | 1.417 / 1.111 / 1.249 | 0.0994 | 0.1419 | 0.1045 | 0.1496 | 1.661 | 1.635 | 0.985 |

Test users with a non-empty ground truth: n_days 1246, n_airings 1246, start_days 1246, days_50pct 1244, days_300s 1246, airings_300s 1246, airings_50pct 1244, cont70_days 1241, cont70_airings 1241, start_views 1246, cont80_days 1236, cont80_airings 1236, cont90_days 1226, cont90_airings 1226, watch_sec 1246.

Runtime: 9.3 s.
### Conclusion (written by hand from the table above; data after the time-zone fix, docs/errata.md)

- **n_days** (distinct calendar days with any overlap of a labelled airing) still matches the leaderboard best:
  public cv 0.0048 and private cv 0.0040 (best of all 15 definitions on private, best on public), validation gaps
  1.297 / 1.425 / 1.098 vs public LB gaps 1.302 / 1.441 / 1.107. Before the fix the same definition (with days
  effectively starting at 21:00) gave public cv 0.0024 and private cv 0.0057; the ranking of definitions did not
  change.
- **Continuous-coverage definitions** (one continuous view covering >= 70 / 80 / 90% of an airing; the 80% rule
  is attributed to the prize-winning write-up in docs/external_sources.md, which we could not read ourselves)
  fit clearly worse: cv 0.048-0.070. They compress the gaps between the three submissions (repeat_v1 / popularity
  1.14-1.20 vs 1.30 on the LB). On this evidence the 80% rule is not how the leaderboard ground truth is built;
  it may have been the write-up's own training label, which our data cannot confirm or rule out.
- Start-time and thresholded definitions keep their earlier ranks (start_days 3rd, start_views and all
  coverage definitions near the bottom).
- Same caveat as before: three related submissions give two independent gap ratios, so this ranks candidate
  definitions; it does not identify the exact rule.
