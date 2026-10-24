# Continuous-view coverage of labelled airings

Generated 2026-10-24 12:38:34 on Windows-10-10.0.26200-SP0, Python 3.11.9, duckdb 2.0.0.

Produced by `python -m src.coverage`. Build time 3.3 s (merged), 3.5 s (raw views).

## Counts

| continuous_intervals | user_airing_pairs | max_cont_frac | min_week | max_week |
|---|---|---|---|---|
| 5441773 | 3014129 | 1 | 11 | 30 |

## Pairs reaching each coverage threshold (single continuous view vs summed views)

| threshold | continuous | summed |
|---|---|---|
| 0.3 | 1201815 | 1260335 |
| 0.5 | 879339 | 938140 |
| 0.7 | 660998 | 708972 |
| 0.8 | 573725 | 611760 |
| 0.9 | 496475 | 521370 |

## Merged continuous intervals vs raw single views: pairs reaching each threshold

Strict > as in the write-up's 'more than 50%'.

| threshold | merged_gt | raw_gt |
|---|---|---|
| 0.3 | 1201183 | 1193278 |
| 0.5 | 878863 | 869879 |
| 0.8 | 573399 | 562606 |
