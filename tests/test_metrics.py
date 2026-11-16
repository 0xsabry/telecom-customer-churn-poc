import unittest

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from src.gci_telecom_churn_analysis import auc_score, average_precision


class BinaryRankingMetricTests(unittest.TestCase):
    def test_roc_auc_all_tied_scores_is_chance_level(self):
        self.assertEqual(auc_score([0, 1], [0.5, 0.5]), 0.5)

    def test_roc_auc_matches_sklearn_for_perfect_and_reversed_order(self):
        self.assertEqual(auc_score([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)
        self.assertEqual(auc_score([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]), 0.0)

    def test_roc_auc_matches_sklearn_with_repeated_ties(self):
        labels = np.array([0, 1, 0, 1, 1, 0])
        scores = np.array([0.2, 0.2, 0.5, 0.5, 0.8, 0.8])
        self.assertAlmostEqual(auc_score(labels, scores), roc_auc_score(labels, scores))

    def test_average_precision_all_tied_scores_is_prevalence(self):
        labels = np.array([0, 1, 0, 1])
        scores = np.full(4, 0.5)
        self.assertEqual(average_precision(labels, scores), 0.5)

    def test_average_precision_matches_sklearn_with_repeated_ties(self):
        labels = np.array([0, 1, 0, 1, 1, 0])
        scores = np.array([0.2, 0.2, 0.5, 0.5, 0.8, 0.8])
        self.assertAlmostEqual(
            average_precision(labels, scores),
            average_precision_score(labels, scores),
        )

    def test_metrics_reject_single_class_targets(self):
        for metric in (auc_score, average_precision):
            with self.subTest(metric=metric.__name__):
                with self.assertRaisesRegex(ValueError, "each class"):
                    metric([1, 1], [0.2, 0.8])


if __name__ == "__main__":
    unittest.main()
