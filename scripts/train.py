import argparse
import csv
from pathlib import Path

import numpy as np
import torch
from monai.data import DataLoader, Dataset
from monai.networks.nets import DenseNet121
from monai.transforms import Compose, EnsureChannelFirstd, LoadImaged, ScaleIntensityd, ToTensord
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42


def build_dataset(rows, is_train):
    transform = Compose([
        LoadImaged(keys="img", image_only=True),
        EnsureChannelFirstd(keys="img"),
        ScaleIntensityd(keys="img"),
        ToTensord(keys=("img", "label")),
    ])
    if is_train:
        import monai.transforms as T
        transform = Compose([
            LoadImaged(keys="img", image_only=True),
            EnsureChannelFirstd(keys="img"),
            T.RandRotated(keys="img", range_x=0.05, prob=0.5),
            T.RandGaussianNoised(keys="img", prob=0.3, std=0.02),
            ScaleIntensityd(keys="img"),
            ToTensord(keys=("img", "label")),
        ])
    return Dataset(data=[{"img": r["path"], "label": r["label"]} for r in rows], transform=transform)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="labels.csv generado por make_synthetic_labels.py")
    parser.add_argument("--task", choices=["rotation", "noise"], default="rotation")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--output", default="models")
    args = parser.parse_args()

    torch.manual_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    label_key = f"{args.task}_label"
    with open(args.csv) as fh:
        rows = [{"path": r["path"], "label": int(r[label_key])} for r in csv.DictReader(fh)]

    train_rows, val_rows = train_test_split(rows, test_size=0.2, stratify=[r["label"] for r in rows], random_state=RANDOM_SEED)
    print(f"Train: {len(train_rows)} | Val: {len(val_rows)} | Tarea: {args.task}")

    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=2).to(device)
    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    train_loader = DataLoader(build_dataset(train_rows, is_train=True), batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(build_dataset(val_rows, is_train=False), batch_size=args.batch_size, shuffle=False, num_workers=2)

    best_auc = -1.0
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
        f1 = f1_score(y_true_np, y_pred)
        auc = roc_auc_score(y_true_np, probs[:, 1].cpu().numpy())

        print(f"Epoch {epoch + 1}/{args.epochs} | loss {total_loss / len(train_loader):.4f} | acc {acc:.4f} | f1 {f1:.4f} | AUC {auc:.4f}")

        if auc > best_auc:
            best_auc = auc
            Path(args.output).mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), Path(args.output) / f"best_{args.task}.pt")

    print(f"\nMejor AUC: {best_auc:.4f} -> models/best_{args.task}.pt")
    print(classification_report(y_true_np, y_pred, target_names=["clean", args.task]))


if __name__ == "__main__":
    main()
