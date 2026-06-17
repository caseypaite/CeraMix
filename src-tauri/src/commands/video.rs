//! Video export command — stream-copies video, replaces audio with mixed stems.

use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

use super::process::JobResult;

#[derive(Debug, Deserialize, Serialize)]
pub struct ExportVideoRequest {
    pub video_path: String,
    pub audio_path: String,
    pub output_path: String,
}

/// Mux the original video stream with the mixed-stem audio track via FFmpeg.
/// The video bitstream is never re-encoded.
#[tauri::command]
pub async fn export_video(app: AppHandle, req: ExportVideoRequest) -> Result<JobResult, String> {
    let request_json =
        serde_json::to_string(&req).map_err(|e| format!("Serialise error: {e}"))?;

    let output = app
        .shell()
        .sidecar("ceramix-engine")
        .map_err(|e| format!("Failed to locate sidecar: {e}"))?
        .args(["--command", "export_video", "--request", &request_json])
        .output()
        .await
        .map_err(|e| format!("Sidecar launch failed: {e}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("export_video failed: {stderr}"));
    }

    serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse sidecar output: {e}"))
}
