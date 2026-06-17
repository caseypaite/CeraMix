//! Audio file inspection commands.

use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct AudioInfo {
    pub path: String,
    pub format: String,
    pub sample_rate: u32,
    pub channels: u16,
    pub duration_secs: f64,
}

/// Probe an audio file's metadata via FFmpeg (delegated to the Python backend).
#[tauri::command]
pub async fn probe_audio(path: String) -> Result<AudioInfo, String> {
    // TODO: ffprobe / soundfile lookup through the backend.
    let _ = &path;
    Err("probe_audio not yet implemented (scaffold).".into())
}
