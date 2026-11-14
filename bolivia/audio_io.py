"""Audio helpers for the notebook. validate(original, modified) returns edit percentages."""

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 16_000
CLIP_SAMPLES = 32_000
MAX_MODIFICATION_ENERGY_FRACTION = 0.01


def validate(original, modified):
    """Check transformed audio against the supplied original (B, 32000) array."""
    if not isinstance(modified, np.ndarray) or modified.dtype != np.float32:
        raise ValueError("Return a NumPy array with dtype float32.")
    if modified.shape != original.shape:
        raise ValueError(f"Keep the original audio shape: {original.shape}.")
    if not np.isfinite(modified).all():
        raise ValueError("Audio contains NaN or infinity.")

    percentages = []
    for index, (before, after) in enumerate(zip(original, modified)):
        try:
            percentages.append(preservation(before, after))
        except ValueError as error:
            raise ValueError(f"Recording {index}: {error}") from None
    return np.array(percentages)


def preservation(original, modified):
    """Check one recording's amplitude and edit energy; return the edit percentage."""
    if np.max(np.abs(modified)) >= 1.0:
        raise ValueError(
            "Output samples must stay strictly between -1 and 1. "
            "Reduce the strength of your changes and avoid clipping."
        )
    original = original.astype(np.float64)
    edit = modified.astype(np.float64) - original
    original_energy = float(np.sum(original ** 2))
    edit_energy = float(np.sum(edit ** 2))
    if original_energy:
        fraction = edit_energy / original_energy
    else:
        fraction = 0.0 if edit_energy == 0 else np.inf
    # Allow float32 rounding at the 1% boundary.
    if fraction > MAX_MODIFICATION_ENERGY_FRACTION * (1 + 1e-7):
        raise ValueError(
            f"Edit energy is {100*fraction:.6g}% of the recording; "
            "maximum is 1%. Reduce the strength of your changes."
        )
    return 100 * fraction


def decode_wav_mono(path):
    """Read a supplied mono PCM16 WAV as float32 audio amplitudes."""
    rate, samples = wavfile.read(path)
    return samples.astype(np.float32) / 32768.0, int(rate)
