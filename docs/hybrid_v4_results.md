# Hybrid v4 (cov50 target)

Produced by `python -m src.hybrid_v4` on 2026-10-24 11:15. Validation: 1,260 test users, features weeks 11-20, cov50 target weeks 21-30; temporal check = same model trained only on folds with labels before week 21. Previous final hybrid_v2: main 0.4271, temporal 0.4161 (docs/hybrid_cov50_results.md).

## Step 0: repeat_cov widened

Previous best 0.4080, widened best 0.4080: `{'cut': 0.3, 'half_life': 4, 'min_count': 3, 'scale': 'loyalty10', 'source': 'merged', 'tie': 'pop', 'unit': 'airings'}`.

## Candidate recall (cov50, test users, 7 sources)

| top-N per source | candidates per user | recall |
|---|---|---|
| 20 | 49.5 | 0.7740 |
| 50 | 121.2 | 0.8387 |
| 100 | 249.4 | 0.8738 |

## Models (main = trained on folds incl. 11-20 -> 21-30 of non-test users; temporal = earlier folds only)

| kind | params | main cov50 | main n_days | temporal cov50 | temporal n_days |
|---|---|---|---|---|---|
| model | `{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [119], 'n_cand': 50}` | 0.4275 | 0.4245 | 0.4203 | 0.4223 |
| model | `{'setup': 'stacked', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [363], 'n_cand': 50}` | 0.4275 | 0.4253 | 0.4219 | 0.4218 |
| model | `{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 100, 'seeds': [42], 'n_trees': [122], 'n_cand': 50}` | 0.4266 | 0.4241 | 0.4196 | 0.4198 |
| model | `{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [66], 'n_cand': 50}` | 0.4272 | 0.4233 | 0.4200 | 0.4187 |
| model | `{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 63, 'min_child_samples': 100, 'seeds': [42], 'n_trees': [14], 'n_cand': 50}` | 0.4193 | 0.4178 | 0.4201 | 0.4188 |
| model | `{'setup': 'single', 'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [232], 'n_cand': 50}` | 0.4218 | 0.4274 | 0.4121 | 0.4232 |
| model | `{'setup': 'single', 'objective': 'binary', 'num_leaves': 15, 'min_child_samples': 100, 'seeds': [42], 'n_trees': [308], 'n_cand': 50}` | 0.4213 | 0.4261 | 0.4157 | 0.4249 |
| model | `{'setup': 'single', 'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [205], 'n_cand': 50}` | 0.4225 | 0.4259 | 0.4159 | 0.4282 |
| model | `{'setup': 'single', 'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'seeds': [42], 'n_trees': [119], 'n_cand': 50}` | 0.4235 | 0.4285 | 0.4209 | 0.4331 |
| model | `{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42, 43, 44], 'n_trees': [119, 208, 152], 'n_cand': 50}` | 0.4271 | 0.4236 | 0.4204 | 0.4204 |
| model | `{'setup': 'single', 'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'seeds': [42, 43, 44], 'n_trees': [119, 123, 159], 'n_cand': 50}` | 0.4239 | 0.4292 | 0.4216 | 0.4326 |
| ensemble | `{'ensemble': 'lambdarank x3 seeds + binary x3 seeds', 'members': [{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42, 43, 44], 'n_trees': [119, 208, 152], 'n_cand': 50}, {'setup': 'single', 'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'seeds': [42, 43, 44], 'n_trees': [119, 123, 159], 'n_cand': 50}]}` | 0.4272 | 0.4278 | 0.4228 | 0.4284 |
| ensemble | `{'ensemble': 'lambdarank + binary, 1 seed', 'members': [{'setup': 'single', 'objective': 'lambdarank_log', 'num_leaves': 15, 'min_child_samples': 20, 'seeds': [42], 'n_trees': [119], 'n_cand': 50}, {'setup': 'single', 'objective': 'binary', 'num_leaves': 63, 'min_child_samples': 100, 'seeds': [42], 'n_trees': [119], 'n_cand': 50}]}` | 0.4262 | 0.4283 | 0.4225 | 0.4303 |

## Submission files (ranked by main validation)

| file | main cov50 | temporal cov50 | check |
|---|---|---|---|
| hybrid_v3_lr | 0.4275 | 0.4203 | hybrid_v3_lr.csv: format OK |
| hybrid_v3_ens | 0.4272 | 0.4228 | hybrid_v3_ens.csv: format OK |
| hybrid_v3_lr_seeds | 0.4271 | 0.4204 | hybrid_v3_lr_seeds.csv: format OK |

Total runtime: 783.0 s.
