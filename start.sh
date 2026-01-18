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

# 1. Start the User Component (Audio/UI) in background
echo "Starting Audio Service (User Mode)..."
$UV_PATH run voice_daemon_local.py &
USER_PID=$!

# Wait for it to initialize
sleep 2

# 2. Start the Root Component (Keyboard)
echo "Starting Keyboard Listener (Root Mode)..."
echo "Please enter sudo password if prompted:"
sudo $UV_PATH run key_listener.py

# Cleanup when key listener exits
echo "Shutting down..."
kill $USER_PID
