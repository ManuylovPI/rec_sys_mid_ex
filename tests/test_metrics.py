"""Hand-computed MAP@5 examples. Run: python -m unittest tests.test_metrics"""
import unittest

from src.metrics import apk, mapk


class TestMap5(unittest.TestCase):
    def test_apk_hand_example(self):
        # actual {1, 2, 3}; hits at ranks 1 and 3 -> (1/1 + 2/3) / min(3, 5) = 5/9
        self.assertAlmostEqual(apk([1, 2, 3], [1, 9, 2, 8, 7]), 5 / 9)

    def test_apk_denominator_capped_at_k(self):
        # 7 relevant items, all 5 predictions hit -> 5/5 = 1
        self.assertAlmostEqual(apk(list(range(7)), [0, 1, 2, 3, 4]), 1.0)

    def test_apk_short_truth(self):
        # actual {4}; hit at rank 2 -> (1/2) / 1
        self.assertAlmostEqual(apk([4], [9, 4, 8, 7, 6]), 0.5)

    def test_apk_only_first_k(self):
        self.assertEqual(apk([6], [1, 2, 3, 4, 5, 6]), 0.0)

    def test_empty_truth_counts_zero(self):
        self.assertEqual(apk([], [1, 2, 3, 4, 5]), 0.0)

    def test_mapk_average_over_users(self):
        # users: 5/9, 0.5, 0 (empty truth) -> (5/9 + 1/2 + 0) / 3 = 19/54
        actual = [[1, 2, 3], [4], []]
        predicted = [[1, 9, 2, 8, 7], [9, 4, 8, 7, 6], [1, 2, 3, 4, 5]]
        self.assertAlmostEqual(mapk(actual, predicted), 19 / 54)


if __name__ == "__main__":
    unittest.main()
