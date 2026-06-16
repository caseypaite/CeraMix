/**
 * Typed wrapper around Tauri's async IPC. All long-running work is delegated to
 * the Rust shell, which in turn drives the Python backend — keeping the UI
 * thread free.
 */
import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";

export type SplitTopology = "2stem" | "4stem";
export type ExportFormat = "wav" | "mp3";

export interface BackendStatus {
  python_ok: boolean;
  ffmpeg_ok: boolean;
  onnx_provider: string;
  message: string;
}

export interface JobResult {
  job_id: string;
  outputs: string[];
}

export interface ProgressEvent {
  jobId: string;
  stage: string; // "Loading Model…" | "Analyzing Spectrum…" | "Writing Audio Files…"
  progress: number; // 0..1
}

export const ipc = {
  checkBackend: () => invoke<BackendStatus>("check_backend"),

  probeAudio: (path: string) => invoke("probe_audio", { path }),

  runStemSplit: (input_path: string, topology: SplitTopology, output_dir: string) =>
    invoke<JobResult>("run_stem_split", { req: { input_path, topology, output_dir } }),

  runDenoise: (input_path: string, intensity: number, output_dir: string) =>
    invoke<JobResult>("run_denoise", { req: { input_path, intensity, output_dir } }),

  exportAudio: (
    source_path: string,
    output_path: string,
    format: ExportFormat,
    bit_depth = 24,
  ) =>
    invoke<JobResult>("export_audio", {
      req: { source_path, output_path, format, bit_depth },
    }),

  /** Subscribe to staged progress events emitted during processing. */
  onProgress: (cb: (e: ProgressEvent) => void): Promise<UnlistenFn> =>
    listen<ProgressEvent>("processing://progress", (event) => cb(event.payload)),
};
