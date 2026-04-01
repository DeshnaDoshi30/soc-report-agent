# 🛡️ SOC Incident Report Agent - Semantic RAG Edition (v2026)

Generate professional, Tier 3 security incident reports using a **Multi-Agent RAG Pipeline**. This system is specifically engineered for **32GB VRAM (4x 8GB GPU)** environments, utilizing **DeepSeek-R1** for reasoning and **ChromaDB** for local company knowledge retrieval.

---

## 🚀 Key Features
* **Semantic RAG Memory**: Uses a local Vector Database (`data/vector_db/`) to "remember" 30+ historical company reports, ensuring every new report matches your established professional tone and remediation standards.
* **DeepSeek-R1 Reasoning**: Leverages 32B parameter models to write expansive, narrative-driven paragraphs that synthesize complex log data into executive-level intelligence.
* **JSON Forensic Vault**: Every investigation is anchored by a structured **JSON Truth Block**. This ensures 100% data integrity between raw logs, RAG context, and the final report.
* **Multi-GPU Orchestration**: Optimized for Ubuntu servers to distribute model layers across 4 GPUs, keeping the Extractor, Embedder, and Reporter models resident in VRAM for high-speed execution.
* **Hallucination Auditor**: An upgraded forensic validator (`src/report_validator.py`) that cross-references AI narratives against the JSON Truth Block to catch fabricated IPs or security claims.

---

## 🛠️ Install & Setup (GPU Server)

### Requirements
* **OS**: Ubuntu 22.04+ (Recommended).
* **Hardware**: **32GB VRAM** (Optimized for 4x 8GB GPU setups).
* **Software**: Python 3.9+, Ollama AI Framework, NVIDIA Drivers & CUDA Toolkit.

### Installation Steps
1. **Prepare Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Models**:
   Run the automated pull script to download the **Qwen (7B)**, **Nomic (Embed)**, and **DeepSeek-R1 (32B)** stack:
   ```bash
   ./scripts/pull_model.sh --setup-all
   ```

3. **Initialize the Brain (RAG)**:
   Ingest your historical reports from `data/knowledge/` into the local vector store:
   ```bash
   python3 src/ingest_knowledge.py
   ```

4. **Verify Deployment**:
   ```bash
   python3 scripts/verify_setup.py
   ```

---

Here is the second part of your updated **README.md**, optimized for your **3x GTX 1070 (24GB VRAM)** infrastructure and synchronized with the folder structure shown in your images.

---

## 📖 Usage

### 1. Ignite the GPU Stack
```bash
./scripts/start_ollama.sh
```
* **What it does**: Initializes the multi-GPU service, splitting the **14B DeepSeek-R1** layers across your three cards.

### 2. Run Forensic Pipeline
Pass raw CSV logs from the `data/input/` directory. Use the `--insight` flag to guide the AI with your expert conclusions.
```bash
# Running from the project root
python3 src/pipeline.py data/input/network_logs.csv --insight "Unauthorized SSH login attempts on 111.90.173.220"
```

---

## 📂 The Forensic Vault (JSON Synchronized)
All results are saved to `data/output/` and share a synchronized **Run ID** to ensure a verifiable chain of custody:
* **`truth_block_[ID].json`**: The authoritative **Semantic Truth Block** (Validated facts).
* **`SOC_Report_[ID].docx`**: The professional **iSecurify Word Export** with corporate branding.
* **`incident_report_[ID].md`**: The expansive, Tier 3 narrative report script.
* **`validation_[ID].txt`**: The forensic audit identifying any AI inconsistencies.

---

## 🏗️ Modular Architecture

### Logic Flow & File Map
Based on the project structure in `src/`:
```text
src/
 ├── pipeline.py (Master Orchestrator - Syncs Extraction, RAG, and Reporting)
 ├── config.py (Hardware Logic - Manages 3-GPU VRAM & Phased Actuation)
 ├── ingest_knowledge.py (The Librarian - Builds the Vector Database)
 │
 ├── csv_to_incident.py (Phase 1: Workflow Management for CSV Evidence)
 │    └── semantic_extractor.py (Produces the JSON Truth Block via Qwen-7B)
 │
 ├── knowledge_base.py (Phase 2: RAG Retrieval - Fetches historical context)
 │
 ├── report_generator.py (Phase 3: Synthesis via DeepSeek-R1 14B)
 │    └── report_validator.py (Phase 4: JSON-Native Fact Auditing)
 │
 └── docx_exporter.py (Final Phase: Professional Word Document Generation)
```

---

## 🛠️ GPU Server Optimization (3x 1070 Environment)

| Feature | Setting | Purpose |
| :--- | :--- | :--- |
| **VRAM Pool** | **24GB (3x 8GB)** | Supports Phased 14B reasoning without system RAM spill. |
| **Context Window** | **8,192 (NUM_CTX)** | Optimized for deep RAG injection on Pascal-series hardware. |
| **VRAM Flush** | **KEEP_ALIVE=0** | Ensures sequential card clearing between Acts A, B, and C. |
| **Branding** | **iSecurify Blue** | Standardizes all exports to corporate Tier 3 styles. |

---

## ⚙️ Customization

| To Change... | Edit This File |
| :--- | :--- |
| **AI Tone/Persona** | `src/templates/global_header.txt` |
| **Expert Memory** | Add PDFs to `data/knowledge/` & run `ingest_knowledge.py` |
| **Model Selection** | `.env` (Change Extractor or Reporter models) |

---

## ⚠️ Troubleshooting

* **"Device Handle" Errors**: If a GPU disconnects, reseat the card and ensure dedicated power rails are used.
* **Hallucination Flags**: If `validation_[ID].txt` flags "CRITICAL" issues, the AI has diverged from the JSON Truth Block.
* **OOM (Out of Memory)**: Ensure no other processes are using the 1070s. Run `nvidia-smi` to confirm cards are idle before starting a run.