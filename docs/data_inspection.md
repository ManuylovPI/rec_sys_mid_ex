# Raw data inspection

Generated 2026-10-24 12:37:44 on Windows-10-10.0.26200-SP0, Python 3.11.9, duckdb 2.0.0.

All numbers below are produced by `python -m src.inspect_raw` on the unmodified files in `data/raw/`.

## Row counts

| file | n_rows |
|---|---|
| dataset11-30.csv | 5821987 |
| export_arh_11-20-final.csv | 1074235 |
| export_arh_21-30-final.csv | 1074394 |
| export_arh_31-42-final.csv | 1295378 |
| submission.csv | 1260 |

## View log: columns

| column_name | column_type | null | key | default | extra |
|---|---|---|---|---|---|
| user_id | UBIGINT | YES |  |  |  |
| vsetv_id | INTEGER | YES |  |  |  |
| start_time | TIMESTAMP | YES |  |  |  |
| stop_time | TIMESTAMP | YES |  |  |  |
| duraton | BIGINT | YES |  |  |  |

## Schedule: columns (all three files share them)

| column_name | column_type | null | key | default | extra |
|---|---|---|---|---|---|
| channel_id | INTEGER | YES |  |  |  |
| channel_title | VARCHAR | YES |  |  |  |
| duration | BIGINT | YES |  |  |  |
| tv_show_title | VARCHAR | YES |  |  |  |
| tv_show_id | BIGINT | YES |  |  |  |
| tv_show_category | VARCHAR | YES |  |  |  |
| tv_show_genre_1 | VARCHAR | YES |  |  |  |
| tv_show_genre_2 | VARCHAR | YES |  |  |  |
| tv_show_genre_3 | VARCHAR | YES |  |  |  |
| year_of_production | VARCHAR | YES |  |  |  |
| director | VARCHAR | YES |  |  |  |
| actors | VARCHAR | YES |  |  |  |
| start_time | TIMESTAMP | YES |  |  |  |

## View log: first rows (times are stored as 'YYYY-MM-DD HH:MM:SS' strings)

| user_id | vsetv_id | start_time | stop_time | duraton |
|---|---|---|---|---|
| 3398461054087191302 | 6 | 2020-03-09 00:00:02 | 2020-03-09 00:01:53 | 111 |
| 17226860011138219284 | 353 | 2020-03-09 00:00:02 | 2020-03-09 00:03:26 | 204 |
| 18417531283109304442 | 332 | 2020-03-09 00:00:05 | 2020-03-09 00:01:26 | 81 |
| 3677642666679759206 | 7 | 2020-03-09 00:00:08 | 2020-03-09 01:07:41 | 4053 |
| 15105343836194894915 | 108 | 2020-03-09 00:00:10 | 2020-03-09 00:02:34 | 144 |

## Schedule: first rows (times are stored as 'DD.MM.YYYY HH:MM:SS' strings, parsed here)

| channel_id | channel_title | start_time | duration | tv_show_title | tv_show_id | tv_show_category |
|---|---|---|---|---|---|---|
| 3 | 1+1 | 2020-03-09 06:00:00 | 6000 | 'Жизнь известных людей', 2 сезон. | 0 | Другое |
| 3 | 1+1 | 2020-03-09 07:40:00 | 5400 | 'ТСН. Неделя'. | 2400480 | Инфо |
| 3 | 1+1 | 2020-03-09 09:10:00 | 8400 | 'Голос страны', 10 сезон, 8 эп. 'Бои'. | 700475 | Развлечения |
| 3 | 1+1 | 2020-03-09 11:30:00 | 28800 | Т/с 'По праву любви', 1-8 с. | 0 | Сериалы |
| 3 | 1+1 | 2020-03-09 19:30:00 | 2700 | ТСН. | 2400480 | Инфо |

## View log: summary

| n | users | channels | min_start | max_start | max_stop | min_dur | median_dur | p90_dur | max_dur | dur_ne_stop_minus_start | negative_intervals |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5821987 | 4914 | 202 | 2020-03-09 00:00:02 | 2020-07-26 23:58:42 | 2020-07-26 23:59:58 | 61 | 396 | 3911 | 342145 | 117 | 0 |

## View log: rows and users per ISO week (week = ISO week of start_time, Monday 00:00 start)

| iso_year | week | first_day | last_day | n_views | users | views_per_user |
|---|---|---|---|---|---|---|
| 2020 | 11 | 2020-03-09 | 2020-03-15 | 407493 | 4697 | 86.8 |
| 2020 | 12 | 2020-03-16 | 2020-03-22 | 452314 | 4721 | 95.8 |
| 2020 | 13 | 2020-03-23 | 2020-03-29 | 465318 | 4689 | 99.2 |
| 2020 | 14 | 2020-03-30 | 2020-04-05 | 428820 | 4666 | 91.9 |
| 2020 | 15 | 2020-04-06 | 2020-04-12 | 412698 | 4658 | 88.6 |
| 2020 | 16 | 2020-04-13 | 2020-04-19 | 406317 | 4682 | 86.8 |
| 2020 | 17 | 2020-04-20 | 2020-04-26 | 417854 | 4638 | 90.1 |
| 2020 | 18 | 2020-04-27 | 2020-05-03 | 385637 | 4599 | 83.9 |
| 2020 | 19 | 2020-05-04 | 2020-05-10 | 336042 | 4606 | 73 |
| 2020 | 20 | 2020-05-11 | 2020-05-17 | 232680 | 4220 | 55.1 |
| 2020 | 21 | 2020-05-18 | 2020-05-24 | 182044 | 3572 | 51 |
| 2020 | 22 | 2020-05-25 | 2020-05-31 | 192998 | 3562 | 54.2 |
| 2020 | 23 | 2020-06-01 | 2020-06-07 | 162882 | 3440 | 47.3 |
| 2020 | 24 | 2020-06-08 | 2020-06-14 | 156928 | 3252 | 48.3 |
| 2020 | 25 | 2020-06-15 | 2020-06-21 | 138807 | 3108 | 44.7 |
| 2020 | 26 | 2020-06-22 | 2020-06-28 | 126940 | 2406 | 52.8 |
| 2020 | 27 | 2020-06-29 | 2020-07-05 | 105223 | 4275 | 24.6 |
| 2020 | 28 | 2020-07-06 | 2020-07-12 | 271172 | 4620 | 58.7 |
| 2020 | 29 | 2020-07-13 | 2020-07-19 | 261698 | 4620 | 56.6 |
| 2020 | 30 | 2020-07-20 | 2020-07-26 | 278122 | 4565 | 60.9 |

## View log: share of views by start hour (%)

| hour | pct |
|---|---|
| 0 | 2.77 |
| 1 | 1.34 |
| 2 | 0.67 |
| 3 | 0.49 |
| 4 | 0.5 |
| 5 | 0.71 |
| 6 | 1.62 |
| 7 | 2.81 |
| 8 | 3.62 |
| 9 | 4.06 |
| 10 | 3.96 |
| 11 | 3.92 |
| 12 | 4.11 |
| 13 | 4.16 |
| 14 | 4.27 |
| 15 | 4.57 |
| 16 | 4.85 |
| 17 | 5.65 |
| 18 | 6.58 |
| 19 | 7.77 |
| 20 | 8.79 |
| 21 | 9.31 |
| 22 | 8.1 |
| 23 | 5.35 |

## View log: rows where the same user starts a view before their previous view ended

Across all channels. The interaction build merges overlaps per (user, channel).

| n_overlapping |
|---|
| 379324 |

## Schedule 11-20: summary

| n | labelled | labelled_pct | programmes_excl_0 | programmes_incl_0 | channels | categories | min_start | max_start | min_duration | median_duration | max_duration |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1074235 | 115613 | 10.76 | 5847 | 5848 | 400 | 9 | 2020-03-08 23:00:00 | 2020-05-18 11:45:00 | 0 | 1500 | 86400 |

## Schedule 11-20: rows per ISO week of start_time

| week | first_day | last_day | n |
|---|---|---|---|
| 10 | 2020-03-08 | 2020-03-08 | 86 |
| 11 | 2020-03-09 | 2020-03-15 | 106036 |
| 12 | 2020-03-16 | 2020-03-22 | 108177 |
| 13 | 2020-03-23 | 2020-03-29 | 107363 |
| 14 | 2020-03-30 | 2020-04-05 | 106527 |
| 15 | 2020-04-06 | 2020-04-12 | 108126 |
| 16 | 2020-04-13 | 2020-04-19 | 107697 |
| 17 | 2020-04-20 | 2020-04-26 | 107721 |
| 18 | 2020-04-27 | 2020-05-03 | 107505 |
| 19 | 2020-05-04 | 2020-05-10 | 105473 |
| 20 | 2020-05-11 | 2020-05-17 | 107093 |
| 21 | 2020-05-18 | 2020-05-18 | 2431 |

## Schedule 21-30: summary

| n | labelled | labelled_pct | programmes_excl_0 | programmes_incl_0 | channels | categories | min_start | max_start | min_duration | median_duration | max_duration |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1074394 | 121505 | 11.31 | 6363 | 6364 | 403 | 9 | 2020-05-18 00:00:00 | 2020-07-27 11:55:00 | 60 | 1500 | 86400 |

## Schedule 21-30: rows per ISO week of start_time

| week | first_day | last_day | n |
|---|---|---|---|
| 21 | 2020-05-18 | 2020-05-24 | 104798 |
| 22 | 2020-05-25 | 2020-05-31 | 107274 |
| 23 | 2020-06-01 | 2020-06-07 | 107657 |
| 24 | 2020-06-08 | 2020-06-14 | 107449 |
| 25 | 2020-06-15 | 2020-06-21 | 107104 |
| 26 | 2020-06-22 | 2020-06-28 | 107544 |
| 27 | 2020-06-29 | 2020-07-05 | 106878 |
| 28 | 2020-07-06 | 2020-07-12 | 107528 |
| 29 | 2020-07-13 | 2020-07-19 | 107640 |
| 30 | 2020-07-20 | 2020-07-26 | 108093 |
| 31 | 2020-07-27 | 2020-07-27 | 2429 |

## Schedule 31-42: summary

| n | labelled | labelled_pct | programmes_excl_0 | programmes_incl_0 | channels | categories | min_start | max_start | min_duration | median_duration | max_duration |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1295378 | 144774 | 11.18 | 6636 | 6637 | 404 | 9 | 2020-07-27 00:00:00 | 2020-10-19 11:55:00 | 60 | 1500 | 43200 |

## Schedule 31-42: rows per ISO week of start_time

| week | first_day | last_day | n |
|---|---|---|---|
| 31 | 2020-07-27 | 2020-08-02 | 105719 |
| 32 | 2020-08-03 | 2020-08-09 | 108256 |
| 33 | 2020-08-10 | 2020-08-16 | 107039 |
| 34 | 2020-08-17 | 2020-08-23 | 106862 |
| 35 | 2020-08-24 | 2020-08-30 | 107028 |
| 36 | 2020-08-31 | 2020-09-06 | 107492 |
| 37 | 2020-09-07 | 2020-09-13 | 107558 |
| 38 | 2020-09-14 | 2020-09-20 | 108258 |
| 39 | 2020-09-21 | 2020-09-27 | 108512 |
| 40 | 2020-09-28 | 2020-10-04 | 108763 |
| 41 | 2020-10-05 | 2020-10-11 | 108843 |
| 42 | 2020-10-12 | 2020-10-18 | 108649 |
| 43 | 2020-10-19 | 2020-10-19 | 2399 |

## Schedule: duration units (duration vs gap to the next airing on the same channel, within file)

| file | n_pairs | share_equal_seconds | share_equal_if_minutes | share_gap_after | share_overlap |
|---|---|---|---|---|---|
| 11-20 | 1073835 | 0.9996 | 0 | 0.0004 | 0 |
| 21-30 | 1073991 | 1 | 0 | 0 | 0 |
| 31-42 | 1294974 | 1 | 0 | 0 | 0 |

## Schedule: categories (11-20)

| tv_show_category | n |
|---|---|
| Другое | 484058 |
| Познавательное | 221981 |
| Детям | 104593 |
| Сериалы | 72031 |
| Спорт | 62197 |
| Инфо | 50585 |
| Фильмы | 41579 |
| Музыка | 29200 |
| Развлечения | 8011 |

## Schedule: zero-length rows and duplicate (channel_id, start_time) keys

| file | zero_duration | duplicate_keys |
|---|---|---|
| 11-20 | 1 | 1 |
| 21-30 | 0 | 0 |
| 31-42 | 0 | 0 |

## DST evidence: view starts per hour on 2020-03-29 00:00-06:00 (Kyiv clocks jumped 03:00 -> 04:00)

| hour | n |
|---|---|
| 0 | 1740 |
| 1 | 938 |
| 2 | 424 |
| 4 | 290 |
| 5 | 334 |

## DST evidence: channel 3 grid on the same night (01:25 + 6000 s = 03:05, next airing 04:05)

| start_time | duration | tv_show_title |
|---|---|---|
| 2020-03-28 23:25:00 | 7200 | 'Светская жизнь с Катериной Осадчей'. |
| 2020-03-29 01:25:00 | 6000 | 'Лига смеха', 6 сезон, 3 эп. |
| 2020-03-29 04:05:00 | 4500 | 'Чистоnews'. |
| 2020-03-29 05:20:00 | 2400 | ТСН. |
| 2020-03-29 06:00:00 | 1500 | Детский кинозал. Мультфильм. |
| 2020-03-29 06:25:00 | 5700 | 'Жизнь известных людей', 2 сезон. |

## File hand-off: rows starting after the file's last ISO week (overhang)

| source_file | n_overhang | last_start | starting_at_or_after_06 |
|---|---|---|---|
| 11-20 | 2431 | 2020-05-18 11:45:00 | 206 |
| 21-30 | 2429 | 2020-07-27 11:55:00 | 201 |
| 31-42 | 2399 | 2020-10-19 11:55:00 | 207 |

## File hand-off: overlaps between consecutive airings on a channel after gluing all files

Few overlaps and only one across files: the files hand off cleanly and can simply be unioned.

| source_file | next_file | n_overlaps |
|---|---|---|
| 11-20 | 11-20 | 2 |
| 11-20 | 21-30 | 1 |
| 21-30 | 21-30 | 2 |
| 31-42 | 31-42 | 8 |

## Week-10 rows (2020-03-08) that run into week 11

| n_week10 | end_in_week11 | max_end |
|---|---|---|
| 86 | 27 | 2020-03-09 02:00:00 |

## Channels: view-log vsetv_id vs schedule channel_id

| view_channels | schedule_channels | in_both |
|---|---|---|
| 202 | 405 | 197 |

## Channels: top-10 viewed vsetv_id with the schedule's channel_title for that id

| vsetv_id | n_views | schedule_title |
|---|---|---|
| 3 | 589869 | 1+1 |
| 5 | 442553 | ICTV |
| 7 | 315759 | Новый канал |
| 6 | 312470 | СТБ |
| 108 | 298457 | Украина |
| 4 | 256323 | Интер |
| 1521 | 220057 | TV1000 Action CEE |
| 921 | 207769 | 112 Украина |
| 23 | 152860 | 2+2 |
| 1516 | 147868 | TV1000 CEE |

## Channels: viewed channels absent from every schedule (views can never match)

| vsetv_id | n_views |
|---|---|
| 1174 | 86883 |
| 1510 | 9357 |
| 1509 | 8546 |
| 1508 | 7491 |
| 149 | 1302 |

## Coverage: random sample of 100,000 views from weeks 21-30 (seed 42)

| n | pct_overlap_any_airing | pct_overlap_labelled_airing |
|---|---|---|
| 100000 | 97.59 | 56.83 |

## Labelled programmes airing in weeks 31-42 that also air in a training schedule

| test_pool_weeks_31_42 | also_in_training |
|---|---|
| 6632 | 5197 |

## Submission template

| n_rows | users | in_view_log | with_views_wk11_20 | with_views_wk21_30 | distinct_template_values |
|---|---|---|---|---|---|
| 1260 | 1260 | 1260 | 1256 | 1246 | 0 0 0 0 0 |

Runtime: 20.2 s.
