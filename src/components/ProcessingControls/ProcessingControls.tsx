import { useAppStore } from "../../store/useAppStore";

/**
 * Right panel — processing controls.
 * Scaffold: stem-split topology, denoise intensity slider, and export options
 * bound to the store. Action buttons call into `ipc` in Step 4.
 */
export default function ProcessingControls() {
  const config = useAppStore((s) => s.config);
  const updateConfig = useAppStore((s) => s.updateConfig);

  return (
    <div className="flex h-full flex-col gap-6 p-4">
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
          Denoise Intensity
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

      {/* Export */}
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

      {/* Actions — TODO: wire to ipc.runStemSplit / runDenoise / exportAudio. */}
      <div className="mt-auto flex flex-col gap-2">
        <button className="rounded bg-accent-violet/90 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-accent-violet">
          Split Stems
        </button>
        <button className="rounded bg-accent-amber/90 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-accent-amber">
          Denoise
        </button>
      </div>
    </div>
  );
}
