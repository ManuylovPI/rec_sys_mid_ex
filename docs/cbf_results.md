> **Superseded** (stage 4, any-overlap targets). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Content-based filtering: validation results

Produced by `python -m src.cbf` on 2026-10-22 16:48. 8233 shows with metadata (schedule weeks <= 30); 6376 of 6376 pool shows have a vector. Already-watched shows are not filtered. Same harness and selection as repeat_v2.

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 1.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.1055 | 0.1056 | 0.1054 | 0.0746 | 0.0975 | 0.0961 | 0.0688 |
| cbf | `{'rep': 'tfidf', 'min_df': 5, 'people_weight': 1.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0862 | 0.0863 | 0.0860 | 0.0627 | 0.0816 | 0.0809 | 0.0599 |
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 0.5, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0800 | 0.0799 | 0.0800 | 0.0585 | 0.0762 | 0.0755 | 0.0565 |
| cbf | `{'rep': 'tfidf', 'min_df': 5, 'people_weight': 0.5, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0665 | 0.0667 | 0.0662 | 0.0479 | 0.0642 | 0.0637 | 0.0484 |
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 1.0, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0201 | 0.0196 | 0.0206 | 0.0162 | 0.0237 | 0.0238 | 0.0206 |
| cbf | `{'rep': 'tfidf', 'min_df': 5, 'people_weight': 1.0, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0149 | 0.0146 | 0.0153 | 0.0111 | 0.0165 | 0.0167 | 0.0140 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 1.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0132 | 0.0133 | 0.0131 | 0.0098 | 0.0162 | 0.0157 | 0.0136 |
| cbf | `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 0.5, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0124 | 0.0120 | 0.0128 | 0.0090 | 0.0134 | 0.0136 | 0.0114 |
| cbf | `{'rep': 'onehot', 'min_df': 5, 'people_weight': 1.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0124 | 0.0127 | 0.0122 | 0.0092 | 0.0149 | 0.0145 | 0.0129 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 0.5, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0100 | 0.0101 | 0.0099 | 0.0075 | 0.0128 | 0.0123 | 0.0110 |
| cbf | `{'rep': 'onehot', 'min_df': 5, 'people_weight': 0.5, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0098 | 0.0098 | 0.0097 | 0.0073 | 0.0123 | 0.0120 | 0.0108 |
| cbf | `{'rep': 'tfidf', 'min_df': 5, 'people_weight': 0.5, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0087 | 0.0086 | 0.0088 | 0.0061 | 0.0100 | 0.0103 | 0.0084 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 1.0, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0025 | 0.0027 | 0.0024 | 0.0014 | 0.0031 | 0.0030 | 0.0027 |
| cbf | `{'rep': 'onehot', 'min_df': 5, 'people_weight': 0.5, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0022 | 0.0025 | 0.0020 | 0.0012 | 0.0026 | 0.0025 | 0.0020 |
| cbf | `{'rep': 'onehot', 'min_df': 2, 'people_weight': 0.5, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0022 | 0.0024 | 0.0020 | 0.0011 | 0.0023 | 0.0022 | 0.0019 |
| cbf | `{'rep': 'onehot', 'min_df': 5, 'people_weight': 1.0, 'profile': 'log', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` | 0.0022 | 0.0024 | 0.0019 | 0.0011 | 0.0027 | 0.0027 | 0.0023 |

Selected: `{'rep': 'tfidf', 'min_df': 2, 'people_weight': 1.0, 'profile': 'linear', 'max_actors': 5, 'profile_unit': 'n_days_hl8'}` (select 0.1055).

Total runtime: 27.1 s.
