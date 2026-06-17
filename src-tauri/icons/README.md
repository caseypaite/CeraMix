# App icons

Place the generated icon set here. Once you have a 1024×1024 master PNG
(`app-icon.png`), generate the full cross-platform set with:

```bash
pnpm tauri icon path/to/app-icon.png
```

This produces `32x32.png`, `128x128.png`, `128x128@2x.png`, `icon.icns`
(macOS), and `icon.ico` (Windows), which are referenced in `tauri.conf.json`.
