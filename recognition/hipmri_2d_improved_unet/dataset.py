"""Data loading and preprocessing helpers for the guided HipMRI rebuild."""

from pathlib import Path

import nibabel as nib
import numpy as np
import torch
from torch.utils.data import Dataset


def minmax_normalize(values):
    if not torch.isfinite(values).all():
        raise ValueError("MRI intensities must be finite before normalization.")
    minimum = values.min()
    maximum = values.max()
    if maximum == minimum:
        return torch.zeros_like(values)
    return (values - minimum) / (maximum - minimum)


def load_pair(image_path, mask_path):
    """Load one already-paired 2D MRI/mask as normalized image and class IDs."""
    image = nib.load(image_path).get_fdata()
    mask = nib.load(mask_path).get_fdata()
    if image.ndim != 2 or image.shape != mask.shape:
        raise ValueError("Expected matching 2D MRI and mask shapes.")
    if not np.isfinite(mask).all() or not np.equal(mask, np.floor(mask)).all():
        raise ValueError("Mask values must be finite integers before casting.")
    image_tensor = torch.from_numpy(image).to(torch.float32).unsqueeze(0)
    mask_tensor = torch.from_numpy(mask).to(torch.long)
    return minmax_normalize(image_tensor), mask_tensor


def collect_pairs(image_dir, mask_dir):
    """Match existing case_/seg_ filenames without reading NIfTI contents."""
    image_paths = sorted(
        path for path in Path(image_dir).glob("case_*.nii.gz") if path.is_file()
    )
    if not image_paths:
        raise ValueError(f"No MRI files found in {image_dir}")
    pairs = []
    for image_path in image_paths:
        mask_name = image_path.name.replace("case_", "seg_", 1)
        mask_path = Path(mask_dir) / mask_name
        if not mask_path.is_file():
            raise FileNotFoundError(f"Missing mask: {mask_path}")
        pairs.append((image_path, mask_path))
    mask_count = sum(
        path.is_file() for path in Path(mask_dir).glob("seg_*.nii.gz")
    )
    if mask_count != len(pairs):
        raise ValueError("Extra mask files without a matching MRI; check filenames.")
    return pairs


class HipMRIPairDataset(Dataset):
    """Load single samples from a caller-verified list of MRI/mask path pairs."""

    def __init__(self, pairs):
        self.pairs = list(pairs)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, mask_path = self.pairs[index]
        return load_pair(image_path, mask_path)
