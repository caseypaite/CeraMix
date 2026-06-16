"""High-fidelity audio I/O via FFmpeg (decode/encode) and soundfile (WAV/FLAC).

Decoding path: FFmpeg normalizes arbitrary inputs (MP3/M4A/FLAC/WAV) to float32
PCM; soundfile/libsndfile handles lossless writes. MP3 export goes back through
FFmpeg at 320 kbps.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AudioBuffer:
    """In-memory float32 audio. ``samples`` shape is (channels, frames)."""

    samples: "object"  # numpy.ndarray once implemented
    sample_rate: int
    channels: int


def load(path: str, target_sr: int | None = None) -> AudioBuffer:
    """Decode any supported file to a float32 AudioBuffer. TODO: FFmpeg pipe."""
    raise NotImplementedError


def write_wav(path: str, buf: AudioBuffer, bit_depth: int = 24) -> None:
    """Write lossless WAV (16/24/32-bit float). TODO: soundfile.write."""
    raise NotImplementedError


def write_mp3(path: str, buf: AudioBuffer, bitrate: str = "320k") -> None:
    """Encode MP3 via FFmpeg. TODO: subprocess pipe to libmp3lame."""
    raise NotImplementedError
