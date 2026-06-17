/**
 * Wavesurfer.js lifecycle hook for the waveform editor.
 *
 * Scaffold: returns a ref to attach to the container and stubbed transport
 * controls. Wire up an actual WaveSurfer instance in Step 2.
 */
import { useCallback, useRef } from "react";

export interface Transport {
  play: () => void;
  pause: () => void;
  seek: (seconds: number) => void;
  toggleLoop: () => void;
}

export function useWaveform(_url?: string) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  // TODO: instantiate WaveSurfer in a useEffect keyed on `_url`, apply the
  // cyber-noir palette (electric blue / violet), and clean up on unmount.

  const transport: Transport = {
    play: useCallback(() => {}, []),
    pause: useCallback(() => {}, []),
    seek: useCallback((_s: number) => {}, []),
    toggleLoop: useCallback(() => {}, []),
  };

  return { containerRef, transport };
}
