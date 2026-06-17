//! Long-running processing commands. Each spawns work on the Python backend and
//! streams staged progress events (`processing://progress`) back to the UI so
//! the main thread never blocks.

use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct StemSplitRequest {
    pub input_path: String,
    pub topology: String, // "2stem" | "4stem"
    pub output_dir: String,
}

#[derive(Debug, Deserialize)]
pub struct DenoiseRequest {
    pub input_path: String,
    pub intensity: u8, // 0-100
    pub output_dir: String,
}

#[derive(Debug, Deserialize)]
pub struct ExportRequest {
    pub source_path: String,
    pub output_path: String,
    pub format: String,   // "wav" | "mp3"
    pub bit_depth: u8,     // 16 | 24 | 32 (WAV only)
}

#[derive(Debug, Serialize)]
pub struct JobResult {
    pub job_id: String,
    pub outputs: Vec<String>,
}

/// Run AI stem splitting (Demucs/HTDemucs via ONNX) on a separate worker.
#[tauri::command]
pub async fn run_stem_split(req: StemSplitRequest) -> Result<JobResult, String> {
    let _ = &req;
    Err("run_stem_split not yet implemented (scaffold).".into())
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
