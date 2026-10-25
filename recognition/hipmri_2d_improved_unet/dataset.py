"""Data preprocessing helpers for the guided HipMRI rebuild."""

import torch


def minmax_normalize(values):
    if not torch.isfinite(values).all():
        raise ValueError("MRI intensities must be finite before normalization.")
    minimum = values.min()
    maximum = values.max()
    if maximum == minimum:
        return torch.zeros_like(values)
    return (values - minimum) / (maximum - minimum)
