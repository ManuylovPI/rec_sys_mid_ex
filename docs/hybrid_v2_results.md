# Hybrid v2 (slot habits): candidate generation + LightGBM re-ranker

Produced by `python -m src.hybrid --slots` on 2026-10-22 17:10. Validation on the 1260 test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). Re-ranker trained on 3589 non-test users (182474 candidate rows). Candidates: top-20 of repeat, popularity, ALS, channel, slot lists (48.3 per test user).

## Candidate recall (days target, test users)

| top-N per source | candidates per user | recall of target top-5 |
|---|---|---|
| 5 | 12.2 | 0.6896 |
| 10 | 24.8 | 0.8022 |
| 20 | 48.3 | 0.8645 |
| 50 | 124.4 | 0.9142 |

## Re-ranker grid

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4756 | 0.4756 | 0.4628 | 0.3021 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 191, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4745 | 0.4745 | 0.4639 | 0.3056 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 133, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4741 | 0.4741 | 0.4613 | 0.3037 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 198, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4740 | 0.4740 | 0.4638 | 0.3009 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 471, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4739 | 0.4739 | 0.4638 | 0.3050 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 237, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4735 | 0.4735 | 0.4639 | 0.3022 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 119, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4732 | 0.4732 | 0.4607 | 0.3026 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 288, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4732 | 0.4732 | 0.4632 | 0.3043 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 126, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4730 | 0.4730 | 0.4625 | 0.3047 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 58, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4716 | 0.4716 | 0.4635 | 0.2976 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 291, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4714 | 0.4714 | 0.4616 | 0.3069 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 97, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4702 | 0.4702 | 0.4615 | 0.3039 |

## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 149, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4666 | 0.4666 | 0.4562 | 0.2949 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 101, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4698 | 0.4698 | 0.4606 | 0.2945 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 165, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4665 | 0.4665 | 0.4571 | 0.2986 |

Selected: `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` (select 0.4756); repeat 0.4566. Clearly better (>= v1 + 0.01 on n_days in both runs (v1 main 0.4733, v1 temporal 0.4636)): False. Final config (objective with the best temporal check): `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`. Submission: not written.

Total runtime: 93.1 s.
