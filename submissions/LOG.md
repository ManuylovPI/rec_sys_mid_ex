# Submission log

Kaggle scores are filled in by hand after submitting.

| file | method | date | public score | private score | kaggle name |
| --- | --- | --- | --- | --- | --- |
| popularity_v1.csv | popularity, n_weeks=10 (weeks 21-30); fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 | 0.255 | 0.244 | submission (2).csv |
| repeat_v1.csv | repeat, {'half_life': 8, 'transform': 'log', 'alpha': 0.0}, fallback popularity n_weeks=10; fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 | 0.332 | 0.314 | submission.csv |
| repeat_v2.csv | repeat_v2, {'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}, fallback popularity n_weeks=10; fit weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 | 0.36752 | 0.348 | submission (3).csv |
| hybrid_v1.csv | hybrid LightGBM re-ranker {'min_child_samples': 100, 'n_cand': 20, 'n_trees': 189, 'num_leaves': 15, 'objective': 'lambdarank_log', 'train': 'weeks 11-20 -> 21-30, non-test users'}; trained weeks 11-20 -> 21-30 on all users with 189 trees; features weeks 11-30, pool = labelled shows airing weeks 31-42 | 2026-10-22 |  |  |  |
| repeat_cont50.csv | repeat_cont: top-5 by number of airings with one continuous view covering > 50%, weeks 11-30, no decay, ties by popularity, fallback popularity n_weeks=10; pool = labelled shows airing weeks 31-42 (re-implementation of the write-up's Algorithm 1 from its description) | 2026-10-22 |  |  |  |
