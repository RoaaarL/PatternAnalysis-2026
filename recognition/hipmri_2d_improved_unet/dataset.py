"""Data loading and preprocessing helpers for the guided HipMRI rebuild."""

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


class HipMRIPairDataset(Dataset):
    """Load single samples from a caller-verified list of MRI/mask path pairs."""

    def __init__(self, pairs):
        self.pairs = list(pairs)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, mask_path = self.pairs[index]
        return load_pair(image_path, mask_path)
