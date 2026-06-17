import { useEffect, useState } from "react";
import { convertFileSrc } from "@tauri-apps/api/core";

interface Props {
  path: string;
}

export default function VideoPreview({ path }: Props) {
  const [src, setSrc] = useState("");

  useEffect(() => {
    setSrc(convertFileSrc(path));
  }, [path]);

  return (
    <video
      key={src}
      src={src}
      controls
      className="h-full w-full rounded-md border border-slate-800 bg-slate-950 object-contain"
    />
  );
}
