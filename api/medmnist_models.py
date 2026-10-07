from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import torch
from medmnist import INFO
from monai.networks.nets import DenseNet121
from PIL import Image


class MedMNISTModelRegistry:
    def __init__(self, model_dir: Path, device: torch.device):
        self.model_dir = model_dir
        self.device = device
        self.models: dict[str, dict] = {}

    def load(self) -> None:
        self.models.clear()
        for path in sorted(self.model_dir.glob("medmnist_*.pt")):
            try:
                checkpoint = torch.load(path, map_location=self.device)
                dataset = str(checkpoint["dataset"])
                size = int(checkpoint["size"])
                output_channels = int(checkpoint["output_channels"])
                model = DenseNet121(
                    spatial_dims=2,
                    in_channels=1,
                    out_channels=output_channels,
                ).to(self.device)
                model.load_state_dict(checkpoint["state_dict"])
                model.eval()
                self.models[dataset] = {
                    "model": model,
                    "size": size,
                    "output_channels": output_channels,
                    "path": path,
                    "best_val_roc_auc": checkpoint.get("best_val_roc_auc"),
                }
            except (KeyError, RuntimeError, ValueError, TypeError) as exc:
                print(f"Checkpoint MedMNIST ignorado ({path}): {exc}")

    def catalog(self) -> list[dict]:
        return [
            {
                "dataset": dataset,
                "size": entry["size"],
                "output_channels": entry["output_channels"],
                "best_val_roc_auc": entry["best_val_roc_auc"],
                "labels": label_names(dataset),
            }
            for dataset, entry in sorted(self.models.items())
        ]

    def predict(self, dataset: str, image: Image.Image) -> dict:
        if dataset not in self.models:
            raise KeyError(dataset)
        entry = self.models[dataset]
        array = np.asarray(
            image.convert("L").resize((entry["size"], entry["size"])),
            dtype=np.float32,
        ) / 255.0
        tensor = torch.from_numpy((array - 0.5) / 0.5)[None, None].to(self.device)
        with torch.no_grad():
            probabilities = torch.sigmoid(entry["model"](tensor))[0].cpu().numpy()
        names = label_names(dataset)
        if entry["output_channels"] == 1 and len(names) == 2:
            formatted_predictions = binary_predictions(names, float(probabilities[0]))
        else:
            formatted_predictions = [
                {"label": names[index], "probability": round(float(value), 5)}
                for index, value in enumerate(probabilities)
            ]
        return {
            "dataset": dataset,
            "input_size": entry["size"],
            "predictions": formatted_predictions,
            "warning": "Clasificacion experimental; no es diagnostico medico.",
        }


def label_names(dataset: str) -> list[str]:
    info = INFO.get(dataset, {})
    labels = info.get("label", {})
    return [str(labels.get(str(index), index)) for index in range(len(labels))]


def binary_predictions(names: list[str], positive: float) -> list[dict]:
    return [
        {"label": names[0], "probability": round(1.0 - positive, 5)},
        {"label": names[1], "probability": round(positive, 5)},
    ]


def raster_image_from_bytes(content: bytes) -> Image.Image:
    return Image.open(io.BytesIO(content)).convert("L")
