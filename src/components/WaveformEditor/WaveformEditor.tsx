import { convertFileSrc } from "@tauri-apps/api/core";
import { useAppStore } from "../../store/useAppStore";
import { useWaveform } from "../../hooks/useWaveform";
import VideoPreview from "../VideoPreview/VideoPreview";
import { isVideoFile } from "../FileExplorer/FileExplorer";

/**
 * Center panel — waveform editor or video preview, plus transport controls.
 */
export default function WaveformEditor() {
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const activeFile = queue.find((f) => f.id === activeFileId) ?? null;
  const isVideo = activeFile ? isVideoFile(activeFile.path) : false;

  // Convert the local file path to an asset:// URL that WaveSurfer can load.
  const waveformUrl =
    activeFile && !isVideo ? convertFileSrc(activeFile.path) : undefined;

  const { containerRef, transport } = useWaveform(waveformUrl);

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-hidden p-4">
        {/* Input track / video preview */}
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          {isVideo ? "Video Preview" : "Input"}
        </div>

        {isVideo && activeFile ? (
          <div className="mb-4 h-48 overflow-hidden rounded-md">
            <VideoPreview path={activeFile.path} />
          </div>
        ) : (
          <div
            ref={containerRef}
            className="mb-4 h-32 rounded-md border border-slate-800 bg-slate-900/50"
          />
        )}

        {/* Output / stem lanes */}
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Output / Stems
        </div>
        <div className="flex h-40 items-center justify-center rounded-md border border-dashed border-slate-800 text-xs text-slate-600">
          Processed tracks appear here
        </div>
      </div>

      {/* Transport bar — audio only; video uses native HTML5 controls */}
      {!isVideo && (
        <div className="flex items-center gap-3 border-t border-slate-800 px-4 py-2">
          <button
            onClick={transport.isPlaying ? transport.pause : transport.play}
            className={`rounded px-3 py-1 text-sm transition ${
              transport.isPlaying
                ? "bg-accent-blue text-slate-950 hover:bg-accent-blue/80"
                : "bg-slate-800 text-accent-blue hover:bg-slate-700"
            }`}
          >
            {transport.isPlaying ? "⏸ Pause" : "▶ Play"}
          </button>
          <button
            onClick={transport.toggleLoop}
            className={`rounded px-3 py-1 text-sm transition ${
              transport.isLooping
                ? "bg-accent-violet/30 text-accent-violet ring-1 ring-accent-violet"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            ↻ Loop
          </button>
        </div>
      )}
    </div>
  );
}
