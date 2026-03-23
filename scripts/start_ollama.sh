#!/bin/bash
# Linux Ignition Switch for Ollama

echo "=========================================="
echo "Starting Ollama (Linux Mode)..."
echo "=========================================="

# Check if Ollama is already running on the standard port
if lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null ; then
    echo "[System] Ollama is already running on port 11434!"
    exit 0
fi

# Attempt to start the service
echo "Starting Ollama service..."
ollama serve & 

# Wait a moment for it to wake up
sleep 2

if lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ Ollama is now active."
else
    echo "✗ ERROR: Ollama failed to start."
    echo "Install via: curl -fsSL https://ollama.com/install.sh | sh"
fi