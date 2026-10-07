import io
import unittest

import torch
from fastapi.testclient import TestClient
from PIL import Image

import api.main as api_main


class FixedViewModel(torch.nn.Module):
    def forward(self, tensor):
        return torch.tensor([[-1.0, 2.0]], device=tensor.device).repeat(tensor.shape[0], 1)


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(api_main.app)

    def setUp(self):
        self.original_models = dict(api_main.models)
        self.original_transforms = dict(api_main.transforms)
        api_main.models.clear()
        api_main.transforms.clear()

    def tearDown(self):
        api_main.models.clear()
        api_main.models.update(self.original_models)
        api_main.transforms.clear()
        api_main.transforms.update(self.original_transforms)

    @staticmethod
    def png_bytes() -> bytes:
        buffer = io.BytesIO()
        Image.new("L", (32, 24), color=128).save(buffer, format="PNG")
        return buffer.getvalue()

    def test_formats_endpoint(self):
        response = self.client.get("/formats")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["max_upload_mib"], 64)

    def test_predict_png_without_checkpoints_returns_metrics(self):
        response = self.client.post(
            "/predict",
            files={"file": ("sample.png", self.png_bytes(), "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["input"]["format"], "raster")
        self.assertEqual(body["quality_metrics"]["width"], 32)
        self.assertEqual(body["results"], {})

    def test_predict_rejects_invalid_raster(self):
        response = self.client.post(
            "/predict",
            files={"file": ("broken.png", b"not-an-image", "image/png")},
        )
        self.assertEqual(response.status_code, 400)

    def test_view_model_uses_frontal_lateral_labels(self):
        api_main.models["view"] = FixedViewModel()
        api_main.transforms["view"] = lambda item: {
            "img": torch.from_numpy(item["img"].copy()).float().unsqueeze(0)
        }
        response = self.client.post(
            "/predict",
            files={"file": ("sample.png", self.png_bytes(), "image/png")},
        )
        self.assertEqual(response.status_code, 200)
        prediction = response.json()["results"]["view"]
        self.assertEqual(set(prediction), {"frontal", "lateral"})
        self.assertGreater(prediction["lateral"], prediction["frontal"])
        self.assertNotIn("view", {item["code"] for item in response.json()["agent_report"]["findings"]})


if __name__ == "__main__":
    unittest.main()
