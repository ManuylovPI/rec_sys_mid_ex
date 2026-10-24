> **Superseded** (stage 3, selection on n_days + n_airings (any overlap)). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Repeat v2: validation results

Produced by `python -m src.repeat_v2` on 2026-10-22 16:35. Same harness as stage 2: history weeks 11-20, target weeks 21-30, pool 6376 shows, populations test_users 1260 / active_both 4752. `select` = mean MAP@5 of n_days, n_airings on test_users (see docs/target_definition.md).

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4491 | 0.4558 | 0.4424 | 0.2953 | 0.3898 | 0.3821 | 0.2495 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m5'}` | 0.4491 | 0.4558 | 0.4424 | 0.2953 | 0.3899 | 0.3821 | 0.2496 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4490 | 0.4557 | 0.4423 | 0.2951 | 0.3899 | 0.3822 | 0.2496 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m1'}` | 0.4490 | 0.4557 | 0.4423 | 0.2951 | 0.3898 | 0.3821 | 0.2495 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4453 | 0.4505 | 0.4402 | 0.2921 | 0.3868 | 0.3799 | 0.2461 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m5'}` | 0.4453 | 0.4505 | 0.4402 | 0.2921 | 0.3868 | 0.3799 | 0.2461 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4452 | 0.4504 | 0.4400 | 0.2919 | 0.3869 | 0.3799 | 0.2462 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m1'}` | 0.4452 | 0.4503 | 0.4400 | 0.2919 | 0.3868 | 0.3799 | 0.2461 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4403 | 0.4469 | 0.4337 | 0.2919 | 0.3788 | 0.3711 | 0.2446 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'channels_m5'}` | 0.4403 | 0.4469 | 0.4337 | 0.2919 | 0.3788 | 0.3712 | 0.2446 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4402 | 0.4468 | 0.4335 | 0.2917 | 0.3789 | 0.3712 | 0.2447 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'channels_m1'}` | 0.4402 | 0.4468 | 0.4335 | 0.2917 | 0.3788 | 0.3711 | 0.2446 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4400 | 0.4339 | 0.4460 | 0.2849 | 0.3747 | 0.3871 | 0.2405 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4380 | 0.4400 | 0.4361 | 0.2941 | 0.3824 | 0.3794 | 0.2497 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 4, 'fill': 'global'}` | 0.4374 | 0.4331 | 0.4416 | 0.2906 | 0.3725 | 0.3820 | 0.2465 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'fill': 'global'}` | 0.4367 | 0.4322 | 0.4411 | 0.2897 | 0.3734 | 0.3826 | 0.2456 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4362 | 0.4411 | 0.4314 | 0.2888 | 0.3755 | 0.3688 | 0.2415 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'fill': 'global'}` | 0.4354 | 0.4407 | 0.4302 | 0.2914 | 0.3787 | 0.3737 | 0.2468 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4343 | 0.4355 | 0.4331 | 0.2897 | 0.3774 | 0.3746 | 0.2453 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4342 | 0.4386 | 0.4299 | 0.3084 | 0.3799 | 0.3726 | 0.2592 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4331 | 0.4265 | 0.4397 | 0.2812 | 0.3706 | 0.3835 | 0.2381 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'none', 'half_life': 4, 'fill': 'global'}` | 0.4329 | 0.4387 | 0.4272 | 0.2910 | 0.3785 | 0.3723 | 0.2475 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4319 | 0.4356 | 0.4282 | 0.3050 | 0.3758 | 0.3694 | 0.2546 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'fill': 'global'}` | 0.4293 | 0.4238 | 0.4348 | 0.2826 | 0.3672 | 0.3776 | 0.2409 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4288 | 0.4230 | 0.4347 | 0.2991 | 0.3659 | 0.3763 | 0.2509 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'fill': 'global'}` | 0.4280 | 0.4310 | 0.4250 | 0.2865 | 0.3739 | 0.3702 | 0.2428 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4280 | 0.4297 | 0.4263 | 0.2921 | 0.3696 | 0.3672 | 0.2449 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4275 | 0.4215 | 0.4335 | 0.2807 | 0.3628 | 0.3748 | 0.2362 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4275 | 0.4188 | 0.4362 | 0.2830 | 0.3656 | 0.3806 | 0.2401 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'fill': 'global'}` | 0.4262 | 0.4273 | 0.4252 | 0.2901 | 0.3712 | 0.3697 | 0.2466 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4260 | 0.4168 | 0.4352 | 0.2815 | 0.3628 | 0.3778 | 0.2381 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4258 | 0.4310 | 0.4206 | 0.2894 | 0.3642 | 0.3583 | 0.2417 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 4, 'fill': 'global'}` | 0.4257 | 0.4271 | 0.4243 | 0.2907 | 0.3694 | 0.3674 | 0.2465 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 5, 'delta': 1.0, 'fill': 'global'}` | 0.4243 | 0.4175 | 0.4311 | 0.2959 | 0.3611 | 0.3718 | 0.2478 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4242 | 0.4307 | 0.4178 | 0.2847 | 0.3613 | 0.3539 | 0.2364 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4236 | 0.4287 | 0.4184 | 0.2833 | 0.3617 | 0.3550 | 0.2351 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4231 | 0.4240 | 0.4222 | 0.2869 | 0.3643 | 0.3621 | 0.2401 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4230 | 0.4164 | 0.4296 | 0.2770 | 0.3598 | 0.3722 | 0.2338 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'fill': 'global'}` | 0.4229 | 0.4166 | 0.4292 | 0.2842 | 0.3608 | 0.3726 | 0.2419 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4228 | 0.4270 | 0.4186 | 0.3051 | 0.3656 | 0.3589 | 0.2527 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'fill': 'global'}` | 0.4221 | 0.4182 | 0.4260 | 0.3023 | 0.3605 | 0.3680 | 0.2542 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 4, 'fill': 'global'}` | 0.4220 | 0.4155 | 0.4284 | 0.2860 | 0.3591 | 0.3708 | 0.2425 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'fill': 'global'}` | 0.4218 | 0.4255 | 0.4181 | 0.3031 | 0.3669 | 0.3618 | 0.2557 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4216 | 0.4254 | 0.4179 | 0.2870 | 0.3581 | 0.3530 | 0.2383 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 4, 'fill': 'global'}` | 0.4216 | 0.4174 | 0.4257 | 0.3031 | 0.3589 | 0.3665 | 0.2552 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 4, 'fill': 'global'}` | 0.4206 | 0.4243 | 0.4170 | 0.3044 | 0.3658 | 0.3607 | 0.2569 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'fill': 'global'}` | 0.4200 | 0.4197 | 0.4203 | 0.2843 | 0.3657 | 0.3653 | 0.2420 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4195 | 0.4233 | 0.4156 | 0.3001 | 0.3610 | 0.3550 | 0.2479 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4172 | 0.4091 | 0.4253 | 0.2802 | 0.3544 | 0.3690 | 0.2361 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4169 | 0.4117 | 0.4222 | 0.2943 | 0.3528 | 0.3625 | 0.2453 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'fill': 'global'}` | 0.4165 | 0.4187 | 0.4142 | 0.2970 | 0.3627 | 0.3594 | 0.2504 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'fill': 'global'}` | 0.4152 | 0.4079 | 0.4225 | 0.2790 | 0.3563 | 0.3686 | 0.2384 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4150 | 0.4066 | 0.4235 | 0.2782 | 0.3512 | 0.3655 | 0.2339 |
| repeat_v2 | `{'score': 'freq', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'fill': 'global'}` | 0.4147 | 0.4096 | 0.4198 | 0.2949 | 0.3559 | 0.3638 | 0.2495 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4139 | 0.4082 | 0.4197 | 0.2744 | 0.3476 | 0.3590 | 0.2291 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 1, 'delta': 1.0, 'fill': 'global'}` | 0.4138 | 0.4079 | 0.4196 | 0.2923 | 0.3491 | 0.3585 | 0.2427 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4137 | 0.4153 | 0.4121 | 0.2855 | 0.3539 | 0.3512 | 0.2367 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4133 | 0.4141 | 0.4126 | 0.2885 | 0.3527 | 0.3509 | 0.2403 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4117 | 0.4126 | 0.4107 | 0.2818 | 0.3527 | 0.3502 | 0.2342 |
| repeat | `{'half_life': 8, 'transform': 'log', 'alpha': 0.0}` | 0.4102 | 0.4142 | 0.4062 | 0.2988 | 0.3577 | 0.3527 | 0.2541 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4099 | 0.4132 | 0.4067 | 0.3016 | 0.3480 | 0.3431 | 0.2485 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4099 | 0.4038 | 0.4159 | 0.2716 | 0.3459 | 0.3576 | 0.2274 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4069 | 0.4072 | 0.4067 | 0.2847 | 0.3459 | 0.3447 | 0.2359 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4064 | 0.4104 | 0.4023 | 0.2958 | 0.3465 | 0.3401 | 0.2426 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4053 | 0.4093 | 0.4014 | 0.2924 | 0.3460 | 0.3401 | 0.2402 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4039 | 0.3961 | 0.4117 | 0.2746 | 0.3412 | 0.3549 | 0.2296 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4036 | 0.3956 | 0.4116 | 0.2731 | 0.3400 | 0.3535 | 0.2285 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.4020 | 0.4047 | 0.3992 | 0.2967 | 0.3393 | 0.3352 | 0.2424 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.4004 | 0.3954 | 0.4054 | 0.2868 | 0.3361 | 0.3456 | 0.2369 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 0, 'delta': 1.0, 'fill': 'global'}` | 0.3986 | 0.3931 | 0.4041 | 0.2848 | 0.3345 | 0.3435 | 0.2352 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3816 | 0.3863 | 0.3769 | 0.2702 | 0.3172 | 0.3121 | 0.2204 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3743 | 0.3771 | 0.3714 | 0.2653 | 0.3077 | 0.3038 | 0.2142 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3660 | 0.3660 | 0.3661 | 0.2659 | 0.3044 | 0.3030 | 0.2170 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3543 | 0.3540 | 0.3545 | 0.2569 | 0.2951 | 0.2938 | 0.2101 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3538 | 0.3563 | 0.3514 | 0.2720 | 0.2926 | 0.2884 | 0.2198 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.3434 | 0.3456 | 0.3412 | 0.2641 | 0.2824 | 0.2792 | 0.2120 |
| popularity | `{'n_weeks': 10}` | 0.3137 | 0.3174 | 0.3100 | 0.1799 | 0.2769 | 0.2706 | 0.1563 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.3014 | 0.2998 | 0.3029 | 0.2421 | 0.2478 | 0.2489 | 0.1936 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.2958 | 0.2959 | 0.2956 | 0.2352 | 0.2433 | 0.2438 | 0.1889 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2940 | 0.2951 | 0.2930 | 0.2190 | 0.2383 | 0.2364 | 0.1748 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2904 | 0.2922 | 0.2887 | 0.2182 | 0.2349 | 0.2326 | 0.1740 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2893 | 0.2890 | 0.2896 | 0.2199 | 0.2391 | 0.2381 | 0.1775 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.2883 | 0.2865 | 0.2901 | 0.2327 | 0.2364 | 0.2378 | 0.1862 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2879 | 0.2881 | 0.2877 | 0.2200 | 0.2373 | 0.2366 | 0.1776 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.2804 | 0.2815 | 0.2793 | 0.2424 | 0.2302 | 0.2295 | 0.1918 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.2791 | 0.2784 | 0.2797 | 0.2255 | 0.2302 | 0.2311 | 0.1811 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2661 | 0.2669 | 0.2654 | 0.2150 | 0.2175 | 0.2163 | 0.1719 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 5, 'delta': 0.5, 'fill': 'global'}` | 0.2660 | 0.2664 | 0.2656 | 0.2294 | 0.2177 | 0.2176 | 0.1826 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.2630 | 0.2644 | 0.2617 | 0.2144 | 0.2155 | 0.2135 | 0.1716 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.2133 | 0.2129 | 0.2137 | 0.1830 | 0.1690 | 0.1701 | 0.1420 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.2070 | 0.2069 | 0.2070 | 0.1776 | 0.1632 | 0.1638 | 0.1376 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.1989 | 0.1980 | 0.1998 | 0.1727 | 0.1581 | 0.1590 | 0.1337 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.1908 | 0.1908 | 0.1909 | 0.1668 | 0.1514 | 0.1523 | 0.1293 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.1901 | 0.1909 | 0.1893 | 0.1749 | 0.1498 | 0.1496 | 0.1344 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 1, 'delta': 0.5, 'fill': 'global'}` | 0.1744 | 0.1749 | 0.1740 | 0.1631 | 0.1386 | 0.1387 | 0.1260 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1300 | 0.1294 | 0.1306 | 0.1171 | 0.1052 | 0.1060 | 0.0926 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1278 | 0.1278 | 0.1279 | 0.1163 | 0.1031 | 0.1032 | 0.0908 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1140 | 0.1140 | 0.1140 | 0.1043 | 0.0896 | 0.0905 | 0.0803 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1116 | 0.1118 | 0.1113 | 0.1027 | 0.0878 | 0.0883 | 0.0792 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1058 | 0.1062 | 0.1055 | 0.1025 | 0.0856 | 0.0855 | 0.0803 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 0, 'delta': 0.5, 'fill': 'global'}` | 0.1043 | 0.1047 | 0.1038 | 0.1018 | 0.0840 | 0.0837 | 0.0793 |

Selected: {'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}.

Final refit (weeks 11-30 -> 31-42), test users: 2 with no own items, 11 of 6300 slots not filled by own items; after channel fill 5 slots left for global popularity.

Submission format check repeat_v2.csv: OK.

Total runtime: 47.8 s.
