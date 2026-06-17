"""Registry of available models: id → download URL, checksum, and metadata.

Keeping weights out of the installer (Step 3) means the registry is the single
source of truth for what gets fetched on first use.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    task: str               # "stem_split" | "denoise"
    url: str                # remote ONNX weight location
    sha256: str             # integrity check
    topology: tuple[str, ...] = field(default_factory=tuple)


# TODO: populate with real URLs + checksums once weights are hosted/converted.
REGISTRY: dict[str, ModelSpec] = {
    "htdemucs-4stem": ModelSpec(
        model_id="htdemucs-4stem",
        task="stem_split",
        url="",
        sha256="",
        topology=("vocals", "drums", "bass", "other"),
    ),
    "htdemucs-2stem": ModelSpec(
        model_id="htdemucs-2stem",
        task="stem_split",
        url="",
        sha256="",
        topology=("vocals", "accompaniment"),
    ),
    "deepfilternet3": ModelSpec(
        model_id="deepfilternet3",
        task="denoise",
        url="",
        sha256="",
    ),
}
