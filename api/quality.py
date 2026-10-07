from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def image_quality_metrics(image: Image.Image) -> dict:
    """Return descriptive, model-free image quality indicators.

    These values are deliberately not clinical labels.  They make it possible to
    monitor an input even when trained checkpoints are unavailable.
    """

    gray = image.convert("L")
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    smoothed = np.asarray(gray.filter(ImageFilter.BoxBlur(1)), dtype=np.float32) / 255.0

    gx = np.diff(arr, axis=1)
    gy = np.diff(arr, axis=0)
    sharpness = (float(np.var(gx)) + float(np.var(gy))) / 2.0
    noise = float(np.median(np.abs(arr - smoothed)))

    return {
        "width": gray.width,
        "height": gray.height,
        "brightness_mean": round(float(arr.mean()), 4),
        "contrast_std": round(float(arr.std()), 4),
        "noise_estimate": round(noise, 4),
        "sharpness_estimate": round(sharpness, 6),
        "interpretation": "Indicadores descriptivos; no constituyen una evaluacion clinica.",
    }

