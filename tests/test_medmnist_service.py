import os
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from api.medmnist_service import list_datasets, sample_png


class MedMNISTServiceTests(unittest.TestCase):
    def test_catalog_does_not_download_data(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {"MEDMNIST_ROOT": root}):
            catalog = list_datasets()
        self.assertEqual([item["id"] for item in catalog], ["chestmnist", "pneumoniamnist"])
        self.assertEqual(catalog[0]["installed_sizes"], [])

    def test_reads_local_sample(self):
        class FakeDataset:
            def __len__(self):
                return 2

            def __getitem__(self, index):
                return Image.fromarray(np.zeros((28, 28), dtype=np.uint8)), np.array([index])

        with patch("api.medmnist_service.load_dataset", return_value=FakeDataset()):
            content, sample_labels, count = sample_png("pneumoniamnist", "test", 28, 1)
        self.assertTrue(content.startswith(b"\x89PNG"))
        self.assertEqual(sample_labels, [1])
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
