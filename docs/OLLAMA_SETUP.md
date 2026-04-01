# 🛡️ SOC Agent v2026: 3x GTX 1070 & RAG Startup Guide

## 1. High-Performance Start (Ubuntu Server)

### Step 1: Ignite the GPU Stack
This command optimizes Ollama for your **3x 8GB Pascal** environment. Since 10-series cards do not natively support Flash Attention 2, we focus on layer splitting and sequential VRAM management:
```bash
# Set OLLAMA_KEEP_ALIVE=0 to ensure sequential VRAM flushing between acts
# Layer splitting is handled automatically across your 3x 1070s
export OLLAMA_KEEP_ALIVE=0
ollama serve
```
* **What it does**: Clears the VRAM immediately after each phase (A, B, or C) to prevent memory fragmentation on your 8GB cards.

### Step 2: Build the Brain (RAG Ingestion)
```bash
python3 src/ingest_knowledge.py
```
* **What it does**: Indexes your forensic reports into **ChromaDB**. This uses the **Nomic Embed** model, which fits easily (<1GB) on any of your three GPUs.

### Step 3: Run the Multi-Agent Pipeline
```bash
python3 pipeline.py logs.csv --insight "Unauthorized SSH attempts on 111.90.173.220"
```
* **What it does**: Triggers the **Semantic Extractor** (Qwen 7B) → **Librarian** (RAG) → **Lead Investigator** (DeepSeek-R1-14B) in a sequential loop to maximize your 24GB total VRAM.

---

## 2. Advanced "Forensic Vault" Features

### Sequential Actuation
Unlike single-GPU setups, your pipeline runs in **Phases (Acts A, B, C)**. This allows the **DeepSeek-14B** model to utilize the full bandwidth of all three cards for reasoning without hitting the OOM (Out-of-Memory) wall that occurs when trying to process 5 pages of text at once.

### Institutional Memory (RAG)
The agent fetches **Expert Context** from your past investigations. The final **SOC_Report.docx** will automatically include iSecurify-branded remediation steps based on your local database.

---

## 3. Hardware & VRAM Stats (3x 1070 Optimized)

| Metric | 1070-Optimized Mode (Current) | Laptop Mode (Fallback) |
| :--- | :--- | :--- |
| **Primary Model** | **DeepSeek-R1 (14B)** | Qwen 2.5 Coder (3B) |
| **VRAM Usage** | ~12GB - 14GB (Phased) | ~2.5GB |
| **Context Window** | **8,192 Tokens (NUM_CTX)** | 4,096 Tokens |
| **Architecture** | **3x 8GB GPU Splitting**| Single GPU / CPU |
| **Output Target** | **5-Page Narrative (Phased)** | 1-Page Summary |

---

## 4. Pro Troubleshooting

### "GPU Fallen Off the Bus" (Unknown Error)
* **Problem**: `nvidia-smi` shows an "Unknown Error" or unable to determine handle for a card.
* **Solution**: This is often a power spike or physical seating issue. **Reseat** the card and ensure each 1070 has a **dedicated power cable** (no pigtails). Enable persistence mode to keep the driver active: `sudo nvidia-smi -pm 1`.

### "Slow Inference on Act B"
* **Problem**: Act B (Forensic Deep-Dive) is slower than Act A.
* **Solution**: Act B is the most data-intensive act. Ensure `KEEP_ALIVE=0` is set so the VRAM is fully cleared of Act A's KV-cache before Act B begins.