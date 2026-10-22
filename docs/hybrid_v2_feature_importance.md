# Hybrid re-ranker: feature importance

Produced by `python -m src.hybrid --slots` on 2026-10-22 17:10. Model: `{'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'n_trees': 215, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`.

| feature | gain share | splits |
|---|---|---|
| rep_rank | 0.4050 | 592 |
| slot_rank | 0.2267 | 679 |
| h_loyalty_score | 0.0370 | 361 |
| s_pop_users | 0.0332 | 391 |
| slot_score | 0.0235 | 443 |
| als_rank | 0.0223 | 612 |
| slot_hours | 0.0195 | 509 |
| s_pop_days_pw | 0.0176 | 286 |
| u_n_shows | 0.0167 | 665 |
| u_sec_pw | 0.0158 | 635 |
| ch_share | 0.0154 | 702 |
| u_days_frac | 0.0146 | 664 |
| cbf_score | 0.0140 | 719 |
| chan_rank | 0.0140 | 420 |
| s_t_days_pw | 0.0139 | 379 |
| s_t_airings_pw | 0.0135 | 558 |
| tod_fit | 0.0113 | 681 |
| als_score | 0.0104 | 579 |
| s_pop_sec_pw | 0.0100 | 311 |
| chan_score | 0.0089 | 415 |
| h_d_airings | 0.0063 | 288 |
| h_d_days | 0.0058 | 213 |
| h_d_sec | 0.0058 | 321 |
| repl_score | 0.0058 | 349 |
| s_hist_air_days_pw | 0.0057 | 254 |
| h_sec_pw | 0.0056 | 360 |
| h_weeks_since_last | 0.0055 | 225 |
| h_loyalty | 0.0052 | 298 |
| s_category | 0.0047 | 134 |
| pop_rank | 0.0033 | 123 |
| h_weeks_frac | 0.0015 | 81 |
| h_days_pw | 0.0012 | 83 |
| s_aired_in_hist | 0.0000 | 0 |
| s_no_view_hist | 0.0000 | 0 |
