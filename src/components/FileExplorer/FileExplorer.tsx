import { useAppStore } from "../../store/useAppStore";

const VIDEO_EXTS = new Set(["mp4", "m4v", "mov", "mkv", "webm", "avi"]);

export function isVideoFile(path: string): boolean {
  const ext = path.split(".").pop()?.toLowerCase() ?? "";
  return VIDEO_EXTS.has(ext);
}

/**
 * Left panel — file explorer & batch queue.
 * Accepts audio (WAV, MP3, FLAC, M4A) and video (MP4, MKV, MOV, WebM, AVI).
 */
export default function FileExplorer() {
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const setActive = useAppStore((s) => s.setActive);
  const setSourceIsVideo = useAppStore((s) => s.setSourceIsVideo);
  const clearStems = useAppStore((s) => s.clearStems);

  function handleSelect(id: string, path: string) {
    setActive(id);
    setSourceIsVideo(isVideoFile(path));
    clearStems();
  }

  return (
    <div className="flex h-full flex-col">
      <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Batch Queue
      </div>

      {/* Drop target */}
      <div className="mx-3 mb-2 rounded-md border border-dashed border-slate-700 px-3 py-6 text-center text-xs text-slate-500">
        Drop audio or video here
        <div className="mt-1 text-[10px] text-slate-600">
          WAV · MP3 · FLAC · M4A · MP4 · MKV · MOV
        </div>
      </div>

      <ul className="flex-1 space-y-1 overflow-y-auto px-2">
        {queue.length === 0 && (
          <li className="px-2 py-3 text-xs text-slate-600">No files queued.</li>
        )}
        {queue.map((f) => {
          const isVideo = isVideoFile(f.path);
          return (
            <li key={f.id}>
              <button
                onClick={() => handleSelect(f.id, f.path)}
                className={`w-full truncate rounded px-2 py-1.5 text-left text-sm transition ${
                  f.id === activeFileId
                    ? "bg-slate-800 text-accent-blue shadow-neon"
                    : "text-slate-300 hover:bg-slate-800/60"
                }`}
              >
                <span className="mr-1.5 text-[10px] text-slate-500">
                  {isVideo ? "▶" : "♪"}
                </span>
                {f.name}
                <span className="ml-2 text-[10px] text-slate-500">{f.status}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
