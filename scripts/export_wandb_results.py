"""Importa las métricas existentes a W&B offline, sin volver a entrenar."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    # Deliberadamente offline: autenticar y sincronizar es un paso separado.
    base = ROOT / "output" / "wandb"
    base.mkdir(parents=True, exist_ok=True)
    for key, name in [("WANDB_CACHE_DIR", "cache"),
                      ("WANDB_CONFIG_DIR", "config"),
                      ("WANDB_DATA_DIR", "data")]:
        folder = base / name
        folder.mkdir(exist_ok=True)
        os.environ[key] = str(folder)
    import wandb

    source = ROOT / "models" / "medmnist_pneumoniamnist_28_metrics.json"
    results = json.loads(source.read_text())
    with wandb.init(
        project="ipre-dicom-medmnist",
        name="pneumoniamnist-epoca1-importacion-resultados",
        mode="offline",
        dir=str(base),
        job_type="import-existing-results",
        tags=["post-hoc", "una-epoca", "resultados-reales"],
        notes=("Importación posterior desde el JSON del experimento. "
               "No es un entrenamiento nuevo ni seguimiento en vivo. "
               "La corrida original se detuvo durante la segunda época; "
               "el checkpoint evaluado corresponde a la primera. "
               "No hay una curva completa de aprendizaje."),
        config={
            "dataset": results["dataset"],
            "architecture": "MONAI-DenseNet121",
            "source_size": results["source_size"],
            "input_size": results["input_size"],
            "epochs_completed": results["epochs_completed"],
            "train_samples": results["train_samples"],
            "validation_samples": results["validation_samples"],
            "test_samples": results["test_samples"],
            "record_type": "post_hoc_import",
        },
    ) as run:
        run.define_metric("epoch")
        run.define_metric("train/*", step_metric="epoch")
        run.define_metric("val/*", step_metric="epoch")
        epoch = results["epoch_1"]
        run.log({"epoch": 1, "train/loss": epoch["train_loss"],
                 "val/roc_auc": epoch["validation_roc_auc"],
                 "val/f1_macro": epoch["validation_f1"]})
        for key, value in results["test"].items():
            run.summary[f"test/{'f1_macro' if key == 'f1' else key}"] = value
        run.summary["results_source"] = source.name
        artifact = wandb.Artifact("pneumoniamnist-epoch1-metrics", type="evaluation")
        artifact.add_file(str(source))
        run.log_artifact(artifact)
        run_dir = Path(run.dir).parent
    print("\nRegistro real creado en:", run_dir)
    print("Para verlo en W&B, autenticar y luego sincronizar este directorio:")
    print(".venv/bin/wandb login")
    print(f'.venv/bin/wandb sync "{run_dir}"')


if __name__ == "__main__":
    main()
