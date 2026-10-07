"""Prepara imágenes no identificables para demostrar IPRE-DICOM.

Usa una muestra pública de PneumoniaMNIST y crea variantes controladas. No genera
etiquetas clínicas nuevas ni usa información de pacientes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.medmnist_service import load_dataset


def prepare_assets(root: Path, output: Path, index: int, size: int, download: bool) -> dict:
    os.environ["MEDMNIST_ROOT"] = str(root.resolve())
    dataset = load_dataset("pneumoniamnist", "test", size, download=download)
    if index < 0 or index >= len(dataset):
        raise ValueError(f"Indice fuera de rango: 0..{len(dataset) - 1}")

    image, label = dataset[index]
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    base = image.convert("L").resize((512, 512), Image.Resampling.BICUBIC)

    output.mkdir(parents=True, exist_ok=True)
    original_path = output / "01_original_medmnist.png"
    rotated_path = output / "02_rotada_25_grados.png"
    noisy_path = output / "03_ruidosa.png"
    volume_path = output / "04_volumen_demo.npy"

    base.save(original_path)
    base.rotate(25, resample=Image.Resampling.BICUBIC, fillcolor=0).save(rotated_path)

    rng = np.random.default_rng(42)
    array = np.asarray(base, dtype=np.float32)
    noisy = np.clip(array + rng.normal(0, 35, array.shape), 0, 255).astype(np.uint8)
    Image.fromarray(noisy).filter(ImageFilter.GaussianBlur(radius=0.4)).save(noisy_path)

    # Volumen artificial para mostrar que la API abre .npy, sin afirmar que es CT/MR.
    volume = np.stack([np.asarray(base, dtype=np.float32) * factor for factor in (0.6, 0.8, 1.0, 0.8, 0.6)], axis=-1)
    np.save(volume_path, volume)

    manifest = {
        "source": "PneumoniaMNIST test split",
        "index": index,
        "source_size": size,
        "dataset_label": [int(value) for value in np.asarray(label).reshape(-1)],
        "warning": "Etiqueta original del dataset; no es una prediccion ni diagnostico.",
        "files": [str(path.resolve()) for path in (original_path, rotated_path, noisy_path, volume_path)],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(os.getenv("MEDMNIST_ROOT", "data/medmnist")))
    parser.add_argument("--output", type=Path, default=Path("demo_assets"))
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--size", type=int, choices=(28, 64, 128, 224), default=28)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()

    try:
        manifest = prepare_assets(args.root, args.output, args.index, args.size, args.download)
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(manifest, indent=2))
    print("\nArchivos de demostracion listos. Inicie la API y carguelos desde el visor.")


if __name__ == "__main__":
    main()
