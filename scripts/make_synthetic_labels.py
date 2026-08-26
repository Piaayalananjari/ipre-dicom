import argparse
import csv
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

RANDOM_SEED = 42


def apply_rotation(img: Image.Image, angle: float) -> Image.Image:
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=0)


def apply_noise(img: Image.Image, sigma: float, blur: bool) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    gauss = np.random.default_rng(RANDOM_SEED).normal(0, sigma, arr.shape)
    arr = np.clip(arr + gauss, 0, 255).astype(np.uint8)
    noisy = Image.fromarray(arr)
    if blur:
        noisy = noisy.filter(ImageFilter.GaussianBlur(radius=1.5))
    enhancer = ImageEnhance.Brightness(noisy)
    noisy = enhancer.enhance(random.uniform(0.75, 1.25))
    return noisy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Carpeta con PNG originales (limpios)")
    parser.add_argument("--output", required=True, help="Carpeta de salida")
    parser.add_argument("--n-rotated", type=int, default=1000)
    parser.add_argument("--n-noisy", type=int, default=1000)
    parser.add_argument("--size", type=int, default=224)
    args = parser.parse_args()

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    clean_dir = out_dir / "clean"
    rotated_dir = out_dir / "rotated"
    noisy_dir = out_dir / "noisy"
    for d in (clean_dir, rotated_dir, noisy_dir):
        d.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in in_dir.glob("*.png") if p.is_file())
    if not files:
        raise SystemExit(f"No se encontraron PNG en {in_dir}")

    tilt_range = (-45.0, 45.0)
    gross_angles = [90.0, 180.0, 270.0]

    rows = []
    for i, f in enumerate(files):
        img = Image.open(f).convert("L").resize((args.size, args.size))
        clean_path = clean_dir / f.name
        img.save(clean_path)
        rows.append({"path": clean_path, "rotation_label": 0, "noise_label": 0})

        if i < args.n_rotated:
            angle = random.choice(gross_angles) if random.random() < 0.6 else random.uniform(*tilt_range)
            rot = apply_rotation(img, angle)
            rot_path = rotated_dir / f"{f.stem}_rot{i}.png"
            rot.save(rot_path)
            rows.append({"path": rot_path, "rotation_label": 1, "noise_label": 0})

        if i < args.n_noisy:
            sigma = random.uniform(5.0, 40.0)
            noisy = apply_noise(img, sigma, blur=random.random() < 0.4)
            noisy_path = noisy_dir / f"{f.stem}_noisy{i}.png"
            noisy.save(noisy_path)
            rows.append({"path": noisy_path, "rotation_label": 0, "noise_label": 1})

    csv_path = out_dir / "labels.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "rotation_label", "noise_label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"OK: {len(files)} limpias, {len(rows) - len(files)} sinteticas -> {csv_path}")


if __name__ == "__main__":
    main()
