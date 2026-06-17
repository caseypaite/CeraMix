"""Lazy model-weight downloader.

Fetches ONNX weights into the OS app-data directory on first use, verifies the
SHA-256 checksum, and reports progress. Keeps the installer small (Step 3).
"""

from __future__ import annotations

from pathlib import Path

from .registry import REGISTRY, ModelSpec


def model_cache_dir() -> Path:
    """Return the per-user model cache directory (created if missing).

    TODO: resolve the real platform app-data path passed from the Tauri shell.
    """
    path = Path.home() / ".cache" / "ceramix" / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_model(model_id: str) -> Path:
    """Ensure weights for ``model_id`` are present locally; download if needed.

    TODO: stream download with progress + checksum verification against the spec.
    """
    spec: ModelSpec = REGISTRY[model_id]
    target = model_cache_dir() / f"{spec.model_id}.onnx"
    if not target.exists():
        raise NotImplementedError(
            f"Download for '{model_id}' not yet implemented (scaffold)."
        )
    return target
