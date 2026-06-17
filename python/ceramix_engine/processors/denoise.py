"""Spectral-subtraction noise reduction.

Estimates the noise floor from the quietest frames of the signal and
subtracts it from every frame's magnitude spectrum, then reconstructs via
overlap-add ISTFT.  ``intensity`` (0–100) controls the dry/wet blend between
the original and the enhanced signal.

This is a pure-numpy implementation with no external model weights.  Replace
_spectral_denoise() with ONNX DeepFilterNet inference for higher-quality
speech enhancement once model weights are available.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ..audio_io import AudioBuffer

ProgressFn = Callable[[str, float], None]

_FRAME_LEN = 2048
_HOP = _FRAME_LEN // 4          # 75 % overlap
_ALPHA = 2.0                     # over-subtraction factor (reduces musical noise)
_BETA = 0.01                     # spectral floor relative to original magnitude


def denoise(
    buf: AudioBuffer,
    intensity: int = 100,
    on_progress: ProgressFn | None = None,
) -> AudioBuffer:
    """Return a noise-reduced copy of *buf*.

    *intensity* maps to a dry/wet blend: 0 = original, 100 = fully enhanced.
    """
    if not 0 <= intensity <= 100:
        raise ValueError("intensity must be between 0 and 100")

    wet = intensity / 100.0
    if wet == 0.0:
        return AudioBuffer(
            samples=buf.samples.copy(),
            sample_rate=buf.sample_rate,
            channels=buf.channels,
        )

    samples = np.asarray(buf.samples, dtype=np.float32)  # (channels, frames)
    n_ch = samples.shape[0]
    enhanced_channels = []

    for ch in range(n_ch):
        enhanced = _spectral_denoise(samples[ch], buf.sample_rate)
        enhanced_channels.append(enhanced)
        if on_progress:
            on_progress("denoise", (ch + 1) / n_ch)

    enhanced = np.stack(enhanced_channels, axis=0)
    blended = (1.0 - wet) * samples + wet * enhanced

    return AudioBuffer(
        samples=blended.astype(np.float32),
        sample_rate=buf.sample_rate,
        channels=buf.channels,
    )


def _spectral_denoise(signal: np.ndarray, sample_rate: int) -> np.ndarray:
    """Spectral-subtraction noise reduction on a mono float32 signal."""
    n = len(signal)
    win = np.hanning(_FRAME_LEN).astype(np.float32)
    win_sq = win ** 2

    n_frames = max(1, (n - _FRAME_LEN) // _HOP + 1)
    pad = max(0, (n_frames - 1) * _HOP + _FRAME_LEN - n)
    padded = np.pad(signal, (0, pad))

    # Analysis: window each frame and compute FFT.
    from numpy.lib.stride_tricks import as_strided
    shape = (n_frames, _FRAME_LEN)
    strides = (padded.strides[0] * _HOP, padded.strides[0])
    frames = as_strided(padded, shape=shape, strides=strides) * win  # copy
    spectra = np.fft.rfft(frames, axis=1)  # (n_frames, bins)
    mag = np.abs(spectra).astype(np.float32)
    phase = np.angle(spectra).astype(np.float32)

    # Noise profile: average magnitude of the quietest 10 % of frames.
    frame_level = mag.mean(axis=1)
    n_noise = max(1, n_frames // 10)
    noise_frames = np.argsort(frame_level)[:n_noise]
    noise_profile = mag[noise_frames].mean(axis=0)  # (bins,)

    # Spectral subtraction with over-subtraction and a hard spectral floor.
    enhanced_mag = np.maximum(
        mag - _ALPHA * noise_profile,
        _BETA * mag,
    )

    # Synthesis: reconstruct via overlap-add ISTFT.
    enhanced_spectra = enhanced_mag * np.exp(1j * phase)
    enhanced_frames = np.fft.irfft(enhanced_spectra, n=_FRAME_LEN, axis=1).astype(np.float32)

    output = np.zeros(len(padded), dtype=np.float32)
    norm = np.zeros(len(padded), dtype=np.float32)
    for i in range(n_frames):
        s = i * _HOP
        output[s:s + _FRAME_LEN] += enhanced_frames[i] * win
        norm[s:s + _FRAME_LEN] += win_sq

    norm = np.where(norm > 1e-8, norm, 1.0)
    return (output / norm)[:n].astype(np.float32)
