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


def handle_run_denoise(request: dict) -> dict:
    import pathlib
    from .audio_io import load, write_wav
    from .processors.denoise import denoise

    input_path = request["input_path"]
    intensity = int(request.get("intensity", 100))
    output_dir = request.get("output_dir", "")

    out_dir = pathlib.Path(output_dir) if output_dir else pathlib.Path(input_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(out_dir / f"{pathlib.Path(input_path).stem}_denoised.wav")

    buf = load(input_path)
    enhanced = denoise(buf, intensity=intensity)
    write_wav(output_path, enhanced)

    return {"job_id": str(uuid.uuid4()), "outputs": [output_path]}


def handle_export_audio(request: dict) -> dict:
    from .audio_io import load, write_wav, write_mp3

    source_path = request["source_path"]
    output_path = request["output_path"]
    fmt = request.get("format", "wav").lower()
    bit_depth = int(request.get("bit_depth", 24))

    buf = load(source_path)
    if fmt == "mp3":
        write_mp3(output_path, buf)
    else:
        write_wav(output_path, buf, bit_depth=bit_depth)

    return {"job_id": str(uuid.uuid4()), "outputs": [output_path]}


_HANDLERS = {
    "mix_stems": handle_mix_stems,
    "export_video": handle_export_video,
    "run_stem_split": handle_run_stem_split,
    "run_denoise": handle_run_denoise,
    "export_audio": handle_export_audio,
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
