"""AI stem splitting (Demucs v4 / HTDemucs via ONNX Runtime).

Supports 2-stem (vocals / accompaniment) and 4-stem (vocals / drums / bass /
other) topologies. Emits staged progress: load model → analyze → separate →
write.
"""

from __future__ import annotations

from collections.abc import Callable

from ..audio_io import AudioBuffer

ProgressFn = Callable[[str, float], None]

TOPOLOGIES = {
    "2stem": ("vocals", "accompaniment"),
    "4stem": ("vocals", "drums", "bass", "other"),
}


def split(
    buf: AudioBuffer,
    topology: str = "4stem",
    on_progress: ProgressFn | None = None,
) -> dict[str, AudioBuffer]:
    """Separate ``buf`` into stems keyed by stem name.

    TODO: load ONNX session (runtime.select_provider), chunk + overlap-add
    inference, recombine stems.
    """
    if topology not in TOPOLOGIES:
        raise ValueError(f"Unknown topology: {topology!r}")
    raise NotImplementedError("Stem splitting not yet implemented (scaffold).")
