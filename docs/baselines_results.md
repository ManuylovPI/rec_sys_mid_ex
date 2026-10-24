> **Superseded** (stage 2, any-overlap targets, selection on the mean of three any-overlap targets). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Baselines: validation results

Produced by `python -m src.baselines` on 2026-10-22 16:23. History weeks 11-20, target weeks 21-30, pool = 6376 labelled shows airing in weeks 21-30. Populations: test_users = 1260, active_both = 4752 (labelled interactions in both windows). MAP@5; users with empty ground truth count as 0. `select` = mean over the three targets on test_users.

Ground-truth users with a non-empty top-5 (any population): watch_sec 4806, n_days 4806, n_airings 4806; test users with empty ground truth: 14.

| method | params | select | test_users/watch_sec | test_users/n_days | test_users/n_airings | active_both/watch_sec | active_both/n_days | active_both/n_airings |
|---|---|---|---|---|---|---|---|---|
| popularity | `{'n_weeks': 10}` | 0.2691 | 0.1799 | 0.3174 | 0.3100 | 0.1563 | 0.2769 | 0.2706 |
| popularity | `{'n_weeks': 4}` | 0.2684 | 0.1850 | 0.3165 | 0.3037 | 0.1620 | 0.2777 | 0.2669 |
| popularity | `{'n_weeks': 2}` | 0.2615 | 0.1886 | 0.3062 | 0.2897 | 0.1664 | 0.2695 | 0.2559 |
| popularity | `{'n_weeks': 1}` | 0.2191 | 0.1645 | 0.2574 | 0.2353 | 0.1465 | 0.2298 | 0.2120 |
| repeat | `{'half_life': 8, 'transform': 'log', 'alpha': 0.0}` | 0.3731 | 0.2988 | 0.4142 | 0.4062 | 0.2541 | 0.3577 | 0.3527 |
| repeat | `{'half_life': None, 'transform': 'log', 'alpha': 0.0}` | 0.3705 | 0.2974 | 0.4106 | 0.4036 | 0.2514 | 0.3556 | 0.3519 |
| repeat | `{'half_life': 4, 'transform': 'log', 'alpha': 0.0}` | 0.3680 | 0.2968 | 0.4080 | 0.3990 | 0.2528 | 0.3533 | 0.3473 |
| repeat | `{'half_life': 4, 'transform': 'raw', 'alpha': 0.5}` | 0.3560 | 0.3113 | 0.3797 | 0.3771 | 0.2626 | 0.3308 | 0.3306 |
| repeat | `{'half_life': 8, 'transform': 'raw', 'alpha': 0.5}` | 0.3558 | 0.3093 | 0.3799 | 0.3783 | 0.2611 | 0.3325 | 0.3328 |
| repeat | `{'half_life': None, 'transform': 'raw', 'alpha': 0.5}` | 0.3542 | 0.3072 | 0.3785 | 0.3771 | 0.2588 | 0.3315 | 0.3321 |
| repeat | `{'half_life': 2, 'transform': 'log', 'alpha': 0.0}` | 0.3499 | 0.2884 | 0.3854 | 0.3759 | 0.2430 | 0.3312 | 0.3238 |
| repeat | `{'half_life': 8, 'transform': 'log', 'alpha': 0.5}` | 0.3470 | 0.2744 | 0.3827 | 0.3837 | 0.2379 | 0.3430 | 0.3461 |
| repeat | `{'half_life': 4, 'transform': 'log', 'alpha': 0.5}` | 0.3460 | 0.2747 | 0.3810 | 0.3821 | 0.2384 | 0.3424 | 0.3450 |
| repeat | `{'half_life': 2, 'transform': 'raw', 'alpha': 0.5}` | 0.3458 | 0.3075 | 0.3660 | 0.3639 | 0.2575 | 0.3188 | 0.3183 |
| repeat | `{'half_life': None, 'transform': 'log', 'alpha': 0.5}` | 0.3441 | 0.2718 | 0.3796 | 0.3810 | 0.2352 | 0.3399 | 0.3436 |
| repeat | `{'half_life': 2, 'transform': 'log', 'alpha': 0.5}` | 0.3398 | 0.2724 | 0.3725 | 0.3747 | 0.2345 | 0.3323 | 0.3337 |
| repeat | `{'half_life': 8, 'transform': 'raw', 'alpha': 1.0}` | 0.3360 | 0.2872 | 0.3586 | 0.3621 | 0.2420 | 0.3158 | 0.3199 |
| repeat | `{'half_life': 4, 'transform': 'raw', 'alpha': 1.0}` | 0.3356 | 0.2872 | 0.3584 | 0.3611 | 0.2428 | 0.3154 | 0.3191 |
| repeat | `{'half_life': 2, 'transform': 'raw', 'alpha': 1.0}` | 0.3339 | 0.2869 | 0.3565 | 0.3582 | 0.2425 | 0.3127 | 0.3156 |
| repeat | `{'half_life': None, 'transform': 'raw', 'alpha': 1.0}` | 0.3331 | 0.2849 | 0.3554 | 0.3589 | 0.2400 | 0.3136 | 0.3177 |
| repeat | `{'half_life': 1, 'transform': 'raw', 'alpha': 1.0}` | 0.3252 | 0.2821 | 0.3457 | 0.3479 | 0.2360 | 0.3008 | 0.3030 |
| repeat | `{'half_life': 1, 'transform': 'raw', 'alpha': 0.5}` | 0.3241 | 0.2905 | 0.3415 | 0.3403 | 0.2412 | 0.2927 | 0.2920 |
| repeat | `{'half_life': 8, 'transform': 'raw', 'alpha': 0.0}` | 0.3234 | 0.2989 | 0.3389 | 0.3325 | 0.2459 | 0.2887 | 0.2848 |
| repeat | `{'half_life': None, 'transform': 'raw', 'alpha': 0.0}` | 0.3226 | 0.2982 | 0.3370 | 0.3325 | 0.2461 | 0.2898 | 0.2872 |
| repeat | `{'half_life': 4, 'transform': 'raw', 'alpha': 0.0}` | 0.3172 | 0.2961 | 0.3313 | 0.3241 | 0.2423 | 0.2798 | 0.2751 |
| repeat | `{'half_life': 1, 'transform': 'log', 'alpha': 0.5}` | 0.3168 | 0.2566 | 0.3467 | 0.3471 | 0.2200 | 0.3066 | 0.3072 |
| repeat | `{'half_life': 1, 'transform': 'log', 'alpha': 0.0}` | 0.3057 | 0.2615 | 0.3314 | 0.3242 | 0.2145 | 0.2777 | 0.2716 |
| repeat | `{'half_life': 4, 'transform': 'log', 'alpha': 1.0}` | 0.2890 | 0.2314 | 0.3145 | 0.3209 | 0.2049 | 0.2893 | 0.2959 |
| repeat | `{'half_life': 2, 'transform': 'raw', 'alpha': 0.0}` | 0.2887 | 0.2723 | 0.3001 | 0.2937 | 0.2212 | 0.2484 | 0.2442 |
| repeat | `{'half_life': 8, 'transform': 'log', 'alpha': 1.0}` | 0.2877 | 0.2304 | 0.3134 | 0.3193 | 0.2040 | 0.2883 | 0.2948 |
| repeat | `{'half_life': None, 'transform': 'log', 'alpha': 1.0}` | 0.2871 | 0.2289 | 0.3127 | 0.3195 | 0.2022 | 0.2858 | 0.2929 |
| repeat | `{'half_life': 2, 'transform': 'log', 'alpha': 1.0}` | 0.2857 | 0.2294 | 0.3108 | 0.3169 | 0.2026 | 0.2846 | 0.2901 |
| repeat | `{'half_life': 1, 'transform': 'log', 'alpha': 1.0}` | 0.2776 | 0.2233 | 0.3020 | 0.3076 | 0.1959 | 0.2737 | 0.2776 |
| repeat | `{'half_life': 1, 'transform': 'raw', 'alpha': 0.0}` | 0.2329 | 0.2233 | 0.2399 | 0.2355 | 0.1831 | 0.1994 | 0.1960 |

Selected: popularity n_weeks=10; repeat {'half_life': 8, 'transform': 'log', 'alpha': 0.0}.

Fallback use for the selected repeat on test users: validation 10 users fully on fallback, 60 of 6300 slots from fallback; final refit 2 users, 11 slots.

Test pool (weeks 31-42): 6642 labelled shows.

Submission format checks: popularity_v1.csv: OK; repeat_v1.csv: OK

Total runtime: 27.9 s.
