"""Notebook helpers for loading, listening to, and inspecting recordings."""
import csv
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Audio, HTML, display

from audio_io import SAMPLE_RATE, decode_wav_mono
from challenge_model import CLASS_NAMES, predict_probabilities


def load_recordings(root="."):
    """Load the supplied audio in recordings.csv order."""
    root = Path(root)
    with (root / "recordings.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    clips = [decode_wav_mono(root / row["path"])[0] for row in rows]
    return np.stack(clips), rows


def playback(audio):
    """Create a notebook audio player without changing the playback level."""
    return Audio(audio, rate=SAMPLE_RATE, normalize=False)


def show_table(headers, rows, *, details=None):
    """Display a notebook table, optionally inside a collapsible details panel."""
    headings = "".join(f"<th>{escape(str(value))}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    markup = f"<table><thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table>"
    if details:
        markup = f"<details><summary>{escape(details)}</summary>{markup}</details>"
    display(HTML(markup))


def show_recordings(rows, probabilities):
    """Show a compact audit overview with an expandable recording list."""
    failures = sum(row["classification_status"] == "misclassified" for row in rows)
    print(f"Loaded {len(rows)} recordings: {failures} failures and {len(rows) - failures} references.")
    show_table(
        ["Index", "Recording", "Correct label", "Status", "Model prediction"],
        [(index, row["clip_id"], row["label"], row["classification_status"],
          CLASS_NAMES[int(probs.argmax())])
         for index, (row, probs) in enumerate(zip(rows, probabilities))],
        details=f"Browse all {len(rows)} recordings",
    )


def inspect_recording(recordings, rows, model, index=0):
    """Listen to one recording and show its plots and all class probabilities."""
    if not 0 <= index < len(recordings):
        raise ValueError(f"Choose an index from 0 to {len(recordings) - 1}.")
    audio, row = recordings[index], rows[index]
    print(f"{row['clip_id']} — correct label: {row['label']}")
    display(playback(audio))
    fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    axes[0].plot(np.arange(len(audio)) / SAMPLE_RATE, audio, linewidth=.6)
    axes[0].set_ylabel("Amplitude")
    axes[1].specgram(audio, Fs=SAMPLE_RATE, NFFT=512, noverlap=352, cmap="magma")
    axes[1].set(xlabel="Time (s)", ylabel="Frequency (Hz)")
    fig.tight_layout()
    plt.show()
    probabilities = predict_probabilities(model, audio)[0]
    show_table(["Class", "Probability"],
               [(name, f"{probability:.1%}")
                for name, probability in zip(CLASS_NAMES, probabilities)])
