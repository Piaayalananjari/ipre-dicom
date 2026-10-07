import gzip
import io
import unittest

import nibabel as nib
import numpy as np

from api.image_io import load_nifti, load_numpy, normalized_extension, supported_formats


class ImageIOTests(unittest.TestCase):
    def test_compound_extension(self):
        self.assertEqual(normalized_extension("brain.NII.GZ"), ".nii.gz")

    def test_numpy_volume_selects_center_slice(self):
        buffer = io.BytesIO()
        np.save(buffer, np.arange(4 * 5 * 6, dtype=np.float32).reshape(4, 5, 6))
        loaded = load_numpy(buffer.getvalue())
        self.assertEqual(loaded.image.size, (5, 4))
        self.assertEqual(loaded.metadata["original_shape"], [4, 5, 6])
        self.assertEqual(loaded.metadata["selected_slices"], [{"axis": 2, "index": 3}])

    def test_nifti_gzip_volume(self):
        image = nib.Nifti1Image(np.ones((8, 9, 10), dtype=np.float32), np.eye(4))
        loaded = load_nifti(gzip.compress(image.to_bytes()), compressed=True)
        self.assertEqual(loaded.image.size, (9, 8))
        self.assertEqual(loaded.metadata["original_shape"], [8, 9, 10])

    def test_formats_document_medmnist_npz_separately(self):
        families = {item["family"] for item in supported_formats()}
        self.assertIn("DICOM", families)
        self.assertIn("NIfTI-1", families)
        self.assertIn("MedMNIST", families)


if __name__ == "__main__":
    unittest.main()
