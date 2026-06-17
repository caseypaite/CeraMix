"""JSON-RPC entrypoint for the CeraMix backend.

Invoked by the Tauri shell. Reads requests from stdin, dispatches to the
processors, and writes progress + results to stdout as newline-delimited JSON.

Usage:
    python -m ceramix_engine.server            # serve over stdio
    python -m ceramix_engine.server --check    # print environment status & exit
"""

from __future__ import annotations

import argparse
import json
import sys


def health_check() -> dict:
    """Probe the environment: FFmpeg, ONNX provider, model cache.

    TODO: actually inspect FFmpeg on PATH and call runtime.select_provider().
    """
    from . import runtime

    provider = runtime.select_provider()
    return {
        "python": sys.version.split()[0],
        "onnx_provider": provider,
        "ffmpeg_ok": False,  # TODO: shutil.which("ffmpeg") + version probe
        "ready": False,
        "message": "Scaffold — processors not yet implemented.",
    }


def serve() -> None:
    """Main stdio JSON-RPC loop. TODO: implement dispatch + progress events."""
    raise NotImplementedError("JSON-RPC server loop not yet implemented.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ceramix-engine")
    parser.add_argument("--check", action="store_true", help="print env status and exit")
    args = parser.parse_args(argv)

    if args.check:
        print(json.dumps(health_check()))
        return 0

    serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
