# CeraMix Inference Backend

Python + ONNX Runtime backend that performs the actual audio AI work. It is
spawned by the Tauri shell and communicates over JSON-RPC (stdio), streaming
staged progress so the UI stays responsive.

## Layout

```
ceramix_engine/
├── server.py            # JSON-RPC entrypoint + `--check` health probe
├── runtime.py           # ONNX provider selection + CPU fallback + logging
├── audio_io.py          # FFmpeg / soundfile read & write
├── models/
│   ├── registry.py      # model id → url / checksum / topology
│   └── downloader.py    # lazy weight download into app data dir
└── processors/
    ├── stem_split.py    # Demucs/HTDemucs (2-stem / 4-stem)
    └── denoise.py       # DeepFilterNet speech enhancement
```

## Execution providers

`runtime.py` selects the best available ONNX Runtime execution provider and
falls back to CPU, logging the decision:

| Platform     | Preferred provider        | Package                |
| ------------ | ------------------------- | ---------------------- |
| macOS (ARM)  | `CoreMLExecutionProvider` | `onnxruntime-silicon`  |
| Windows      | `DmlExecutionProvider`    | `onnxruntime-directml` |
| NVIDIA       | `CUDAExecutionProvider`   | `onnxruntime-gpu`      |
| Fallback     | `CPUExecutionProvider`    | `onnxruntime`          |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ceramix_engine.server --check   # prints environment status JSON
```

## Model weights

Weights are **not** bundled. They are downloaded on first use into the OS app
data directory and verified against checksums in `models/registry.py`.
