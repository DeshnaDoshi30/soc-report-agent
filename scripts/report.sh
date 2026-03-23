#!/bin/bash
# Universal Entry Point - Forensic Vault Edition (Linux/Ubuntu)
# Usage: ./report.sh input_file [--insight "Your findings"] [--model model_name]

# 1. Usage Check
if [ -z "$1" ]; then
    echo "Usage: ./report.sh input_file [--insight \"Text\"] [--model name]"
    exit 1
fi

# 2. File Existence Check
if [ ! -f "$1" ]; then
    echo "Error: File not found: \"$1\""
    exit 1
fi

echo ""
echo "=========================================="
echo "SOC AGENT: FORENSIC PIPELINE (v2026)"
echo "=========================================="
echo ""

# 3. AUTOMATIC VENV ACTIVATION
# Note: Linux uses bin/activate instead of Scripts/activate.bat
if [ -f "../.venv/bin/activate" ]; then
    echo "[System] Activating Linux Virtual Environment..."
    source "../.venv/bin/activate"
else
    echo "[Warning] Virtual environment (.venv) not found. Using system Python3."
fi

# 4. Execute Pipeline
# "$@" passes all arguments exactly as you typed them (like %* in Windows)
python3 "../src/pipeline.py" "$@"

echo ""
echo "Pipeline Complete."
echo "------------------------------------------"
echo "Check \"data/output/\" for synchronized Run ID files."
echo "------------------------------------------"
echo ""

# 5. Pause equivalent in Linux
read -p "Press [Enter] to continue..."