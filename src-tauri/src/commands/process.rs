//! Long-running processing commands. Each spawns work on the Python backend and
//! streams staged progress events (`processing://progress`) back to the UI so
//! the main thread never blocks.

use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

#[derive(Debug, Deserialize, Serialize)]
pub struct StemSplitRequest {
    pub input_path: String,
    pub topology: String, // "2stem" | "4stem"
    pub output_dir: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct DenoiseRequest {
    pub input_path: String,
    pub intensity: u8, // 0-100
    pub output_dir: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ExportRequest {
    pub source_path: String,
    pub output_path: String,
    pub format: String,   // "wav" | "mp3"
    pub bit_depth: u8,    // 16 | 24 | 32 (WAV only)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct JobResult {
    pub job_id: String,
    pub outputs: Vec<String>,
}

/// Run AI stem splitting (Demucs/HTDemucs via ONNX) on a separate worker.
/// Delegates to the Python sidecar which extracts audio via FFmpeg and writes
/// per-stem WAV files.  Replace with ONNX inference once model weights are bundled.
#[tauri::command]
pub async fn run_stem_split(app: AppHandle, req: StemSplitRequest) -> Result<JobResult, String> {
    let request_json =
        serde_json::to_string(&req).map_err(|e| format!("Serialise error: {e}"))?;

    let output = app
        .shell()
        .sidecar("ceramix-engine")
        .map_err(|e| format!("Failed to locate sidecar: {e}"))?
        .args(["--command", "run_stem_split", "--request", &request_json])
        .output()
        .await
        .map_err(|e| format!("Sidecar launch failed: {e}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("run_stem_split failed: {stderr}"));
    }

    serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse sidecar output: {e}"))
}

/// Run AI noise removal / speech enhancement (DeepFilterNet via ONNX).
#[tauri::command]
pub async fn run_denoise(req: DenoiseRequest) -> Result<JobResult, String> {
    let _ = &req;
    Err("run_denoise not yet implemented (scaffold).".into())
}

/// Mux/encode a processed buffer to the requested output format via FFmpeg.
#[tauri::command]
pub async fn export_audio(req: ExportRequest) -> Result<JobResult, String> {
    let _ = &req;
    Err("export_audio not yet implemented (scaffold).".into())
}
