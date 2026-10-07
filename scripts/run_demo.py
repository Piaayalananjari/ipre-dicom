"""Ejecuta una demostración reproducible de la API sin iniciar un servidor externo."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import api.main as api_main  # noqa: E402


DEMO_FILES = (
    "01_original_medmnist.png",
    "02_rotada_25_grados.png",
    "03_ruidosa.png",
    "04_volumen_demo.npy",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path("demo_assets"))
    parser.add_argument("--medmnist-root", type=Path, default=Path("data/medmnist"))
    parser.add_argument("--output", type=Path, default=Path("demo_assets/demo_results.json"))
    args = parser.parse_args()

    os.environ["MEDMNIST_ROOT"] = str(args.medmnist_root.resolve())
    missing = [name for name in DEMO_FILES if not (args.assets / name).exists()]
    if missing:
        raise SystemExit(
            "Faltan assets: " + ", ".join(missing)
            + ". Ejecute primero: python scripts/prepare_demo.py --download"
        )

    api_main.models.clear()
    api_main.transforms.clear()
    api_main.load_models()
    api_main.medmnist_models.load()
    client = TestClient(api_main.app)

    report = {
        "scope": "Ejecucion local reproducible; no es validacion clinica.",
        "health": client.get("/health").json(),
        "analyses": [],
    }
    for filename in DEMO_FILES:
        path = args.assets / filename
        media_type = "application/octet-stream" if path.suffix == ".npy" else "image/png"
        with path.open("rb") as stream:
            response = client.post("/predict", files={"file": (filename, stream, media_type)})
        body = response.json()
        report["analyses"].append({
            "filename": filename,
            "http_status": response.status_code,
            "format": body.get("input", {}).get("format"),
            "quality_metrics": body.get("quality_metrics"),
            "model_applicability": body.get("model_applicability"),
            "results": body.get("results"),
            "agent_report": body.get("agent_report"),
        })

    sample = client.get(
        "/datasets/medmnist/pneumoniamnist/sample?split=test&size=28&index=0"
    )
    report["medmnist_sample"] = {
        "http_status": sample.status_code,
        "labels": sample.headers.get("X-MedMNIST-Labels"),
        "samples": sample.headers.get("X-MedMNIST-Samples"),
        "content_type": sample.headers.get("content-type"),
    }
    prediction = client.post(
        "/predict/medmnist/pneumoniamnist",
        files={"file": ("pneumoniamnist-test-0.png", sample.content, "image/png")},
    )
    report["medmnist_prediction"] = {
        "http_status": prediction.status_code,
        "response": prediction.json(),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Dispositivo: {report['health']['device']}")
    print(f"Modelos generales: {', '.join(report['health']['models']) or 'ninguno'}")
    print(f"Modelos MedMNIST: {len(report['health']['medmnist_models'])}")
    print("\nArchivo                         ruido_est.  P(noise)  P(rotation)  modelos")
    for item in report["analyses"]:
        metrics = item["quality_metrics"] or {}
        results = item["results"] or {}
        noise_probability = results.get("noise", {}).get("noise")
        rotation_probability = results.get("rotation", {}).get("rotation")
        print(
            f"{item['filename']:<31} "
            f"{str(metrics.get('noise_estimate', '-')):>10}  "
            f"{str(noise_probability if noise_probability is not None else '-'):>8}  "
            f"{str(rotation_probability if rotation_probability is not None else '-'):>11}  "
            f"{'sí' if results else 'no'}"
        )
    med = report["medmnist_sample"]
    print(
        f"\nMedMNIST sample: HTTP {med['http_status']} | "
        f"test samples={med['samples']} | labels={med['labels']}"
    )
    print(
        "Predicción MedMNIST: HTTP "
        f"{report['medmnist_prediction']['http_status']} | "
        f"{report['medmnist_prediction']['response'].get('predictions')}"
    )
    print(f"Reporte completo: {args.output.resolve()}")


if __name__ == "__main__":
    main()
