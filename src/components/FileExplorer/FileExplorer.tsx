import { useEffect, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { useAppStore } from "../../store/useAppStore";

const AUDIO_EXTS = new Set(["wav", "mp3", "flac", "m4a", "aac", "ogg", "opus"]);
const VIDEO_EXTS = new Set(["mp4", "m4v", "mov", "mkv", "webm", "avi"]);

export function isVideoFile(path: string): boolean {
  const ext = path.split(".").pop()?.toLowerCase() ?? "";
  return VIDEO_EXTS.has(ext);
}

function isMediaFile(path: string): boolean {
  const ext = path.split(".").pop()?.toLowerCase() ?? "";
  return AUDIO_EXTS.has(ext) || VIDEO_EXTS.has(ext);
}

/**
 * Left panel — file explorer & batch queue.
 * Files are added by dragging them from the OS onto any part of the window.
 */
export default function FileExplorer() {
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const addFiles = useAppStore((s) => s.addFiles);
  const setActive = useAppStore((s) => s.setActive);
  const setSourceIsVideo = useAppStore((s) => s.setSourceIsVideo);
  const clearStems = useAppStore((s) => s.clearStems);

  const [isDragOver, setIsDragOver] = useState(false);

  // Register Tauri window-level drag-drop listeners.
  // These fire regardless of where in the window the user drops files and
  // supply real OS paths (not browser File objects, which lack path access).
  useEffect(() => {
    const unlistens: Array<() => void> = [];

    listen("tauri://drag-enter", () => setIsDragOver(true))
      .then((fn) => unlistens.push(fn));

    listen("tauri://drag-leave", () => setIsDragOver(false))
      .then((fn) => unlistens.push(fn));

    listen<{ paths: string[]; position: { x: number; y: number } }>(
      "tauri://drag-drop",
      (event) => {
        setIsDragOver(false);
        const paths = (event.payload.paths ?? []).filter(isMediaFile);
        if (paths.length === 0) return;

        const newFiles = paths.map((p) => ({
          id: crypto.randomUUID(),
          name: p.split(/[/\\]/).pop() ?? p,
          path: p,
          status: "queued" as const,
        }));
        addFiles(newFiles);

        // Auto-select the first dropped file if nothing is active yet.
        if (!activeFileId) {
          const first = newFiles[0];
          setActive(first.id);
          setSourceIsVideo(isVideoFile(first.path));
          clearStems();
        }
      },
    ).then((fn) => unlistens.push(fn));

    return () => {
      unlistens.forEach((fn) => fn());
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // intentionally run once; store refs are stable

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

      {/* Drop target — lights up when files are dragged over the window */}
      <div
        className={`mx-3 mb-2 rounded-md border border-dashed px-3 py-6 text-center text-xs transition-colors duration-150 ${
          isDragOver
            ? "border-accent-blue bg-accent-blue/10 text-accent-blue"
            : "border-slate-700 text-slate-500"
        }`}
      >
        {isDragOver ? "Release to add files" : "Drop audio or video here"}
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
