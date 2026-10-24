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

## What the fourth submission showed: the n_days target was wrong

The study above compared the leaderboard with three submissions that **all rank shows by any-overlap counts**
(popularity_v1, repeat_v1, repeat_v2). Such configs are bound to agree best with an any-overlap target, so the
study could only rank candidate targets among themselves; it could not test a definition none of the submitted
models used. We missed this selection effect and selected models on n_days (stages 7-8).

The project author pointed to a prize-winning write-up (docs/external_sources.md #1) whose simplest baseline counts
a show as watched only if one sitting covers more than 50% of it. We re-implemented that baseline
(`src/repeat_cont.py`, repeat_cont50) and submitted it as a direct test. Before submitting, we wrote down what each
target hypothesis predicted for its leaderboard score (docs/repeat_cont_results.md; one scale factor per target
fitted on the three earlier submissions):

| target hypothesis | predicted public | predicted private |
|---|---|---|
| n_days (any overlap, distinct days) | 0.298 | 0.283 |
| cont50 (one continuous view > 50%, airings) | 0.380 | 0.360 |
| cont80 (one continuous view > 80%, airings) | 0.387 | 0.368 |
| **actual result** | **0.417** | **0.400** |

On validation the same config scored 0.369 on n_days, against 0.4535 for repeat_v2; on the leaderboard it beat
repeat_v2 by 0.049 public (0.417 vs 0.368) and 0.052 private. The n_days hypothesis predicted 0.298 and is
clearly rejected. The coverage hypotheses point the right way but still under-predict by about 0.03, so neither
of our cont definitions is the exact rule either.

Consequences:
- Every model choice made on n_days (stages 7-8) was tuned to the wrong label: the loyalty repeat, the hybrid
  re-rankers and their "improvements" were measured against a target that does not match the leaderboard.
  The earlier ranking of methods may still hold qualitatively, but its numbers have to be re-measured.
- The target study is redone below with all four leaderboard points; repeat_cont50 is the point that actually
  discriminates between definitions.
- Lesson for the report: agreement with the leaderboard is only informative if the submitted models disagree
  about the candidate targets. A cheap diagnostic submission built on a different definition was worth more
  than the whole study.

## Study with four leaderboard points

Produced by `python -m src.target_study4` on 2026-10-24 12:38 (data after the time-zone fix). Validation weeks 11-20 -> 21-30, 1260 test users, the four submitted configs. `cov{cut}_{unit}_{source}`: airings (or distinct days) where one view covers more than cut% of the airing; merged = our merged continuous intervals per user and channel, raw = each raw view row on its own. `cv` = coefficient of variation of the four LB/val ratios; `LOO pred` = repeat_cont50's leaderboard score predicted from a scale fitted on the other three submissions (actual 0.417 public / 0.400 private). Sorted by cv public + cv private.

| target | pop_v1 | repeat_v1 | repeat_v2 | repeat_cont50 | LB/val ratios public | cv public | cv private | LOO pred public | LOO pred private |
|---|---|---|---|---|---|---|---|---|---|
| cov50_airings_merged | 0.2752 | 0.3335 | 0.3576 | 0.3841 | 0.927 / 0.996 / 1.028 / 1.086 | 0.0569 | 0.0582 | 0.381 | 0.362 |
| cov50_airings_raw | 0.2749 | 0.3325 | 0.3564 | 0.3827 | 0.928 / 0.999 / 1.031 / 1.090 | 0.0578 | 0.0591 | 0.381 | 0.361 |
| cov80_airings_merged | 0.2600 | 0.3015 | 0.3231 | 0.3583 | 0.981 / 1.101 / 1.137 / 1.164 | 0.0639 | 0.0633 | 0.389 | 0.369 |
| cov80_airings_raw | 0.2607 | 0.3001 | 0.3223 | 0.3588 | 0.978 / 1.106 / 1.140 / 1.162 | 0.0651 | 0.0642 | 0.390 | 0.370 |
| cov30_airings_raw | 0.2847 | 0.3548 | 0.3811 | 0.3918 | 0.896 / 0.936 / 0.964 / 1.064 | 0.0646 | 0.0676 | 0.368 | 0.349 |
| cov30_airings_merged | 0.2849 | 0.3554 | 0.3812 | 0.3919 | 0.895 / 0.934 / 0.964 / 1.064 | 0.0648 | 0.0678 | 0.367 | 0.349 |
| cov80_days_merged | 0.2646 | 0.3104 | 0.3341 | 0.3518 | 0.964 / 1.070 / 1.100 / 1.185 | 0.0733 | 0.0745 | 0.371 | 0.352 |
| cov80_days_raw | 0.2645 | 0.3090 | 0.3329 | 0.3516 | 0.964 / 1.075 / 1.104 / 1.186 | 0.0735 | 0.0746 | 0.372 | 0.353 |
| cov50_days_merged | 0.2793 | 0.3394 | 0.3693 | 0.3718 | 0.913 / 0.978 / 0.995 / 1.121 | 0.0754 | 0.0782 | 0.361 | 0.342 |
| cov50_days_raw | 0.2794 | 0.3389 | 0.3685 | 0.3709 | 0.913 / 0.980 / 0.997 / 1.124 | 0.0763 | 0.0791 | 0.360 | 0.342 |
| cov30_days_raw | 0.2879 | 0.3624 | 0.3918 | 0.3812 | 0.886 / 0.916 / 0.938 / 1.094 | 0.0839 | 0.0877 | 0.350 | 0.332 |
| cov30_days_merged | 0.2882 | 0.3625 | 0.3921 | 0.3809 | 0.885 / 0.916 / 0.937 / 1.095 | 0.0846 | 0.0885 | 0.350 | 0.332 |
| n_airings | 0.3100 | 0.4062 | 0.4395 | 0.3888 | 0.823 / 0.817 / 0.836 / 1.072 | 0.1209 | 0.1257 | 0.321 | 0.305 |
| n_days | 0.3167 | 0.4108 | 0.4512 | 0.3690 | 0.805 / 0.808 / 0.815 / 1.130 | 0.1562 | 0.1611 | 0.299 | 0.284 |

Runtime: 7.9 s.
### Conclusion of the four-point study (written by hand from the table above)

- With repeat_cont50 included, the any-overlap targets fit worst: n_days cv 0.156 public / 0.161 private, and
  its leave-one-out prediction for repeat_cont50 is 0.299 against the actual 0.417.
- The best candidate is **cov50_airings_merged** (airings where one merged continuous view covers more than 50%
  of the airing): cv 0.057 / 0.058. The raw single-view variant is practically identical (cv 0.058 / 0.059),
  so our cross-device merge does not matter for the target. Model selection uses cov50 from stage 10 on.
- No candidate fits well. Even for cov50 the LB/val ratio rises with model quality (0.93 popularity, 0.99
  repeat_v1, 1.03 repeat_v2, 1.09 repeat_cont50) and the leave-one-out prediction for repeat_cont50 is 0.381
  against 0.417. The hidden rule is therefore still not identified; cov50 is the best available approximation,
  and validation numbers on it should be read as rankings rather than as leaderboard estimates.
