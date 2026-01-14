# Voice Prompt Daemon 🎤

A background voice transcription daemon that listens for voice input and copies transcribed text to your clipboard using local Whisper models. Perfect for hands-free text input and voice-to-text workflows.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)

## ✨ Features

- 🎤 **Voice Recording**: Continuous audio recording using ALSA
- 🧠 **Local Transcription**: Offline speech-to-text using Whisper models
- 📋 **Clipboard Integration**: Automatic copying of transcribed text
- 🖥️ **System Tray**: Visual feedback with colored tray icons
- ⚡ **Signal Control**: Toggle listening state via SIGUSR1
- 🔄 **Background Operation**: Runs as a daemon process
- 🎯 **Debounced Input**: Prevents accidental rapid toggling

## 🚀 Quick Start

### Prerequisites

```bash
# Install system dependencies
sudo apt install alsa-utils wl-clipboard  # Ubuntu/Debian

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd voice-to-cli
```

2. **Run the daemon** (models download automatically):
```bash
uv run voice_daemon_local.py
```

**Note**: The first run will automatically download the required Whisper model (~147MB for base.en). Subsequent runs will use the cached model.

3. **(Optional) Manual model management**:
```bash
# If you prefer to manage models manually
# Models should be placed in ./whisper.cpp/models/
# Visit: https://github.com/ggerganov/whisper.cpp for more models
```

4. **Control the daemon**:
```bash
# Toggle listening state (or start if not running)
./voice_daemon_control.sh

# Or send signal manually
pkill -SIGUSR1 -f voice_daemon_local.py
```

## 📖 Usage

### Basic Operation

1. **Start the daemon**: `uv run voice_daemon_local.py`
2. **Toggle listening**: Use the control script or send SIGUSR1
3. **Speak**: When listening (red blinking icon), speak clearly
4. **Get text**: Transcribed text is automatically copied to clipboard
5. **Paste**: Paste the transcribed text anywhere (Ctrl+V)

### System Tray Indicators

- 🟦 **Blue Square**: Daemon idle, not listening
- 🔴 **Red Blinking**: Actively recording and listening
- ⚫ **Transparent**: Between blinks when recording

### Control Methods

```bash
# Method 1: Control script (recommended)
./voice_daemon_control.sh

# Method 2: Direct signal
kill -SIGUSR1 $(pgrep -f voice_daemon_local.py)

# Method 3: Keyboard shortcut (configure in your DE)
# Bind the control script to a hotkey
```

## 🛠️ Configuration

### Audio Settings

Edit these constants in `voice_daemon_local.py`:

```python
CHANNELS = 1
RATE = 16000  # Whisper works best with 16kHz
FORMAT = "S16_LE"  # 16-bit little endian
```

### Model Selection

Change the Whisper model by modifying:

```python
WHISPER_MODEL_NAME = "base.en"  # Model name for auto-download
```

Available models (auto-downloaded):
- `tiny.en` (~39MB) - Fastest, less accurate
- `base.en` (~147MB) - Good balance (default)
- `small.en` (~466MB) - More accurate
- `medium.en` (~1.5GB) - Very accurate

**Note**: Models are downloaded automatically on first run. You can also place models manually in `./whisper.cpp/models/` using the format `ggml-{model_name}.bin`.

## 📁 Project Structure

```
voice-to-cli/
├── voice_daemon_local.py      # Main daemon script
├── voice_daemon_control.sh    # Control script
├── REQUIREMENTS.md            # Detailed requirements
├── README.md                  # This file
├── whisper.cpp/
│   └── models/
│       └── ggml-base.en.bin   # Whisper model
├── test_env/                  # Test environment
└── .gitignore                 # Git ignore rules
```

## 🔧 Development

### Running from Source

```bash
# Install dependencies manually (if not using uv)
pip install numpy pywhispercpp pystray pillow pyperclip

# Run the daemon
python voice_daemon_local.py
```

### Testing

```bash
# Test audio recording
arecord -f S16_LE -c 1 -r 16000 -t wav test.wav

# Test transcription
python -c "
from pywhispercpp.model import Model
model = Model('whisper.cpp/models/ggml-base.en.bin')
segments = model.transcribe('test.wav')
print([s.text for s in segments])
"
```

## 🐛 Troubleshooting

### Common Issues

**"arecord command not found"**
```bash
sudo apt install alsa-utils
```

**"Model not found"**
```bash
# The daemon should auto-download models on first run
# If download fails, check internet connection or manually download:
ls -la whisper.cpp/models/ggml-base.en.bin

# Manual download (if needed)
mkdir -p whisper.cpp/models/
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin -O whisper.cpp/models/ggml-base.en.bin
```

**"Clipboard not working"**
```bash
# Install clipboard backend
sudo apt install wl-clipboard  # For Wayland
sudo apt install xclip         # For X11
```

**"Permission denied"**
```bash
# Ensure user has access to audio devices
sudo usermod -a -G audio $USER
# Log out and back in
```

### Debug Mode

Add debug prints by modifying the script or run with verbose output:

```bash
# Run with additional logging
python voice_daemon_local.py 2>&1 | tee daemon.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Improvement

- [ ] Cross-platform audio support (macOS/Windows)
- [ ] GUI configuration interface
- [ ] Multiple language model support
- [ ] Voice command detection
- [ ] Audio level visualization
- [ ] Custom hotkey configuration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) - C++ implementation of Whisper
- [OpenAI](https://openai.com/) - Whisper speech recognition model
- [pystray](https://github.com/muellerberndt/pystray) - System tray icon library
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard library

## 📞 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [REQUIREMENTS.md](REQUIREMENTS.md) for detailed setup
3. Open an Issue on GitHub
4. Join our discussions for community support

---

**Made with ❤️ for hands-free computing**