# Components re-scored after the time-zone fix

Produced by `python -m src.refresh` on 2026-10-22 17:17. Test users, MAP@5 on n_days (selection target). `before` = value on the shifted day counts (docs/errata.md).

| method | params after | n_days before | n_days after | n_airings after | watch_sec after |
|---|---|---|---|---|---|
| popularity | `{'n_weeks': 10}` | 0.3174 | 0.3167 | 0.3100 | 0.1799 |
| repeat | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4566 | 0.4535 | 0.4422 | 0.2940 |
| als | `{'alpha': 0.3, 'bm25_b': 0.8, 'bm25_k1': 100, 'conf': 'n_days_hl8', 'factors': 8, 'iters': 15, 'reg': 0.01, 'weighting': 'bm25'}` | 0.2998 | 0.2927 | 0.2911 | 0.1818 |
| cbf | `{'max_actors': 5, 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'profile_unit': 'n_days_hl8', 'rep': 'tfidf'}` | 0.1286 | 0.1276 | 0.1265 | 0.0882 |
| slot habits | `{'agg': 'airings', 'daytype': 'we2', 'half_life': 8, 'model': 'slot'}` | 0.4048 | 0.4041 | 0.4240 | 0.2637 |

## Repeat re-selection grid (n_days, test users)

| params | n_days |
|---|---|
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4535 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4534 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4527 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4511 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4476 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4470 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4455 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4417 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4374 |
| `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4367 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4367 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4332 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4325 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4305 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4253 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4205 |
| `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4153 |

Total runtime: 18.5 s.
