"""Vanilla 2D U-Net baseline; no Improved U-Net components or pretrained weights."""

import torch
from torch import nn


class DoubleConv(nn.Module):
    """Two same-padding 3x3 convolutions, each followed by ReLU."""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

    def forward(self, values):
        return self.layers(values)


class UNet(nn.Module):
    """Four-downsampling U-Net returning [B,num_classes,H,W] raw logits.

    Same-padding convolutions preserve the padded sample dimensions. Input
    height and width must be multiples of 16, matching the preprocessing API.
    Channel width is a configurable resource choice; the default is 16.
    """

    required_multiple = 16

    def __init__(self, in_channels=1, num_classes=6, base_channels=16):
        super().__init__()
        for name, value in (
            ("in_channels", in_channels),
            ("num_classes", num_classes),
            ("base_channels", base_channels),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.base_channels = base_channels
        width = base_channels

        self.enc1 = DoubleConv(in_channels, width)
        self.enc2 = DoubleConv(width, width * 2)
        self.enc3 = DoubleConv(width * 2, width * 4)
        self.enc4 = DoubleConv(width * 4, width * 8)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.bottleneck = DoubleConv(width * 8, width * 16)

        self.up4 = nn.ConvTranspose2d(width * 16, width * 8, kernel_size=2, stride=2)
        self.dec4 = DoubleConv(width * 16, width * 8)
        self.up3 = nn.ConvTranspose2d(width * 8, width * 4, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(width * 8, width * 4)
        self.up2 = nn.ConvTranspose2d(width * 4, width * 2, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(width * 4, width * 2)
        self.up1 = nn.ConvTranspose2d(width * 2, width, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(width * 2, width)
        self.output = nn.Conv2d(width, num_classes, kernel_size=1)

    def forward(self, image):
        if image.ndim != 4:
            raise ValueError("U-Net input must have shape [B,C,H,W].")
        if image.shape[0] == 0 or image.shape[1] != self.in_channels:
            raise ValueError(f"Expected a nonempty batch with {self.in_channels} channels.")
        height, width = image.shape[-2:]
        if min(height, width) < self.required_multiple or (
            height % self.required_multiple or width % self.required_multiple
        ):
            raise ValueError("Input height and width must be >=16 and multiples of 16.")
        if not image.is_floating_point():
            raise TypeError("U-Net input must be floating-point image values.")

        skip1 = self.enc1(image)
        skip2 = self.enc2(self.pool(skip1))
        skip3 = self.enc3(self.pool(skip2))
        skip4 = self.enc4(self.pool(skip3))
        encoded = self.bottleneck(self.pool(skip4))

        decoded4 = self.dec4(torch.cat((self.up4(encoded), skip4), dim=1))
        decoded3 = self.dec3(torch.cat((self.up3(decoded4), skip3), dim=1))
        decoded2 = self.dec2(torch.cat((self.up2(decoded3), skip2), dim=1))
        decoded1 = self.dec1(torch.cat((self.up1(decoded2), skip1), dim=1))
        return self.output(decoded1)
