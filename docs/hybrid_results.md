# Hybrid: candidate generation + LightGBM re-ranker

Produced by `python -m src.hybrid` on 2026-10-22 16:58. Validation on the 1260 test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). Re-ranker trained on 3589 non-test users (162291 candidate rows). Candidates: top-20 of repeat, popularity, ALS and channel lists (43.4 per test user).

## Candidate recall (days target, test users)

| top-N per source | candidates per user | recall of target top-5 |
|---|---|---|
| 5 | 11.0 | 0.6541 |
| 10 | 22.4 | 0.7728 |
| 20 | 43.4 | 0.8401 |
| 50 | 108.4 | 0.8902 |

## Re-ranker grid

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 363, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4660 | 0.4730 | 0.4590 | 0.3032 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 531, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4659 | 0.4732 | 0.4586 | 0.3052 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 189, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4656 | 0.4730 | 0.4582 | 0.3000 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 195, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4650 | 0.4733 | 0.4568 | 0.3036 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 248, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4645 | 0.4716 | 0.4575 | 0.3004 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 149, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4641 | 0.4722 | 0.4561 | 0.3017 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 169, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4638 | 0.4704 | 0.4573 | 0.3052 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 107, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4636 | 0.4698 | 0.4574 | 0.3022 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 99, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4632 | 0.4698 | 0.4565 | 0.2994 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 142, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4628 | 0.4697 | 0.4559 | 0.3043 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 62, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4607 | 0.4676 | 0.4538 | 0.2950 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 31, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4578 | 0.4637 | 0.4519 | 0.2970 |

## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 773, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4521 | 0.4585 | 0.4456 | 0.2888 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 218, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4581 | 0.4636 | 0.4526 | 0.2921 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 263, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4525 | 0.4580 | 0.4470 | 0.2932 |

Selected: `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 363, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` (select 0.4660); repeat 0.4499. Clearly beats repeat (>= +0.01 and temporal check above repeat): True. Submission: hybrid_v1.csv: format OK.

Total runtime: 93.3 s.
