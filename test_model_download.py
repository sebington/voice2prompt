# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "numpy",
#     "pywhispercpp",
# ]
# ///
"""
Test script to verify automatic model downloading functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from voice_daemon_local import WHISPER_MODEL_NAME, WHISPER_MODEL, WHISPER_PATH
    from pywhispercpp.model import Model
    
    print("🧪 Testing automatic model downloading...")
    print(f"📁 Whisper path: {WHISPER_PATH}")
    print(f"🎯 Model name: {WHISPER_MODEL_NAME}")
    print(f"📂 Local model path: {WHISPER_MODEL}")
    print(f"📦 Local model exists: {WHISPER_MODEL.exists()}")
    
    if WHISPER_MODEL.exists():
        print("✅ Using local model")
        model = Model(str(WHISPER_MODEL))
    else:
        print("📥 Testing automatic download...")
        print("⏳ This may take a moment...")
        model = Model(WHISPER_MODEL_NAME)
        print("✅ Model downloaded and loaded successfully!")
    
    print(f"🎉 Test completed successfully!")
    print(f"📊 Model loaded: {type(model)}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure dependencies are installed: uv run python test_model_download.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)