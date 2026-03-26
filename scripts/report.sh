#!/bin/bash
# Universal Entry Point - Forensic Vault Edition (Linux/Ubuntu)
# Refactored for Semantic RAG Pipeline (v2026)
# Usage: ./report.sh input_file [--insight "Your findings"]

# 1. Usage Check
if [ -z "$1" ]; then
    echo "Usage: ./report.sh input_file [--insight \"Text\"]"
    exit 1
fi

# 2. File Existence Check
if [ ! -f "$1" ]; then
    echo "Error: Forensic source not found: \"$1\""
    exit 1
fi

echo ""
echo "=========================================="
echo "🛡️ SOC AGENT: SEMANTIC RAG PIPELINE (v2026)"
echo "=========================================="
echo ""

# 3. PRE-FLIGHT CHECKS (GPU AGNOSTIC)

# Check for Knowledge Base (RAG)
# If the vector_db folder is missing, the agent will have no 'memory'
if [ ! -d "../data/vector_db" ]; then
    echo "⚠️ [Warning] Knowledge Base (RAG) not found in vault."
    echo "   Please run: python3 ../src/ingest_knowledge.py"
    echo "   Continuing with basic extraction only..."
    echo ""
fi

# Check if Ollama is reachable
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ [Error] Ollama is not running."
    echo "   Please run: ./scripts/start_ollama.sh"
    exit 1
fi

# 4. AUTOMATIC VENV ACTIVATION
if [ -f "../.venv/bin/activate" ]; then
    echo "[System] Activating Linux Virtual Environment..."
    source "../.venv/bin/activate"
else
    echo "[Warning] .venv not found. Ensure dependencies are installed."
fi

# 5. EXECUTE PIPELINE
# Passes all arguments directly to the Master Orchestrator
python3 "../src/pipeline.py" "$@"

echo ""
echo "Investigation Complete."
echo "------------------------------------------"
echo "Vault Results Location: data/output/"
echo "Sync ID: (Check logs above for Run ID)"
echo "------------------------------------------"
echo ""

# 6. Pause equivalent in Linux
read -p "Press [Enter] to return to terminal..."