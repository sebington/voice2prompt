#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "numpy",
#     "pywhispercpp",
# ]
# ///

"""
Voice Prompt Daemon using pywhispercpp (Local Whisper)
A background daemon that listens for voice input and copies transcribed text to clipboard
Uses SIGUSR1 signal to toggle listening state
"""

import queue
import signal
import subprocess
import os
import sys
import tempfile
import wave
import threading
import time
import select
from pathlib import Path
from pywhispercpp.model import Model

# Configuration
CHANNELS = 1
RATE = 16000  # whisper works best with 16kHz
FORMAT = "S16_LE"  # 16-bit little endian
ARECORD_CMD = ["arecord"]
WHISPER_PATH = Path(__file__).parent / "whisper.cpp"
WHISPER_MODEL = WHISPER_PATH / "models" / "ggml-base.en.bin"  # Default model path

audio_q = queue.Queue()
listening = False
recording_process = None
whisper_model = None
last_signal_time = 0

def notify(msg):
    """Send desktop notification (Disabled)"""
    # Desktop notifications are disabled as requested
    pass

def toggle_listening(signum, frame):
    """Toggle listening state via signal"""
    global listening, recording_process, last_signal_time
    
    current_time = time.time()
    time_diff = current_time - last_signal_time
    
    # Debounce: ignore signals that come too close together (1.0s)
    if time_diff < 1.0:
        print(f"⚠️  Ignoring signal (debounce active, diff: {time_diff:.2f}s)")
        return
        
    last_signal_time = current_time
    
    if not listening:
        # Starting to listen
        listening = True
        print(f"🎤 Listening started via signal (Time: {time.ctime()})")
        notify("🎤 Listening…")
    else:
        # Stopping listening
        listening = False
        print(f"⏹️  Listening stopped via signal (Time: {time.ctime()})")
        notify("⏹️  Finalizing…")

def record_audio_segment(filename):
    """Record a segment of audio using arecord"""
    global recording_process
    
    cmd = ARECORD_CMD + [
        "-f", FORMAT,
        "-c", str(CHANNELS),
        "-r", str(RATE),
        "-t", "wav",
        filename
    ]
    
    try:
        recording_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except Exception as e:
        print(f"❌ Error starting recording: {e}")
        return False

def stop_recording():
    """Stop the current recording"""
    global recording_process
    if recording_process and recording_process.poll() is None:
        recording_process.terminate()
        recording_process.wait()

def normalize_prompt(text):
    """Format text as a prompt"""
    return text.strip()

def transcribe_audio(audio_file):
    """Transcribe audio using pywhispercpp"""
    try:
        # Check if file exists and has content
        if not os.path.exists(audio_file):
            print(f"⚠️  Audio file not found: {audio_file}")
            return None
        
        file_size = os.path.getsize(audio_file)
        if file_size < 1000:  # Less than 1KB is probably empty
            print(f"⚠️  Audio file seems too small: {file_size} bytes")
            return None
        
        print(f"🔄 Transcribing {audio_file} ({file_size} bytes)...")
        
        # Use pywhispercpp to transcribe
        segments = whisper_model.transcribe(str(audio_file))
        
        # Extract text from all segments
        if segments and len(segments) > 0:
            transcription_parts = []
            for segment in segments:
                if hasattr(segment, 'text') and segment.text.strip():
                    transcription_parts.append(segment.text.strip())
            
            transcription = ' '.join(transcription_parts) if transcription_parts else None
            
            if transcription:
                print(f"✅ Transcription complete")
            else:
                print("⚠️  No speech detected")
                
            return transcription
        else:
            print("⚠️  No speech detected")
            return None
            
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return None

def main():
    global listening, recording_process, whisper_model, last_signal_time
    
    # Check if arecord is available
    try:
        subprocess.run(ARECORD_CMD + ["--help"], 
                     capture_output=True, check=True)
        print("✅ Using arecord for audio recording")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: 'arecord' command not found")
        print("Please install ALSA utilities:")
        print("  sudo apt-get install alsa-utils  # Ubuntu/Debian")
        sys.exit(1)
    
    # Initialize pywhispercpp
    try:
        if not WHISPER_MODEL.exists():
            print(f"Error: Model not found at {WHISPER_MODEL}")
            print("Please download a whisper model (e.g., ggml-base.en.bin)")
            sys.exit(1)
        
        whisper_model = Model(str(WHISPER_MODEL))
        print(f"✅ Loaded whisper model: {WHISPER_MODEL.name}")
        
    except Exception as e:
        print(f"Error initializing whisper: {e}")
        sys.exit(1)

    # Set up the signal handler for toggling
    signal.signal(signal.SIGUSR1, toggle_listening)

    with tempfile.TemporaryDirectory() as tmpdir:
        recording_file = os.path.join(tmpdir, "recording.wav")
        
        print("🚀 Voice Prompt Daemon Ready")
        print("📋 Current state: NOT LISTENING (waiting for SIGUSR1)")
        print("🎯 Send SIGUSR1 to start/stop listening")

        while True:
            try:
                if listening:
                    # Start recording
                    if not recording_process or recording_process.poll() is not None:
                        print("🎤 Starting recording...")
                        if record_audio_segment(recording_file):
                            print("🔴 Recording in progress...")
                        else:
                            print("❌ Failed to start recording")
                            listening = False
                    
                    # Check for signal to stop (non-blocking)
                    # We use a small timeout to allow signal handling
                    time.sleep(0.1)
                    
                else:
                    # Not listening - check if we were recording
                    if recording_process and recording_process.poll() is None:
                        stop_recording()
                        print("⏹️  Recording stopped")
                        
                        # Process the recorded audio
                        if os.path.exists(recording_file) and os.path.getsize(recording_file) > 0:
                            print(f"🎤 Processing recorded audio...")
                            transcription = transcribe_audio(recording_file)
                            
                            if transcription:
                                #print(f"✅ Transcription successful: '{transcription}'")
                                prompt = normalize_prompt(transcription)
                                
                                if prompt:
                                    try:
                                        # Copy to clipboard using wl-copy (Wayland)
                                        subprocess.run(
                                            ["wl-copy"],
                                            input=prompt.encode("utf-8"),
                                            check=True
                                        )
                                        print(f"📋 Copied to clipboard: {transcription}")
                                        
                                    except Exception as e:
                                        print(f"🖶️  Clipboard error: {e}")
                            else:
                                print("❌ No transcription produced")
                        else:
                            print("⚠️  No audio recorded")
                        
                        # Clean up for next recording
                        recording_process = None
                    else:
                        # Small sleep to prevent CPU overload when not listening
                        time.sleep(0.1)
                        
            except KeyboardInterrupt:
                print("\nShutting down daemon...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

    # Cleanup
    if recording_process and recording_process.poll() is None:
        recording_process.terminate()
        recording_process.wait()

if __name__ == "__main__":
    main()
