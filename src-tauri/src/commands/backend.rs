//! Backend health & environment checks.

use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

#[derive(Debug, Serialize)]
pub struct BackendStatus {
    pub python_ok: bool,
    pub ffmpeg_ok: bool,
    pub onnx_provider: String, // "CUDA" | "DirectML" | "CoreML" | "CPU"
    pub message: String,
}

/// JSON shape returned by `ceramix-engine --check`.
#[derive(Debug, Deserialize)]
struct EngineCheckOutput {
    #[serde(default)]
    ffmpeg_ok: bool,
    #[serde(default = "default_provider")]
    onnx_provider: String,
    #[serde(default)]
    message: String,
}

fn default_provider() -> String {
    "CPU".into()
}

/// Probe the Python inference sidecar: confirm it starts, detect the best
/// available ONNX execution provider (CUDA → DirectML → CoreML → CPU), and
/// verify FFmpeg is on PATH inside the sidecar environment.
#[tauri::command]
pub async fn check_backend(app: AppHandle) -> Result<BackendStatus, String> {
    let output = app
        .shell()
        .sidecar("ceramix-engine")
        .map_err(|e| format!("Failed to locate sidecar: {e}"))?
        .args(["--check"])
        .output()
        .await
        .map_err(|e| format!("Sidecar launch failed: {e}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("ceramix-engine --check exited non-zero: {stderr}"));
    }

    let parsed: EngineCheckOutput = serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse sidecar output: {e}"))?;

    Ok(BackendStatus {
        python_ok: true,
        ffmpeg_ok: parsed.ffmpeg_ok,
        onnx_provider: parsed.onnx_provider,
        message: parsed.message,
    })
}
