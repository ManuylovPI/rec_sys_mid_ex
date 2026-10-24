> **Superseded** (stage 7-8, any-overlap n_days labels). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Hybrid re-ranker: feature importance

Produced by `python -m src.hybrid --slots` on 2026-10-22 17:20. Model: `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`.

| feature | gain share | splits |
|---|---|---|
| rep_rank | 0.4019 | 515 |
| slot_rank | 0.2278 | 668 |
| h_loyalty_score | 0.0369 | 356 |
| s_pop_users | 0.0322 | 387 |
| slot_score | 0.0228 | 443 |
| slot_hours | 0.0204 | 506 |
| als_rank | 0.0194 | 646 |
| u_n_shows | 0.0172 | 662 |
| ch_share | 0.0169 | 753 |
| u_sec_pw | 0.0160 | 643 |
| s_t_days_pw | 0.0153 | 372 |
| u_days_frac | 0.0152 | 596 |
| s_pop_days_pw | 0.0145 | 258 |
| chan_rank | 0.0136 | 409 |
| cbf_score | 0.0129 | 691 |
| als_score | 0.0127 | 676 |
| tod_fit | 0.0127 | 737 |
| s_t_airings_pw | 0.0120 | 451 |
| s_pop_sec_pw | 0.0098 | 303 |
| chan_score | 0.0098 | 466 |
| h_d_airings | 0.0073 | 306 |
| h_d_sec | 0.0062 | 321 |
| h_weeks_since_last | 0.0061 | 243 |
| repl_score | 0.0061 | 355 |
| h_sec_pw | 0.0056 | 363 |
| h_loyalty | 0.0054 | 293 |
| pop_rank | 0.0053 | 142 |
| s_hist_air_days_pw | 0.0053 | 246 |
| h_d_days | 0.0049 | 220 |
| s_category | 0.0047 | 117 |
| h_weeks_frac | 0.0017 | 74 |
| h_days_pw | 0.0016 | 112 |
| s_aired_in_hist | 0.0000 | 0 |
| s_no_view_hist | 0.0000 | 0 |
