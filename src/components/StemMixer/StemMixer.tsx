import { useAppStore, StemTrack } from "../../store/useAppStore";

const STEM_COLORS: Record<string, string> = {
  vocals: "text-accent-violet",
  drums: "text-accent-amber",
  bass: "text-accent-blue",
  other: "text-slate-400",
  accompaniment: "text-slate-300",
};

const STEM_BG: Record<string, string> = {
  vocals: "bg-accent-violet/20 ring-accent-violet/40",
  drums: "bg-accent-amber/20 ring-accent-amber/40",
  bass: "bg-accent-blue/20 ring-accent-blue/40",
  other: "bg-slate-700/40 ring-slate-600/40",
  accompaniment: "bg-slate-700/40 ring-slate-600/40",
};

function StemRow({ stem }: { stem: StemTrack }) {
  const updateStem = useAppStore((s) => s.updateStem);
  const color = STEM_COLORS[stem.id] ?? "text-slate-300";
  const bg = STEM_BG[stem.id] ?? "bg-slate-700/40 ring-slate-600/40";

  const dbLabel =
    stem.volume === 0
      ? "-∞ dB"
      : `${(20 * Math.log10(stem.volume)).toFixed(1)} dB`;

  const panLabel =
    stem.pan === 0 ? "C" : stem.pan < 0 ? `L${Math.round(-stem.pan * 100)}` : `R${Math.round(stem.pan * 100)}`;

  return (
    <div
      className={`rounded-md p-3 ring-1 transition ${bg} ${stem.muted ? "opacity-40" : ""}`}
    >
      {/* Header row: label + mute */}
      <div className="mb-2 flex items-center justify-between">
        <span className={`text-xs font-semibold uppercase tracking-wider ${color}`}>
          {stem.label}
        </span>
        <button
          onClick={() => updateStem(stem.id, { muted: !stem.muted })}
          className={`rounded px-2 py-0.5 text-[10px] font-bold transition ${
            stem.muted
              ? "bg-slate-700 text-slate-400"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          {stem.muted ? "UNMUTE" : "MUTE"}
        </button>
      </div>

      {/* Volume */}
      <div className="mb-2">
        <div className="mb-1 flex items-center justify-between text-[10px] text-slate-500">
          <span>VOL</span>
          <span className="font-mono text-slate-400">{dbLabel}</span>
        </div>
        <input
          type="range"
          min={0}
          max={200}
          step={1}
          value={Math.round(stem.volume * 100)}
          onChange={(e) => updateStem(stem.id, { volume: Number(e.target.value) / 100 })}
          className="w-full accent-current"
          disabled={stem.muted}
        />
      </div>

      {/* Pan */}
      <div>
        <div className="mb-1 flex items-center justify-between text-[10px] text-slate-500">
          <span>PAN</span>
          <span className="font-mono text-slate-400">{panLabel}</span>
        </div>
        <input
          type="range"
          min={-100}
          max={100}
          step={1}
          value={Math.round(stem.pan * 100)}
          onChange={(e) => updateStem(stem.id, { pan: Number(e.target.value) / 100 })}
          className="w-full accent-current"
          disabled={stem.muted}
        />
      </div>
    </div>
  );
}

export default function StemMixer() {
  const stems = useAppStore((s) => s.stems);

  if (stems.length === 0) return null;

  return (
    <section>
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Stem Mixer
      </h2>
      <div className="flex flex-col gap-2">
        {stems.map((stem) => (
          <StemRow key={stem.id} stem={stem} />
        ))}
      </div>
    </section>
  );
}
