# Hybrid v3 (slot habits + coverage): candidate generation + LightGBM re-ranker

Produced by `python -m src.hybrid --coverage` on 2026-10-22 17:22. Validation on the 1260 test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). Re-ranker trained on 3589 non-test users (182627 candidate rows). Candidates: top-20 of repeat, popularity, ALS, channel, slot lists (48.4 per test user).

## Candidate recall (days target, test users)

| top-N per source | candidates per user | recall of target top-5 |
|---|---|---|
| 5 | 12.2 | 0.6873 |
| 10 | 24.7 | 0.7975 |
| 20 | 48.4 | 0.8625 |
| 50 | 124.6 | 0.9136 |

## Re-ranker grid

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 275, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4762 | 0.4762 | 0.4650 | 0.3047 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 389, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4754 | 0.4754 | 0.4644 | 0.3049 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 145, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4743 | 0.4743 | 0.4631 | 0.3038 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 134, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4738 | 0.4738 | 0.4619 | 0.3057 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 134, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4733 | 0.4733 | 0.4629 | 0.3053 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 402, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4726 | 0.4726 | 0.4617 | 0.3075 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 328, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4725 | 0.4725 | 0.4625 | 0.3070 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 71, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4712 | 0.4712 | 0.4619 | 0.2998 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 227, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4706 | 0.4706 | 0.4622 | 0.3076 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 279, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4705 | 0.4705 | 0.4632 | 0.3083 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 161, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4688 | 0.4688 | 0.4618 | 0.3072 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 261, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4681 | 0.4681 | 0.4624 | 0.3092 |

## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 173, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4575 | 0.4575 | 0.4497 | 0.2946 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 139, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4620 | 0.4620 | 0.4548 | 0.2965 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 279, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4493 | 0.4493 | 0.4401 | 0.2921 |

Selected: `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 275, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` (select 0.4762); repeat 0.4535. Clearly better (>= hybrid v2 (fixed data) + 0.01 on n_days in both runs (v2 main 0.4748, v2 temporal 0.4651)): False. Final config (objective with the best temporal check): `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 275, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`. Submission: not written.

Total runtime: 114.2 s.
