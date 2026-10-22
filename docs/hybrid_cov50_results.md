# Hybrid on cov50 labels: candidate generation + LightGBM re-ranker

Produced by `python -m src.hybrid --cov-target` on 2026-10-22 17:34. Validation on the 1260 test users (history weeks 11-20, target weeks 21-30, same pool and fallback as all methods). Re-ranker trained on 3589 non-test users (142938 candidate rows). Candidates: top-20 of repeat_cov, popularity, ALS, slot lists (38.8 per test user).

## Candidate recall (cov50 target, test users)

| top-N per source | candidates per user | recall of target top-5 |
|---|---|---|
| 5 | 10.5 | 0.5841 |
| 10 | 20.8 | 0.6890 |
| 20 | 38.8 | 0.7570 |
| 50 | 89.8 | 0.8291 |

## Re-ranker grid

| params | select | cov50 | n_days | n_airings | watch_sec |
|---|---|---|---|---|---|
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 208, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4271 | 0.4271 | 0.4226 | 0.4433 | 0.2674 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 72, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4261 | 0.4261 | 0.4221 | 0.4436 | 0.2666 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 104, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4255 | 0.4255 | 0.4190 | 0.4430 | 0.2697 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 350, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4254 | 0.4254 | 0.4303 | 0.4498 | 0.2757 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 115, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4248 | 0.4248 | 0.4312 | 0.4504 | 0.2768 |
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 239, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4240 | 0.4240 | 0.4318 | 0.4507 | 0.2760 |
| `{'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 84, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4237 | 0.4237 | 0.4303 | 0.4489 | 0.2754 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 134, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4234 | 0.4234 | 0.4182 | 0.4406 | 0.2690 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 61, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4231 | 0.4231 | 0.4191 | 0.4389 | 0.2653 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 277, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4225 | 0.4225 | 0.4176 | 0.4396 | 0.2702 |
| `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 38, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4222 | 0.4222 | 0.4196 | 0.4392 | 0.2649 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 78, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` | 0.4221 | 0.4221 | 0.4169 | 0.4404 | 0.2671 |

## Temporal check (trained on weeks 11-15 -> 16-20, no label from weeks 21-30)

| params | select | cov50 | n_days | n_airings | watch_sec |
|---|---|---|---|---|---|
| `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'n_trees': 334, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4143 | 0.4143 | 0.4330 | 0.4454 | 0.2764 |
| `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 68, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4161 | 0.4161 | 0.4238 | 0.4385 | 0.2626 |
| `{'objective': 'lambdarank_top5', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 146, 'n_cand': 20, 'train': 'weeks 11-15 -> 16-20, non-test users'}` | 0.4147 | 0.4147 | 0.4227 | 0.4374 | 0.2705 |

Selected: `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 208, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}` (select 0.4271); old loyalty repeat (tuned on n_days) 0.3602. Clearly better (>= best repeat on cov50 + 0.01 and temporal check above it (repeat 0.4080)): True. Final config (objective with the best temporal check): `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 208, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`. Submission: hybrid_v2.csv: format OK.

Total runtime: 110.4 s.
