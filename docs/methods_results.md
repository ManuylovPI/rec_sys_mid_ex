# Method comparison (validation)

Produced by `python -m src.compare_methods` on 2026-10-22 17:06. History weeks 11-20, target weeks 21-30, pool = 6376 labelled shows airing in weeks 21-30, repeats allowed, shared fallback = popularity (watch seconds, last 10 history weeks). MAP@5; `select` = mean of n_days and n_airings targets on the 1260 test users. Selection scores were checked against the logged grid runs.

## Accuracy

| method | select | test: n_days | test: n_airings | test: watch_sec | active_both: n_days | active_both: n_airings | already watched | no-history ids | users with a no-history id |
|---|---|---|---|---|---|---|---|---|---|
| popularity | 0.3174 | 0.3174 | 0.3100 | 0.1799 | 0.2769 | 0.2706 | 0.8792 | 0.0000 | 0.0000 |
| repeat | 0.4566 | 0.4566 | 0.4432 | 0.2947 | 0.3932 | 0.3855 | 0.9905 | 0.0000 | 0.0000 |
| als | 0.2998 | 0.2998 | 0.2927 | 0.1832 | 0.2677 | 0.2675 | 0.9195 | 0.0000 | 0.0000 |
| cbf | 0.1286 | 0.1286 | 0.1276 | 0.0886 | 0.1182 | 0.1159 | 0.6352 | 0.1406 | 0.5198 |

`already watched` and `no-history ids` are shares of all recommended ids (5 per test user); the last column is the share of test users with at least one no-history id in their top-5.

## Complementarity with repeat (test users)

| method | target | GT shows hit | hit and not in repeat top-5 | hit by method or repeat |
|---|---|---|---|---|
| popularity | n_days | 0.3883 | 0.0771 | 0.5998 |
| popularity | n_airings | 0.3769 | 0.0726 | 0.5821 |
| repeat | n_days | 0.5227 | 0.0000 | 0.5227 |
| repeat | n_airings | 0.5096 | 0.0000 | 0.5096 |
| als | n_days | 0.3819 | 0.0631 | 0.5858 |
| als | n_airings | 0.3742 | 0.0621 | 0.5717 |
| cbf | n_days | 0.2255 | 0.0220 | 0.5447 |
| cbf | n_airings | 0.2226 | 0.0210 | 0.5306 |

Shares are over all ground-truth target shows of the test users (up to 5 per user).

## Selected parameters

- popularity: `{'n_weeks': 10}`
- repeat: `{'beta': 10, 'delta': 1.0, 'fill': 'channels_m3', 'half_life': 8, 'score': 'loyalty', 'threshold': 'none', 'unit': 'n_days'}`
- als: `{'alpha': 0.3, 'bm25_b': 0.8, 'bm25_k1': 100, 'conf': 'n_days_hl8', 'factors': 8, 'iters': 15, 'reg': 0.01, 'weighting': 'bm25'}`
- cbf: `{'max_actors': 5, 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'profile_unit': 'n_days_hl8', 'rep': 'tfidf'}`

Total runtime: 7.9 s.

## Hybrid vs components (test users)

Produced by `python -m src.hybrid --coverage`. Components from experiments.csv (rows on the fixed data where available, docs/errata.md); hybrid = best re-ranker (trained on non-test users, weeks 11-20 -> 21-30) and its temporal check (trained on weeks 11-15 -> 16-20).

| method | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| popularity | 0.3167 | 0.3167 | 0.3100 | 0.1799 |
| repeat | 0.4535 | 0.4535 | 0.4422 | 0.2940 |
| als | 0.2927 | 0.2927 | 0.2911 | 0.1818 |
| cbf | 0.1276 | 0.1276 | 0.1265 | 0.0882 |
| slot habits | 0.4041 | 0.4041 | 0.4240 | 0.2637 |
| hybrid v2 (+ slot habits), before tz fix | 0.4756 | 0.4756 | 0.4628 | 0.3021 |
| hybrid v2, temporal check, before tz fix | 0.4698 | 0.4698 | 0.4606 | 0.2945 |
| hybrid v2 (+ slot habits), fixed data | 0.4748 | 0.4748 | 0.4639 | 0.3050 |
| hybrid v2, temporal check, fixed data | 0.4651 | 0.4651 | 0.4582 | 0.2939 |
| hybrid v3 (+ coverage, schedule change, channel) | 0.4762 | 0.4762 | 0.4650 | 0.3047 |
| hybrid v3, temporal check | 0.4620 | 0.4620 | 0.4548 | 0.2965 |
