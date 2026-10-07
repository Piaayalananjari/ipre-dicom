import argparse
import csv
from pathlib import Path

import numpy as np
import torch
from monai.data import DataLoader, Dataset
from monai.networks.nets import DenseNet121
from monai.transforms import Compose, EnsureChannelFirstd, LoadImaged, ScaleIntensityd, ToTensord
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split

RANDOM_SEED = 42


def build_dataset(rows, is_train):
    transform = Compose([
        LoadImaged(keys="img", image_only=True),
        EnsureChannelFirstd(keys="img"),
        ScaleIntensityd(keys="img"),
        ToTensord(keys=("img", "label")),
    ])
    return Dataset(data=[{"img": r["path"], "label": r["label"]} for r in rows], transform=transform)


def split_rows(rows, test_size=0.2):
    """Prefer a source/patient-level split so derived variants never cross partitions."""

    if rows and all(row.get("group") for row in rows):
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=RANDOM_SEED)
        train_idx, val_idx = next(splitter.split(rows, groups=[row["group"] for row in rows]))
        return [rows[index] for index in train_idx], [rows[index] for index in val_idx], "grouped"

    train, val = train_test_split(
        rows,
        test_size=test_size,
        stratify=[row["label"] for row in rows],
        random_state=RANDOM_SEED,
    )
    return train, val, "row-stratified (sin group/source_id; riesgo de fuga)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="labels.csv generado por make_synthetic_labels.py")
    parser.add_argument("--task", choices=["rotation", "noise", "view"], default="rotation")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--output", default="models")
    parser.add_argument("--wandb-mode", choices=["disabled", "offline", "online"], default="disabled")
    parser.add_argument("--wandb-project", default="ipre-dicom")
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--group-column", default="source_id", help="Paciente/imagen origen para evitar fuga entre splits")
    args = parser.parse_args()

    torch.manual_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    label_key = f"{args.task}_label"
    with open(args.csv) as fh:
        rows = [
            {"path": row["path"], "label": int(row[label_key]), "group": row.get(args.group_column)}
            for row in csv.DictReader(fh)
        ]

    train_rows, val_rows, split_method = split_rows(rows)
    print(f"Train: {len(train_rows)} | Val: {len(val_rows)} | Tarea: {args.task} | Split: {split_method}")
    if split_method != "grouped":
        print(f"ADVERTENCIA: agregue la columna '{args.group_column}' para una evaluacion valida.")

    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2).to(device)
    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    train_loader = DataLoader(build_dataset(train_rows, is_train=True), batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(build_dataset(val_rows, is_train=False), batch_size=args.batch_size, shuffle=False, num_workers=2)

    run = None
    if args.wandb_mode != "disabled":
        try:
            import wandb
        except ImportError as exc:
            raise SystemExit("W&B no esta instalado. Ejecute: pip install -r requirements-experiment.txt") from exc
        run = wandb.init(
            project=args.wandb_project,
            name=args.run_name,
            mode=args.wandb_mode,
            job_type="train",
            config={
                "task": args.task,
                "architecture": "MONAI-DenseNet121",
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "learning_rate": args.lr,
                "seed": RANDOM_SEED,
                "train_samples": len(train_rows),
                "validation_samples": len(val_rows),
                "device": str(device),
                "split_method": split_method,
            },
        )
        run.define_metric("epoch")
        run.define_metric("train/*", step_metric="epoch")
        run.define_metric("val/*", step_metric="epoch")

    best_auc = -1.0
    best_path = Path(args.output) / f"best_{args.task}.pt"
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            x, y = batch["img"].to(device), batch["label"].to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()

        model.eval()
        preds, targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                x, y = batch["img"].to(device), batch["label"]
                probs = torch.softmax(model(x), dim=1)
                preds.append(probs)
                targets.append(y)
        probs = torch.cat(preds)
        y_true = torch.cat(targets)
        y_pred = probs.argmax(dim=1).cpu().numpy()
        y_true_np = y_true.cpu().numpy()

        acc = accuracy_score(y_true_np, y_pred)
        balanced_acc = balanced_accuracy_score(y_true_np, y_pred)
        f1 = f1_score(y_true_np, y_pred)
        auc = roc_auc_score(y_true_np, probs[:, 1].cpu().numpy())

        mean_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{args.epochs} | loss {mean_loss:.4f} | acc {acc:.4f} | f1 {f1:.4f} | AUC {auc:.4f}")
        if run:
            run.log({
                "epoch": epoch + 1,
                "train/loss": mean_loss,
                "train/learning_rate": optimizer.param_groups[0]["lr"],
                "val/accuracy": acc,
                "val/balanced_accuracy": balanced_acc,
                "val/f1": f1,
                "val/roc_auc": auc,
            })

        if auc > best_auc:
            best_auc = auc
            Path(args.output).mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), best_path)

    print(f"\nMejor AUC: {best_auc:.4f} -> {best_path}")
    target_names = ["frontal", "lateral"] if args.task == "view" else ["clean", args.task]
    print(classification_report(y_true_np, y_pred, target_names=target_names))
    if run:
        run.summary["best/val_roc_auc"] = best_auc
        artifact = wandb.Artifact(
            name=f"{args.task}-densenet121",
            type="model",
            metadata={"task": args.task, "best_val_roc_auc": best_auc},
        )
        artifact.add_file(str(best_path))
        run.log_artifact(artifact, aliases=["best", "latest"])
        run.finish()


if __name__ == "__main__":
    main()
