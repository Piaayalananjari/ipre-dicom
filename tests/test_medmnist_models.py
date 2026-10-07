import unittest

from api.medmnist_models import binary_predictions, label_names


class MedMNISTModelTests(unittest.TestCase):
    def test_pneumonia_labels(self):
        self.assertEqual(label_names("pneumoniamnist"), ["normal", "pneumonia"])

    def test_chest_has_fourteen_labels(self):
        self.assertEqual(len(label_names("chestmnist")), 14)

    def test_binary_probability_is_assigned_to_positive_class(self):
        predictions = binary_predictions(["normal", "pneumonia"], 0.8)
        self.assertEqual(predictions, [
            {"label": "normal", "probability": 0.2},
            {"label": "pneumonia", "probability": 0.8},
        ])


if __name__ == "__main__":
    unittest.main()
