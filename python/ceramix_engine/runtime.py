"""ONNX Runtime provider selection with graceful CPU fallback.

Implements guardrail Step 5: detect hardware acceleration, fall back to CPU on
failure, and log the decision so hardware incompatibilities are diagnosable.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("ceramix.runtime")

# Preference order — first available wins; CPU is the guaranteed fallback.
_PREFERRED_PROVIDERS = (
    "CUDAExecutionProvider",     # NVIDIA
    "DmlExecutionProvider",      # Windows DirectML
    "CoreMLExecutionProvider",   # Apple Silicon
    "CPUExecutionProvider",      # universal fallback
)


def select_provider() -> str:
    """Return the best available ONNX execution provider name.

    Falls back to ``CPUExecutionProvider`` and logs a warning if no accelerator
    is available or provider initialization fails.
    """
    try:
        import onnxruntime as ort  # noqa: PLC0415

        available = set(ort.get_available_providers())
        for provider in _PREFERRED_PROVIDERS:
            if provider in available:
                logger.info("Selected ONNX execution provider: %s", provider)
                return provider
    except Exception as exc:  # pragma: no cover - scaffold
        logger.warning("ONNX Runtime unavailable, defaulting to CPU: %s", exc)

    return "CPUExecutionProvider"
