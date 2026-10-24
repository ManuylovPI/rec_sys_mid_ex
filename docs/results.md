# Results (one data version, one label)

Produced by `python -m src.report_tables` on 2026-10-24 13:00. Data after the time-zone fix (docs/errata.md). Validation: history weeks 11-20, target weeks 21-30, the 1,260 test users, pool = 6376 labelled shows airing in weeks 21-30, repeats allowed, shared popularity fallback. MAP@5. Main target cov50 (airings where one continuous view covers > 50% of the airing); cov80 (> 80%) and n_days (the earlier any-overlap target) for comparison. Temporal check = the same re-ranker trained only on labels before week 21; methods without label-trained parameters have none. Runtime = wall-clock seconds for fitting and scoring on this machine (docs/environment.md); for the two hybrids it includes the temporal check and the regeneration of the submission file.

| method | configuration | cov50 | cov80 | n_days | temporal cov50 | temporal cov80 | runtime (s) |
|---|---|---|---|---|---|---|---|
| popularity | watch seconds, last 10 history weeks | 0.2752 | 0.2600 | 0.3167 | – | – | 0 |
| ALS | implicit ALS, BM25, 8 factors, alpha 0.3 | 0.2528 | 0.2380 | 0.2927 | – | – | 1 |
| CBF | TF-IDF metadata, people weight 4 | 0.1154 | 0.1068 | 0.1276 | – | – | 2 |
| repeat_cont50 | count of > 50% continuous watches (write-up Algorithm 1) | 0.3841 | 0.3583 | 0.3690 | – | – | 0 |
| repeat_cov | > 30% watches, half-life 4, loyalty beta 10, min 3 watches | 0.4080 | 0.3748 | 0.4020 | – | – | 1 |
| slot habits | channel x weekday/weekend x hour affinity | 0.4015 | 0.3710 | 0.4041 | – | – | 2 |
| hybrid_v2 setup | LightGBM lambdarank, 1 fold, top-20 candidates, cov50 labels | 0.4263 | 0.3928 | 0.4228 | 0.4172 | 0.3872 | 60 |
| final (hybrid_v4_cov80) | LightGBM lambdarank + binary x 3 seeds, 5 recency-weighted folds, cov80 labels | 0.4265 | 0.3977 | 0.4154 | 0.4229 | 0.3940 | 1263 |

## Reproducibility of the submitted hybrids

- hybrid_v2.csv: regenerated file identical in 688 of 1260 rows, item overlap 0.9540, format OK
- hybrid_v4_cov80.csv: regenerated file identical in 824 of 1260 rows, item overlap 0.9686, format OK

Total runtime: 1333.0 s.
