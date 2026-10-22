# repeat_cont (write-up's Algorithm 1, re-implemented)

Produced by `python -m src.repeat_cont` on 2026-10-22 17:24. History weeks 11-20, target weeks 21-30, pool 6376 shows, shared popularity fallback. MAP@5. Targets: n_days, and cont50 / cont80 = top-5 by number of target airings with one continuous view covering > 50% / > 80%.

Test users with a non-empty ground truth: n_days 1246, cont50 1244, cont80 1236.

| method | params | test_users: n_days | test_users: cont50 | test_users: cont80 | active_both: n_days | active_both: cont50 | active_both: cont80 |
|---|---|---|---|---|---|---|---|
| popularity | `{'n_weeks': 10}` | 0.3167 | 0.2752 | 0.2600 | 0.2749 | 0.2374 | 0.2284 |
| repeat_v1 | `{'half_life': 8, 'transform': 'log', 'alpha': 0.0}` | 0.4108 | 0.3335 | 0.3015 | 0.3565 | 0.2897 | 0.2675 |
| repeat_v2 | `{'beta': 10, 'delta': 1.0, 'fill': 'channels_m3', 'half_life': 8, 'score': 'loyalty', 'threshold': 'none', 'unit': 'n_days'}` | 0.4535 | 0.3602 | 0.3257 | 0.3908 | 0.3125 | 0.2892 |
| repeat_cont30 | `{'cut': 0.3, 'tie': 'pop', 'history': 'whole window, no decay'}` | 0.3897 | 0.3864 | 0.3570 | 0.3419 | 0.3332 | 0.3166 |
| repeat_cont30 | `{'cut': 0.3, 'tie': 'id', 'history': 'whole window, no decay'}` | 0.3816 | 0.3835 | 0.3535 | 0.3345 | 0.3295 | 0.3133 |
| repeat_cont50 | `{'cut': 0.5, 'tie': 'pop', 'history': 'whole window, no decay'}` | 0.3690 | 0.3841 | 0.3583 | 0.3265 | 0.3288 | 0.3157 |
| repeat_cont50 | `{'cut': 0.5, 'tie': 'id', 'history': 'whole window, no decay'}` | 0.3609 | 0.3795 | 0.3533 | 0.3177 | 0.3236 | 0.3110 |
| repeat_cont80 | `{'cut': 0.8, 'tie': 'pop', 'history': 'whole window, no decay'}` | 0.3432 | 0.3679 | 0.3502 | 0.3024 | 0.3137 | 0.3067 |
| repeat_cont80 | `{'cut': 0.8, 'tie': 'id', 'history': 'whole window, no decay'}` | 0.3309 | 0.3615 | 0.3431 | 0.2905 | 0.3063 | 0.2996 |

Submission repeat_cont50.csv (cut 0.5, pop tie-break, refit on weeks 11-30): format OK; 40 of 6300 slots filled by the popularity fallback.

Total runtime: 7.9 s.

## What each target hypothesis predicts for repeat_cont50.csv on Kaggle (written before submitting)

For each target, LB is fitted as one scale factor times validation MAP@5 over the three submitted configs (popularity_v1, repeat_v1, repeat_v2; public / private LB from submissions/LOG.md), and the factor is applied to repeat_cont50's validation score. Rough: three related points, and the validation configs are the fixed-data re-runs (repeat_v2 row = currently selected repeat config, which differs slightly from the submitted v2).

| target hypothesis | scale public | predicted public | scale private | predicted private |
|---|---|---|---|---|
| n_days | 0.809 | 0.298 | 0.767 | 0.283 |
| cont50 | 0.989 | 0.380 | 0.938 | 0.360 |
| cont80 | 1.081 | 0.387 | 1.026 | 0.368 |

The write-up reports 0.41296 public for its own version of this baseline. Our implementation may differ in details the description does not fix (what counts as one sitting, tie-break, popularity definition).
