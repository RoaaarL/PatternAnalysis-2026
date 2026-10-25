"""Read one training pair; run from the guided repository root."""

from pathlib import Path

import nibabel as nib
import numpy as np

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
