# 🛡️ SOC Agent v2026: Pro GPU & RAG Startup Guide

## 1. High-Performance Start (Ubuntu Server)

### Step 1: Ignite the GPU Stack
This command optimizes Ollama for your **4x 8GB GPU** environment, ensuring the 32B model is distributed correctly:
```bash
./scripts/start_ollama.sh
```
* **What it does**: Sets VRAM residency for 3 models and enables **Flash Attention** for 32k context reasoning.

### Step 2: Build the Brain (RAG Ingestion)
If you've updated your historical reports or it's your first time on the server:
```bash
python3 src/ingest_knowledge.py
```
* **What it does**: Indexes your 30+ company reports into the local **ChromaDB** vector vault.

### Step 3: Run the Multi-Agent Pipeline
```bash
./scripts/report.sh logs.csv --insight "Suspected unauthorized lateral movement."
```
* **What it does**: Triggers the **Semantic Extractor** (Qwen 7B) → **Librarian** (RAG) → **Lead Investigator** (DeepSeek-R1).

---

## 2. Advanced "Forensic Vault" Features

### Dual-Input Detection
The pipeline automatically senses your input type:
* **CSV Input**: Triggers full log cleaning and semantic JSON extraction.
* **Direct File (`.json` / `.txt`)**: Treats the file as a pre-verified "Truth Block" and moves straight to RAG enrichment and reporting.

### Semantic Memory (RAG)
Unlike the 8GB version, the Pro version fetches **Expert Context**. The final report will automatically cite historical remediation steps or MITRE techniques found in your database.

---

## 3. Hardware & VRAM Stats

| Metric | Pro GPU Mode | Laptop Mode (Fallback) |
| :--- | :--- | :--- |
| **Primary Model** | DeepSeek-R1 (32B) | Qwen 2.5 Coder (3B) |
| **Reasoning** | Chain-of-Thought (`<think>`) | Standard Inference |
| **VRAM Usage** | ~28GB (Distributed) | ~2.5GB |
| **Context Window** | **32,768 Tokens** | 4,096 Tokens |
| **Intelligence** | Semantic RAG + JSON Truth | Regex + Text Truth |

---

## 4. Pro Troubleshooting

### "RAG Context Missing"
* **Problem**: The report doesn't mention any past company incidents.
* **Solution**: Ensure `data/vector_db/` exists. Re-run `ingest_knowledge.py`.

### "OOM / Slow Inference"
* **Problem**: DeepSeek-R1 is taking 10+ minutes.
* **Solution**: Run `nvidia-smi` to ensure all 4 GPUs are visible. Check if `OLLAMA_NUM_PARALLEL` is set in `start_ollama.sh`.