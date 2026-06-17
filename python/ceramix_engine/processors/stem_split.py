"""DSP-based stem splitting via HPSS + frequency masking.

Supports 2-stem (vocals / accompaniment) and 4-stem (vocals / drums / bass /
other) topologies.  The separation pipeline is:
  1. Extract audio via FFmpeg (handles audio and video containers).
  2. Decompose the spectrogram into harmonic (H) and percussive (P) components
     using Harmonic-Percussive Source Separation (HPSS) with Wiener masks.
  3. Apply frequency-band and mid/side masks to assign energy to each stem.

Replace _dsp_separate() with ONNX model inference (Demucs / HTDemucs) once
model weights are available — the public split_files() API is unchanged.
"""

from __future__ import annotations

import subprocess
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.ndimage import median_filter

TOPOLOGIES: dict[str, tuple[str, ...]] = {
    "2stem": ("vocals", "accompaniment"),
    "4stem": ("vocals", "drums", "bass", "other"),
}

# STFT parameters
_FRAME_LEN = 4096
_HOP = 1024

# HPSS median-filter kernel width (bins / frames)
_HPSS_KERNEL = 17

# Frequency boundaries (Hz)
_BASS_MAX_HZ = 300.0
_VOCAL_MIN_HZ = 150.0
_VOCAL_MAX_HZ = 4000.0


def split_files(
    input_path: str,
    topology: str = "4stem",
    output_dir: str = "",
) -> dict[str, str]:
    """Separate *input_path* (audio or video) into per-stem 24-bit WAV files.

    Returns a ``{stem_name: output_path}`` mapping.
    """
    import shutil as _shutil

    if topology not in TOPOLOGIES:
        raise ValueError(f"Unknown topology {topology!r}. Choose from: {list(TOPOLOGIES)}")

    stem_names = TOPOLOGIES[topology]
    base = Path(input_path).stem
    out_dir = Path(output_dir) if output_dir else Path(input_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = _shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found on PATH. Install it to enable stem splitting.")

    tmp_wav = out_dir / f"{base}_tmp_{uuid.uuid4().hex[:8]}.wav"
    try:
        # Step 1 — extract a clean 44.1 kHz stereo WAV from the source.
        subprocess.run(
            [
                ffmpeg, "-y", "-i", input_path,
                "-vn",
                "-ar", "44100",
                "-ac", "2",
                "-f", "wav",
                str(tmp_wav),
            ],
            check=True,
            capture_output=True,
        )

        data, sr = sf.read(str(tmp_wav), dtype="float32", always_2d=True)
        signal = data.T  # (channels, frames)
        if signal.shape[0] == 1:
            signal = np.concatenate([signal, signal], axis=0)

        # Step 2 — DSP separation.
        stems = _dsp_separate(signal, sr, topology)

        # Step 3 — write one WAV per stem.
        output_paths: dict[str, str] = {}
        for name in stem_names:
            out_path = out_dir / f"{base}_{name}.wav"
            sf.write(str(out_path), stems[name].T, sr, subtype="PCM_24")
            output_paths[name] = str(out_path)

    finally:
        tmp_wav.unlink(missing_ok=True)

    return output_paths


# ──────────────────────────────────────────────────────────────────────────────
# STFT / ISTFT helpers
# ──────────────────────────────────────────────────────────────────────────────

def _window() -> np.ndarray:
    return np.hanning(_FRAME_LEN).astype(np.float32)


def _stft(x: np.ndarray) -> tuple[np.ndarray, int]:
    """Short-time FFT of a 1-D signal.

    Returns (spec, n_orig) where spec has shape (bins, frames), complex64.
    """
    from numpy.lib.stride_tricks import as_strided

    n = len(x)
    win = _window()
    n_frames = max(1, (n - _FRAME_LEN) // _HOP + 1)
    pad = max(0, (n_frames - 1) * _HOP + _FRAME_LEN - n)
    xp = np.pad(x.astype(np.float32), (0, pad))

    shape = (n_frames, _FRAME_LEN)
    strides = (xp.strides[0] * _HOP, xp.strides[0])
    frames = as_strided(xp, shape=shape, strides=strides) * win  # copy on multiply
    spec = np.fft.rfft(frames, axis=1).T.astype(np.complex64)    # (bins, frames)
    return spec, n


def _istft(spec: np.ndarray, n_orig: int) -> np.ndarray:
    """Inverse STFT via overlap-add synthesis.

    spec: (bins, frames) complex → float32 (n_orig,)
    """
    win = _window()
    frames = np.fft.irfft(spec.T, n=_FRAME_LEN, axis=1).astype(np.float32)
    n_frames = frames.shape[0]
    n_out = (n_frames - 1) * _HOP + _FRAME_LEN
    output = np.zeros(n_out, dtype=np.float32)
    norm = np.zeros(n_out, dtype=np.float32)
    win_sq = win ** 2

    for i in range(n_frames):
        s = i * _HOP
        output[s:s + _FRAME_LEN] += frames[i] * win
        norm[s:s + _FRAME_LEN] += win_sq

    norm = np.where(norm > 1e-8, norm, 1.0)
    return (output / norm)[:n_orig]


# ──────────────────────────────────────────────────────────────────────────────
# HPSS
# ──────────────────────────────────────────────────────────────────────────────

def _hpss(spec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Wiener-masked Harmonic-Percussive Source Separation.

    Harmonic components are stable over time (horizontal in STFT); percussive
    ones are impulsive and stable across frequency (vertical).

    Returns (harmonic_spec, percussive_spec).
    """
    mag = np.abs(spec)
    # H_hat: smooth along time axis → estimate of harmonic energy
    H_hat = median_filter(mag, size=(1, _HPSS_KERNEL), mode="reflect")
    # P_hat: smooth along freq axis → estimate of percussive energy
    P_hat = median_filter(mag, size=(_HPSS_KERNEL, 1), mode="reflect")

    eps = 1e-8
    denom = H_hat ** 2 + P_hat ** 2 + eps
    mask_H = H_hat ** 2 / denom
    mask_P = P_hat ** 2 / denom
    return spec * mask_H, spec * mask_P


# ──────────────────────────────────────────────────────────────────────────────
# Frequency-bin mask helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fbins(sr: int, lo: float | None, hi: float | None) -> np.ndarray:
    """Boolean mask of shape (bins, 1) selecting [lo, hi) Hz."""
    freqs = np.fft.rfftfreq(_FRAME_LEN, 1.0 / sr)
    mask = np.ones(len(freqs), dtype=bool)
    if lo is not None:
        mask &= freqs >= lo
    if hi is not None:
        mask &= freqs < hi
    return mask[:, np.newaxis]  # broadcast over frames


# ──────────────────────────────────────────────────────────────────────────────
# Separation topologies
# ──────────────────────────────────────────────────────────────────────────────

def _dsp_separate(signal: np.ndarray, sr: int, topology: str) -> dict[str, np.ndarray]:
    """Route to the correct DSP separation strategy."""
    n = signal.shape[1]

    # Mid/side decomposition: mid ≈ center-panned content (vocals, kick);
    # side ≈ laterally-panned content (rhythm instruments, room).
    mid = (signal[0] + signal[1]) * 0.5
    side = (signal[0] - signal[1]) * 0.5

    S_mid, _ = _stft(mid)
    S_side, _ = _stft(side)
    H_mid, P_mid = _hpss(S_mid)
    H_side, P_side = _hpss(S_side)

    def ms_to_stereo(m: np.ndarray, s: np.ndarray) -> np.ndarray:
        return np.stack([m + s, m - s], axis=0)

    def mono_to_stereo(m: np.ndarray) -> np.ndarray:
        return np.stack([m, m], axis=0)

    if topology == "2stem":
        vm = _fbins(sr, _VOCAL_MIN_HZ, _VOCAL_MAX_HZ)
        vocals_sig = _istft(H_mid * vm, n)
        acc_mid = _istft(H_mid * ~vm + P_mid, n)
        acc_side = _istft(H_side + P_side, n)
        return {
            "vocals": mono_to_stereo(vocals_sig),
            "accompaniment": ms_to_stereo(acc_mid, acc_side),
        }

    # 4-stem
    bm = _fbins(sr, None, _BASS_MAX_HZ)            # bass band
    vm = _fbins(sr, _VOCAL_MIN_HZ, _VOCAL_MAX_HZ) & ~bm  # vocal band (no overlap)
    hm = ~bm & ~vm                                  # high-freq harmonic → "other"

    bass_sig = _istft(H_mid * bm, n)
    drums_mid = _istft(P_mid, n)
    drums_side = _istft(P_side, n)
    vocals_sig = _istft(H_mid * vm, n)
    other_mid = _istft(H_mid * hm, n)
    other_side = _istft(H_side, n)

    return {
        "vocals": mono_to_stereo(vocals_sig),
        "drums": ms_to_stereo(drums_mid, drums_side),
        "bass": mono_to_stereo(bass_sig),
        "other": ms_to_stereo(other_mid, other_side),
    }
