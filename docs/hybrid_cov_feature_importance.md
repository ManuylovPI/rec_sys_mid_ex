# Hybrid re-ranker: feature importance

Produced by `python -m src.hybrid --coverage` on 2026-10-22 17:22. Model: `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 275, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`.

| feature | gain share | splits |
|---|---|---|
| rep_rank | 0.4006 | 185 |
| slot_rank | 0.2165 | 226 |
| h_loyalty_score | 0.1114 | 126 |
| s_pop_users | 0.0431 | 87 |
| s_channel | 0.0392 | 547 |
| slot_hours | 0.0211 | 138 |
| chan_rank | 0.0189 | 83 |
| als_rank | 0.0175 | 144 |
| ch_share | 0.0110 | 219 |
| u_n_shows | 0.0098 | 136 |
| u_days_frac | 0.0093 | 164 |
| s_sched_ratio_airings | 0.0078 | 69 |
| u_sec_pw | 0.0070 | 105 |
| cbf_score | 0.0067 | 171 |
| s_t_days_pw | 0.0063 | 72 |
| s_pop_sec_pw | 0.0060 | 56 |
| s_sched_ratio_days | 0.0060 | 79 |
| slot_score | 0.0053 | 77 |
| h_weeks_since_last | 0.0051 | 77 |
| h_d_airings | 0.0047 | 63 |
| cov80_rank | 0.0045 | 49 |
| s_pop_days_pw | 0.0045 | 37 |
| tod_fit | 0.0044 | 149 |
| chan_score | 0.0041 | 105 |
| als_score | 0.0039 | 109 |
| s_t_airings_pw | 0.0038 | 45 |
| h_d_days | 0.0030 | 44 |
| h_d_sec | 0.0027 | 64 |
| repl_score | 0.0021 | 72 |
| h_loyalty | 0.0020 | 53 |
| h_weeks_frac | 0.0018 | 22 |
| cov80_share | 0.0017 | 59 |
| s_hist_air_days_pw | 0.0015 | 19 |
| h_sec_pw | 0.0015 | 53 |
| pop_rank | 0.0014 | 22 |
| cov30 | 0.0010 | 37 |
| cov80 | 0.0010 | 34 |
| cov50 | 0.0007 | 26 |
| s_category | 0.0005 | 7 |
| h_days_pw | 0.0005 | 20 |
| s_aired_in_hist | 0.0000 | 0 |
| s_no_view_hist | 0.0000 | 0 |
