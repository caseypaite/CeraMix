import { useWaveform } from "../../hooks/useWaveform";

/**
 * Center panel — waveform editor & track layers.
 * Scaffold: renders the waveform container + a transport bar. Step 2 wires the
 * wavesurfer.js instance and per-stem track lanes.
 */
export default function WaveformEditor() {
  const { containerRef, transport } = useWaveform();

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 p-4">
        {/* Input track */}
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Input
        </div>
        <div
          ref={containerRef}
          className="mb-4 h-32 rounded-md border border-slate-800 bg-slate-900/50"
        />

        {/* Output / stem lanes — populated after processing. */}
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Output / Stems
        </div>
        <div className="flex h-40 items-center justify-center rounded-md border border-dashed border-slate-800 text-xs text-slate-600">
          Processed tracks appear here
        </div>
      </div>

      {/* Transport bar */}
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
    </div>
  );
}
