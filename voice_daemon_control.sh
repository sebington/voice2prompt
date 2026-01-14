#!/bin/bash
# Voice Daemon Control Script
# Toggles the voice prompt daemon listening state or starts it if not running

DAEMON_PID=$(pgrep -f voice_daemon_local.py)

if [ -z "$DAEMON_PID" ]; then
    echo "Voice daemon not running. Starting..."
    # Check if we're in the voice-to-cli directory
    if [ -f "voice_daemon_local.py" ]; then
        uv run voice_daemon_local.py &
    else
        echo "Error: voice_daemon_local.py not found in current directory"
        exit 1
    fi
else
    echo "Toggling daemon listening state..."
    kill -SIGUSR1 $DAEMON_PID
fi