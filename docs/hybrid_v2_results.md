# Hybrid v2 (slot habits): candidate generation + LightGBM re-ranker

Produced by `python -m src.hybrid --slots` on 2026-10-22 17:20. Validation on the 1260 test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). Re-ranker trained on 3589 non-test users (182627 candidate rows). Candidates: top-20 of repeat, popularity, ALS, channel, slot lists (48.4 per test user).

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
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4748 | 0.4748 | 0.4639 | 0.3050 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 148, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4747 | 0.4747 | 0.4643 | 0.3036 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 173, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4729 | 0.4729 | 0.4646 | 0.3029 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 494, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4722 | 0.4722 | 0.4613 | 0.3067 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 369, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4714 | 0.4714 | 0.4623 | 0.3063 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 149, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4707 | 0.4707 | 0.4605 | 0.3059 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 216, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4707 | 0.4707 | 0.4627 | 0.3084 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 175, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4699 | 0.4699 | 0.4610 | 0.3066 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 446, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4698 | 0.4698 | 0.4610 | 0.3080 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 111, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4693 | 0.4693 | 0.4614 | 0.3007 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 91, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4671 | 0.4671 | 0.4595 | 0.3045 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 54, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4666 | 0.4666 | 0.4603 | 0.3011 |

## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)

| params | select | n_days | n_airings | watch_sec |
|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 481, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4651 | 0.4651 | 0.4559 | 0.2958 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 109, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4651 | 0.4651 | 0.4582 | 0.2939 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 142, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4632 | 0.4632 | 0.4562 | 0.2985 |

Selected: `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` (select 0.4748); repeat 0.4535. Clearly better (>= v1 + 0.01 on n_days in both runs (v1 main 0.4733, v1 temporal 0.4636)): False. Final config (objective with the best temporal check): `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`. Submission: not written (--no-submission).

Total runtime: 95.1 s.
