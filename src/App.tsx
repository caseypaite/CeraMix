import FileExplorer from "./components/FileExplorer/FileExplorer";
import WaveformEditor from "./components/WaveformEditor/WaveformEditor";
import ProcessingControls from "./components/ProcessingControls/ProcessingControls";
import ProgressOverlay from "./components/ProgressOverlay/ProgressOverlay";

/**
 * Three-panel pro-audio layout:
 *   Left   — File Explorer / batch queue
 *   Center — Waveform editor & track layers
 *   Right  — Processing controls (denoise + stem splitting)
 */
export default function App() {
  return (
    <div className="flex h-screen w-screen flex-col bg-canvas text-slate-100">
      <header className="flex items-center gap-2 border-b border-slate-800 px-4 py-2">
        <span className="font-mono text-lg font-bold tracking-tight text-accent-blue">
          Cera<span className="text-accent-violet">Mix</span>
        </span>
        <span className="text-xs text-slate-500">audio cleanup · stems · denoise</span>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-[260px_1fr_320px]">
        <aside className="min-h-0 overflow-y-auto border-r border-slate-800">
          <FileExplorer />
        </aside>

        <section className="min-h-0 overflow-hidden">
          <WaveformEditor />
        </section>

        <aside className="min-h-0 overflow-y-auto border-l border-slate-800">
          <ProcessingControls />
        </aside>
      </main>

      <ProgressOverlay />
    </div>
  );
}
