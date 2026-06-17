/**
 * Global application state (Zustand).
 *
 * Scaffold: shapes the data model for the batch queue, active track, processing
 * config, and progress. Actions are stubbed where they will call into `ipc`.
 */
import { create } from "zustand";
import type { ExportFormat, SplitTopology } from "../lib/ipc";

export interface AudioFile {
  id: string;
  name: string;
  path: string;
  status: "queued" | "processing" | "done" | "error";
}

export interface ProcessingConfig {
  topology: SplitTopology;
  denoiseIntensity: number; // 0-100
  exportFormat: ExportFormat;
  bitDepth: 16 | 24 | 32;
}

export interface ProgressState {
  active: boolean;
  stage: string;
  progress: number; // 0..1
}

interface AppState {
  queue: AudioFile[];
  activeFileId: string | null;
  config: ProcessingConfig;
  progress: ProgressState;

  addFiles: (files: AudioFile[]) => void;
  removeFile: (id: string) => void;
  setActive: (id: string | null) => void;
  updateConfig: (patch: Partial<ProcessingConfig>) => void;
  setProgress: (patch: Partial<ProgressState>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  queue: [],
  activeFileId: null,
  config: {
    topology: "4stem",
    denoiseIntensity: 80,
    exportFormat: "wav",
    bitDepth: 24,
  },
  progress: { active: false, stage: "", progress: 0 },

  addFiles: (files) => set((s) => ({ queue: [...s.queue, ...files] })),
  removeFile: (id) =>
    set((s) => ({ queue: s.queue.filter((f) => f.id !== id) })),
  setActive: (id) => set({ activeFileId: id }),
  updateConfig: (patch) => set((s) => ({ config: { ...s.config, ...patch } })),
  setProgress: (patch) => set((s) => ({ progress: { ...s.progress, ...patch } })),
}));
