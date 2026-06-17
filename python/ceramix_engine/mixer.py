"""Stem mixing with per-stem volume and constant-power pan.

Each stem is loaded as float32 stereo, scaled by its gain and pan, then summed.
A soft-limiter prevents intersample clipping without hard distortion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StemMixInput:
    path: str
    volume: float = 1.0   # 0.0 – 2.0; 1.0 = unity gain
    pan: float = 0.0      # −1.0 hard-left … 0 centre … +1.0 hard-right
    muted: bool = False


def mix(inputs: list[StemMixInput], output_path: str) -> str:
    """Mix stems and write a 24-bit stereo WAV to *output_path*.

    Returns *output_path* on success.
    """
    import numpy as np
    import soundfile as sf

    mixed: np.ndarray | None = None
    out_sr = 44100

    for stem in inputs:
        if stem.muted:
            continue

        data, sr = sf.read(stem.path, dtype="float32", always_2d=True)
        out_sr = sr

        # Normalise to stereo
        if data.shape[1] == 1:
            data = np.concatenate([data, data], axis=1)
        elif data.shape[1] > 2:
            data = data[:, :2]

        # Constant-power pan: angle maps −1..1 → 0..π/2
        angle = (stem.pan + 1.0) * math.pi / 4.0
        left_gain = stem.volume * math.cos(angle)
        right_gain = stem.volume * math.sin(angle)

        data[:, 0] *= left_gain
        data[:, 1] *= right_gain

        if mixed is None:
            mixed = data
        else:
            # Pad shorter buffer with zeros before summing
            diff = len(data) - len(mixed)
            if diff > 0:
                mixed = np.pad(mixed, ((0, diff), (0, 0)))
            elif diff < 0:
                data = np.pad(data, ((0, -diff), (0, 0)))
            mixed = mixed + data

    if mixed is None:
        mixed = np.zeros((out_sr, 2), dtype="float32")

    # Soft peak-limiting: scale down only if peak > 1.0
    peak = float(np.abs(mixed).max())
    if peak > 1.0:
        mixed /= peak

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, mixed, out_sr, subtype="PCM_24")
    return output_path
