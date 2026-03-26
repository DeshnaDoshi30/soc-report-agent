#!/bin/bash
# 🚀 SOC Agent - Linux Ignition Switch (Multi-GPU Optimized)

echo "=========================================="
echo "🛡️ Starting Ollama: 4x 8GB GPU Mode"
echo "=========================================="

# 1. GPU PRE-FLIGHT CHECK
# Ensures the NVIDIA drivers and all 4 GPUs are visible to the OS
if command -v nvidia-smi &> /dev/null; then
    GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
    echo "[System] Detected $GPU_COUNT NVIDIA GPU(s)."
    if [ "$GPU_COUNT" -lt 4 ]; then
        echo "⚠️ [Warning] Expected 4 GPUs, found $GPU_COUNT. Performance may vary."
    fi
else
    echo "⚠️ [Warning] nvidia-smi not found. Ensure drivers are installed for GPU acceleration."
fi

# 2. MULTI-GPU ENVIRONMENT VARIABLES
# OLLAMA_MAX_LOADED_MODELS: Keeps our 3 models (Qwen, Nomic, DeepSeek) in VRAM simultaneously.
# OLLAMA_NUM_PARALLEL: Allows parallel processing across your 4 GPUs.
# OLLAMA_FLASH_ATTENTION: Boosts speed and reduces VRAM usage for the 32B model.
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_FLASH_ATTENTION=1
export CUDA_VISIBLE_DEVICES=0,1,2,3

# 3. PORT CHECK
if lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null ; then
    echo "[System] Ollama is already active on port 11434!"
    exit 0
fi

# 4. START SERVICE
echo "[System] Igniting Ollama service with Multi-GPU Scheduler..."
ollama serve > ../data/ollama_server.log 2>&1 & 

# Wait for initialization
sleep 3

if lsof -Pi :11434 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Ollama is now active on all 4 GPUs."
    echo "[Log] Monitoring output saved to data/ollama_server.log"
else
    echo "❌ ERROR: Ollama failed to ignite."
    echo "   Check logs at: data/ollama_server.log"
fi