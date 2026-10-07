import unittest

import numpy as np
from PIL import Image

from api.agent_workflow import build_report, run_report_workflow
from api.privacy import audit_dicom_privacy, non_dicom_privacy_audit
from api.quality import image_quality_metrics


class DatasetStub:
    PatientName = "Persona^Prueba"
    PatientID = "123"
    BurnedInAnnotation = "NO"


class ServiceTests(unittest.TestCase):
    def test_quality_metrics_are_bounded(self):
        image = Image.fromarray(np.full((32, 48), 128, dtype=np.uint8))
        metrics = image_quality_metrics(image)
        self.assertEqual(metrics["width"], 48)
        self.assertEqual(metrics["height"], 32)
        self.assertAlmostEqual(metrics["brightness_mean"], 128 / 255, places=3)
        self.assertEqual(metrics["noise_estimate"], 0.0)

    def test_privacy_does_not_leak_values(self):
        audit = audit_dicom_privacy(DatasetStub())
        self.assertEqual(audit["metadata_identifier_count"], 2)
        self.assertIn("PatientName", audit["metadata_identifiers_present"])
        self.assertNotIn("Persona^Prueba", str(audit))
        self.assertFalse(audit["anonymous"])

    def test_raster_privacy_requires_ocr(self):
        self.assertTrue(non_dicom_privacy_audit()["pixel_text_review_required"])

    def test_agent_report_is_bounded_and_structured(self):
        report = build_report({
            "results": {"noise": {"clean": 0.2, "noise": 0.8}},
            "privacy": non_dicom_privacy_audit(),
        })
        self.assertEqual(report["status"], "review")
        self.assertEqual(report["findings"][0]["code"], "noise")
        self.assertIn("no es diagnostico", report["disclaimer"])

    def test_agent_workflow_has_safe_fallback(self):
        report = run_report_workflow({"results": {}, "privacy": {}})
        self.assertEqual(report["status"], "ok")
        self.assertTrue(report["langgraph_ready"])

    def test_lateral_view_is_not_a_quality_finding(self):
        report = build_report({
            "results": {"view": {"frontal": 0.1, "lateral": 0.9}},
            "privacy": {},
        })
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
