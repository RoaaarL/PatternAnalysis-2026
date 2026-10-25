"""Inspect one training pair as arrays and tensors; run from the repository root."""

from pathlib import Path

import nibabel as nib
import numpy as np
import torch
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

data_root = Path(
    "../../Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data"
)
image_path = data_root / "keras_slices_train" / "case_004_week_0_slice_12.nii.gz"
mask_path = data_root / "keras_slices_seg_train" / "seg_004_week_0_slice_12.nii.gz"

image = nib.load(image_path).get_fdata()
mask = nib.load(mask_path).get_fdata()

print("MRI shape:", image.shape)
print("Mask shape:", mask.shape)
print("Mask labels:", np.unique(mask))

if not np.isfinite(mask).all() or not np.equal(mask, np.floor(mask)).all():
    raise ValueError("Mask values must be finite integers before casting.")

image_tensor = torch.from_numpy(image).to(torch.float32).unsqueeze(0)
mask_tensor = torch.from_numpy(mask).to(torch.long)

print("MRI tensor shape:", tuple(image_tensor.shape))
print("MRI tensor dtype:", image_tensor.dtype)
print("Mask tensor shape:", tuple(mask_tensor.shape))
print("Mask tensor dtype:", mask_tensor.dtype)
print("Mask tensor labels:", torch.unique(mask_tensor).tolist())

# These four display colors cover the labels observed in this fixed slice.
mask_colors = ListedColormap(["black", "gold", "deepskyblue", "magenta"])
fig, axes = plt.subplots(1, 2, figsize=(8, 6), layout="constrained")
axes[0].imshow(image, cmap="gray", origin="upper", interpolation="nearest")
axes[0].set_title("Training MRI")
mask_plot = axes[1].imshow(
    mask, cmap=mask_colors, vmin=-0.5, vmax=3.5,
    origin="upper", interpolation="nearest"
)
axes[1].set_title("Reference mask")
fig.colorbar(mask_plot, ax=axes[1], ticks=[0, 1, 2, 3], label="Class ID")
fig.suptitle("Training pair: case 004 | week 0 | slice 12")

output_path = Path("outputs/training_pair_case_004_week_0_slice_12.png")
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_path, dpi=150)
plt.close(fig)
print("Preview saved:", output_path.resolve())
