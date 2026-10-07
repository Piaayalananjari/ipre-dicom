import io
import json
import os
from pathlib import Path

import numpy as np
import pydicom
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from monai.networks.nets import DenseNet121
from monai.transforms import Compose, EnsureChannelFirstd, ScaleIntensityd, ToTensord
from PIL import Image

from api.agent_workflow import langgraph_available, run_report_workflow
from api.anonymize import anonymize_dicom
from api.image_io import load_nifti, load_numpy, load_raster, normalized_extension, supported_formats
from api.medmnist_service import list_datasets, load_dataset, sample_png
from api.medmnist_models import MedMNISTModelRegistry, raster_image_from_bytes
from api.privacy import audit_dicom_privacy, non_dicom_privacy_audit
from api.quality import image_quality_metrics

MODEL_DIR = Path("models")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

app = FastAPI(title="IPRE-DICOM", description="Clasificador de calidad de radiografias de torax")

models: dict[str, torch.nn.Module] = {}
transforms: dict[str, Compose] = {}
medmnist_models = MedMNISTModelRegistry(MODEL_DIR, DEVICE)
MODEL_LABELS = {
    "rotation": ("clean", "rotation"),
    "noise": ("clean", "noise"),
    "view": ("frontal", "lateral"),
}


def is_dicom(content: bytes, filename=None) -> bool:
    if content[128:132] == b"DICM":
        return True
    return bool(filename) and filename.lower().endswith((".dcm", ".dicom"))


def read_dicom_array(ds) -> np.ndarray:
    arr = ds.pixel_array.astype(np.float32)
    if arr.ndim > 2:
        arr = arr[0]
    intercept = float(getattr(ds, "RescaleIntercept", 0) or 0)
    slope = float(getattr(ds, "RescaleSlope", 1) or 1)
    arr = arr * slope + intercept

    center = getattr(ds, "WindowCenter", None)
    width = getattr(ds, "WindowWidth", None)
    if center is None or width is None:
        lo, hi = float(arr.min()), float(arr.max())
    else:
        if hasattr(center, "__len__"):
            center, width = float(center[0]), float(width[0])
        center, width = float(center), float(width)
        lo, hi = center - width / 2, center + width / 2

    arr = np.clip(arr, lo, hi)
    if hi > lo:
        arr = (arr - lo) / (hi - lo)
    if str(getattr(ds, "PhotometricInterpretation", "")).upper() == "MONOCHROME1":
        arr = 1.0 - arr
    return (arr * 255).astype(np.uint8)


def load_models():
    for task in MODEL_LABELS:
        path = MODEL_DIR / f"best_{task}.pt"
        if path.exists():
            model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2).to(DEVICE)
            model.load_state_dict(torch.load(path, map_location=DEVICE))
            model.eval()
            models[task] = model
            transforms[task] = Compose([
                EnsureChannelFirstd(keys="img", channel_dim="no_channel"),
                ScaleIntensityd(keys="img"),
                ToTensord(keys="img"),
            ])


@app.on_event("startup")
def startup():
    load_models()
    medmnist_models.load()
    print(f"Modelos cargados: {list(models.keys())}; MedMNIST: {medmnist_models.catalog()}")


@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / "static" / "index.html").read_text()


app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models": list(models.keys()),
        "device": str(DEVICE),
        "medmnist": list_datasets(),
        "medmnist_models": medmnist_models.catalog(),
        "agent": {"engine": "deterministic", "langgraph_installed": langgraph_available()},
    }


@app.get("/formats")
def formats():
    return {"formats": supported_formats(), "max_upload_mib": 64}


@app.get("/datasets/medmnist")
def medmnist_catalog():
    return {"datasets": list_datasets(), "download_is_explicit": True}


@app.post("/datasets/medmnist/{flag}/download")
def medmnist_download(flag: str, size: int = 28):
    try:
        dataset = load_dataset(flag, "train", size, download=True)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"dataset": flag, "size": size, "train_samples": len(dataset), "status": "ready"}


@app.get("/datasets/medmnist/{flag}/sample")
def medmnist_sample(flag: str, split: str = "train", size: int = 28, index: int = 0):
    try:
        content, labels, count = sample_png(flag, split, size, index)
    except (ValueError, RuntimeError, IndexError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=content,
        media_type="image/png",
        headers={
            "X-MedMNIST-Labels": json.dumps(labels),
            "X-MedMNIST-Samples": str(count),
        },
    )


@app.post("/predict/medmnist/{flag}")
async def predict_medmnist(flag: str, file: UploadFile = File(...)):
    content = await file.read()
    if not content or len(content) > 64 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo vacio o demasiado grande")
    try:
        image = raster_image_from_bytes(content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Se requiere una imagen raster valida") from exc
    try:
        return medmnist_models.predict(flag, image)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"No hay checkpoint cargado para {flag}. Entrene scripts/train_medmnist.py y reinicie la API.",
        ) from exc


@app.post("/anonymize/dicom")
async def anonymize_dicom_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    if not is_dicom(content, file.filename):
        raise HTTPException(status_code=400, detail="Se requiere un archivo DICOM")
    secret = os.getenv("DICOM_PSEUDONYM_SECRET", "")
    if not secret:
        raise HTTPException(status_code=503, detail="Configure DICOM_PSEUDONYM_SECRET en el servidor")
    try:
        dataset = pydicom.dcmread(io.BytesIO(content), force=True)
        anonymized, audit = anonymize_dicom(dataset, secret)
        output = io.BytesIO()
        pydicom.dcmwrite(output, anonymized, write_like_original=False)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="No se pudo anonimizar el DICOM") from exc
    return Response(
        content=output.getvalue(),
        media_type="application/dicom",
        headers={
            "Content-Disposition": 'attachment; filename="anonymized.dcm"',
            "X-Anonymization-Profile": audit["profile"],
            "X-Pixel-Data-Modified": "false",
        },
    )


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Archivo vacio")
    if len(content) > 64 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (maximo 64 MiB)")

    extension = normalized_extension(file.filename)
    input_info = {"extension": extension or None, "content_type": file.content_type}

    if is_dicom(content, file.filename):
        try:
            ds = pydicom.dcmread(io.BytesIO(content), force=True)
        except Exception:
            raise HTTPException(status_code=400, detail="Archivo DICOM invalido")
        try:
            arr = read_dicom_array(ds)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"No se pudo decodificar PixelData: {exc}") from exc
        original_img = Image.fromarray(arr)
        img = Image.fromarray(arr).resize((224, 224))
        meta = {
            "Modality": str(getattr(ds, "Modality", "?")),
            "Rows": getattr(ds, "Rows", None),
            "Columns": getattr(ds, "Columns", None),
            "ViewPosition": str(getattr(ds, "ViewPosition", "")),
            "PhotometricInterpretation": str(getattr(ds, "PhotometricInterpretation", "")),
        }
        privacy = audit_dicom_privacy(ds)
        input_info.update({"format": "dicom", "metadata": meta})
    else:
        try:
            if extension in (".nii", ".nii.gz"):
                loaded = load_nifti(content, compressed=extension == ".nii.gz")
            elif extension in (".npy", ".npz"):
                loaded = load_numpy(content)
            else:
                loaded = load_raster(content)
            original_img = loaded.image
            input_info.update({"format": loaded.format, "metadata": loaded.metadata})
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Formato o contenido no soportado: {exc}") from exc
        img = original_img.resize((224, 224))
        meta = None
        privacy = non_dicom_privacy_audit()

    # PIL may expose a read-only NumPy view; MONAI/PyTorch expect writable memory.
    arr = np.asarray(img).copy()

    model_applicable = input_info["format"] == "raster" or (
        input_info["format"] == "dicom" and meta["Modality"].upper() in {"CR", "DX"}
    )
    results = {}
    if model_applicable:
        for task, model in models.items():
            tensor = transforms[task]({"img": arr})["img"].unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                probs = torch.softmax(model(tensor), dim=1)
            labels = MODEL_LABELS[task]
            results[task] = {
                labels[index]: round(float(probs[0, index]), 4)
                for index in range(2)
            }

    analysis = {
        "filename": file.filename,
        "input": input_info,
        "dicom": meta,
        "privacy": privacy,
        "quality_metrics": image_quality_metrics(original_img),
        "model_applicability": {
            "chest_xray_models_executed": model_applicable,
            "reason": (
                "Entrada raster o radiografia DICOM CR/DX."
                if model_applicable
                else "Formato/modalidad visible, pero fuera del dominio de los clasificadores de torax."
            ),
        },
        "results": results,
    }
    analysis["agent_report"] = run_report_workflow(analysis)
    return analysis
