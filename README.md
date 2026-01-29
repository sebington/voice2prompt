# Voice2Prompt

A voice-to-text app that lets you dictate text anywhere by holding down Right Ctrl. Audio is transcribed using Whisper and automatically pasted into your active application.

## Features

- **Push-to-talk**: Hold Right Ctrl to record, release to transcribe and paste
- **System-wide**: Works in any application
- **Local processing**: Uses Whisper.cpp for fast, private transcription
- **Fast transcription**: ~0.5-0.8 seconds with optimized tiny.en model
- **Visual feedback**: System tray icon (green=ready, red=recording)
- **Automatic model setup**: Downloads Whisper model on first run
- **Memory optimized**: Direct audio processing without disk I/O overhead

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Linux with audio input device (only tested on Ubuntu 25.10 so far)
- sudo access (for keyboard listener)
- Clipboard tool:
  - **X11**: `xclip` or `xsel` (`sudo apt install xclip`)
  - **Wayland**: `wl-clipboard` (`sudo apt install wl-clipboard`)

## Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository:
```bash
git clone https://github.com/sebington/voice2prompt.git
cd voice2prompt
```

3. Make the start script executable:
```bash
chmod +x start.sh
```

## Usage

Run the following script in a terminal:

```bash
./start.sh
```

Once running:
1. **Hold Right Ctrl** to start recording (tray icon turns red)
2. Speak your text
3. **Release Right Ctrl** to stop recording
4. Text is automatically transcribed and pasted

To stop, press Ctrl+C

## How It Works

The system uses a split-privilege architecture with two processes:

- **voice_daemon_local.py**: Handles audio recording and Whisper transcription (runs as regular user)
- **key_listener.py**: Monitors Right Ctrl key press/release (requires root)

The processes communicate via UDP on localhost for security and isolation.

### Performance Optimizations

- **Tiny.en model**: Uses Whisper's smallest English model for 3-4x faster transcription
- **In-memory processing**: Audio data is processed directly without writing to disk
- **Efficient cleanup**: Temporary files are immediately deleted after use
- **Result**: Typical transcription completes in 0.5-0.8 seconds

## Dependencies

All dependencies are managed via inline PEP 723 specifications and installed automatically by `uv run`:

- Audio: sounddevice, numpy
- Transcription: pywhispercpp (with tiny.en model)
- UI: pystray, pillow
- Clipboard: pyperclip
- Keyboard: keyboard

Note: The startup script requests sudo access upfront for a clean password prompt, then launches both processes with proper signal handling for clean shutdown via Ctrl+C.

## Troubleshooting

**No audio recording**: Check your microphone permissions and default input device.

**Paste not working**: 
- First check if transcription is shown in terminal (if yes, clipboard is the issue)
- Install clipboard tools: `sudo apt install xclip` (X11) or `sudo apt install wl-clipboard` (Wayland)
- Ensure key_listener.py is running with sudo (the startup script handles this automatically)
- The error messages will tell you which clipboard tool is missing

**Ctrl+C not stopping**: This has been fixed - the script now properly traps signals and cleanly shuts down both processes.

**Model download fails**: Check your internet connection. The Whisper tiny.en model (~75MB) downloads on first run.

**Clipboard issues**: The system tries multiple clipboard backends in order (pyperclip → wl-copy → xclip). Error messages will indicate which tool needs to be installed.

**Slow transcription**: The system now uses the tiny.en model and memory optimization for fast processing (~0.5-0.8s). 

**Accuracy**: If you need higher accuracy, you can manually change `WHISPER_MODEL_NAME` to `base.en` in voice_daemon_local.py.

## Recent Improvements

### v1.1 - Performance & Stability Updates
- **4x faster transcription**: Switched to tiny.en model (0.5-0.8s vs 2s)
- **Memory optimization**: Eliminated disk I/O by processing audio directly in memory
- **Fixed startup**: Sudo password prompt now works correctly
- **Fixed shutdown**: Ctrl+C now properly terminates both processes
- **Better signal handling**: Clean process cleanup on exit
- **Removed scipy dependency**: Lighter installation footprint
