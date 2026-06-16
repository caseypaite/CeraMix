<div align="center">

# 🎛️ CeraMix

### AI-Powered Audio Cleanup, Stem Splitting & Noise Removal

*A cross-platform desktop audio workstation that runs entirely on your machine.*

[![License: MIT](https://img.shields.io/badge/License-MIT-22d3ee.svg)](LICENSE)
[![Tauri](https://img.shields.io/badge/Tauri-v2-8b5cf6.svg)](https://tauri.app)
[![React](https://img.shields.io/badge/React-18-38bdf8.svg)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-f59e0b.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-scaffold-lightgrey.svg)](#-roadmap)

</div>

---

> ⚠️ **Project status: Skeleton / scaffold.** This repository currently contains the
> project structure, configuration, and stubbed modules. Core inference and audio
> engine logic are marked with `TODO` and are being implemented per the
> [roadmap](#-roadmap).

## ✨ Overview

**CeraMix** is a cyber-noir, pro-audio desktop application for restoring and
deconstructing audio recordings. It wraps best-in-class **open-source AI models**
for **music source separation** (stem splitting) and **speech enhancement**
(denoising / dereverb) behind a clean, fast, dark-mode-first interface.

Everything runs **100% locally** — no audio ever leaves your device. Model
weights are downloaded on first use to keep the installer small, and inference is
hardware-accelerated where available (CoreML on macOS, DirectML/CUDA on Windows,
CPU fallback everywhere).

## 🚀 Features

### 🎧 Audio Ingestion & Playback
- Drag-and-drop import for **WAV, MP3, FLAC, M4A**.
- High-performance **waveform visualization** for input and output tracks.
- Real-time transport: **play, pause, seek, loop**.

### 🪓 AI Stem Splitting
- Powered by **Demucs v4 / HTDemucs** (and MDX-Net as an alternate backend).
- Splitting topologies:
  - **2-stem** → Vocals / Accompaniment
  - **4-stem** → Vocals / Drums / Bass / Other
- Runs locally via **ONNX Runtime** for native hardware acceleration.

### 🔇 AI Noise Removal & Speech Enhancement
- Powered by **DeepFilterNet** (with CleanUNet / VoiceFixer as alternates).
- Removes **static hiss, room reverb, and background environmental noise**.
- Simple **Denoise Intensity** slider (0–100%).

### 📦 Export & Batch Processing
- Export isolated stems or the cleaned mixdown.
- Formats: **Lossless WAV** (16 / 24 / 32-bit float) and **MP3 320 kbps**.
- **Batch queue** for processing multiple files sequentially.

## 🧱 Architecture

CeraMix is a three-layer application connected by asynchronous IPC:

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend  ·  React + TailwindCSS  (src/)                     │
│  Three-panel pro-audio UI · waveform editor · controls        │
└───────────────────────────┬─────────────────────────────────┘
                            │  Tauri IPC (invoke / events)
┌───────────────────────────┴─────────────────────────────────┐
│  Core / Shell  ·  Rust + Tauri v2  (src-tauri/)               │
│  Window mgmt · file dialogs · process orchestration · sidecar │
└───────────────────────────┬─────────────────────────────────┘
                            │  JSON-RPC over stdio / local socket
┌───────────────────────────┴─────────────────────────────────┐
│  Inference Backend  ·  Python + ONNX Runtime  (python/)       │
│  Stem splitting · denoise · FFmpeg muxing · audio I/O         │
└─────────────────────────────────────────────────────────────┘
```

| Layer        | Technology                                   |
| ------------ | -------------------------------------------- |
| Shell        | [Tauri v2](https://tauri.app) (Rust)         |
| Frontend     | React 18, TypeScript, TailwindCSS, Zustand   |
| Waveform     | wavesurfer.js                                |
| Backend      | Python 3.10+, ONNX Runtime                   |
| AI (stems)   | Demucs v4 / HTDemucs, MDX-Net                |
| AI (denoise) | DeepFilterNet, CleanUNet, VoiceFixer         |
| Audio I/O    | FFmpeg, libsndfile / soundfile               |

## 📂 Project Structure

```
CeraMix/
├── src/                      # React + Tailwind frontend
│   ├── components/
│   │   ├── FileExplorer/      # Left panel — batch queue & file list
│   │   ├── WaveformEditor/    # Center panel — waveform + track layers
│   │   ├── ProcessingControls/# Right panel — denoise & stem config
│   │   ├── ProgressOverlay/   # Staged progress feedback
│   │   └── common/            # Shared UI primitives
│   ├── hooks/                 # React hooks (audio, ipc, transport)
│   ├── store/                 # Zustand global state
│   ├── lib/                   # IPC client, formatters, constants
│   └── styles/                # Tailwind + theme tokens
├── src-tauri/                # Rust / Tauri v2 shell
│   ├── src/commands/          # IPC command handlers
│   ├── Cargo.toml
│   └── tauri.conf.json
├── python/                   # AI inference backend
│   └── ceramix_engine/
│       ├── processors/        # stem_split.py, denoise.py
│       ├── models/            # model registry & downloader
│       ├── audio_io.py        # FFmpeg / soundfile I/O
│       └── server.py          # JSON-RPC entrypoint
├── resources/                # Sample audio, bundled assets
└── docs/                     # Design notes & ADRs
```

## 🛠️ Getting Started

> These steps will work once the implementation lands. For now they document the
> intended developer workflow.

### Prerequisites
- [Node.js](https://nodejs.org) ≥ 18 and [pnpm](https://pnpm.io)
- [Rust](https://rustup.rs) (stable) + Tauri v2 [system deps](https://tauri.app/start/prerequisites/)
- [Python](https://python.org) ≥ 3.10
- [FFmpeg](https://ffmpeg.org) available on `PATH`

### Setup

```bash
# 1. Install frontend dependencies
pnpm install

# 2. Set up the Python inference backend
cd python
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..

# 3. Run the app in development
pnpm tauri dev
```

Model weights are **not** bundled; they are fetched on first use into the app's
data directory (see [`python/ceramix_engine/models`](python/ceramix_engine/models)).

### Build

```bash
pnpm tauri build
```

## 🎨 Design Language

CeraMix uses a **Cyber-noir / Pro-Audio** dark theme:

| Token            | Role                         | Sample        |
| ---------------- | ---------------------------- | ------------- |
| Slate background | Base canvas                  | `#0f172a`     |
| Electric blue    | Primary waveform / accents   | `#38bdf8`     |
| Violet           | Secondary waveform / stems   | `#8b5cf6`     |
| Amber            | Sliders / active controls    | `#f59e0b`     |

## 🗺️ Roadmap

- [x] **Step 0** — Project scaffolding & async IPC wiring
- [ ] **Step 1** — Audio playback engine + waveform renderer (dummy file)
- [ ] **Step 2** — Python/ONNX environment check + model auto-downloader
- [ ] **Step 3** — Wire UI controls to inference workers (off the UI thread)
- [ ] **Step 4** — Stem splitting (2/4 stems) end-to-end
- [ ] **Step 5** — Noise removal & speech enhancement end-to-end
- [ ] **Step 6** — Export pipeline (WAV/MP3) + batch queue
- [ ] **Step 7** — Hardware accel detection + graceful CPU fallback & logging

## 🤝 Contributing

Contributions are welcome! This is an early-stage scaffold — issues and design
discussion are especially valuable right now. Please open an issue using the
provided templates before submitting large PRs.

## 📜 License

Released under the [MIT License](LICENSE).

> CeraMix integrates third-party open-source AI models (Demucs, DeepFilterNet,
> etc.). Each model is governed by its own license — review them before
> redistribution or commercial use.
