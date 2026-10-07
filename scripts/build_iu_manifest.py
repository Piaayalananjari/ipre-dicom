"""Build a patient/study-grouped frontal/lateral manifest for IU Chest X-Ray."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FRONTAL_VALUES = {"frontal", "front", "pa", "ap", "ap portable", "ap supine"}
LATERAL_VALUES = {"lateral", "lat", "ll", "rl"}


def normalize_projection(value: str) -> tuple[str, int] | None:
    normalized = " ".join(str(value).strip().lower().replace("_", " ").split())
    if normalized in FRONTAL_VALUES or normalized.startswith(("pa ", "ap ")):
        return "frontal", 0
    if normalized in LATERAL_VALUES or "lateral" in normalized:
        return "lateral", 1
    return None


def find_column(fieldnames: list[str], candidates: tuple[str, ...], description: str) -> str:
    lookup = {name.strip().lower(): name for name in fieldnames}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    raise ValueError(f"No se encontro columna de {description}. Columnas: {fieldnames}")


def build_manifest(projections: Path, images: Path, output: Path) -> dict[str, int]:
    image_index = {
        path.name.lower(): path.resolve()
        for path in images.rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    }
    with projections.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames or []
        filename_col = find_column(fields, ("filename", "file_name", "image", "path"), "archivo")
        projection_col = find_column(fields, ("projection", "view", "viewposition", "view_position"), "proyeccion")
        group_col = find_column(fields, ("uid", "study_id", "study", "report_id", "patient_id"), "grupo/estudio")
        rows = list(reader)

    written = skipped_projection = missing_image = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=[
            "path", "source_id", "view_name", "view_label", "original_projection"
        ])
        writer.writeheader()
        for row in rows:
            label = normalize_projection(row[projection_col])
            if label is None:
                skipped_projection += 1
                continue
            filename = Path(row[filename_col]).name.lower()
            image_path = image_index.get(filename)
            if image_path is None:
                missing_image += 1
                continue
            view_name, view_label = label
            writer.writerow({
                "path": image_path,
                "source_id": row[group_col].strip(),
                "view_name": view_name,
                "view_label": view_label,
                "original_projection": row[projection_col].strip(),
            })
            written += 1
    return {"written": written, "skipped_projection": skipped_projection, "missing_image": missing_image}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projections", type=Path, required=True, help="indiana_projections.csv")
    parser.add_argument("--images", type=Path, required=True, help="Carpeta que contiene las imagenes IU")
    parser.add_argument("--output", type=Path, required=True, help="CSV de salida")
    args = parser.parse_args()
    stats = build_manifest(args.projections, args.images, args.output)
    print(f"Manifest: {args.output} | {stats}")
    if stats["written"] == 0:
        raise SystemExit("No se escribieron filas; revise rutas y nombres de columnas.")


if __name__ == "__main__":
    main()
