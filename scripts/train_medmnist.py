import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
from medmnist import ChestMNIST, PneumoniaMNIST
from monai.networks.nets import DenseNet121
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, Resize, ToTensor

RANDOM_SEED = 42
DATASETS = {
    "chestmnist": ChestMNIST,
    "pneumoniamnist": PneumoniaMNIST,
}


def compute_multilabel_metrics(targets, probabilities):
    targets = np.asarray(targets, dtype=np.int64)
    probabilities = np.asarray(probabilities, dtype=np.float32)
    if targets.ndim == 1:
        targets = targets[:, None]
    if probabilities.ndim == 1:
        probabilities = probabilities[:, None]
    predictions = (probabilities >= 0.5).astype(np.int64)
    aucs = [
        roc_auc_score(targets[:, index], probabilities[:, index])
        for index in range(targets.shape[1])
        if np.unique(targets[:, index]).size > 1
    ]
    return {
        "roc_auc_macro": float(np.mean(aucs)) if aucs else float("nan"),
        "f1_macro": float(f1_score(targets, predictions, average="macro", zero_division=0)),
        "label_accuracy": float((targets == predictions).mean()),
    }


def evaluate(model, loader, device):
    model.eval()
    all_targets, all_probabilities = [], []
    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            logits = model(images)
            all_probabilities.append(torch.sigmoid(logits).cpu().numpy())
            all_targets.append(targets.numpy())
    return compute_multilabel_metrics(
        np.concatenate(all_targets),
        np.concatenate(all_probabilities),
    )


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento reproducible sobre MedMNIST+")
    parser.add_argument("--dataset", choices=DATASETS, default="pneumoniamnist")
    parser.add_argument("--size", type=int, choices=[28, 64, 128, 224], default=128)
    parser.add_argument("--root", default=os.getenv("MEDMNIST_ROOT", "data/medmnist"))
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--output", default="models")
    parser.add_argument("--wandb-mode", choices=["disabled", "offline", "online"], default="disabled")
    parser.add_argument("--wandb-project", default="ipre-dicom-medmnist")
    parser.add_argument("--run-name", default=None)
    args = parser.parse_args()

    torch.manual_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

    input_size = max(args.size, 64)
    transform = Compose([Resize((input_size, input_size)), ToTensor(), Normalize(mean=(0.5,), std=(0.5,))])
    dataset_class = DATASETS[args.dataset]
    common = {"root": args.root, "size": args.size, "download": args.download, "transform": transform}
    train_dataset = dataset_class(split="train", **common)
    val_dataset = dataset_class(split="val", **common)
    test_dataset = dataset_class(split="test", **common)
    output_channels = int(np.asarray(train_dataset.labels).reshape(len(train_dataset), -1).shape[1])

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=output_channels).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    run = None
    if args.wandb_mode != "disabled":
        import wandb
        run = wandb.init(
            project=args.wandb_project,
            name=args.run_name,
            mode=args.wandb_mode,
            job_type="train",
            config={**vars(args), "architecture": "MONAI-DenseNet121", "device": str(device)},
        )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    best_path = output_dir / f"medmnist_{args.dataset}_{args.size}.pt"
    metrics_path = output_dir / f"medmnist_{args.dataset}_{args.size}_metrics.json"
    best_auc = -1.0
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        losses = []
        for images, targets in train_loader:
            images = images.to(device)
            targets = targets.float().to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(images), targets)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        scheduler.step()

        metrics = evaluate(model, val_loader, device)
        mean_loss = float(np.mean(losses))
        history.append({"epoch": epoch, "train_loss": mean_loss, **metrics})
        print(f"Epoch {epoch}/{args.epochs} loss={mean_loss:.4f} val_auc={metrics['roc_auc_macro']:.4f} val_f1={metrics['f1_macro']:.4f}")
        if run:
            run.log({"epoch": epoch, "train/loss": mean_loss, **{f"val/{key}": value for key, value in metrics.items()}})
        if metrics["roc_auc_macro"] > best_auc:
            best_auc = metrics["roc_auc_macro"]
            torch.save({
                "state_dict": model.state_dict(),
                "dataset": args.dataset,
                "size": input_size,
                "source_size": args.size,
                "output_channels": output_channels,
                "best_val_roc_auc": best_auc,
            }, best_path)

    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint["state_dict"])
    test_metrics = evaluate(model, test_loader, device)
    metrics_path.write_text(json.dumps({
        "dataset": args.dataset,
        "size": input_size,
        "source_size": args.size,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "seed": RANDOM_SEED,
        "device": str(device),
        "split_samples": {"train": len(train_dataset), "val": len(val_dataset), "test": len(test_dataset)},
        "history": history,
        "best_val_roc_auc": best_auc,
        "test": test_metrics,
        "checkpoint": str(best_path),
    }, indent=2))
    print({"best_val_roc_auc": best_auc, "test": test_metrics, "checkpoint": str(best_path)})
    print({"metrics": str(metrics_path)})

    if run:
        for key, value in test_metrics.items():
            run.summary[f"test/{key}"] = value
        artifact = wandb.Artifact(
            f"{args.dataset}-densenet121",
            type="model",
            metadata={key: value for key, value in checkpoint.items() if key != "state_dict"},
        )
        artifact.add_file(str(best_path))
        run.log_artifact(artifact, aliases=["best", "latest"])
        run.finish()


if __name__ == "__main__":
    main()
