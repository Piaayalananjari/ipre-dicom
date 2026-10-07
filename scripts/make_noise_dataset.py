import argparse
import csv
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

RANDOM_SEED = 42


def apply_noise(img: Image.Image, rng: np.random.Generator, sigma: float, blur: bool) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    gauss = rng.normal(0, sigma, arr.shape)
    arr = np.clip(arr + gauss, 0, 255).astype(np.uint8)
    noisy = Image.fromarray(arr)
    if blur:
        noisy = noisy.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.8, 2.5)))
    noisy = ImageEnhance.Brightness(noisy).enhance(rng.uniform(0.7, 1.3))
    noisy = ImageEnhance.Contrast(noisy).enhance(rng.uniform(0.8, 1.2))
    return noisy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Carpeta con PNG originales (limpios)")
    parser.add_argument("--output", required=True, help="Carpeta de salida")
    parser.add_argument("--variants", type=int, default=150, help="Variantes ruidosas por imagen")
    parser.add_argument("--size", type=int, default=224)
    args = parser.parse_args()

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    clean_dir = out_dir / "clean"
    noisy_dir = out_dir / "noisy"
    for d in (clean_dir, noisy_dir):
        d.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in in_dir.glob("*.png") if p.is_file())
    if not files:
        raise SystemExit(f"No se encontraron PNG en {in_dir}")

    rows = []
    for i, f in enumerate(files):
        img = Image.open(f).convert("L").resize((args.size, args.size))
        clean_path = clean_dir / f.name
        img.save(clean_path)
        rows.append({"path": clean_path, "source_id": f.stem, "noise_label": 0})

        for v in range(args.variants):
            rng = np.random.default_rng(RANDOM_SEED * 1000 + i * args.variants + v)
            sigma = rng.uniform(8.0, 45.0)
            noisy = apply_noise(img, rng, sigma, blur=rng.random() < 0.5)
            noisy_path = noisy_dir / f"{f.stem}_noisy_{v:03d}.png"
            noisy.save(noisy_path)
            rows.append({"path": noisy_path, "source_id": f.stem, "noise_label": 1})

            if v < args.variants // 2:
                clean_var = ImageEnhance.Brightness(img).enhance(rng.uniform(0.85, 1.15))
                clean_var = ImageEnhance.Contrast(clean_var).enhance(rng.uniform(0.9, 1.1))
                clean_var_path = clean_dir / f"{f.stem}_clean_{v:03d}.png"
                clean_var.save(clean_var_path)
                rows.append({"path": clean_var_path, "source_id": f.stem, "noise_label": 0})

    csv_path = out_dir / "labels_noise.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "source_id", "noise_label"])
        writer.writeheader()
        writer.writerows(rows)

    n_clean = sum(1 for r in rows if r["noise_label"] == 0)
    n_noisy = sum(1 for r in rows if r["noise_label"] == 1)
    print(f"OK: {n_clean} limpias, {n_noisy} ruidosas -> {csv_path}")


if __name__ == "__main__":
    main()
