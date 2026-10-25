"""Inspect training filenames only; run from the guided repository root."""

from pathlib import Path

from dataset import collect_pairs

data_root = Path(
    "../../Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data"
)
image_dir = data_root / "keras_slices_train"
mask_dir = data_root / "keras_slices_seg_train"
training_pairs = collect_pairs(image_dir, mask_dir)
reference_pair = (
    image_dir / "case_004_week_0_slice_12.nii.gz",
    mask_dir / "seg_004_week_0_slice_12.nii.gz",
)

print("Paired training filenames:", len(training_pairs))
print("Reference pair found:", reference_pair in training_pairs)
