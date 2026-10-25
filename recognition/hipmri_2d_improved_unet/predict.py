"""Reload the checkpoint's model and inspect one training/validation sample only."""

import argparse
import json
import os
from pathlib import Path

import torch

from dataset import collate_padded, collect_pairs, crop_to_original, load_pair
from losses import segmentation_cross_entropy
from metrics import SegmentationMetrics
from modules import build_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    workspace = Path(__file__).resolve().parents[4]
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, default=workspace / "Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data")
    parser.add_argument("--split", choices=("training", "validation"), default="training")
    parser.add_argument("--filename", default="case_004_week_0_slice_12.nii.gz")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/baseline_reference"))
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("Use a new output directory to preserve previous inference evidence.")
    if Path(args.filename).name != args.filename:
        raise ValueError("filename must be a basename within the selected split.")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable.")
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else ("cpu" if args.device == "auto" else args.device))
    torch.set_num_threads(1)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    image_folder, mask_folder = {
        "training": ("keras_slices_train", "keras_slices_seg_train"),
        "validation": ("keras_slices_validate", "keras_slices_seg_validate"),
    }[args.split]
    pairs = collect_pairs(args.data_root / image_folder, args.data_root / mask_folder)
    pair = next((pair for pair in pairs if pair[0].name == args.filename), None)
    if pair is None:
        raise ValueError("Requested filename not found in the selected training/validation split.")
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    model_name = checkpoint["model"]
    model = build_model(model_name, **checkpoint["model_config"]).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    sample = load_pair(*pair)
    batch = collate_padded([sample])
    image, target, valid = [batch[key].to(device) for key in ("image", "target", "valid_mask")]
    with torch.inference_mode():
        logits = model(image)
        loss = segmentation_cross_entropy(logits, target, valid)
        prediction = logits.argmax(dim=1)
    metrics = SegmentationMetrics(checkpoint["model_config"]["num_classes"])
    metrics.update(prediction, target, valid)
    size = sample["original_size"]
    image_original = crop_to_original(sample["image"], size)[0].numpy()
    target_original = crop_to_original(sample["target"], size).numpy()
    prediction_original = crop_to_original(prediction[0].cpu(), size).numpy()
    args.output_dir.mkdir(parents=True)
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(args.output_dir.resolve() / ".matplotlib"))
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    num_classes = checkpoint["model_config"]["num_classes"]
    palette = ["black", "gold", "deepskyblue", "magenta", "limegreen", "orange"]
    colors = ListedColormap(palette[:num_classes]) if num_classes <= 6 else plt.get_cmap("tab20", num_classes)
    fig, axes = plt.subplots(1, 3, figsize=(10, 6), layout="constrained")
    axes[0].imshow(image_original, cmap="gray", interpolation="nearest")
    axes[0].set_title("Training MRI" if args.split == "training" else "Validation MRI")
    prediction_title = f"{model_name} prediction"
    for axis, values, title in ((axes[1], target_original, "Reference mask"), (axes[2], prediction_original, prediction_title)):
        shown = axis.imshow(values, cmap=colors, vmin=-0.5, vmax=num_classes - 0.5, interpolation="nearest")
        axis.set_title(title)
    fig.colorbar(shown, ax=list(axes[1:]), ticks=list(range(num_classes)), label="Class ID")
    fig.suptitle(f"{args.split}: {args.filename} | checkpoint epoch {checkpoint['epoch']}")
    fig.savefig(args.output_dir / "prediction.png", dpi=150)
    plt.close(fig)
    summary = {"model": model_name, "performed_by": "Codex automation", "split": args.split,
               "is_improved_run": model_name == "improved_unet",
               "filename": args.filename, "checkpoint_epoch": checkpoint["epoch"],
               "limited_training_smoke": checkpoint.get("limited_training_smoke", False),
               "logit_shape": list(logits.shape), "restored_shape": list(prediction_original.shape),
               "cross_entropy": float(loss.item()), "metrics": metrics.compute(),
               "test_split_read": False, "claim_boundary": "Single-sample inspection; not independent test evaluation or final model quality."}
    (args.output_dir / "prediction_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("split", "filename", "checkpoint_epoch", "logit_shape", "restored_shape", "cross_entropy")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
