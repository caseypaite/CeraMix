import { useCallback, useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

export interface Transport {
  play: () => void;
  pause: () => void;
  seek: (seconds: number) => void;
  toggleLoop: () => void;
  isPlaying: boolean;
  isLooping: boolean;
}

/**
 * Manages a WaveSurfer instance bound to a container ref.
 * Re-creates the instance when `url` changes; tears it down on unmount.
 */
export function useWaveform(url?: string) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WaveSurfer | null>(null);
  const loopRef = useRef(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLooping, setIsLooping] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !url) return;

    wsRef.current?.destroy();
    wsRef.current = null;
    setIsPlaying(false);

    const ws = WaveSurfer.create({
      container,
      waveColor: "#38bdf8",     // electric blue
      progressColor: "#8b5cf6", // violet
      cursorColor: "#8b5cf6",
      height: 128,
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      normalize: true,
    });

    ws.on("play", () => setIsPlaying(true));
    ws.on("pause", () => setIsPlaying(false));
    ws.on("finish", () => {
      setIsPlaying(false);
      if (loopRef.current) {
        ws.seekTo(0);
        ws.play();
      }
    });

    ws.load(url).catch(() => {/* ignore load errors — file may not exist yet */});
    wsRef.current = ws;

    return () => {
      ws.destroy();
      wsRef.current = null;
      setIsPlaying(false);
    };
  }, [url]);

  const play = useCallback(() => wsRef.current?.play(), []);
  const pause = useCallback(() => wsRef.current?.pause(), []);

  const seek = useCallback((seconds: number) => {
    const ws = wsRef.current;
    if (!ws) return;
    const d = ws.getDuration();
    if (d > 0) ws.seekTo(seconds / d);
  }, []);

  const toggleLoop = useCallback(() => {
    setIsLooping((prev) => {
      loopRef.current = !prev;
      return !prev;
    });
  }, []);

  return {
    containerRef,
    transport: { play, pause, seek, toggleLoop, isPlaying, isLooping },
  };
}
