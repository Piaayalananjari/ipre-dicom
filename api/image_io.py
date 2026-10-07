from __future__ import annotations

import gzip
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image


RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")
MEDICAL_EXTENSIONS = (".dcm", ".dicom", ".nii", ".nii.gz")
ARRAY_EXTENSIONS = (".npy",)


@dataclass
class LoadedImage:
    image: Image.Image
    format: str
    metadata: dict


def supported_formats() -> list[dict]:
    return [
        {"family": "DICOM", "extensions": [".dcm", ".dicom"], "dimensionality": "2D/multiframe"},
        {"family": "NIfTI-1", "extensions": [".nii", ".nii.gz"], "dimensionality": "2D/3D/4D"},
        {"family": "Raster", "extensions": list(RASTER_EXTENSIONS), "dimensionality": "2D/multipagina"},
        {"family": "NumPy", "extensions": [".npy"], "dimensionality": "2D/3D/4D"},
        {"family": "MedMNIST", "extensions": [".npz"], "dimensionality": "dataset; usar endpoints /datasets"},
    ]


def normalized_extension(filename: str | None) -> str:
    name = (filename or "").lower()
    if name.endswith(".nii.gz"):
        return ".nii.gz"
    dot = name.rfind(".")
    return name[dot:] if dot >= 0 else ""


def array_to_grayscale(array: np.ndarray) -> tuple[Image.Image, dict]:
    data = np.asarray(array)
    original_shape = list(data.shape)
    data = np.squeeze(data)
    if data.ndim < 2 or data.ndim > 4:
        raise ValueError(f"Dimensiones no soportadas: {original_shape}")

    selected = []
    while data.ndim > 2:
        axis = data.ndim - 1
        index = data.shape[axis] // 2
        selected.append({"axis": axis, "index": index})
        data = np.take(data, index, axis=axis)

    data = np.nan_to_num(data.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    finite = data[np.isfinite(data)]
    if not finite.size:
        raise ValueError("La imagen no contiene valores numericos validos")
    lo, hi = np.percentile(finite, (1, 99))
    if hi <= lo:
        lo, hi = float(finite.min()), float(finite.max())
    if hi > lo:
        data = np.clip((data - lo) / (hi - lo), 0, 1)
    else:
        data = np.zeros_like(data)
    return Image.fromarray((data * 255).astype(np.uint8)), {
        "original_shape": original_shape,
        "display_shape": list(data.shape),
        "selected_slices": selected,
    }


def load_raster(content: bytes) -> LoadedImage:
    image = Image.open(io.BytesIO(content))
    metadata = {
        "pil_format": image.format,
        "original_mode": image.mode,
        "frames": int(getattr(image, "n_frames", 1)),
    }
    image.seek(0)
    return LoadedImage(image.convert("L"), "raster", metadata)


def load_numpy(content: bytes) -> LoadedImage:
    array = np.load(io.BytesIO(content), allow_pickle=False)
    if isinstance(array, np.lib.npyio.NpzFile):
        raise ValueError("Los archivos .npz representan datasets; use los endpoints MedMNIST")
    image, metadata = array_to_grayscale(array)
    metadata["dtype"] = str(array.dtype)
    return LoadedImage(image, "numpy", metadata)


def load_nifti(content: bytes, compressed: bool) -> LoadedImage:
    try:
        import nibabel as nib
    except ImportError as exc:
        raise RuntimeError("NiBabel no esta instalado") from exc

    raw = gzip.decompress(content) if compressed else content
    nifti = nib.Nifti1Image.from_bytes(raw)
    array = np.asanyarray(nifti.dataobj)
    image, metadata = array_to_grayscale(array)
    metadata.update({
        "dtype": str(array.dtype),
        "voxel_spacing": [round(float(value), 5) for value in nifti.header.get_zooms()],
    })
    return LoadedImage(image, "nifti", metadata)

