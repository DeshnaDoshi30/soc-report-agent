#!/bin/bash

# 1. SMART PATHING: Find the project root relative to this script
# This finds the directory where 'report.sh' lives, then goes up one level
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 2. MOVE TO ROOT: Everything happens from the project home
cd "$PROJECT_ROOT" || exit

echo "=========================================="
echo "🛡️ SOC AGENT: SEMANTIC RAG PIPELINE (v2026)"
echo "=========================================="

# 3. CHECK FOR KNOWLEDGE BASE (Vector DB)
if [ ! -d "data/vector_db" ]; then
    echo "⚠️ [Warning] Knowledge Base (RAG) not found in data/vector_db"
    echo "   Continuing with basic extraction only..."
fi

# 4. ACTIVATE VIRTUAL ENVIRONMENT
if [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
else
    echo "❌ [Error] .venv not found in $PROJECT_ROOT"
    exit 1
fi

# 5. GPU OPTIMIZATION (Use your 3 GPUs)
export CUDA_VISIBLE_DEVICES=0,1,2
export OLLAMA_MAX_LOADED_MODELS=1

# 6. EXECUTE MASTER PIPELINE
# We use -m src.pipeline to solve the "No module named src" error forever
python3 -m src.pipeline "$@"

echo ""
echo "Investigation Complete."
echo "------------------------------------------"
echo "Vault Results Location: data/output/"
echo "------------------------------------------"