"""AI stem splitting (Demucs v4 / HTDemucs via ONNX Runtime).

Supports 2-stem (vocals / accompaniment) and 4-stem (vocals / drums / bass /
other) topologies.

split_files() is the file-path–level entry point used by the server dispatcher.
It currently extracts audio with FFmpeg and writes identical copies per stem so
the full UI pipeline (drag-drop → split → mixer → export) works without model
weights.  Replace the shutil.copy2 block with ONNX inference when models are
bundled.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path

TOPOLOGIES: dict[str, tuple[str, ...]] = {
    "2stem": ("vocals", "accompaniment"),
    "4stem": ("vocals", "drums", "bass", "other"),
}


def split_files(
    input_path: str,
    topology: str = "4stem",
    output_dir: str = "",
) -> dict[str, str]:
    """Separate *input_path* (audio or video) into per-stem WAV files.

    Returns a ``{stem_name: output_path}`` mapping.

    Current implementation:
      1. Extract audio track via FFmpeg (handles audio and video containers).
      2. Copy the extracted audio once per stem name.

    Replace step 2 with ONNX model inference when model weights are available.
    """
    if topology not in TOPOLOGIES:
        raise ValueError(f"Unknown topology: {topology!r}. Choose from: {list(TOPOLOGIES)}")

    stem_names = TOPOLOGIES[topology]
    base = Path(input_path).stem
    out_dir = Path(output_dir) if output_dir else Path(input_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install it to enable stem splitting."
        )

    # Step 1 — extract a clean 44.1 kHz stereo WAV from the source.
    tmp_wav = out_dir / f"{base}_tmp_{uuid.uuid4().hex[:8]}.wav"
    try:
        subprocess.run(
            [
                ffmpeg, "-y", "-i", input_path,
                "-vn",            # drop video track
                "-ar", "44100",   # 44.1 kHz
                "-ac", "2",       # stereo
                "-f", "wav",
                str(tmp_wav),
            ],
            check=True,
            capture_output=True,
        )

        # Step 2 — write one output file per stem.
        # TODO: replace shutil.copy2 with ONNX inference (Demucs / HTDemucs).
        output_paths: dict[str, str] = {}
        for stem_name in stem_names:
            out_path = out_dir / f"{base}_{stem_name}.wav"
            shutil.copy2(str(tmp_wav), str(out_path))
            output_paths[stem_name] = str(out_path)

    finally:
        tmp_wav.unlink(missing_ok=True)

    return output_paths
