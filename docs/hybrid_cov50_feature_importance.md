# Hybrid re-ranker: feature importance

Produced by `python -m src.hybrid --cov-target` on 2026-10-22 17:33. Model: `{'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 208, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`.

| feature | gain share | splits |
|---|---|---|
| slot_rank | 0.4474 | 151 |
| rc_rank | 0.1513 | 69 |
| cov30_rank | 0.0781 | 43 |
| s_channel | 0.0504 | 363 |
| s_pop_days_pw | 0.0323 | 66 |
| rep_rank | 0.0309 | 72 |
| rc_score | 0.0258 | 92 |
| s_t_airings_pw | 0.0258 | 114 |
| slot_score | 0.0257 | 140 |
| ch_share | 0.0118 | 172 |
| s_sched_ratio_airings | 0.0113 | 61 |
| cov50_rank | 0.0107 | 51 |
| als_rank | 0.0091 | 103 |
| u_n_shows | 0.0076 | 98 |
| u_days_frac | 0.0066 | 90 |
| cbf_score | 0.0061 | 111 |
| u_sec_pw | 0.0058 | 83 |
| cov50 | 0.0051 | 35 |
| cov80_rank | 0.0050 | 46 |
| repl_score | 0.0040 | 64 |
| cov30 | 0.0036 | 25 |
| chan_rank | 0.0035 | 39 |
| als_score | 0.0033 | 85 |
| chan_score | 0.0033 | 71 |
| cov80 | 0.0031 | 38 |
| tod_fit | 0.0031 | 77 |
| h_loyalty_score | 0.0029 | 46 |
| cov80_share | 0.0026 | 57 |
| h_d_days | 0.0026 | 40 |
| h_loyalty | 0.0026 | 55 |
| h_weeks_since_last | 0.0025 | 45 |
| slot_hours | 0.0022 | 53 |
| h_d_airings | 0.0019 | 43 |
| s_pop_users | 0.0018 | 36 |
| h_sec_pw | 0.0018 | 42 |
| s_sched_ratio_days | 0.0017 | 21 |
| pop_rank | 0.0014 | 13 |
| s_t_days_pw | 0.0013 | 23 |
| s_pop_sec_pw | 0.0013 | 18 |
| h_d_sec | 0.0012 | 27 |
| s_category | 0.0006 | 7 |
| h_days_pw | 0.0005 | 7 |
| s_hist_air_days_pw | 0.0004 | 10 |
| h_weeks_frac | 0.0004 | 10 |
| s_aired_in_hist | 0.0000 | 0 |
| s_no_view_hist | 0.0000 | 0 |
