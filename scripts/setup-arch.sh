#!/usr/bin/env bash
# CeraMix — development environment setup for Arch Linux / EndeavourOS (Wayland)
#
# Run as a regular user with sudo rights:
#   bash scripts/setup-arch.sh
#
# What this script does:
#   1. Installs system packages via pacman (WebKitGTK, GTK3, Wayland stack, etc.)
#   2. Installs Rust via rustup (if not already present)
#   3. Installs pnpm (Node.js package manager used by the frontend build)
#   4. Installs the Python inference backend's pip dependencies

set -euo pipefail

# ── Colour helpers ─────────────────────────────────────────────────────────────
green()  { printf '\e[32m%s\e[0m\n' "$*"; }
yellow() { printf '\e[33m%s\e[0m\n' "$*"; }
red()    { printf '\e[31m%s\e[0m\n' "$*"; }

# ── 1. System packages ─────────────────────────────────────────────────────────
green "==> Refreshing package database and installing system dependencies..."

sudo pacman -Syu --noconfirm

sudo pacman -S --needed --noconfirm \
    base-devel \
    curl \
    wget \
    git \
    file \
    pkg-config \
    \
    `# WebKitGTK 4.1 — required by Tauri 2.x on Linux` \
    webkit2gtk-4.1 \
    gtk3 \
    libayatana-appindicator-gtk3 \
    librsvg \
    \
    `# Wayland display server stack` \
    wayland \
    wayland-protocols \
    libxkbcommon \
    xdg-desktop-portal \
    \
    `# Recommended Wayland portal backends (install at least one)` \
    xdg-desktop-portal-wlr \
    \
    `# Build tooling` \
    openssl \
    glib2 \
    patchelf \
    \
    `# Audio / video processing (runtime dependency of the engine)` \
    ffmpeg \
    \
    `# Python (for the ceramix-engine sidecar)` \
    python \
    python-pip \
    \
    `# Node.js (for the frontend build)` \
    nodejs \
    npm

# Optional: portal backend for KDE Plasma Wayland sessions
if pacman -Qi plasma-desktop &>/dev/null 2>&1; then
    yellow "==> Detected KDE Plasma — installing xdg-desktop-portal-kde..."
    sudo pacman -S --needed --noconfirm xdg-desktop-portal-kde
fi

# ── 2. Rust / rustup ──────────────────────────────────────────────────────────
if command -v rustup &>/dev/null; then
    green "==> Rust already installed — updating..."
    rustup update stable
else
    green "==> Installing Rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable
    # shellcheck disable=SC1091
    source "${HOME}/.cargo/env"
fi

rustup target add x86_64-unknown-linux-gnu

# ── 3. pnpm ───────────────────────────────────────────────────────────────────
if ! command -v pnpm &>/dev/null; then
    green "==> Installing pnpm..."
    npm install -g pnpm
fi

# ── 4. Python inference backend dependencies ───────────────────────────────────
green "==> Installing Python backend dependencies..."
(
    cd "$(dirname "$0")/../python"
    pip install --user --quiet --upgrade pip
    pip install --user --quiet -r requirements.txt
)

# ── 5. Node.js frontend dependencies ──────────────────────────────────────────
green "==> Installing Node.js frontend dependencies..."
(
    cd "$(dirname "$0")/.."
    pnpm install
)

# ── Done ───────────────────────────────────────────────────────────────────────
green ""
green "Setup complete.  Wayland session tips:"
green ""
green "  • pnpm tauri dev          Start the dev server (auto-detects Wayland/X11)"
green "  • GDK_BACKEND=wayland     Force Wayland backend if GTK falls back to X11"
green "  • WEBKIT_FORCE_SANDBOX=0  Disable WebKit sandbox if you see blank windows"
green ""
yellow "Note: log out and back in if this is a first-time Rust install (PATH update)."
