# View-schedule join summary

Generated 2026-10-24 12:38:18 on Windows-10-10.0.26200-SP0, Python 3.11.9, duckdb 2.0.0.

Produced by `python -m src.build_interactions`. No watch threshold is applied in the cached tables. `frac_watched` = overlap seconds / airing duration for one airing; in `user_show_week`, `frac_max` is the best single-airing fraction that week, `frac_total` = watch_sec / summed duration of the airings touched.

Timings (s): schedule 4.4, merge_views 4.7, join 0.8, aggregate_and_write 3.9; total 14.3.

## Row counts

| step | n_rows |
|---|---|
| raw views | 5821987 |
| merged views (user, channel) | 5441773 |
| view segments (after week split) | 5458899 |
| schedule airings kept | 3441607 |
| segment-airing overlaps | 7375362 |
| pairs_labelled (user, airing, week) | 3026937 |
| pairs_unlabelled (user, airing, week) | 3316433 |
| user_show_week | 2159681 |

## Schedule airings kept by week range

| weeks | airings | labelled | programmes |
|---|---|---|---|
| 10 (join only) | 86 | 21 | 11 |
| 11-20 | 1071717 | 115309 | 5842 |
| 21-30 | 1074396 | 121521 | 6376 |
| 31-42 | 1295408 | 144784 | 6642 |

## Merge effect: viewing seconds before and after merging overlapping views

| raw_sec | merged_sec | segments_sec | merged_intervals_from_2plus_views |
|---|---|---|---|
| 8619636424 | 8503411121 | 8503411121 | 187005 |

## Where viewing time goes (merged segments, seconds)

| pct_on_labelled_airings | pct_on_unlabelled_airings | pct_unmatched |
|---|---|---|
| 52.89 | 41.15 | 5.96 |

## Sanity: overlap never exceeds airing duration; weeks of interactions

| max_frac | min_overlap_sec | min_week | max_week |
|---|---|---|---|
| 1 | 1 | 11 | 30 |

## Distribution: overlap seconds per (user, airing, week), labelled

| n | mean | quantiles p10/p25/p50/p75/p90/p99 | max |
|---|---|---|---|
| 3026937 | 1486 | [89, 214, 711, 1981, 4154, 7845] | 30000 |

## Distribution: fraction of the airing watched per (user, airing, week), labelled

| n | mean | quantiles p10/p25/p50/p75/p90/p99 | share_full |
|---|---|---|---|
| 3026937 | 0.3578 | [0.0155, 0.0437, 0.1941, 0.6507, 1.0, 1.0] | 0.1392 |

## Histogram: overlap seconds per (user, airing, week), labelled

| bin | n | pct |
|---|---|---|
| 01: <10 s | 11471 | 0.38 |
| 02: 10-59 s | 65074 | 2.15 |
| 03: 1-5 min | 861407 | 28.46 |
| 04: 5-15 min | 722103 | 23.86 |
| 05: 15-30 min | 530087 | 17.51 |
| 06: 30-60 min | 455171 | 15.04 |
| 07: >=60 min | 381624 | 12.61 |

## Histogram: fraction of the airing watched per (user, airing, week), labelled

| bin | n | pct |
|---|---|---|
| 01: <5% | 819503 | 27.07 |
| 02: 5-10% | 339394 | 11.21 |
| 03: 10-25% | 498812 | 16.48 |
| 04: 25-50% | 432646 | 14.29 |
| 05: 50-75% | 280628 | 9.27 |
| 06: 75-<100% | 234703 | 7.75 |
| 07: 100% | 421251 | 13.92 |

## Airing duration of labelled airings that were watched (seconds)

| quantiles p10/p25/p50/p75/p90/p99 | max |
|---|---|
| [1200, 2700, 5700, 7200, 9300, 16800] | 32700 |

## Distribution: user_show_week watch_sec, frac_max, n_airings, n_days

| n | watch_sec p25/p50/p75/p90 | frac_max p25/p50/p75/p90 | n_airings p50/p90/p99 | n_days p50/p90/p99 |
|---|---|---|---|---|
| 2159681 | [215, 886, 2907, 5717] | [0.036, 0.159, 0.567, 1.0] | [1, 2, 7] | [1, 2, 4] |

## (user, show) pairs surviving candidate thresholds, per window

watch_sec = total seconds over all airings and weeks in the window; frac = best single-airing fraction in the window (frac_max). Thresholds are illustrations only; none is applied.

| win | any_overlap | sec>=60 | sec>=300 | frac>=10% | frac>=25% | users_any | shows_any |
|---|---|---|---|---|---|---|---|
| 11-20 | 856904 | 842385 | 582187 | 461969 | 315719 | 4841 | 2973 |
| 11-30 | 1371685 | 1350626 | 963229 | 777443 | 553200 | 4895 | 4363 |
| 21-30 | 659890 | 650382 | 479414 | 399511 | 297959 | 4806 | 3231 |

## Test users (1,260 in submission.csv) with ZERO labelled (user, show) pairs at each threshold

| win | any_overlap | sec>=60 | sec>=300 | frac>=10% | frac>=25% |
|---|---|---|---|---|---|
| 11-20 | 10 | 10 | 10 | 10 | 11 |
| 11-30 | 2 | 2 | 2 | 2 | 3 |
| 21-30 | 14 | 14 | 14 | 14 | 14 |
