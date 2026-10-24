> **Superseded** (stage 7, selection on n_days (the new-content measurement in it is still valid)). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Slot habits

Produced by `python -m src.slots` on 2026-10-22 17:07. Same harness as all methods (history 11-20, target 21-30, 1,260 test users, shared popularity fallback); `select` = MAP@5 on n_days.

## How much of the target is new content

Test users' true top-5 shows in weeks 21-30 (n_days): 6227 (user, show) pairs.

| share of true top-5 shows that ... | value |
|---|---|
| nobody watched in weeks 11-20 | 0.0329 |
| did not air at all in weeks 11-20 | 0.0247 |
| this user did not watch in weeks 11-20 | 0.1593 |

### Labelled airings in weeks 21-30 whose id nobody watched in weeks 11-20

All airings: 0.3409; prime time (start 19:00-22:59): 0.3266.

| week | airings | share no history | prime airings | prime share no history | prime airtime share no history |
|---|---|---|---|---|---|
| 21 | 11371 | 0.3117 | 2021 | 0.2796 | 0.3545 |
| 22 | 12144 | 0.3532 | 2120 | 0.3179 | 0.4171 |
| 23 | 11929 | 0.3357 | 2070 | 0.3275 | 0.4255 |
| 24 | 12001 | 0.3398 | 2131 | 0.3336 | 0.4131 |
| 25 | 12155 | 0.3399 | 2170 | 0.3382 | 0.4210 |
| 26 | 12604 | 0.3427 | 2207 | 0.3344 | 0.4231 |
| 27 | 12541 | 0.3524 | 2221 | 0.3422 | 0.4197 |
| 28 | 12000 | 0.3345 | 2112 | 0.3277 | 0.3865 |
| 29 | 12686 | 0.3572 | 2188 | 0.3410 | 0.4299 |
| 30 | 12090 | 0.3384 | 1991 | 0.3189 | 0.3953 |

### Labelled airings in weeks 31-42 whose id nobody watched in weeks 11-30

All airings: 0.2911; prime time (start 19:00-22:59): 0.2776.

| week | airings | share no history | prime airings | prime share no history | prime airtime share no history |
|---|---|---|---|---|---|
| 31 | 12328 | 0.2936 | 2085 | 0.2921 | 0.3724 |
| 32 | 11911 | 0.2711 | 1870 | 0.2610 | 0.3116 |
| 33 | 11646 | 0.2867 | 1956 | 0.2587 | 0.3128 |
| 34 | 11619 | 0.2924 | 1986 | 0.2684 | 0.3131 |
| 35 | 12728 | 0.3082 | 2252 | 0.2971 | 0.3758 |
| 36 | 12376 | 0.3036 | 2165 | 0.2781 | 0.3428 |
| 37 | 11738 | 0.2913 | 1999 | 0.2641 | 0.2972 |
| 38 | 12062 | 0.2847 | 2077 | 0.2788 | 0.3168 |
| 39 | 11992 | 0.2740 | 2046 | 0.2571 | 0.3028 |
| 40 | 11870 | 0.2837 | 1980 | 0.2813 | 0.3466 |
| 41 | 12199 | 0.3053 | 2122 | 0.2912 | 0.3570 |
| 42 | 12315 | 0.2964 | 2178 | 0.2971 | 0.3540 |

## Slot model and replacement score alone

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| slot | `{'model': 'slot', 'daytype': 'we2', 'half_life': 8, 'agg': 'airings'}` | 0.4048 | 0.4048 | 0.4240 | 0.2637 | 0.3601 | 0.3769 | 0.2296 |
| slot | `{'model': 'slot', 'daytype': 'we2', 'half_life': None, 'agg': 'airings'}` | 0.4035 | 0.4035 | 0.4218 | 0.2613 | 0.3588 | 0.3753 | 0.2272 |
| slot | `{'model': 'slot', 'daytype': 'dow7', 'half_life': 8, 'agg': 'airings'}` | 0.4034 | 0.4034 | 0.4230 | 0.2667 | 0.3582 | 0.3756 | 0.2328 |
| slot | `{'model': 'slot', 'daytype': 'dow7', 'half_life': None, 'agg': 'airings'}` | 0.4013 | 0.4013 | 0.4202 | 0.2631 | 0.3568 | 0.3738 | 0.2303 |
| slot | `{'model': 'slot', 'daytype': 'we2', 'half_life': 8, 'agg': 'hours'}` | 0.3813 | 0.3813 | 0.3700 | 0.3155 | 0.3347 | 0.3267 | 0.2712 |
| slot | `{'model': 'slot', 'daytype': 'we2', 'half_life': None, 'agg': 'hours'}` | 0.3753 | 0.3753 | 0.3656 | 0.3108 | 0.3326 | 0.3254 | 0.2685 |
| slot | `{'model': 'slot', 'daytype': 'dow7', 'half_life': 8, 'agg': 'hours'}` | 0.3707 | 0.3707 | 0.3599 | 0.3161 | 0.3261 | 0.3188 | 0.2715 |
| slot | `{'model': 'slot', 'daytype': 'dow7', 'half_life': None, 'agg': 'hours'}` | 0.3685 | 0.3685 | 0.3582 | 0.3134 | 0.3257 | 0.3186 | 0.2688 |
| slot | `{'model': 'replacement', 'daytype': 'we2', 'half_life': 8, 'agg': 'airings'}` | 0.1239 | 0.1239 | 0.1262 | 0.0869 | 0.1112 | 0.1164 | 0.0772 |

Selected slot config: `{'model': 'slot', 'daytype': 'we2', 'half_life': 8, 'agg': 'airings'}` (select 0.4048).

Total runtime: 18.2 s.
