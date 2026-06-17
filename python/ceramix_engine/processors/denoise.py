"""AI noise removal & speech enhancement (DeepFilterNet via ONNX Runtime).

Removes static hiss, room reverb, and background environmental noise while
isolating the human voice. ``intensity`` (0-100) controls the dry/wet blend
between the original and enhanced signal.
"""

from __future__ import annotations

from collections.abc import Callable

from ..audio_io import AudioBuffer

ProgressFn = Callable[[str, float], None]


def denoise(
    buf: AudioBuffer,
    intensity: int = 100,
    on_progress: ProgressFn | None = None,
) -> AudioBuffer:
    """Return an enhanced copy of ``buf``.

    ``intensity`` maps to a dry/wet mix: 0 = original, 100 = fully enhanced.
    TODO: ONNX inference + dry/wet crossfade.
    """
    if not 0 <= intensity <= 100:
        raise ValueError("intensity must be between 0 and 100")
    raise NotImplementedError("Denoise not yet implemented (scaffold).")
