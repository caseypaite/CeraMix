import { useAppStore } from "../../store/useAppStore";
import type { StemTrack } from "../../store/useAppStore";
import StemMixer from "../StemMixer/StemMixer";
import { ipc } from "../../lib/ipc";
import { isVideoFile } from "../FileExplorer/FileExplorer";

/**
 * Right panel — stem topology, denoise, stem mixer, and export controls.
 */
export default function ProcessingControls() {
  const config = useAppStore((s) => s.config);
  const updateConfig = useAppStore((s) => s.updateConfig);
  const stems = useAppStore((s) => s.stems);
  const sourceIsVideo = useAppStore((s) => s.sourceIsVideo);
  const queue = useAppStore((s) => s.queue);
  const activeFileId = useAppStore((s) => s.activeFileId);
  const mixedAudioPath = useAppStore((s) => s.mixedAudioPath);
  const setProgress = useAppStore((s) => s.setProgress);
  const setMixedAudioPath = useAppStore((s) => s.setMixedAudioPath);
  const addStems = useAppStore((s) => s.addStems);
  const clearStems = useAppStore((s) => s.clearStems);

  const activeFile = queue.find((f) => f.id === activeFileId) ?? null;

  function outputDirFor(filePath: string): string {
    return filePath.replace(/[/\\][^/\\]+$/, "");
  }

  async function handleStemSplit() {
    if (!activeFile) return;
    clearStems();
    setProgress({ active: true, stage: "Splitting stems…", progress: 0.1 });
    try {
      const result = await ipc.runStemSplit(
        activeFile.path,
        config.topology,
        outputDirFor(activeFile.path),
      );
      // Build StemTrack objects from output paths.
      // Paths are named "<base>_<stemname>.wav" by the Python backend.
      const newStems: StemTrack[] = result.outputs.map((path) => {
        const filename = path.split(/[/\\]/).pop() ?? "";
        const m = filename.match(/_(\w+)\.\w+$/);
        const stemId = m?.[1] ?? filename.replace(/\.\w+$/, "");
        return {
          id: stemId,
          label: stemId.charAt(0).toUpperCase() + stemId.slice(1),
          path,
          volume: 1,
          pan: 0,
          muted: false,
        };
      });
      addStems(newStems);
      setProgress({ active: false, stage: "", progress: 0 });
    } catch (err) {
      setProgress({ active: false, stage: "", progress: 0 });
      console.error("run_stem_split failed:", err);
    }
  }

  async function handleMixStems() {
    if (!stems.length || !activeFile) return;
    const outputPath = activeFile.path.replace(/(\.[^.]+)$/, "_mixed.wav");
    setProgress({ active: true, stage: "Mixing stems…", progress: 0.1 });
    try {
      const result = await ipc.mixStems({
        stems: stems.map((s) => ({
          path: s.path,
          volume: s.volume,
          pan: s.pan,
          muted: s.muted,
        })),
        output_path: outputPath,
      });
      setMixedAudioPath(result.outputs[0]);
      setProgress({ active: false, stage: "", progress: 0 });
    } catch (err) {
      setProgress({ active: false, stage: "", progress: 0 });
      console.error("mix_stems failed:", err);
    }
  }

  async function handleExportVideo() {
    if (!activeFile || !mixedAudioPath) return;
    const ext = isVideoFile(activeFile.path)
      ? (activeFile.path.match(/\.[^.]+$/)?.[0] ?? ".mp4")
      : ".mp4";
    const outputPath = activeFile.path.replace(/(\.[^.]+)$/, `_export${ext}`);
    setProgress({ active: true, stage: "Exporting video…", progress: 0.1 });
    try {
      await ipc.exportVideo({
        video_path: activeFile.path,
        audio_path: mixedAudioPath,
        output_path: outputPath,
      });
      setProgress({ active: false, stage: "", progress: 0 });
    } catch (err) {
      setProgress({ active: false, stage: "", progress: 0 });
      console.error("export_video failed:", err);
    }
  }

  return (
    <div className="flex h-full flex-col gap-5 overflow-y-auto p-4">
      {/* Stem splitting */}
      <section>
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent-violet">
          Stem Splitting
        </h2>
        <div className="flex gap-2">
          {(["2stem", "4stem"] as const).map((t) => (
            <button
              key={t}
              onClick={() => updateConfig({ topology: t })}
              className={`flex-1 rounded px-2 py-1.5 text-sm transition ${
                config.topology === t
                  ? "bg-accent-violet/20 text-accent-violet ring-1 ring-accent-violet"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {t === "2stem" ? "2 stems" : "4 stems"}
            </button>
          ))}
        </div>
        <p className="mt-1 text-[10px] text-slate-500">
          {config.topology === "2stem"
            ? "Vocals · Accompaniment"
            : "Vocals · Drums · Bass · Other"}
        </p>
      </section>

      {/* Denoise */}
      <section>
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent-amber">
          Noise Removal
        </h2>
        <label className="flex items-center justify-between text-sm text-slate-300">
          Intensity
          <span className="font-mono text-accent-amber">{config.denoiseIntensity}%</span>
        </label>
        <input
          type="range"
          min={0}
          max={100}
          value={config.denoiseIntensity}
          onChange={(e) => updateConfig({ denoiseIntensity: Number(e.target.value) })}
          className="mt-2 w-full accent-amber-500"
        />
      </section>

      {/* Stem mixer — appears after splitting */}
      {stems.length > 0 && <StemMixer />}

      {/* Export format */}
      <section>
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-accent-blue">
          Export
        </h2>
        <div className="flex gap-2">
          {(["wav", "mp3"] as const).map((f) => (
            <button
              key={f}
              onClick={() => updateConfig({ exportFormat: f })}
              className={`flex-1 rounded px-2 py-1.5 text-sm uppercase transition ${
                config.exportFormat === f
                  ? "bg-accent-blue/20 text-accent-blue ring-1 ring-accent-blue"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </section>

      {/* Action buttons */}
      <div className="mt-auto flex flex-col gap-2">
        <button
          onClick={handleStemSplit}
          disabled={!activeFile}
          className="rounded bg-accent-violet/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-accent-violet disabled:cursor-not-allowed disabled:opacity-40"
        >
          Split Stems
        </button>
        <button
          disabled={!activeFile}
          className="rounded bg-accent-amber/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-accent-amber disabled:cursor-not-allowed disabled:opacity-40"
        >
          Denoise
        </button>
        {stems.length > 0 && (
          <button
            onClick={handleMixStems}
            className="rounded bg-accent-blue/90 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-accent-blue"
          >
            Mix Stems
          </button>
        )}
        {sourceIsVideo && mixedAudioPath && (
          <button
            onClick={handleExportVideo}
            className="rounded bg-emerald-600/90 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-500"
          >
            Export Video
          </button>
        )}
      </div>
    </div>
  );
}
