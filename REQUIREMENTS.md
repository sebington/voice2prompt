# Voice Daemon Requirements

This document outlines the dependencies required to run the Voice Prompt Daemon effectively across different environments.

## 1. Operating System
**Current Status**: Linux Only
*   The script currently uses `arecord` (part of ALSA), which is specific to Linux.
*   *Note*: To make this cross-platform (macOS/Windows), the recording logic would need to be switched from `subprocess.call("arecord")` to a cross-platform library like `sounddevice` or `pyaudio`.

## 2. System Tools (Linux)
These packages must be installed via your system's package manager (e.g., `apt`, `dnf`, `pacman`).

### Audio Recording
*   **Package**: `alsa-utils`
*   **Purpose**: Provides the `arecord` command used to capture voice input.
*   **Install**:
    *   Ubuntu/Debian: `sudo apt install alsa-utils`
    *   Fedora: `sudo dnf install alsa-utils`
    *   Arch: `sudo pacman -S alsa-utils`

### Clipboard Manager
The tool relies on `pyperclip` to access the clipboard. On Linux, this requires a backend utility. **Install both** to ensure compatibility across different login sessions.

*   **For Wayland** (Default on Ubuntu 22.04+, Fedora):
    *   Package: `wl-clipboard`
    *   Install: `sudo apt install wl-clipboard`
*   **For X11** (Legacy/Standard):
    *   Package: `xclip` (recommended) or `xsel`
    *   Install: `sudo apt install xclip`

## 3. Python Environment
*   **Python Version**: 3.10 or newer.
*   **Runner**: The script is designed to run with `uv` (a fast Python package manager), which automatically handles virtual environments and dependencies.
    *   Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Python Libraries
If not using `uv`, you must manually install these dependencies:
```bash
pip install numpy pywhispercpp pystray pillow pyperclip
```

## 4. Model Files
*   **Whisper Model**: GGML-formatted model files (e.g., `ggml-base.en.bin`).
*   **Automatic Download**: Models are downloaded automatically on first run via pywhispercpp.
*   **Manual Location**: If manually downloaded, place in: `./whisper.cpp/models/`
*   **Available Models**:
    *   `tiny.en` (~39MB) - Fastest, less accurate
    *   `base.en` (~147MB) - Good balance (default)
    *   `small.en` (~466MB) - More accurate  
    *   `medium.en` (~1.5GB) - Very accurate
*   **Download Sources**:
    *   Automatic via pywhispercpp (recommended)
    *   Manual from [whisper.cpp repository](https://github.com/ggerganov/whisper.cpp)
    *   HuggingFace: https://huggingface.co/ggerganov/whisper.cpp

## 5. Hardware
*   **Microphone**: A functional audio input device set as the system default.
*   **RAM**: ~500MB - 1GB available (depending on model size).
*   **Storage**: ~200MB for the base model.
