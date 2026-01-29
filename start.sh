#!/bin/bash
# Startup script for Voice Prompt Daemon

echo "Starting Voice Prompt Daemon..."

# Check if uv is installed
UV_PATH=$(which uv)
if [ -z "$UV_PATH" ]; then
    # try common location
    if [ -f "$HOME/.local/bin/uv" ]; then
        UV_PATH="$HOME/.local/bin/uv"
    else
        echo "Error: 'uv' not found. Please install it."
        exit 1
    fi
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ -n "$USER_PID" ]; then
        kill $USER_PID 2>/dev/null
    fi
    if [ -n "$ROOT_PID" ]; then
        sudo kill $ROOT_PID 2>/dev/null
    fi
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

# Get sudo access first (so password prompt is clean)
echo "Requesting sudo access for keyboard listener..."
sudo -v
if [ $? -ne 0 ]; then
    echo "Error: sudo access required"
    exit 1
fi

# 1. Start the User Component (Audio/UI) in background
echo "Starting Audio Service (User Mode)..."
$UV_PATH run voice_daemon_local.py &
USER_PID=$!

# Wait for it to initialize
sleep 2

# 2. Start the Root Component (Keyboard) - sudo is already cached
echo "Starting Keyboard Listener (Root Mode)..."
sudo $UV_PATH run key_listener.py &
ROOT_PID=$!

echo "Press Ctrl+C to stop"

# Wait for both processes (or until Ctrl+C)
wait $ROOT_PID $USER_PID 2>/dev/null

# If we get here naturally (process died), cleanup
cleanup
