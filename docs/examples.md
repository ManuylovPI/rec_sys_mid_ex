# Recommendation examples

Produced by `python -m src.examples` from the validation predictions of `python -m src.report_tables` (history weeks 11-20, target weeks 21-30). Users chosen by the fixed rule in the module docstring: a heavy viewer (closest to the 90th percentile of history viewing time among test users with a non-empty cov50 target) and a light viewer with a thin history (1-20 distinct labelled shows touched in weeks 11-20, against a median of about 200; the one with the most cov50 target shows). Titles and categories are the most frequent values in the schedule.

Columns: **familiar** = watched by this user in weeks 11-20 (any overlap); **hit** = in the user's cov50 top-5 for weeks 21-30; **fallback** = slot filled by the shared popularity fallback.

## Heavy viewer: user 2725163102947201526

History weeks 11-20: 662.4 viewing hours, 504 distinct labelled shows watched. Target weeks 21-30: 5 shows in the cov50 top-5, 5 in the cov80 top-5.

### What the user actually watched (weeks 21-30)

| target | rank | id | title | category | > 50% watches | > 80% watches | familiar |
|---|---|---|---|---|---|---|---|
| cov50 | 1 | 12002378 | М/с 'Удивительный мир Гамбола'. | Детям | 11 | 11 | no |
| cov50 | 2 | 1000589 | Т/с 'Отчаянные домохозяйки', 5 сезон, 15 с. 'Мир, в котором короли работают'. | Сериалы | 8 | 6 | yes |
| cov50 | 3 | 2400508 | Сегодня. | Инфо | 7 | 6 | yes |
| cov50 | 4 | 5900256 | Утро с Украиной. | Инфо | 5 | 5 | yes |
| cov50 | 5 | 12002528 | М/с 'Время приключений'. | Детям | 5 | 5 | no |
| cov80 | 1 | 12002378 | М/с 'Удивительный мир Гамбола'. | Детям | 11 | 11 | no |
| cov80 | 2 | 1000589 | Т/с 'Отчаянные домохозяйки', 5 сезон, 15 с. 'Мир, в котором короли работают'. | Сериалы | 8 | 6 | yes |
| cov80 | 3 | 2400508 | Сегодня. | Инфо | 7 | 6 | yes |
| cov80 | 4 | 5900256 | Утро с Украиной. | Инфо | 5 | 5 | yes |
| cov80 | 5 | 12002528 | М/с 'Время приключений'. | Детям | 5 | 5 | no |

### Top-5 per method

**popularity**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400480 | ТСН. | Инфо | yes |  | – |
| 2 | 240081 | Факты. | Инфо | yes |  | – |
| 3 | 2400508 | Сегодня. | Инфо | yes | yes | – |
| 4 | 20088 | 'Завтрак с 1+1'. Информационно-развлекательная программа. | Развлечения | yes |  | – |
| 5 | 6500479 | 'Мир наизнанку'. | Познавательное | yes |  | – |

**ALS**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400508 | Сегодня. | Инфо | yes | yes |  |
| 2 | 240081 | Факты. | Инфо | yes |  |  |
| 3 | 2400480 | ТСН. | Инфо | yes |  |  |
| 4 | 2400467 | 'Викна-Новости'. | Инфо | yes |  |  |
| 5 | 20088 | 'Завтрак с 1+1'. Информационно-развлекательная программа. | Развлечения | yes |  |  |

**CBF**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 200477 | 'Завтрак. Выходной'. | Развлечения | no |  |  |
| 2 | 500315 | Ток-шоу 'Касается каждого'. | Развлечения | yes |  |  |
| 3 | 400357 | 'Холостяк', 10 сезон, 7 эп., 2 ч. | Развлечения | yes |  |  |
| 4 | 400373 | 'Холостяк'. Реалити-шоу, 7 сезон, 3 эп. | Развлечения | no |  |  |
| 5 | 6000473 | Половинки, 3 сезон, 3 эп. | Развлечения | no |  |  |

**repeat_cov**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400508 | Сегодня. | Инфо | yes | yes |  |
| 2 | 5900256 | Утро с Украиной. | Инфо | yes | yes |  |
| 3 | 240081 | Факты. | Инфо | yes |  |  |
| 4 | 2400480 | ТСН. | Инфо | yes |  |  |
| 5 | 2400467 | 'Викна-Новости'. | Инфо | yes |  |  |

**final (hybrid_v4_cov80)**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400508 | Сегодня. | Инфо | yes | yes |  |
| 2 | 240081 | Факты. | Инфо | yes |  |  |
| 3 | 5900256 | Утро с Украиной. | Инфо | yes | yes |  |
| 4 | 2400467 | 'Викна-Новости'. | Инфо | yes |  |  |
| 5 | 2400480 | ТСН. | Инфо | yes |  |  |

Summary: popularity: 5 familiar / 0 new, 1 hits, it is the fallback list; ALS: 5 familiar / 0 new, 1 hits, 0 fallback slots; CBF: 2 familiar / 3 new, 0 hits, 0 fallback slots; repeat_cov: 5 familiar / 0 new, 2 hits, 0 fallback slots; final (hybrid_v4_cov80): 5 familiar / 0 new, 2 hits, 0 fallback slots.

## Light viewer (thin history): user 3799694907521863650

History weeks 11-20: 2.6 viewing hours, 3 distinct labelled shows watched. Target weeks 21-30: 5 shows in the cov50 top-5, 5 in the cov80 top-5.

### What the user actually watched (weeks 21-30)

| target | rank | id | title | category | > 50% watches | > 80% watches | familiar |
|---|---|---|---|---|---|---|---|
| cov50 | 1 | 700389 | Кто сверху? | Развлечения | 2 | 1 | no |
| cov50 | 2 | 2400480 | ТСН. | Инфо | 2 | 1 | yes |
| cov50 | 3 | 12002733 | М/с 'Буба'. | Детям | 2 | 1 | no |
| cov50 | 4 | 400356 | 'Я стесняюсь своего тела. Украина'. | Познавательное | 1 | 0 | no |
| cov50 | 5 | 90044740 | Х/ф 'Бриллиантовая рука'. | Фильмы | 1 | 1 | no |
| cov80 | 1 | 700389 | Кто сверху? | Развлечения | 2 | 1 | no |
| cov80 | 2 | 2400480 | ТСН. | Инфо | 2 | 1 | yes |
| cov80 | 3 | 90044740 | Х/ф 'Бриллиантовая рука'. | Фильмы | 1 | 1 | no |
| cov80 | 4 | 2400467 | 'Викна-Новости'. | Инфо | 1 | 1 | no |
| cov80 | 5 | 12002733 | М/с 'Буба'. | Детям | 2 | 1 | no |

### Top-5 per method

**popularity**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400480 | ТСН. | Инфо | yes | yes | – |
| 2 | 240081 | Факты. | Инфо | no |  | – |
| 3 | 2400508 | Сегодня. | Инфо | no |  | – |
| 4 | 20088 | 'Завтрак с 1+1'. Информационно-развлекательная программа. | Развлечения | no |  | – |
| 5 | 6500479 | 'Мир наизнанку'. | Познавательное | yes |  | – |

**ALS**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 400361 | 'МастерШеф'. | Познавательное | no |  |  |
| 2 | 400335 | 'Хата на тата'. | Развлечения | no |  |  |
| 3 | 400357 | 'Холостяк', 10 сезон, 7 эп., 2 ч. | Развлечения | no |  |  |
| 4 | 2400467 | 'Викна-Новости'. | Инфо | no |  |  |
| 5 | 6500479 | 'Мир наизнанку'. | Познавательное | yes |  |  |

**CBF**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 400455 | Любовь на выживание, 3 сезон, 9 эп. | Познавательное | no |  |  |
| 2 | 6500479 | 'Мир наизнанку'. | Познавательное | yes |  |  |
| 3 | 400426 | 'Меняю жену'. | Развлечения | yes |  |  |
| 4 | 6500485 | Премьера. 'Невероятно интересные истории'. | Познавательное | no |  |  |
| 5 | 2400480 | ТСН. | Инфо | yes | yes |  |

**repeat_cov**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400480 | ТСН. | Инфо | yes | yes | yes |
| 2 | 240081 | Факты. | Инфо | no |  | yes |
| 3 | 2400508 | Сегодня. | Инфо | no |  | yes |
| 4 | 20088 | 'Завтрак с 1+1'. Информационно-развлекательная программа. | Развлечения | no |  | yes |
| 5 | 6500479 | 'Мир наизнанку'. | Познавательное | yes |  | yes |

**final (hybrid_v4_cov80)**

| rank | id | title | category | familiar | hit | fallback |
|---|---|---|---|---|---|---|
| 1 | 2400480 | ТСН. | Инфо | yes | yes |  |
| 2 | 2400467 | 'Викна-Новости'. | Инфо | no |  |  |
| 3 | 12001682 | М/с 'Губка Боб Квадратные Штаны'. | Детям | no |  |  |
| 4 | 240081 | Факты. | Инфо | no |  |  |
| 5 | 20088 | 'Завтрак с 1+1'. Информационно-развлекательная программа. | Развлечения | no |  |  |

Summary: popularity: 2 familiar / 3 new, 1 hits, it is the fallback list; ALS: 1 familiar / 4 new, 0 hits, 0 fallback slots; CBF: 3 familiar / 2 new, 1 hits, 0 fallback slots; repeat_cov: 2 familiar / 3 new, 1 hits, 5 fallback slots; final (hybrid_v4_cov80): 1 familiar / 4 new, 1 hits, 0 fallback slots.

