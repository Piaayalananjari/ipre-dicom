import unittest

import numpy as np

from scripts.train_medmnist import compute_multilabel_metrics


class MedMNISTTrainingTests(unittest.TestCase):
    def test_perfect_binary_predictions(self):
        targets = np.array([[0], [1], [0], [1]])
        probabilities = np.array([[0.1], [0.9], [0.2], [0.8]])
        metrics = compute_multilabel_metrics(targets, probabilities)
        self.assertEqual(metrics["roc_auc_macro"], 1.0)
        self.assertEqual(metrics["f1_macro"], 1.0)
        self.assertEqual(metrics["label_accuracy"], 1.0)

    def test_multilabel_metrics(self):
        targets = np.array([[0, 1], [1, 0], [1, 1], [0, 0]])
        probabilities = targets * 0.8 + (1 - targets) * 0.2
        metrics = compute_multilabel_metrics(targets, probabilities)
        self.assertEqual(metrics["roc_auc_macro"], 1.0)
        self.assertEqual(metrics["f1_macro"], 1.0)


if __name__ == "__main__":
    unittest.main()
