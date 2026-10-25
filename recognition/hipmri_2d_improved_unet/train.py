"""Train/validate only the baseline U-Net; no test split or Improved model."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch.utils.data import DataLoader

from dataset import HipMRIPairDataset, collate_padded, collect_pairs, load_pair, patient_ids
from losses import segmentation_cross_entropy
from metrics import SegmentationMetrics
from modules import UNet


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def manifest_hash(pairs):
    text = "\n".join(f"{image.name}|{mask.name}" for image, mask in pairs)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def select_training_pairs(pairs, limit, seed, reference_name):
    """Fixed seeded subset for a bounded smoke run; retain the learning reference."""
    if limit is None or limit >= len(pairs):
        return list(pairs)
    if limit <= 0:
        raise ValueError("train-limit must be positive.")
    reference = next((i for i, pair in enumerate(pairs) if pair[0].name == reference_name), None)
    if reference is None:
        raise ValueError(f"Training reference not found: {reference_name}")
    other_indices = [i for i in range(len(pairs)) if i != reference]
    selected = [reference] + random.Random(seed).sample(other_indices, limit - 1)
    return [pairs[i] for i in sorted(selected)]


def move_batch(batch, device):
    return {key: value.to(device) for key, value in batch.items() if key in ("image", "target", "valid_mask")}


def run_epoch(model, loader, device, num_classes, optimizer=None):
    """Update only during training; validation disables gradients and updates."""
    training = optimizer is not None
    model.train(training)
    metrics = SegmentationMetrics(num_classes)
    loss_sum, pixels, samples, steps = 0.0, 0, 0, 0
    gradient_norms = []
    started = time.perf_counter()
    with torch.set_grad_enabled(training):
        for batch in loader:
            batch = move_batch(batch, device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(batch["image"])
            loss = segmentation_cross_entropy(logits, batch["target"], batch["valid_mask"])
            if not torch.isfinite(loss):
                raise ValueError("Non-finite loss; stopping instead of saving a misleading run.")
            if training:
                loss.backward()
                norms = [parameter.grad.detach().float().norm() for parameter in model.parameters() if parameter.grad is not None]
                gradient_norm = torch.stack(norms).norm()
                if not torch.isfinite(gradient_norm) or gradient_norm.item() == 0:
                    raise ValueError("Expected finite, nonzero gradients before the optimizer update.")
                gradient_norms.append(gradient_norm.item())
                optimizer.step()
            count = int(batch["valid_mask"].sum().item())
            loss_sum += loss.detach().item() * count
            pixels += count
            samples += batch["image"].shape[0]
            steps += 1
            metrics.update(logits.detach().argmax(dim=1), batch["target"], batch["valid_mask"])
    result = metrics.compute()
    result.update({
        "cross_entropy": loss_sum / pixels if pixels else None,
        "samples": samples, "batches": steps, "elapsed_seconds": round(time.perf_counter() - started, 3),
        "optimizer_steps": steps if training else 0,
    })
    if gradient_norms:
        result["gradient_norm_range"] = [min(gradient_norms), max(gradient_norms)]
    return result


def reference_probe(model, reference_sample, device):
    batch = move_batch(collate_padded([reference_sample]), device)
    model.eval()
    with torch.inference_mode():
        logits = model(batch["image"])
        loss = segmentation_cross_entropy(logits, batch["target"], batch["valid_mask"])
    return float(loss.item()), logits.detach().cpu()


def plot_history(history, output_dir):
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir.resolve() / ".matplotlib"))
    import matplotlib.pyplot as plt

    epochs = [record["epoch"] for record in history]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for split in ("training", "validation"):
        axes[0].plot(epochs, [record[split]["cross_entropy"] for record in history], marker="o", label=split)
    axes[0].set(xlabel="Epoch on selected training set", ylabel="Valid-pixel CE", title="Baseline loss")
    axes[0].legend()
    for class_id in range(len(history[0]["validation"]["dice_per_class"])):
        values = [record["validation"]["dice_per_class"][class_id] for record in history]
        axes[1].plot(epochs, [float("nan") if value is None else value for value in values], marker="o", label=f"ID {class_id}")
    axes[1].set(xlabel="Epoch on selected training set", ylabel="Full-validation Dice", ylim=(0, 1), title="Class IDs; tissue mapping unconfirmed")
    axes[1].legend(ncol=2)
    fig.savefig(output_dir / "training_curves.png", dpi=150)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    workspace = Path(__file__).resolve().parents[4]
    parser.add_argument("--data-root", type=Path, default=workspace / "Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/baseline"))
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--base-channels", type=int, default=16)
    parser.add_argument("--num-classes", type=int, default=6)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=3710)
    parser.add_argument("--train-limit", type=int, help="Fixed training subset for smoke runs; omitted means all training pairs.")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--reference-name", default="case_004_week_0_slice_12.nii.gz")
    args = parser.parse_args()
    if min(args.epochs, args.batch_size, args.base_channels) <= 0 or args.num_classes < 2 or args.lr <= 0:
        parser.error("Epochs, batch size, width and learning rate must be positive; classes >=2.")
    if args.train_limit is not None and args.train_limit <= 0:
        parser.error("train-limit must be positive")
    return args


def main():
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"Use a new output directory to preserve prior run evidence: {args.output_dir}")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable.")
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else ("cpu" if args.device == "auto" else args.device))
    torch.set_num_threads(1)
    seed_everything(args.seed)
    training_pairs = collect_pairs(args.data_root / "keras_slices_train", args.data_root / "keras_slices_seg_train")
    validation_pairs = collect_pairs(args.data_root / "keras_slices_validate", args.data_root / "keras_slices_seg_validate")
    train_ids, validation_ids = patient_ids(training_pairs), patient_ids(validation_pairs)
    overlap = train_ids & validation_ids
    if overlap:
        raise ValueError(f"Train/validation case-group overlap: {sorted(overlap)}")
    selected = select_training_pairs(training_pairs, args.train_limit, args.seed, args.reference_name)
    reference_pair = next((pair for pair in training_pairs if pair[0].name == args.reference_name), None)
    if reference_pair is None:
        raise ValueError("Fixed training reference not found.")
    reference_sample = load_pair(*reference_pair)
    generator = torch.Generator().manual_seed(args.seed)
    training_loader = DataLoader(HipMRIPairDataset(selected), batch_size=args.batch_size, shuffle=True,
                                 num_workers=0, collate_fn=collate_padded, generator=generator)
    validation_loader = DataLoader(HipMRIPairDataset(validation_pairs), batch_size=args.batch_size, shuffle=False,
                                   num_workers=0, collate_fn=collate_padded)
    config = {"in_channels": 1, "num_classes": args.num_classes, "base_channels": args.base_channels}
    model = UNet(**config).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    initial_reference_ce, _ = reference_probe(model, reference_sample, device)
    initial_parameter = next(model.parameters()).detach().cpu().clone()
    args.output_dir.mkdir(parents=True)
    report = {
        "milestone": "baseline_unet_minimal_training", "performed_by": "Codex automation; not user-performed verification",
        "created_at": datetime.now(timezone(timedelta(hours=10))).isoformat(),
        "status": "running", "model": "baseline_unet", "model_config": config,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "optimizer": {"name": "Adam", "lr": args.lr}, "objective": "valid-region one-hot cross-entropy",
        "selection_metric": "minimum full-validation cross_entropy", "seed": args.seed,
        "device": str(device), "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "versions": {"python_torch": str(torch.__version__), "numpy": np.__version__},
        "settings": {"epochs": args.epochs, "batch_size": args.batch_size, "num_workers": 0, "cudnn_deterministic": True, "cudnn_benchmark": False},
        "data": {"full_training_pairs": len(training_pairs), "selected_training_pairs": len(selected),
                 "full_validation_pairs": len(validation_pairs), "selected_training_case_groups": len(patient_ids(selected)),
                 "training_case_groups": len(train_ids), "validation_case_groups": len(validation_ids), "shared_case_ids": sorted(overlap),
                 "training_manifest_sha256": manifest_hash(selected), "validation_manifest_sha256": manifest_hash(validation_pairs),
                 "selection_policy": "all training pairs" if len(selected) == len(training_pairs) else "fixed seeded subset including the learning reference; indices sorted before seeded epoch shuffling",
                 "selected_training_filenames": [pair[0].name for pair in selected]},
        "limited_training_smoke": len(selected) < len(training_pairs), "test_split_read": False,
        "improved_unet_implemented": False, "reference_name": args.reference_name,
        "reference_ce_before_training": initial_reference_ce, "epochs": [],
        "claim_boundary": "A limited smoke run demonstrates the pipeline, not final baseline quality, fair model comparison or unseen-test performance.",
        "case_identifier_note": "Numeric case field is a grouping proxy; original patient identity mapping is unverified.",
    }
    if not report["limited_training_smoke"]:
        report["claim_boundary"] = "Training/validation run only; not a final fair model comparison or unseen-test evaluation."
    best_loss, best_logits, best_epoch = float("inf"), None, None
    started = time.perf_counter()
    try:
        for epoch in range(1, args.epochs + 1):
            training = run_epoch(model, training_loader, device, args.num_classes, optimizer)
            validation = run_epoch(model, validation_loader, device, args.num_classes)
            record = {"epoch": epoch, "training": training, "validation": validation}
            report["epochs"].append(record)
            checkpoint = {"model": "baseline_unet", "model_config": config, "model_state": model.state_dict(),
                          "optimizer_state": optimizer.state_dict(), "epoch": epoch, "seed": args.seed,
                          "validation_cross_entropy": validation["cross_entropy"], "limited_training_smoke": report["limited_training_smoke"]}
            torch.save(checkpoint, args.output_dir / "last.pt")
            if validation["cross_entropy"] < best_loss:
                best_loss, best_epoch = validation["cross_entropy"], epoch
                _, best_logits = reference_probe(model, reference_sample, device)
                torch.save(checkpoint, args.output_dir / "best.pt")
            print(f"epoch {epoch}/{args.epochs}: train CE={training['cross_entropy']:.6f}; validation CE={validation['cross_entropy']:.6f}; valid pixels={validation['valid_pixels']}", flush=True)
            (args.output_dir / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["first_parameter_max_abs_change"] = float((next(model.parameters()).detach().cpu() - initial_parameter).abs().max())
        report["reference_ce_after_training"], _ = reference_probe(model, reference_sample, device)
        loaded = torch.load(args.output_dir / "best.pt", map_location="cpu", weights_only=True)
        restored = UNet(**loaded["model_config"]).to(device)
        restored.load_state_dict(loaded["model_state"])
        restored_ce, restored_logits = reference_probe(restored, reference_sample, device)
        torch.testing.assert_close(restored_logits, best_logits, rtol=1e-5, atol=1e-6)
        report["checkpoint_reload"] = {"passed": True, "best_epoch": best_epoch, "best_validation_cross_entropy": best_loss,
                                       "reference_ce": restored_ce, "reference_logit_max_abs_difference": float((restored_logits - best_logits).abs().max())}
        report["optimizer_steps"] = sum(record["training"]["optimizer_steps"] for record in report["epochs"])
        report["peak_cuda_allocated_bytes"] = torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None
        report["peak_cuda_reserved_bytes"] = torch.cuda.max_memory_reserved(device) if device.type == "cuda" else None
        plot_history(report["epochs"], args.output_dir)
        report["curves_file"] = "training_curves.png"
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        (args.output_dir / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Completed baseline run: {args.output_dir.resolve()}; optimizer steps={report['optimizer_steps']}; best epoch={best_epoch}", flush=True)


if __name__ == "__main__":
    main()
