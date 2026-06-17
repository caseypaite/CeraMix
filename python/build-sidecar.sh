#!/usr/bin/env bash
# Build the Python inference backend sidecar for local development.
#
# Places the output at src-tauri/binaries/ceramix-engine-{triple}[.exe] so
# `pnpm tauri dev` can find it without running the full CI pipeline.
#
# Usage (from the repo root or the python/ directory):
#   bash python/build-sidecar.sh

set -euo pipefail
cd "$(dirname "$0")"   # always run from python/

echo "▶ Installing PyInstaller..."
pip install pyinstaller -q

echo "▶ Building sidecar..."
pyinstaller ceramix_engine.spec --distpath dist --workpath build --noconfirm

# Detect the current Rust target triple.
TRIPLE=$(rustc -vV 2>/dev/null | grep 'host:' | awk '{print $2}')
if [[ -z "$TRIPLE" ]]; then
  echo "ERROR: rustc not found on PATH. Install Rust: https://rustup.rs" >&2
  exit 1
fi

EXT=""
[[ "$TRIPLE" == *windows* ]] && EXT=".exe"

SRC="dist/ceramix-engine${EXT}"
DST="../src-tauri/binaries/ceramix-engine-${TRIPLE}${EXT}"

mkdir -p ../src-tauri/binaries
cp "$SRC" "$DST"

echo "✓ Sidecar placed at: src-tauri/binaries/ceramix-engine-${TRIPLE}${EXT}"
echo "  Run: pnpm tauri dev"
