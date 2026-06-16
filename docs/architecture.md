# Architecture

CeraMix is split into three layers connected by asynchronous IPC. The guiding
principle: **the UI thread never blocks** — all heavy work is pushed down to a
worker process and progress is streamed back as events.

```
React UI  ──invoke()──▶  Tauri/Rust shell  ──JSON-RPC(stdio)──▶  Python backend
   ▲                          │                                       │
   └──── processing://progress events ◀───── staged progress ◀────────┘
```

## Layers

### 1. Frontend (`src/`) — React + TailwindCSS
- Three-panel pro-audio layout (file queue · waveform editor · controls).
- State in Zustand (`store/useAppStore.ts`).
- All native calls go through the typed `lib/ipc.ts` wrapper.
- Waveform rendering via wavesurfer.js (`hooks/useWaveform.ts`).

### 2. Shell (`src-tauri/`) — Rust + Tauri v2
- Owns the window, native file dialogs, and process lifecycle.
- Thin async coordinator: spawns the Python backend, forwards requests,
  re-emits progress events to the frontend.
- Commands grouped under `src/commands/` (`backend`, `audio`, `process`).

### 3. Backend (`python/`) — Python + ONNX Runtime
- Does the inference: stem splitting (Demucs/HTDemucs) and denoise
  (DeepFilterNet).
- `runtime.py` picks the best ONNX execution provider with CPU fallback.
- FFmpeg + soundfile for I/O; weights downloaded lazily (`models/`).

## Why this split?

- **Tauri** keeps the binary small and uses the OS webview (no bundled Chromium).
- **Python** has the richest ecosystem of audio AI models; isolating it as a
  process keeps model/runtime crashes from taking down the UI.
- **ONNX Runtime** gives one inference path across CoreML / DirectML / CUDA / CPU.

## Threading / responsiveness

Each `run_*` command is `async` on the Rust side and dispatched to the Python
worker. The backend emits staged progress (`Loading Model…`, `Analyzing
Spectrum…`, `Writing Audio Files…`), which the shell relays on the
`processing://progress` channel consumed by `ProgressOverlay`.
