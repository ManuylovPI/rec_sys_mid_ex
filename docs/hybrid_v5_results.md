# Hybrid v5: recency-weighted folds and cov80 labels

Produced by `python -m src.hybrid_v5` on 2026-10-24 12:03. Validation: 1,260 test users, features weeks 11-20, targets in weeks 21-30. main = folds C, B, D, E, G (test users removed from folds whose target overlaps weeks 21-30); temporal = folds A, C only. Fold weights (half-life 4 weeks on the first target week): main {'C': 0.1767766952966369, 'B': 0.29730177875068026, 'D': 0.42044820762685725, 'E': 0.7071067811865476, 'G': 1.0}, temporal {'A': 0.7071067811865476, 'C': 1.0}.

Reference: hybrid_v3_ens (one fold per run, cov50 labels) main cov50 0.4272, temporal cov50 0.4228; leaderboard 0.457 public / 0.442 private.

| model | label | run | cov50 | cov80 | n_days |
|---|---|---|---|---|---|
| hybrid_v4_recent | cov50 | main | 0.4270 | 0.3930 | 0.4261 |
| hybrid_v4_recent | cov50 | temporal | 0.4243 | 0.3916 | 0.4293 |
| label probe (1 lambdarank) | cov80 | main | 0.4242 | 0.3955 | 0.4096 |
| label probe (1 lambdarank) | cov80 | temporal | 0.4189 | 0.3918 | 0.4066 |
| label probe (1 lambdarank) | combo | main | 0.4247 | 0.3944 | 0.4144 |
| label probe (1 lambdarank) | combo | temporal | 0.4197 | 0.3905 | 0.4080 |
| hybrid_v4_cov80 | cov80 | main | 0.4270 | 0.3974 | 0.4136 |
| hybrid_v4_cov80 | cov80 | temporal | 0.4210 | 0.3930 | 0.4119 |

Label used for hybrid_v4_cov80: cov80 (higher temporal-check cov80 score of the probe).

Submission files: hybrid_v4_recent.csv: format OK; hybrid_v4_cov80.csv: format OK.

Total runtime: 2285.1 s.
