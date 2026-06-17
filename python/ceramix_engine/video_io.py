"""Video export: stream-copy the video track, replace audio with mixed stems.

FFmpeg is used for muxing; the video bitstream is never re-encoded, so quality
is lossless with respect to the source and processing is fast.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def export_video(video_path: str, audio_path: str, output_path: str) -> str:
    """Mux *video_path* (video stream only) with *audio_path* into *output_path*.

    Video is stream-copied; audio is encoded to AAC-320k for broad container
    compatibility. Returns *output_path* on success.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg not found on PATH — install FFmpeg and ensure it is in the system PATH."
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Determine output container from extension; default to mp4.
    ext = Path(output_path).suffix.lower()
    extra: list[str] = []
    if ext in (".mp4", ".m4v", ".mov", ""):
        extra = ["-movflags", "+faststart"]

    cmd = [
        ffmpeg, "-y",
        "-i", video_path,        # input 0: source video (video + discarded audio)
        "-i", audio_path,        # input 1: mixed audio
        "-c:v", "copy",          # stream-copy video — no re-encode
        "-c:a", "aac",
        "-b:a", "320k",
        "-map", "0:v:0",         # video track from source
        "-map", "1:a:0",         # audio track from mixed stems
        *extra,
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg mux failed:\n{result.stderr}")

    return output_path
