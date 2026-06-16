//! CeraMix — Tauri shell entrypoint.
//!
//! Responsibilities of this layer:
//!   * window + lifecycle management
//!   * native file dialogs (open / save)
//!   * orchestrating the Python inference backend (spawned as a sidecar/process)
//!   * relaying progress events back to the frontend
//!
//! The heavy lifting (stem splitting, denoise) lives in the Python backend; the
//! Rust layer is a thin, async coordinator that keeps the UI responsive.

mod commands;

/// Build and run the Tauri application.
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            commands::backend::check_backend,
            commands::audio::probe_audio,
            commands::process::run_stem_split,
            commands::process::run_denoise,
            commands::process::export_audio,
        ])
        .run(tauri::generate_context!())
        .expect("error while running CeraMix");
}
