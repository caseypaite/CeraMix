import { useAppStore } from "../../store/useAppStore";
import { useWaveform } from "../../hooks/useWaveform";
import VideoPreview from "../VideoPreview/VideoPreview";
import { isVideoFile } from "../FileExplorer/FileExplorer";

/**
 * Center panel — waveform editor or video preview, plus transport controls.
 */
export default function WaveformEditor() {
  const { containerRef, transport } = useWaveform();
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const activeFile = queue.find((f) => f.id === activeFileId) ?? null;
  const isVideo = activeFile ? isVideoFile(activeFile.path) : false;

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

      {/* Transport bar — hidden for video (uses native controls) */}
      {!isVideo && (
        <div className="flex items-center gap-3 border-t border-slate-800 px-4 py-2">
          <button
            onClick={transport.play}
            className="rounded bg-slate-800 px-3 py-1 text-sm text-accent-blue hover:bg-slate-700"
          >
            ▶ Play
          </button>
          <button
            onClick={transport.pause}
            className="rounded bg-slate-800 px-3 py-1 text-sm text-slate-300 hover:bg-slate-700"
          >
            ⏸ Pause
          </button>
          <button
            onClick={transport.toggleLoop}
            className="rounded bg-slate-800 px-3 py-1 text-sm text-slate-300 hover:bg-slate-700"
          >
            ↻ Loop
          </button>
        </div>
      )}
    </div>
  );
}
