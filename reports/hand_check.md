# Hand check of AP@5 for one validation user

Prepared by the AI assistant for a by-hand computation by the student. The AP@5 below is the value the code computes
(`src.metrics.apk`); the hand computation below was done by the student in Excel.

- User: `2725163102947201526` (the heavy viewer of docs/examples.md)
- Split: history weeks 11-20, target weeks 21-30 (validation)
- Model: final setup (hybrid_v4_cov80 configuration), validation top-5 from the `src.run_all` run on 2026-10-24
  (data/processed/val_preds.parquet)
- Ground truth: the user's cov50 top-5 in weeks 21-30 = shows ranked by the number of airings where one
  continuous view covered more than 50% of the airing (ties by overlap seconds, then id)

## Predicted top-5 (in rank order)

| rank | tv_show_id | title |
|---|---|---|
| 1 | 2400508 | Сегодня. |
| 2 | 240081 | Факты. |
| 3 | 5900256 | Утро с Украиной. |
| 4 | 2400467 | 'Викна-Новости'. |
| 5 | 2400480 | ТСН. |

## Ground truth (cov50 top-5, order does not matter for AP)

| tv_show_id | title | > 50% watches in weeks 21-30 |
|---|---|---|
| 12002378 | М/с 'Удивительный мир Гамбола'. | 11 |
| 1000589 | Т/с 'Отчаянные домохозяйки', 4 сезон, 10 с. 'Добро пожаловать в Канагаву'. | 8 |
| 2400508 | Сегодня. | 7 |
| 5900256 | Утро с Украиной. | 5 |
| 12002528 | М/с 'Время приключений'. | 5 |

## Formula used by the code (Kaggle MAP@K, K = 5)

AP@5 = (1 / min(|truth|, 5)) * sum over ranks k = 1..5 of P(k) * rel(k), where rel(k) = 1 if the k-th prediction is
in the truth list and P(k) = (number of hits in the first k predictions) / k.

## Value printed by the code: AP@5 = 0.333333

## Hand computation (done by the student in Excel, screenshot reports/figures/hand_check.png)

| rank k | predicted id | rel(k) | hits so far | P(k) | P(k) * rel(k) |
|---|---|---|---|---|---|
| 1 | 2400508 | 1 | 1 | 1 | 1 |
| 2 | 240081 | 0 | 1 | 0.5 | 0 |
| 3 | 5900256 | 1 | 2 | 0.6667 | 0.6667 |
| 4 | 2400467 | 0 | 2 | 0.5 | 0 |
| 5 | 2400480 | 0 | 2 | 0.4 | 0 |

Sum = 1.6667 ; min(|truth|, 5) = 5 ; AP@5 by hand = 0.3333 ; matches the code value: yes
