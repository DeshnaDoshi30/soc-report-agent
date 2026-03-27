#!/bin/bash

# 1. SMART PATHING
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit

echo "=========================================="
echo "🛡️ SOC AGENT: SEMANTIC RAG PIPELINE (v2026)"
echo "=========================================="

# 2. FLEXIBLE VENV ACTIVATION
# Checks for .venv, then venv, then skips if already active
if [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    source "venv/bin/activate"
elif [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ [System] Using already active environment: $VIRTUAL_ENV"
else
    echo "⚠️ [Warning] No virtual environment found. Running with system Python."
fi

# 3. GPU OPTIMIZATION
export CUDA_VISIBLE_DEVICES=0,1,2
export OLLAMA_MAX_LOADED_MODELS=1

# 4. EXECUTE PIPELINE
python3 -m src.pipeline "$@"

echo ""
echo "Investigation Complete."
echo "------------------------------------------"
echo "Vault Results Location: data/output/"
echo "------------------------------------------"