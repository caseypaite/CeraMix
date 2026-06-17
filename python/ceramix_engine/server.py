"""JSON-RPC entrypoint for the CeraMix backend.

Invoked by the Tauri shell as a one-shot subprocess per command:

    ceramix-engine --check
    ceramix-engine --command mix_stems    --request '<json>'
    ceramix-engine --command export_video --request '<json>'

Writes a single JSON object to stdout and exits.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid


def health_check() -> dict:
    """Probe the environment: FFmpeg, ONNX provider."""
    import shutil
    from . import runtime

    provider = runtime.select_provider()
    return {
        "python": sys.version.split()[0],
        "onnx_provider": provider,
        "ffmpeg_ok": shutil.which("ffmpeg") is not None,
        "ready": True,
        "message": "OK",
    }


def handle_mix_stems(request: dict) -> dict:
    from .mixer import mix, StemMixInput

    stems = [StemMixInput(**s) for s in request["stems"]]
    output_path = request["output_path"]
    out = mix(stems, output_path)
    return {"job_id": str(uuid.uuid4()), "outputs": [out]}


def handle_export_video(request: dict) -> dict:
    from .video_io import export_video

    out = export_video(
        request["video_path"],
        request["audio_path"],
        request["output_path"],
    )
    return {"job_id": str(uuid.uuid4()), "outputs": [out]}


def handle_run_stem_split(request: dict) -> dict:
    from .processors.stem_split import split_files

    paths = split_files(
        input_path=request["input_path"],
        topology=request.get("topology", "4stem"),
        output_dir=request.get("output_dir", ""),
    )
    return {"job_id": str(uuid.uuid4()), "outputs": list(paths.values())}


_HANDLERS = {
    "mix_stems": handle_mix_stems,
    "export_video": handle_export_video,
    "run_stem_split": handle_run_stem_split,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ceramix-engine")
    parser.add_argument("--check", action="store_true", help="print env status and exit")
    parser.add_argument("--command", help="command name to dispatch")
    parser.add_argument("--request", default="{}", help="JSON-encoded request body")
    args = parser.parse_args(argv)

    if args.check:
        print(json.dumps(health_check()))
        return 0

    if args.command:
        handler = _HANDLERS.get(args.command)
        if handler is None:
            print(json.dumps({"error": f"Unknown command: {args.command!r}"}), file=sys.stderr)
            return 1
        try:
            request = json.loads(args.request)
            result = handler(request)
            print(json.dumps(result))
            return 0
        except Exception as exc:
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
            return 1

    print(json.dumps({"error": "No command specified. Use --check or --command <name>."}), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
