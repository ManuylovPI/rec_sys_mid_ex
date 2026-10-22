# Repeat on the cov50 target

Produced by `python -m src.repeat_v3` on 2026-10-22 17:31. History 11-20, target 21-30, test users / active_both, shared popularity fallback. `select` = MAP@5 on cov50 (one merged continuous view covering > 50% of the airing, counted as airings) on the test users.

## Components re-scored on cov50

| method | params | select | test_users/cov50 | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/cov50 | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|---|---|
| slot | `{'agg': 'airings', 'daytype': 'we2', 'half_life': 8, 'model': 'slot'}` | 0.4015 | 0.4015 | 0.4041 | 0.4240 | 0.2637 | 0.3490 | 0.3589 | 0.3769 | 0.2296 |
| repeat_cont | `{'cut': 0.5, 'tie': 'pop', 'history': 'whole window, no decay'}` | 0.3841 | 0.3841 | 0.3690 | 0.3888 | 0.2493 | 0.3288 | 0.3265 | 0.3427 | 0.2162 |
| repeat_v2 | `{'beta': 10, 'delta': 1.0, 'fill': 'channels_m3', 'half_life': 8, 'score': 'loyalty', 'threshold': 'none', 'unit': 'n_days'}` | 0.3602 | 0.3602 | 0.4535 | 0.4422 | 0.2940 | 0.3125 | 0.3908 | 0.3846 | 0.2497 |
| popularity | `{'n_weeks': 10}` | 0.2752 | 0.2752 | 0.3167 | 0.3100 | 0.1799 | 0.2374 | 0.2749 | 0.2706 | 0.1563 |
| als | `{'alpha': 0.3, 'bm25_b': 0.8, 'bm25_k1': 100, 'conf': 'n_days_hl8', 'factors': 8, 'iters': 15, 'reg': 0.01, 'weighting': 'bm25'}` | 0.2528 | 0.2528 | 0.2927 | 0.2911 | 0.1818 | 0.2235 | 0.2626 | 0.2632 | 0.1629 |
| cbf | `{'max_actors': 5, 'min_df': 2, 'people_weight': 4.0, 'profile': 'linear', 'profile_unit': 'n_days_hl8', 'rep': 'tfidf'}` | 0.1154 | 0.1154 | 0.1276 | 0.1265 | 0.0882 | 0.1057 | 0.1174 | 0.1156 | 0.0803 |

## Repeat grid (cov50)

| method | params | select | test_users/cov50 | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/cov50 | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|---|---|
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 3}` | 0.4080 | 0.4080 | 0.4020 | 0.4233 | 0.2680 | 0.3476 | 0.3507 | 0.3689 | 0.2287 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 2}` | 0.4061 | 0.4061 | 0.3993 | 0.4204 | 0.2691 | 0.3477 | 0.3498 | 0.3682 | 0.2306 |
| repeat_cov | `{'source': 'raw', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.4030 | 0.4030 | 0.3959 | 0.4173 | 0.2677 | 0.3442 | 0.3454 | 0.3633 | 0.2292 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.4026 | 0.4026 | 0.3955 | 0.4169 | 0.2672 | 0.3440 | 0.3453 | 0.3633 | 0.2292 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'id', 'min_count': 1}` | 0.4026 | 0.4026 | 0.3955 | 0.4169 | 0.2672 | 0.3440 | 0.3453 | 0.3633 | 0.2292 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.4012 | 0.4012 | 0.3959 | 0.4158 | 0.2665 | 0.3441 | 0.3462 | 0.3639 | 0.2290 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3981 | 0.3981 | 0.3917 | 0.4137 | 0.2642 | 0.3407 | 0.3421 | 0.3604 | 0.2260 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3976 | 0.3976 | 0.3926 | 0.4122 | 0.2665 | 0.3400 | 0.3413 | 0.3586 | 0.2281 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3970 | 0.3970 | 0.3902 | 0.4110 | 0.2668 | 0.3393 | 0.3399 | 0.3575 | 0.2283 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3961 | 0.3961 | 0.3728 | 0.3953 | 0.2513 | 0.3377 | 0.3284 | 0.3477 | 0.2170 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3948 | 0.3948 | 0.3711 | 0.3940 | 0.2516 | 0.3357 | 0.3263 | 0.3456 | 0.2163 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3947 | 0.3947 | 0.3881 | 0.4087 | 0.2637 | 0.3368 | 0.3378 | 0.3556 | 0.2252 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3932 | 0.3932 | 0.3724 | 0.3944 | 0.2496 | 0.3352 | 0.3268 | 0.3458 | 0.2154 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3917 | 0.3917 | 0.4151 | 0.4195 | 0.2822 | 0.3364 | 0.3630 | 0.3655 | 0.2400 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3915 | 0.3915 | 0.3684 | 0.3898 | 0.2512 | 0.3330 | 0.3232 | 0.3420 | 0.2160 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3902 | 0.3902 | 0.4156 | 0.4191 | 0.2835 | 0.3354 | 0.3616 | 0.3633 | 0.2405 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3901 | 0.3901 | 0.3667 | 0.3891 | 0.2509 | 0.3311 | 0.3210 | 0.3400 | 0.2152 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3892 | 0.3892 | 0.4111 | 0.4156 | 0.2811 | 0.3325 | 0.3576 | 0.3603 | 0.2382 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3891 | 0.3891 | 0.3937 | 0.4002 | 0.2678 | 0.3321 | 0.3437 | 0.3494 | 0.2273 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3889 | 0.3889 | 0.3855 | 0.4048 | 0.2679 | 0.3313 | 0.3355 | 0.3513 | 0.2290 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3879 | 0.3879 | 0.4110 | 0.4159 | 0.2788 | 0.3333 | 0.3592 | 0.3620 | 0.2378 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3875 | 0.3875 | 0.4120 | 0.4162 | 0.2822 | 0.3311 | 0.3567 | 0.3586 | 0.2388 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3871 | 0.3871 | 0.3831 | 0.4033 | 0.2682 | 0.3299 | 0.3334 | 0.3491 | 0.2294 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3870 | 0.3870 | 0.3667 | 0.3881 | 0.2471 | 0.3296 | 0.3210 | 0.3393 | 0.2133 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3869 | 0.3869 | 0.3912 | 0.3986 | 0.2678 | 0.3305 | 0.3414 | 0.3474 | 0.2269 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3864 | 0.3864 | 0.3897 | 0.4077 | 0.2662 | 0.3332 | 0.3419 | 0.3570 | 0.2283 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3859 | 0.3859 | 0.3916 | 0.3982 | 0.2650 | 0.3297 | 0.3429 | 0.3481 | 0.2261 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3858 | 0.3858 | 0.3895 | 0.3962 | 0.2667 | 0.3280 | 0.3390 | 0.3444 | 0.2253 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3851 | 0.3851 | 0.4071 | 0.4118 | 0.2767 | 0.3300 | 0.3549 | 0.3578 | 0.2355 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3845 | 0.3845 | 0.4054 | 0.4130 | 0.2758 | 0.3298 | 0.3540 | 0.3588 | 0.2346 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3841 | 0.3841 | 0.3690 | 0.3888 | 0.2493 | 0.3288 | 0.3265 | 0.3427 | 0.2162 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3834 | 0.3834 | 0.4017 | 0.4084 | 0.2772 | 0.3267 | 0.3482 | 0.3523 | 0.2346 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3828 | 0.3828 | 0.3602 | 0.3819 | 0.2492 | 0.3247 | 0.3172 | 0.3342 | 0.2151 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3823 | 0.3823 | 0.3856 | 0.3928 | 0.2667 | 0.3261 | 0.3364 | 0.3419 | 0.2251 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3822 | 0.3822 | 0.3881 | 0.3970 | 0.2593 | 0.3278 | 0.3408 | 0.3474 | 0.2233 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3812 | 0.3812 | 0.3864 | 0.3929 | 0.2627 | 0.3250 | 0.3375 | 0.3426 | 0.2237 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3800 | 0.3800 | 0.3791 | 0.3883 | 0.2604 | 0.3220 | 0.3296 | 0.3365 | 0.2214 |
| repeat_cov | `{'source': 'merged', 'cut': 0.3, 'unit': 'days', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3799 | 0.3799 | 0.3994 | 0.4049 | 0.2763 | 0.3232 | 0.3442 | 0.3478 | 0.2338 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'airings', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3789 | 0.3789 | 0.3567 | 0.3778 | 0.2487 | 0.3214 | 0.3129 | 0.3297 | 0.2142 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3749 | 0.3749 | 0.3434 | 0.3663 | 0.2313 | 0.3179 | 0.3003 | 0.3204 | 0.1984 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3739 | 0.3739 | 0.3614 | 0.3721 | 0.2463 | 0.3156 | 0.3131 | 0.3225 | 0.2078 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3735 | 0.3735 | 0.3424 | 0.3633 | 0.2333 | 0.3159 | 0.2988 | 0.3181 | 0.1986 |
| repeat_cov | `{'source': 'merged', 'cut': 0.5, 'unit': 'days', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3735 | 0.3735 | 0.3733 | 0.3816 | 0.2596 | 0.3178 | 0.3244 | 0.3310 | 0.2200 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3719 | 0.3719 | 0.3401 | 0.3620 | 0.2287 | 0.3161 | 0.2983 | 0.3183 | 0.1966 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3711 | 0.3711 | 0.3592 | 0.3689 | 0.2468 | 0.3126 | 0.3107 | 0.3192 | 0.2074 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': None, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 1}` | 0.3698 | 0.3698 | 0.3595 | 0.3697 | 0.2447 | 0.3134 | 0.3132 | 0.3219 | 0.2071 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3695 | 0.3695 | 0.3376 | 0.3588 | 0.2294 | 0.3130 | 0.2951 | 0.3145 | 0.1966 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3690 | 0.3690 | 0.3370 | 0.3577 | 0.2316 | 0.3118 | 0.2940 | 0.3131 | 0.1971 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3679 | 0.3679 | 0.3432 | 0.3633 | 0.2313 | 0.3137 | 0.3024 | 0.3196 | 0.1987 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 8, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3677 | 0.3677 | 0.3550 | 0.3651 | 0.2431 | 0.3108 | 0.3079 | 0.3171 | 0.2053 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': None, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3677 | 0.3677 | 0.3584 | 0.3686 | 0.2408 | 0.3145 | 0.3147 | 0.3244 | 0.2059 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 4, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3672 | 0.3672 | 0.3539 | 0.3634 | 0.2447 | 0.3087 | 0.3059 | 0.3144 | 0.2053 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3671 | 0.3671 | 0.3354 | 0.3567 | 0.2271 | 0.3116 | 0.2936 | 0.3132 | 0.1947 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': None, 'scale': 'loyalty5', 'tie': 'pop', 'min_count': 1}` | 0.3659 | 0.3659 | 0.3556 | 0.3652 | 0.2423 | 0.3094 | 0.3086 | 0.3171 | 0.2049 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3620 | 0.3620 | 0.3299 | 0.3504 | 0.2273 | 0.3048 | 0.2870 | 0.3049 | 0.1947 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 8, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3594 | 0.3594 | 0.3429 | 0.3539 | 0.2361 | 0.3038 | 0.2973 | 0.3070 | 0.2005 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'airings', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3565 | 0.3565 | 0.3253 | 0.3447 | 0.2270 | 0.3008 | 0.2830 | 0.3004 | 0.1935 |
| repeat_cov | `{'source': 'merged', 'cut': 0.8, 'unit': 'days', 'half_life': 4, 'scale': 'plain', 'tie': 'pop', 'min_count': 1}` | 0.3558 | 0.3558 | 0.3393 | 0.3500 | 0.2360 | 0.2995 | 0.2927 | 0.3021 | 0.1992 |

Selected repeat: `{'source': 'merged', 'cut': 0.3, 'unit': 'airings', 'half_life': 4, 'scale': 'loyalty10', 'tie': 'pop', 'min_count': 3}` (select 0.4080).

Total runtime: 22.7 s.
