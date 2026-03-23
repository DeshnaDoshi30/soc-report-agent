#!/bin/bash
# Linux Model Manager

if [ -z "$1" ]; then
    echo "Usage: ./pull_model.sh model_name"
    echo ""
    echo "Recommended for GPU Server:"
    echo "  ./pull_model.sh llama3:8b"
    echo "  ./pull_model.sh openchat"
    exit 1
fi

echo "=========================================="
echo "Pulling Intelligence: $1"
echo "=========================================="

ollama pull "$1"

if [ $? -eq 0 ]; then
    echo "✓ $1 is ready. Run investigation with: ./report.sh your_logs.csv --model $1"
else
    echo "✗ Error pulling $1"
fi