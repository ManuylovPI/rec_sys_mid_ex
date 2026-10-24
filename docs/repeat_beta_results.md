> **Superseded** (stage 4, selection on n_days + n_airings (any overlap)). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Repeat v2: beta extension

Produced by `python -m src.repeat_beta` on 2026-10-22 16:43. Same harness and selection as docs/repeat_v2_results.md (beta 0/1/5 results are there). First row is the submitted repeat_v2 config re-evaluated as reference.

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4499 | 0.4566 | 0.4432 | 0.2947 | 0.3933 | 0.3855 | 0.2501 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4498 | 0.4565 | 0.4431 | 0.2945 | 0.3934 | 0.3855 | 0.2502 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 5, 'delta': 1.0, 'fill': 'channels_m3'}` | 0.4491 | 0.4558 | 0.4424 | 0.2953 | 0.3898 | 0.3821 | 0.2496 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4479 | 0.4545 | 0.4413 | 0.2923 | 0.3951 | 0.3872 | 0.2500 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4474 | 0.4537 | 0.4411 | 0.2934 | 0.3920 | 0.3849 | 0.2502 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4472 | 0.4536 | 0.4407 | 0.2898 | 0.3962 | 0.3881 | 0.2490 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4463 | 0.4512 | 0.4413 | 0.2901 | 0.3924 | 0.3858 | 0.2470 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4458 | 0.4510 | 0.4405 | 0.2911 | 0.3903 | 0.3832 | 0.2470 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4450 | 0.4386 | 0.4514 | 0.2824 | 0.3820 | 0.3953 | 0.2400 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4450 | 0.4505 | 0.4394 | 0.2879 | 0.3935 | 0.3857 | 0.2463 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4449 | 0.4507 | 0.4392 | 0.2948 | 0.3858 | 0.3793 | 0.2491 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4439 | 0.4380 | 0.4499 | 0.2838 | 0.3797 | 0.3925 | 0.2413 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4436 | 0.4480 | 0.4392 | 0.2914 | 0.3874 | 0.3818 | 0.2471 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4427 | 0.4354 | 0.4501 | 0.2766 | 0.3807 | 0.3952 | 0.2357 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4420 | 0.4444 | 0.4396 | 0.2921 | 0.3909 | 0.3873 | 0.2508 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4416 | 0.4341 | 0.4492 | 0.2799 | 0.3780 | 0.3921 | 0.2385 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4415 | 0.4436 | 0.4394 | 0.2925 | 0.3891 | 0.3858 | 0.2513 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4406 | 0.4426 | 0.4385 | 0.2950 | 0.3863 | 0.3831 | 0.2513 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4403 | 0.4318 | 0.4487 | 0.2759 | 0.3782 | 0.3934 | 0.2352 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4401 | 0.4459 | 0.4344 | 0.3075 | 0.3883 | 0.3798 | 0.2607 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4400 | 0.4440 | 0.4361 | 0.2920 | 0.3806 | 0.3755 | 0.2458 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4400 | 0.4467 | 0.4333 | 0.3061 | 0.3906 | 0.3815 | 0.2608 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4393 | 0.4408 | 0.4379 | 0.2936 | 0.3848 | 0.3824 | 0.2513 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4388 | 0.4317 | 0.4460 | 0.2820 | 0.3748 | 0.3885 | 0.2392 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4386 | 0.4401 | 0.4371 | 0.2881 | 0.3871 | 0.3837 | 0.2471 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4384 | 0.4398 | 0.4369 | 0.2900 | 0.3845 | 0.3815 | 0.2478 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4382 | 0.4433 | 0.4331 | 0.3021 | 0.3872 | 0.3793 | 0.2568 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4378 | 0.4426 | 0.4330 | 0.3077 | 0.3847 | 0.3768 | 0.2605 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4377 | 0.4421 | 0.4332 | 0.3051 | 0.3843 | 0.3774 | 0.2574 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4376 | 0.4419 | 0.4332 | 0.3097 | 0.3831 | 0.3763 | 0.2615 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4370 | 0.4425 | 0.4315 | 0.2922 | 0.3773 | 0.3711 | 0.2464 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4368 | 0.4301 | 0.4435 | 0.2967 | 0.3760 | 0.3874 | 0.2515 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4364 | 0.4296 | 0.4433 | 0.2893 | 0.3758 | 0.3884 | 0.2460 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4363 | 0.4378 | 0.4348 | 0.2894 | 0.3809 | 0.3778 | 0.2466 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4357 | 0.4268 | 0.4446 | 0.2811 | 0.3732 | 0.3884 | 0.2393 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4356 | 0.4395 | 0.4316 | 0.3055 | 0.3803 | 0.3737 | 0.2563 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4352 | 0.4364 | 0.4340 | 0.2948 | 0.3777 | 0.3752 | 0.2493 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4346 | 0.4273 | 0.4420 | 0.2955 | 0.3718 | 0.3840 | 0.2493 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4341 | 0.4350 | 0.4332 | 0.2905 | 0.3781 | 0.3762 | 0.2467 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4334 | 0.4256 | 0.4412 | 0.2886 | 0.3739 | 0.3867 | 0.2458 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4330 | 0.4272 | 0.4388 | 0.2985 | 0.3716 | 0.3822 | 0.2522 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4330 | 0.4232 | 0.4428 | 0.2737 | 0.3712 | 0.3884 | 0.2342 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4327 | 0.4368 | 0.4287 | 0.3054 | 0.3768 | 0.3715 | 0.2563 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4322 | 0.4231 | 0.4413 | 0.2833 | 0.3697 | 0.3851 | 0.2403 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4320 | 0.4356 | 0.4284 | 0.2903 | 0.3707 | 0.3658 | 0.2430 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 20, 'delta': 1.0, 'fill': 'global'}` | 0.4314 | 0.4220 | 0.4408 | 0.2794 | 0.3689 | 0.3852 | 0.2379 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 50, 'delta': 1.0, 'fill': 'global'}` | 0.4301 | 0.4204 | 0.4398 | 0.2733 | 0.3697 | 0.3867 | 0.2342 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4298 | 0.4339 | 0.4257 | 0.3086 | 0.3739 | 0.3678 | 0.2590 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4298 | 0.4229 | 0.4367 | 0.2956 | 0.3676 | 0.3791 | 0.2495 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 10, 'delta': 1.0, 'fill': 'global'}` | 0.4294 | 0.4200 | 0.4388 | 0.2808 | 0.3667 | 0.3824 | 0.2388 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4289 | 0.4298 | 0.4281 | 0.2907 | 0.3706 | 0.3689 | 0.2449 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.4263 | 0.4300 | 0.4225 | 0.3054 | 0.3683 | 0.3632 | 0.2542 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4259 | 0.4269 | 0.4249 | 0.2922 | 0.3673 | 0.3655 | 0.2459 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4219 | 0.4254 | 0.4183 | 0.3060 | 0.3628 | 0.3574 | 0.2548 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'frac10', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4201 | 0.4207 | 0.4196 | 0.2884 | 0.3605 | 0.3590 | 0.2416 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'sec300', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.4166 | 0.4201 | 0.4131 | 0.3021 | 0.3564 | 0.3519 | 0.2499 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4115 | 0.4096 | 0.4133 | 0.2816 | 0.3532 | 0.3554 | 0.2391 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4085 | 0.4041 | 0.4129 | 0.2862 | 0.3472 | 0.3521 | 0.2400 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.4003 | 0.3991 | 0.4014 | 0.2988 | 0.3412 | 0.3415 | 0.2485 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.3924 | 0.3902 | 0.3947 | 0.2767 | 0.3365 | 0.3386 | 0.2323 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.3918 | 0.3880 | 0.3956 | 0.2820 | 0.3339 | 0.3379 | 0.2342 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 50, 'delta': 0.5, 'fill': 'global'}` | 0.3828 | 0.3817 | 0.3839 | 0.2902 | 0.3253 | 0.3258 | 0.2400 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3676 | 0.3651 | 0.3702 | 0.2752 | 0.3118 | 0.3143 | 0.2269 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3676 | 0.3673 | 0.3679 | 0.2714 | 0.3126 | 0.3129 | 0.2243 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3563 | 0.3565 | 0.3560 | 0.2827 | 0.3006 | 0.3002 | 0.2310 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3556 | 0.3529 | 0.3583 | 0.2676 | 0.3001 | 0.3026 | 0.2203 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3521 | 0.3512 | 0.3530 | 0.2634 | 0.2981 | 0.2987 | 0.2172 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 20, 'delta': 0.5, 'fill': 'global'}` | 0.3375 | 0.3372 | 0.3378 | 0.2708 | 0.2853 | 0.2850 | 0.2218 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3368 | 0.3358 | 0.3378 | 0.2613 | 0.2813 | 0.2829 | 0.2125 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3323 | 0.3319 | 0.3327 | 0.2541 | 0.2780 | 0.2788 | 0.2074 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'frac10', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3222 | 0.3201 | 0.3242 | 0.2513 | 0.2697 | 0.2713 | 0.2045 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': 8, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3204 | 0.3208 | 0.3200 | 0.2632 | 0.2665 | 0.2661 | 0.2129 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'none', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3162 | 0.3155 | 0.3169 | 0.2455 | 0.2647 | 0.2655 | 0.2007 |
| repeat_v2 | `{'score': 'loyalty', 'unit': 'n_airings', 'threshold': 'sec300', 'half_life': None, 'beta': 10, 'delta': 0.5, 'fill': 'global'}` | 0.3025 | 0.3027 | 0.3023 | 0.2523 | 0.2523 | 0.2524 | 0.2040 |

Selected as the repeat baseline: `{'score': 'loyalty', 'unit': 'n_days', 'threshold': 'none', 'half_life': 8, 'beta': 10, 'delta': 1.0, 'fill': 'channels_m3'}` (select 0.4499).

Total runtime: 35.2 s.
