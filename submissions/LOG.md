# Submission log

Kaggle scores are filled in by hand after submitting.

| file | method | date | public score | private score |
| --- | --- | --- | --- | --- |
| popularity_v1.csv | popularity, n_weeks=10 (weeks 21-30); fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 | 0.255 | 0.244 |
| repeat_v1.csv | repeat, {'half_life': 8, 'transform': 'log', 'alpha': 0.0}, fallback popularity n_weeks=10; fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 | 0.332 | 0.314 |
| repeat_v2.csv | repeat_v2, {'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}, fallback popularity n_weeks=10; fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 |  |  |
