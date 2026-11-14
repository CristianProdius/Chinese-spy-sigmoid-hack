"""Public, ordinary learned audio classifier for The Forest Went Quiet."""

from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from audio_io import CLIP_SAMPLES

CLASS_NAMES = ("birds", "frogs", "insects", "rain")
MODEL_FILENAME = "challenge-model.pt"


def stem(cin, cout):
    return nn.Sequential(
        nn.Conv2d(cin, cout, 3, padding=1, bias=False),
        nn.AvgPool2d(2),
        nn.BatchNorm2d(cout),
        nn.ReLU(),
    )


def depthwise(cin, cout, stride):
    return nn.Sequential(
        nn.Conv2d(cin, cin, 3, padding=1, groups=cin, bias=False),
        nn.AvgPool2d(stride),
        nn.BatchNorm2d(cin),
        nn.ReLU(),
        nn.Conv2d(cin, cout, 1, bias=False),
        nn.BatchNorm2d(cout),
        nn.ReLU(),
    )


class SemanticEncoder(nn.Module):
    """PANNs MobileNetV1 encoder, adapted under the bundled MIT license.

    The frequency bank is taken from the authenticated upstream checkpoint. At
    16 kHz, a 512-point STFT has the same frequency spacing as its 32 kHz/1024-point
    counterpart. Multiplying power by four compensates for transform length; bins
    above the input Nyquist frequency contain no energy. No runtime downloads.
    """

    def __init__(self):
        super().__init__()
        self.register_buffer("window", torch.hann_window(512))
        self.register_buffer("mel_bank", torch.zeros(257, 64))
        self.bn0 = nn.BatchNorm2d(64)
        shape = [
            (32, 64, 1),
            (64, 128, 2),
            (128, 128, 1),
            (128, 256, 2),
            (256, 256, 1),
            (256, 512, 2),
            *([(512, 512, 1)] * 5),
            (512, 1024, 2),
            (1024, 1024, 1),
        ]
        self.features = nn.Sequential(
            stem(1, 32), *(depthwise(a, b, s) for a, b, s in shape)
        )
        self.fc1 = nn.Linear(1024, 1024)

    def forward(self, audio):
        power = (
            torch.stft(
                audio,
                n_fft=512,
                hop_length=160,
                window=self.window,
                return_complex=True,
                center=True,
            )
            .abs()
            .square()
            * 4
        )
        mel = 10 * torch.log10(
            torch.clamp(power.transpose(1, 2) @ self.mel_bank, min=1e-10)
        )
        x = self.bn0(mel.transpose(1, 2).unsqueeze(-1)).transpose(1, 3)
        x = self.features(x).mean(-1)
        return F.relu(self.fc1(x.amax(-1) + x.mean(-1)))


class TemporalBlock(nn.Module):
    def __init__(self, channels, dilation):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv1d(channels, channels, 5, padding=2 * dilation, dilation=dilation),
            nn.GroupNorm(8, channels),
            nn.GELU(),
            nn.Conv1d(channels, channels, 1),
        )

    def forward(self, x):
        return x + self.layers(x)


class TemporalEncoder(nn.Module):
    """Encode fine frequency and timing details with convolution and pooling."""

    def __init__(self):
        super().__init__()
        self.register_buffer("window", torch.hann_window(512))
        self.spatial = nn.Sequential(
            nn.Conv2d(1, 8, (5, 3), stride=(4, 1), padding=(2, 1)),
            nn.GroupNorm(4, 8),
            nn.GELU(),
            nn.Conv2d(8, 16, (5, 3), stride=(4, 1), padding=(2, 1)),
            nn.GroupNorm(4, 16),
            nn.GELU(),
            nn.Conv2d(16, 24, (5, 3), stride=(2, 1), padding=(2, 1)),
            nn.GroupNorm(4, 24),
            nn.GELU(),
        )
        self.projection = nn.Sequential(nn.Conv1d(24 * 9, 64, 1), nn.GELU())
        self.temporal = nn.Sequential(*(TemporalBlock(64, d) for d in (1, 2, 4, 8)))

    def forward(self, audio):
        spectrum = torch.log1p(
            10
            * torch.stft(
                audio,
                n_fft=512,
                hop_length=160,
                window=self.window,
                center=True,
                return_complex=True,
            ).abs()
        )

        features = self.spatial(spectrum.unsqueeze(1)).flatten(1, 2)
        features = self.temporal(self.projection(features))
        return torch.cat([features.mean(-1), features.amax(-1)], dim=1)


class AudioClassifier(nn.Module):
    """Learned fusion of semantic and temporally detailed audio representations."""

    architecture_name = "forest-semantic-temporal-v2"

    def __init__(self):
        super().__init__()
        self.semantic = SemanticEncoder()
        self.detail = TemporalEncoder()
        self.classifier = nn.Linear(1152, 4)

    def forward(self, audio):
        if audio.ndim != 2 or audio.shape[1] != CLIP_SAMPLES:
            raise ValueError("Expected (B, 32000) audio")
        audio = audio.float()
        semantic = self.semantic(audio)
        detail = self.detail(audio)
        return self.classifier(torch.cat([semantic, detail], dim=1))


def load_model(path=None):
    """Load the supplied classifier, ready for predictions and inspection."""
    path = Path(path) if path else Path(__file__).with_name(MODEL_FILENAME)
    saved = torch.load(path, map_location="cpu", weights_only=True)
    if (
        saved["architecture"] != AudioClassifier.architecture_name
        or tuple(saved["class_names"]) != CLASS_NAMES
    ):
        raise ValueError("Checkpoint does not match the public architecture")
    model = AudioClassifier()
    model.load_state_dict(saved["state_dict"], strict=True)
    return model.eval()


def predict_probabilities(model, audio, *, batch_size=16):
    """Return four class probabilities per recording, accepting one clip or a batch."""
    x = np.asarray(audio, dtype=np.float32)
    if x.ndim == 1:
        x = x[None]
    if not len(x) or batch_size < 1:
        raise ValueError("Provide at least one recording and a positive batch size.")
    with torch.inference_mode():
        return np.concatenate(
            [
                model(torch.from_numpy(x[i : i + batch_size].copy()))
                .softmax(-1)
                .numpy()
                for i in range(0, len(x), batch_size)
            ]
        )
