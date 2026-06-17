# PyInstaller spec for the CeraMix inference backend.
#
# Produces a single self-contained binary (--onefile mode) that the Tauri shell
# embeds as a sidecar. Model weights are NOT bundled — they are downloaded at
# runtime into ~/.cache/ceramix/models.
#
# Build:
#   cd python
#   pyinstaller ceramix_engine.spec --distpath dist --workpath build --noconfirm
#
# The CI renames the output to the Tauri sidecar convention:
#   ceramix-engine-{rust-target-triple}[.exe]

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# ── Collect packages that ship native extensions PyInstaller's static
#    analyser misses (DLLs on Windows, .so files on Linux). ──────────────────
datas, binaries, hiddenimports = [], [], []

for pkg in ("onnxruntime", "soundfile"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Ensure every ceramix_engine submodule is included even though they are
# currently stubs — prevents ImportError when the engine is launched.
hiddenimports += collect_submodules("ceramix_engine")
hiddenimports += [
    "ceramix_engine.runtime",
    "ceramix_engine.audio_io",
    "ceramix_engine.models.registry",
    "ceramix_engine.models.downloader",
    "ceramix_engine.processors.stem_split",
    "ceramix_engine.processors.denoise",
    # numpy is pulled in transitively but declare it explicitly for safety
    "numpy",
    "numpy.core._multiarray_umath",
]

a = Analysis(
    ["ceramix_engine/server.py"],
    pathex=["python"],          # allow `import ceramix_engine` from the spec dir
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional backends — they're not active in the scaffold.
        # Remove from this list as you wire up each model.
        "torch",
        "torchvision",
        "torchaudio",
        "demucs",
        "deepfilternet",
        "matplotlib",
        "IPython",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ceramix-engine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX compression is disabled: it causes false-positive AV detections on
    # Windows and adds noticeable startup latency on Linux.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # stdio JSON-RPC server — must not hide the console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
