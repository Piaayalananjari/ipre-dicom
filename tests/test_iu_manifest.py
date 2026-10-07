import csv
import tempfile
import unittest
from pathlib import Path

from scripts.build_iu_manifest import build_manifest, normalize_projection


class IUManifestTests(unittest.TestCase):
    def test_projection_normalization(self):
        self.assertEqual(normalize_projection("PA"), ("frontal", 0))
        self.assertEqual(normalize_projection("AP Portable"), ("frontal", 0))
        self.assertEqual(normalize_projection("Left Lateral"), ("lateral", 1))
        self.assertIsNone(normalize_projection("oblique"))

    def test_build_manifest_keeps_study_group(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = root / "images"
            images.mkdir()
            (images / "a.png").write_bytes(b"image-a")
            (images / "b.png").write_bytes(b"image-b")
            projections = root / "indiana_projections.csv"
            with projections.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["filename", "projection", "uid"])
                writer.writeheader()
                writer.writerow({"filename": "a.png", "projection": "PA", "uid": "study-1"})
                writer.writerow({"filename": "b.png", "projection": "lateral", "uid": "study-1"})
            output = root / "manifest.csv"

            stats = build_manifest(projections, images, output)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(stats["written"], 2)
            self.assertEqual({row["source_id"] for row in rows}, {"study-1"})
            self.assertEqual([row["view_label"] for row in rows], ["0", "1"])


if __name__ == "__main__":
    unittest.main()
