import io
from pathlib import Path

import numpy as np
import pydicom
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from monai.networks.nets import DenseNet121
from monai.transforms import Compose, EnsureChannelFirstd, ScaleIntensityd, ToTensord
from PIL import Image

MODEL_DIR = Path("models")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

app = FastAPI(title="IPRE-DICOM", description="Clasificador de calidad de radiografias de torax")

models: dict[str, torch.nn.Module] = {}
transforms: dict[str, Compose] = {}


def is_dicom(content: bytes, filename=None) -> bool:
    if content[128:132] == b"DICM":
        return True
    return bool(filename) and filename.lower().endswith((".dcm", ".dicom"))


def read_dicom_array(ds) -> np.ndarray:
    arr = ds.pixel_array.astype(np.float32)
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
    return (arr * 255).astype(np.uint8)


def load_models():
    for task in ("rotation", "noise"):
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
    print(f"Modelos cargados: {list(models.keys())}")


@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / "static" / "index.html").read_text()


app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok", "models": list(models.keys())}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()

    if is_dicom(content, file.filename):
        try:
            ds = pydicom.dcmread(io.BytesIO(content), force=True)
        except Exception:
            raise HTTPException(status_code=400, detail="Archivo DICOM invalido")
        arr = read_dicom_array(ds)
        img = Image.fromarray(arr).resize((224, 224))
        meta = {
            "Modality": str(getattr(ds, "Modality", "?")),
            "Rows": getattr(ds, "Rows", None),
            "Columns": getattr(ds, "Columns", None),
        }
    else:
        try:
            img = Image.open(io.BytesIO(content)).convert("L")
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
        img = img.resize((224, 224))
        meta = None

    arr = np.asarray(img)

    results = {}
    for task, model in models.items():
        tensor = transforms[task]({"img": arr})["img"].unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)
        results[task] = {"clean": round(float(probs[0, 0]), 4), task: round(float(probs[0, 1]), 4)}

    return {"filename": file.filename, "dicom": meta, "results": results}
