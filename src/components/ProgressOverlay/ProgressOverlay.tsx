import { useAppStore } from "../../store/useAppStore";

/**
 * Staged progress feedback overlay.
 * Displays the current processing stage ("Loading Model…", "Analyzing
 * Spectrum…", "Writing Audio Files…") and a progress bar. Driven by
 * `ipc.onProgress` events in Step 4.
 */
export default function ProgressOverlay() {
  const { active, stage, progress } = useAppStore((s) => s.progress);

  if (!active) return null;

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm">
      <div className="w-80 rounded-lg border border-slate-800 bg-slate-900 p-5 shadow-neon">
        <div className="mb-3 text-sm font-medium text-accent-blue">{stage || "Working…"}</div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-accent-blue to-accent-violet transition-all"
            style={{ width: `${Math.round(progress * 100)}%` }}
          />
        </div>
        <div className="mt-2 text-right font-mono text-xs text-slate-400">
          {Math.round(progress * 100)}%
        </div>
      </div>
    </div>
  );
}
