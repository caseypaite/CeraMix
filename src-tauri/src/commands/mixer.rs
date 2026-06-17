//! Stem mixing command — combines N stem files with per-stem volume and pan.

use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

use super::process::JobResult;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct StemMixInput {
    pub path: String,
    pub volume: f32,  // 0.0 – 2.0
    pub pan: f32,     // −1.0 (hard-left) … 0.0 (centre) … +1.0 (hard-right)
    pub muted: bool,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct MixStemsRequest {
    pub stems: Vec<StemMixInput>,
    pub output_path: String,
}

/// Mix stems with the given volume / pan settings, writing a 24-bit WAV.
#[tauri::command]
pub async fn mix_stems(app: AppHandle, req: MixStemsRequest) -> Result<JobResult, String> {
    let request_json =
        serde_json::to_string(&req).map_err(|e| format!("Serialise error: {e}"))?;

    let output = app
        .shell()
        .sidecar("ceramix-engine")
        .map_err(|e| format!("Failed to locate sidecar: {e}"))?
        .args(["--command", "mix_stems", "--request", &request_json])
        .output()
        .await
        .map_err(|e| format!("Sidecar launch failed: {e}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("mix_stems failed: {stderr}"));
    }

    serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse sidecar output: {e}"))
}
