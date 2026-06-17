"""High-fidelity audio I/O via FFmpeg (decode/encode) and soundfile (WAV/FLAC).

Decoding path: FFmpeg normalizes arbitrary inputs (MP3/M4A/FLAC/WAV) to float32
PCM; soundfile/libsndfile handles lossless writes. MP3 export goes back through
FFmpeg at 320 kbps.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

import numpy as np
import soundfile as sf


@dataclass
class AudioBuffer:
    """In-memory float32 audio. ``samples`` shape is (channels, frames)."""

    samples: np.ndarray
    sample_rate: int
    channels: int


def load(path: str, target_sr: int | None = None) -> AudioBuffer:
    """Decode any supported file to a float32 AudioBuffer via FFmpeg pipe."""
    # Probe native sample rate and channel count.
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels",
            "-of", "csv=p=0",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    sr_str, ch_str = probe.stdout.strip().split(",")
    src_sr = int(sr_str)
    channels = int(ch_str)
    out_sr = target_sr if target_sr is not None else src_sr

    # Decode to interleaved float32 PCM via stdout pipe.
    result = subprocess.run(
        [
            "ffmpeg", "-v", "error",
            "-i", path,
            "-f", "f32le",
            "-acodec", "pcm_f32le",
            "-ar", str(out_sr),
            "-ac", str(channels),
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    samples = np.frombuffer(result.stdout, dtype=np.float32)
    # Reshape interleaved (frames * channels,) → (channels, frames).
    samples = samples.reshape(-1, channels).T.copy()
    return AudioBuffer(samples=samples, sample_rate=out_sr, channels=channels)


_WAV_SUBTYPE: dict[int, str] = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}


def write_wav(path: str, buf: AudioBuffer, bit_depth: int = 24) -> None:
    """Write lossless WAV at 16, 24, or 32-bit (float) depth via soundfile."""
    subtype = _WAV_SUBTYPE.get(bit_depth)
    if subtype is None:
        raise ValueError(f"bit_depth must be 16, 24, or 32; got {bit_depth}")
    # soundfile expects (frames, channels).
    data = np.asarray(buf.samples, dtype=np.float32).T
    sf.write(path, data, buf.sample_rate, subtype=subtype)


def write_mp3(path: str, buf: AudioBuffer, bitrate: str = "320k") -> None:
    """Encode MP3 via FFmpeg subprocess pipe to libmp3lame."""
    # Feed interleaved float32 PCM to FFmpeg via stdin.
    data = np.asarray(buf.samples, dtype=np.float32).T  # (frames, channels)
    subprocess.run(
        [
            "ffmpeg", "-v", "error",
            "-f", "f32le",
            "-ar", str(buf.sample_rate),
            "-ac", str(buf.channels),
            "-i", "pipe:0",
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            "-y",
            path,
        ],
        input=data.tobytes(),
        check=True,
    )
