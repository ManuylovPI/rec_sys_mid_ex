> **Superseded** (stage 5, any-overlap n_days labels). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Hybrid re-ranker: feature importance

Produced by `python -m src.hybrid` on 2026-10-22 16:58. Model: `{'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'n_trees': 363, 'n_cand': 20, 'train': 'weeks 11-20 -> 21-30, non-test users'}`.

| feature | gain share | splits |
|---|---|---|
| rep_rank | 0.4547 | 286 |
| h_loyalty_score | 0.0985 | 134 |
| h_d_airings | 0.0758 | 121 |
| s_pop_users | 0.0335 | 231 |
| h_d_days | 0.0329 | 102 |
| s_t_days_pw | 0.0306 | 195 |
| chan_rank | 0.0270 | 192 |
| als_rank | 0.0265 | 237 |
| ch_share | 0.0249 | 357 |
| h_d_sec | 0.0185 | 196 |
| als_score | 0.0169 | 259 |
| s_t_airings_pw | 0.0167 | 241 |
| tod_fit | 0.0142 | 312 |
| u_sec_pw | 0.0139 | 260 |
| s_pop_days_pw | 0.0133 | 127 |
| chan_score | 0.0128 | 198 |
| s_pop_sec_pw | 0.0128 | 178 |
| u_n_shows | 0.0125 | 258 |
| cbf_score | 0.0125 | 264 |
| h_weeks_since_last | 0.0110 | 106 |
| h_sec_pw | 0.0071 | 145 |
| s_hist_air_days_pw | 0.0066 | 112 |
| h_loyalty | 0.0066 | 151 |
| u_days_frac | 0.0062 | 160 |
| s_category | 0.0061 | 87 |
| pop_rank | 0.0033 | 67 |
| h_weeks_frac | 0.0026 | 38 |
| h_days_pw | 0.0023 | 68 |
| s_aired_in_hist | 0.0000 | 0 |
