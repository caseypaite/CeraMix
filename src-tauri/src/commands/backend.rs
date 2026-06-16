//! Backend health & environment checks.

use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct BackendStatus {
    pub python_ok: bool,
    pub ffmpeg_ok: bool,
    pub onnx_provider: String, // "CUDA" | "DirectML" | "CoreML" | "CPU"
    pub message: String,
}

/// Probe the Python inference backend: confirm the interpreter, FFmpeg, and the
/// best available ONNX execution provider (with CPU fallback).
#[tauri::command]
pub async fn check_backend() -> Result<BackendStatus, String> {
    // TODO: spawn `python -m ceramix_engine.server --check` and parse the result.
    Ok(BackendStatus {
        python_ok: false,
        ffmpeg_ok: false,
        onnx_provider: "CPU".into(),
        message: "Backend check not yet implemented (scaffold).".into(),
    })
}
