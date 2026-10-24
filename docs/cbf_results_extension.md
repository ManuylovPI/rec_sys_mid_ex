> **Superseded** (stage 4, any-overlap targets). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Content-based filtering: validation results

Produced by `python -m src.cbf --extend` on 2026-10-22 16:49. 8233 shows with metadata (schedule weeks <= 30); 6376 of 6376 pool shows have a vector. Already-watched shows are not filtered. Same harness and selection as repeat_v2.

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.1281 | 0.1286 | 0.1276 | 0.0886 | 0.1182 | 0.1159 | 0.0803 |
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 2.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.1199 | 0.1203 | 0.1195 | 0.0833 | 0.1112 | 0.1091 | 0.0762 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0335 | 0.0340 | 0.0331 | 0.0252 | 0.0330 | 0.0320 | 0.0268 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 2.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0227 | 0.0229 | 0.0225 | 0.0172 | 0.0235 | 0.0227 | 0.0201 |

Selected: `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` (select 0.1281).

Total runtime: 9.8 s.
