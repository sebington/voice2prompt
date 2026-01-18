# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a voice-to-text daemon that allows users to hold Right Ctrl to record audio, which is then transcribed using Whisper and automatically pasted as text. The system uses a split-privilege architecture with two separate processes communicating via UDP.

## Architecture

### Two-Process Design

The system consists of two independent Python scripts that must run simultaneously:

1. **voice_daemon_local.py** (User Mode)
   - Handles audio recording using sounddevice
   - Performs speech-to-text transcription using pywhispercpp
   - Manages system tray icon (green=ready, red=recording)
   - Copies transcribed text to clipboard (pyperclip or wl-copy fallback)
   - Runs as regular user (never as root)
   - Listens on UDP port 5005 for START/STOP commands
   - Sends PASTE commands to port 5006

2. **key_listener.py** (Root Mode)
   - Global keyboard listener for Right Ctrl key (scan code 97)
   - Sends START/STOP commands to voice daemon via UDP port 5005
   - Listens on UDP port 5006 for PASTE commands
   - Executes Ctrl+V keyboard simulation when instructed
   - Must run as root (requires sudo)

### Communication Flow

```
User holds Right Ctrl
  -> key_listener detects press (scan code 97)
  -> Sends "START" to UDP 5005
  -> voice_daemon begins recording

User releases Right Ctrl
  -> key_listener detects release
  -> Sends "STOP" to UDP 5005
  -> voice_daemon transcribes audio
  -> voice_daemon copies to clipboard
  -> voice_daemon sends "PASTE" to UDP 5006
  -> key_listener simulates Ctrl+V
```

## Commands

### Running the System

```bash
# Start both components (recommended)
./start.sh

# Or manually start each component:
# Terminal 1 (user mode):
uv run voice_daemon_local.py

# Terminal 2 (root mode):
sudo uv run key_listener.py
```

### Dependencies

Both scripts use inline PEP 723 dependency specifications and are executed via `uv run --script`. No separate virtual environment or pip install needed.

- voice_daemon_local.py: numpy, pywhispercpp, pystray, pillow, pyperclip, sounddevice, scipy
- key_listener.py: keyboard

### Whisper Model

The system uses whisper.cpp with the base.en model. On first run:
- Checks for local model at `whisper.cpp/models/ggml-base.en.bin`
- If not found, pywhispercpp auto-downloads the model
- Model initialization logs are suppressed by redirecting stderr

## Key Implementation Details

### Audio Recording
- Records at 16kHz mono (optimal for Whisper)
- Uses sounddevice with callback-based streaming
- Accumulates audio chunks in `recording_data` list while `listening=True`
- Converts to numpy array and saves as WAV file for transcription

### Transcription
- Transcription happens in main thread after recording stops
- Empty or very small audio files (<1KB) are skipped
- Segments are concatenated with spaces
- Text is normalized and a trailing space is added before pasting

### Clipboard and Pasting
- Primary: pyperclip for cross-platform clipboard
- Fallback: wl-copy for Wayland systems
- Paste is simulated by key_listener (as root) receiving UDP command

### System Tray
- Green square: Ready to record
- Red square: Currently recording
- Runs in separate daemon thread

## Security Considerations

- key_listener MUST run as root (required for global keyboard hooks)
- voice_daemon_local MUST NOT run as root (principle of least privilege)
- UDP communication is localhost-only (127.0.0.1)
- Two-port design separates control flow (5005) from command execution (5006)
