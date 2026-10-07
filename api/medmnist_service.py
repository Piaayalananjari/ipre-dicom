from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

from PIL import Image


DATASETS = {
    "chestmnist": {
        "class_name": "ChestMNIST",
        "task": "multi-label, 14 hallazgos de radiografia de torax",
    },
    "pneumoniamnist": {
        "class_name": "PneumoniaMNIST",
        "task": "clasificacion binaria normal/neumonia pediatrica",
    },
}
SIZES = (28, 64, 128, 224)
SPLITS = ("train", "val", "test")


def dataset_root() -> Path:
    return Path(os.getenv("MEDMNIST_ROOT", "data/medmnist")).expanduser().resolve()


def _package():
    try:
        import medmnist
    except ImportError as exc:
        raise RuntimeError("MedMNIST no esta instalado. Ejecute: pip install medmnist") from exc
    return medmnist


def list_datasets() -> list[dict]:
    root = dataset_root()
    return [
        {
            "id": flag,
            **config,
            "sizes": list(SIZES),
            "installed_sizes": [size for size in SIZES if (root / _filename(flag, size)).exists()],
        }
        for flag, config in DATASETS.items()
    ]


def _filename(flag: str, size: int) -> str:
    suffix = "" if size == 28 else f"_{size}"
    return f"{flag}{suffix}.npz"


def load_dataset(flag: str, split: str, size: int, download: bool = False):
    if flag not in DATASETS:
        raise ValueError(f"Dataset no soportado: {flag}")
    if split not in SPLITS:
        raise ValueError(f"Split no soportado: {split}")
    if size not in SIZES:
        raise ValueError(f"Tamano no soportado: {size}")

    medmnist = _package()
    root = dataset_root()
    root.mkdir(parents=True, exist_ok=True)
    dataset_class = getattr(medmnist, DATASETS[flag]["class_name"])
    try:
        return dataset_class(split=split, size=size, root=str(root), download=download)
    except (OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(
            f"El archivo {_filename(flag, size)} esta incompleto o corrupto; vuelva a descargarlo."
        ) from exc


def sample_png(flag: str, split: str, size: int, index: int) -> tuple[bytes, list[int], int]:
    dataset = load_dataset(flag, split, size, download=False)
    if index < 0 or index >= len(dataset):
        raise IndexError(f"Indice fuera de rango: 0..{len(dataset) - 1}")

    image, label = dataset[index]
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    labels = [int(value) for value in label.reshape(-1).tolist()]
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue(), labels, len(dataset)
