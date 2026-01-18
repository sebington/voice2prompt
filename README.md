# Voice2Prompt

A voice-to-text daemon that lets you dictate text anywhere by holding down Right Ctrl. Audio is transcribed using Whisper and automatically pasted into your active application.

## Features

- **Push-to-talk**: Hold Right Ctrl to record, release to transcribe and paste
- **System-wide**: Works in any application
- **Local processing**: Uses Whisper.cpp for fast, private transcription
- **Visual feedback**: System tray icon (green=ready, red=recording)
- **Automatic model setup**: Downloads Whisper model on first run

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Linux with audio input device
- sudo access (for keyboard listener)

## Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository:
```bash
git clone <repository-url>
cd voice2prompt
```

3. Make the start script executable:
```bash
chmod +x start.sh
```

## Usage

Run both components with the included script:

```bash
./start.sh
```

Once running:
1. **Hold Right Ctrl** to start recording (tray icon turns red)
2. Speak your text
3. **Release Right Ctrl** to stop recording
4. Text is automatically transcribed and pasted

## How It Works

The system uses a split-privilege architecture with two processes:

- **voice_daemon_local.py**: Handles audio recording and Whisper transcription (runs as regular user)
- **key_listener.py**: Monitors Right Ctrl key press/release (requires root)

The processes communicate via UDP on localhost for security and isolation.

## Dependencies

All dependencies are managed via inline PEP 723 specifications and installed automatically by `uv run`:

- Audio: sounddevice, scipy, numpy
- Transcription: pywhispercpp
- UI: pystray, pillow
- Clipboard: pyperclip
- Keyboard: keyboard

## Troubleshooting

**No audio recording**: Check your microphone permissions and default input device.

**Paste not working**: Ensure key_listener.py is running with sudo.

**Model download fails**: Check your internet connection. The Whisper base.en model (~140MB) downloads on first run.

**Wayland clipboard issues**: The system falls back to wl-copy if pyperclip doesn't work.
