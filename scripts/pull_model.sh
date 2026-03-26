#!/bin/bash
# 🛡️ SOC Agent - Linux Model Manager (GPU Optimized)
# Usage: ./pull_model.sh [model_name | --setup-all]

# 1. Setup All Models for the RAG Pipeline
if [ "$1" == "--setup-all" ]; then
    echo "=========================================="
    echo "🚀 INITIALIZING FULL SEMANTIC GPU STACK"
    echo "=========================================="
    
    echo "[1/3] Pulling Extractor: qwen2.5:7b (GPU 1)..."
    ollama pull qwen2.5:7b
    
    echo "[2/3] Pulling Embedder: nomic-embed-text (GPU 1/2)..."
    ollama pull nomic-embed-text
    
    echo "[3/3] Pulling Reporter: deepseek-r1:32b (GPU 3/4)..."
    ollama pull deepseek-r1:32b
    
    echo ""
    echo "✓ GPU Stack Ready. Next Step: python3 ../src/ingest_knowledge.py"
    exit 0
fi

# 2. Usage Check for individual models
if [ -z "$1" ]; then
    echo "Usage: ./pull_model.sh [model_name | --setup-all]"
    echo ""
    echo "Recommended for GPU Server Architecture:"
    echo "  --setup-all             Pulls all three required models"
    echo "  qwen2.5:7b              (Semantic Extraction)"
    echo "  nomic-embed-text        (RAG Knowledge Base)"
    echo "  deepseek-r1:32b         (Lead Investigator Report)"
    exit 1
fi

echo "=========================================="
echo "Pulling Intelligence: $1"
echo "=========================================="

ollama pull "$1"

if [ $? -eq 0 ]; then
    echo "✓ $1 is ready. Run investigation with: ./report.sh your_logs.csv"
else
    echo "❌ Error pulling $1. Ensure Ollama is running."
fi