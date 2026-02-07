# Voice2Prompt Codebase Report

## Project Overview

**voice2prompt** is a voice-to-text application that enables hands-free dictation system-wide by holding down the Right Ctrl key. Audio is recorded, transcribed using OpenAI Whisper, and automatically pasted into the active application.

### Key Characteristics
- **Push-to-talk interface**: Hold Right Ctrl to record, release to transcribe and paste
- **System-wide integration**: Works in any application
- **Local processing**: Uses Whisper.cpp for private, fast transcription
- **Fast performance**: ~0.5-0.8 seconds with tiny.en model
- **Visual feedback**: System tray icon (green=ready, red=recording)
- **Memory optimized**: Direct audio processing without disk I/O

---

## Project Structure

```
voice2prompt/
├── README.md                 # Documentation and setup instructions
├── voice_daemon_local.py     # Main daemon (user component)
├── key_listener.py           # Keyboard listener (root component)
└── start.sh                  # Startup script (referenced in README)
```

---

## Architecture

The system uses a **split-privilege architecture** with two separate processes communicating via UDP on localhost:

```
┌─────────────────────────────────────────────────┐
│ key_listener.py (runs with sudo)                │
├─────────────────────────────────────────────────┤
│ • Monitors Right Ctrl key (scan code 97)        │
│ • Sends START/STOP on UDP:5005 (port 5005)      │
│ • Listens for PASTE on UDP:5006 (port 5006)     │
│ • Simulates Ctrl+V when PASTE received          │
└─────────────────────────────────────────────────┘
              ↑ UDP Communication ↓
┌─────────────────────────────────────────────────┐
│ voice_daemon_local.py (runs as regular user)    │
├─────────────────────────────────────────────────┤
│ • Listens for START/STOP commands on UDP:5005   │
│ • Records audio when recording is active        │
│ • Transcribes using pywhispercpp (tiny.en)      │
│ • Manages system tray icon (visual feedback)    │
│ • Handles clipboard operations                  │
│ • Sends PASTE command to key_listener           │
└─────────────────────────────────────────────────┘
```

### Why Split-Privilege?
- **key_listener** needs root access to listen for global keyboard events and simulate keypresses
- **voice_daemon_local** runs as regular user for security (no need for root to record audio or transcribe)
- UDP localhost communication is secure and isolated from network

---

## File-by-File Analysis

### 1. voice_daemon_local.py
**Purpose**: Main daemon that handles audio recording, transcription, and clipboard operations

**Key Configuration**:
```python
UDP_IP = "127.0.0.1"
UDP_PORT = 5005              # Listens for START/STOP commands
CMD_PORT = 5006              # Sends PASTE commands
CHANNELS = 1                 # Mono audio
RATE = 16000                 # 16kHz (Whisper optimal)
FORMAT = "S16_LE"            # 16-bit little endian
WHISPER_MODEL_NAME = "tiny.en"
```

**Main Components**:

1. **Initialization**:
   - Checks it's NOT running as root (security check)
   - Starts system tray icon in separate thread
   - Initializes pywhispercpp with tiny.en model (auto-downloads if needed)
   - Creates UDP listener socket for START/STOP commands
   - Opens audio input stream via sounddevice

2. **Audio Recording**:
   - `audio_callback()`: Called by sounddevice for each audio chunk
   - Records data only when `listening` flag is True
   - Appends chunks to `recording_data` list
   - Progress indicator (dots) printed every 10 chunks

3. **Transcription**:
   - `transcribe_audio()`: Converts numpy array to WAV format
   - Creates temporary WAV file (required by pywhispercpp)
   - Calls `whisper_model.transcribe()`
   - Immediately deletes temp file
   - Returns text from all segments joined with spaces

4. **Clipboard Operations**:
   - Tries three backends in order:
     1. `pyperclip` (cross-platform)
     2. `wl-copy` (Wayland)
     3. `xclip` (X11)
   - Adds trailing space for better UX
   - Falls back gracefully with error messages

5. **System Tray**:
   - `create_image()`: Generates colored square (64x64 pixels)
   - `run_tray_icon()`: Runs in daemon thread
   - `update_tray_icon()`: Changes color (green=ready, red=recording)

6. **Paste Simulation**:
   - `simulate_ctrl_v()`: Sends UDP "PASTE" command to key_listener
   - key_listener (as root) simulates the actual Ctrl+V

**Dependencies**:
- `numpy` - Audio array operations
- `sounddevice` - Audio input stream
- `pywhispercpp` - Whisper transcription
- `pystray` - System tray icon
- `pillow` - Image generation
- `pyperclip` - Clipboard access
- `socket`, `select` - UDP communication
- `wave` - WAV file format

---

### 2. key_listener.py
**Purpose**: Global keyboard listener that monitors Right Ctrl and sends signals to the daemon

**Configuration**:
```python
UDP_IP = "127.0.0.1"
UDP_PORT = 5005              # Send START/STOP to daemon
CMD_PORT = 5006              # Listen for PASTE commands
RIGHT_CTRL_SCANCODE = 97     # Scan code for Right Ctrl key
```

**Main Components**:

1. **Security Check**:
   - Verifies it's running with sudo (`os.geteuid() == 0`)
   - Exits with error if not root

2. **Keyboard Monitoring**:
   - `on_press()`: Called when Right Ctrl (code 97) is pressed
   - `on_release()`: Called when Right Ctrl is released
   - Uses `is_pressed` flag to prevent auto-repeat issues
   - Sends START command on press, STOP command on release

3. **UDP Command Sending**:
   - `send_cmd()`: Encodes command and sends to UDP:5005
   - Communicates with voice_daemon_local

4. **Command Listening**:
   - `command_listener()`: Runs in daemon thread
   - Listens on UDP:5006 for PASTE commands
   - When received: calls `keyboard.send('ctrl+v')`
   - Uses 0.1s timeout for non-blocking listen

**Dependencies**:
- `keyboard` - Global keyboard monitoring
- `socket`, `select` - UDP communication
- Standard library: `time`, `sys`, `os`, `threading`

---

## Data Flow Sequence

### Recording and Transcription Flow

```
1. User presses Right Ctrl
   ↓
2. key_listener detects press (RIGHT_CTRL_SCANCODE = 97)
   ↓
3. key_listener sends "START" to UDP:5005
   ↓
4. voice_daemon receives "START" command
   ├─ Sets listening = True
   ├─ Resets recording_data buffer
   ├─ Updates tray icon to red
   └─ Begins capturing audio via sounddevice
   ↓
5. User speaks (audio chunks accumulated in recording_data)
   ↓
6. User releases Right Ctrl
   ↓
7. key_listener detects release
   ↓
8. key_listener sends "STOP" to UDP:5005
   ↓
9. voice_daemon receives "STOP" command
   ├─ Sets listening = False
   ├─ Updates tray icon to green
   └─ Begins processing
   ↓
10. voice_daemon concatenates audio chunks (numpy.concatenate)
    ↓
11. voice_daemon transcribes:
    ├─ Converts numpy array to WAV temp file
    ├─ Calls whisper_model.transcribe()
    ├─ Deletes temp file immediately
    └─ Returns transcribed text
    ↓
12. voice_daemon copies text to clipboard:
    ├─ Tries pyperclip.copy()
    ├─ Falls back to wl-copy or xclip if needed
    └─ Adds trailing space for better UX
    ↓
13. voice_daemon sends "PASTE" to UDP:5006
    ↓
14. key_listener receives "PASTE" command
    ↓
15. key_listener executes keyboard.send('ctrl+v')
    ↓
16. Text is pasted into active application
```

---

## Performance Optimizations

1. **Tiny.en Model**:
   - Whisper's smallest English-only model
   - ~75MB download
   - 3-4x faster than base model
   - Sufficient accuracy for most use cases

2. **In-Memory Audio Processing**:
   - Audio chunks stored in numpy arrays
   - No disk I/O until transcription
   - Temp WAV file created only for whisper, then immediately deleted
   - Reduces latency and disk wear

3. **Efficient Audio Streaming**:
   - `sounddevice` with callback for continuous capture
   - Blocksize=1024 for stability
   - Non-blocking UDP communication with select()

4. **Results**:
   - Typical transcription: 0.5-0.8 seconds
   - Total latency: Press to paste usually < 1 second

---

## Dependency Management

Both scripts use **PEP 723 inline script metadata** for dependency specification:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "numpy",
#     "pywhispercpp",
#     ...
# ]
# ///
```

This allows each script to be executed with `uv run script.py` without needing:
- Virtual environments
- requirements.txt files
- Manual dependency installation

The `uv` package manager automatically installs specified dependencies and manages isolation.

---

## System Requirements

- **Python**: 3.10+
- **Package Manager**: uv (https://github.com/astral-sh/uv)
- **OS**: Linux (Ubuntu/Wayland tested, Endeavour/X11 tested)
- **Privileges**: sudo access required for key_listener
- **Audio**: Microphone/audio input device
- **Clipboard Tools**:
  - X11: `xclip` or `xsel`
  - Wayland: `wl-clipboard`

---

## Setup and Usage

### Installation
```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone repository
git clone https://github.com/sebington/voice2prompt.git
cd voice2prompt

# 3. Make start script executable
chmod +x start.sh
```

### Running
```bash
./start.sh
```

The startup script:
1. Requests sudo password upfront
2. Launches key_listener with sudo
3. Launches voice_daemon_local as regular user
4. Handles signal cleanup for Ctrl+C shutdown

### Usage
1. **Hold Right Ctrl** to start recording (tray icon turns red)
2. **Speak clearly** (audio is captured continuously)
3. **Release Right Ctrl** to stop recording
4. Text is **automatically transcribed and pasted**
5. **Press Ctrl+C** to exit both processes

---

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| No audio recording | Microphone permissions or wrong input device | Check default audio device, check microphone permissions |
| Paste not working | Missing clipboard tool or daemon not running | Check error in terminal, install xclip (X11) or wl-clipboard (Wayland) |
| Slow transcription | Using larger model | Confirm tiny.en is being used; can change to base.en for higher accuracy |
| Ctrl+C doesn't stop | Signal handling issue | Should be fixed in v1.1+; press Ctrl+C in terminal running start.sh |
| Model download fails | No internet or storage issue | Check internet connection; model is ~75MB |
| Permission denied | Not using start.sh script | Use ./start.sh which handles sudo correctly |
| Clipboard "multiple backends failed" | No compatible clipboard tool installed | Install xclip (X11): `sudo apt install xclip` or wl-clipboard (Wayland): `sudo apt install wl-clipboard` |

---

## Recent Improvements (v1.1)

### Performance
- **4x faster transcription**: tiny.en model (0.5-0.8s vs 2s previously)
- **Memory optimization**: Eliminated disk I/O by processing audio directly in memory

### Stability
- **Fixed startup**: Sudo password prompt now works correctly
- **Fixed shutdown**: Ctrl+C properly terminates both processes
- **Better signal handling**: Clean process cleanup on exit

### Dependencies
- **Removed scipy**: Lighter installation footprint (scipy was listed but unused)

---

## Security Considerations

1. **Split-Privilege Architecture**:
   - Only key_listener runs as root (minimal code)
   - Daemon runs as regular user
   - No privileged operations in transcription/clipboard code

2. **UDP Localhost Only**:
   - UDP communication restricted to 127.0.0.1
   - Not exposed to network
   - Simple text protocols (START, STOP, PASTE)

3. **No External Services**:
   - Whisper runs locally via whisper.cpp
   - No cloud API calls or telemetry
   - Audio never leaves the system

4. **Temporary Files**:
   - WAV files created in /tmp and immediately deleted
   - Minimal window for file access

---

## Future Enhancement Opportunities

1. **Model Selection**: GUI or config file to choose between tiny.en, base.en, small.en
2. **Language Support**: Add support for other languages via model selection
3. **Auto-start**: Add systemd service or desktop autostart option
4. **Logging**: Optional debug logging mode
5. **Confirmation UI**: Toast notification showing transcribed text before pasting
6. **Custom Hotkey**: Allow configuration of trigger key (currently hardcoded as Right Ctrl)
7. **History**: Store transcription history locally
8. **Multiple Profiles**: Different clipboard backends for different systems

---

## Code Quality Notes

**Strengths**:
- Clean separation of concerns (keyboard vs audio/transcription)
- Proper use of threading for non-blocking operations
- Graceful error handling with fallbacks
- Comprehensive clipboard backend support
- Good use of standard library (socket, select, threading)

**Areas for Enhancement**:
- Could add logging module instead of print statements
- Configuration could be externalized to config file
- Unit tests would be beneficial
- Type hints could be added for clarity
- More detailed docstrings on complex functions

---

## Conclusion

voice2prompt is a well-architected, performant voice-to-text solution that demonstrates:
- Effective use of split-privilege security model
- Smart performance optimization techniques
- Robust error handling and fallbacks
- Clean IPC via UDP for inter-process communication

The project is production-ready with good documentation and recent stability improvements in v1.1.
