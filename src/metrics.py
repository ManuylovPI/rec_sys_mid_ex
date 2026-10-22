"""MAP@K as computed by Kaggle (ml_metrics.apk / mapk).

AP@K = sum over ranks i <= K of P(i) * rel(i), divided by min(len(actual), K).
A repeated prediction is not counted twice; users with an empty ground truth score 0.
"""
from collections.abc import Sequence

K = 5


def apk(actual: Sequence, predicted: Sequence, k: int = K) -> float:
    if not actual:
        return 0.0
    actual_set = set(actual)
    predicted = list(predicted)[:k]
    hits, score = 0, 0.0
    for i, p in enumerate(predicted):
        if p in actual_set and p not in predicted[:i]:
            hits += 1
            score += hits / (i + 1.0)
    return score / min(len(actual_set), k)


def mapk(actual: Sequence[Sequence], predicted: Sequence[Sequence], k: int = K) -> float:
    if len(actual) != len(predicted):
        raise ValueError("actual and predicted must have one entry per user")
    if not actual:
        return 0.0
    return sum(apk(a, p, k) for a, p in zip(actual, predicted)) / len(actual)
