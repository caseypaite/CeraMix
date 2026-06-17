import { useAppStore } from "../../store/useAppStore";

/**
 * Left panel — file explorer & batch queue.
 * Scaffold: renders the queue from the store; drag-and-drop import is wired in
 * Step 1/2. Supports WAV, MP3, FLAC, M4A.
 */
export default function FileExplorer() {
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const setActive = useAppStore((s) => s.setActive);

  return (
    <div className="flex h-full flex-col">
      <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Batch Queue
      </div>

      {/* Drop target — TODO: hook up Tauri file drop + dialog import. */}
      <div className="mx-3 mb-2 rounded-md border border-dashed border-slate-700 px-3 py-6 text-center text-xs text-slate-500">
        Drop audio here
        <div className="mt-1 text-[10px] text-slate-600">WAV · MP3 · FLAC · M4A</div>
      </div>

      <ul className="flex-1 space-y-1 overflow-y-auto px-2">
        {queue.length === 0 && (
          <li className="px-2 py-3 text-xs text-slate-600">No files queued.</li>
        )}
        {queue.map((f) => (
          <li key={f.id}>
            <button
              onClick={() => setActive(f.id)}
              className={`w-full truncate rounded px-2 py-1.5 text-left text-sm transition ${
                f.id === activeFileId
                  ? "bg-slate-800 text-accent-blue shadow-neon"
                  : "text-slate-300 hover:bg-slate-800/60"
              }`}
            >
              {f.name}
              <span className="ml-2 text-[10px] text-slate-500">{f.status}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
