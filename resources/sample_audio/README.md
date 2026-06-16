# Sample audio

Drop a short, license-clean dummy clip here (e.g. `dummy.wav`) for developing
the playback engine and waveform renderer in Step 2 before any AI processing is
wired up.

Do **not** commit large or copyrighted audio. Generate a test tone instead:

```bash
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -ac 2 dummy.wav
```
