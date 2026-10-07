import torch
import torch.nn as nn
import torch.nn.functional as F

MODULATION_CLASSES = ["BPSK", "QPSK", "8PSK", "FSK", "16QAM"]


class ResidualBlock1D(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(channels)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return F.relu(out)


class ModulationCNN(nn.Module):
    """1D ResNet/CNN Architecture for IQ Modulation Classification.

    Input shape: (batch_size, 2, 1024) where channel 0 = I, channel 1 = Q.
    Output shape: (batch_size, num_classes)
    """

    def __init__(self, num_classes: int = len(MODULATION_CLASSES)):
        super().__init__()
        self.num_classes = num_classes

        self.prep = nn.Sequential(
            nn.Conv1d(2, 32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2),
        )

        self.res1 = ResidualBlock1D(32)

        self.layer2 = nn.Sequential(
            nn.Conv1d(32, 64, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
        )

        self.res2 = ResidualBlock1D(64)

        self.layer3 = nn.Sequential(
            nn.Conv1d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
        )

        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.prep(x)
        out = self.res1(out)
        out = self.layer2(out)
        out = self.res2(out)
        out = self.layer3(out)
        out = self.pool(out)
        out = torch.flatten(out, 1)
        logits = self.fc(out)
        return logits
