# 🛡️ SOC Incident Report Agent - Semantic RAG Edition (v2026)

Generate professional, Tier 3 security incident reports using a **Multi-Agent RAG Pipeline**. This system is specifically engineered for **32GB VRAM (4x 8GB GPU)** environments, utilizing **DeepSeek-R1** for reasoning and **ChromaDB** for local company knowledge retrieval.

---

## 🚀 Key Features
* **Semantic RAG Memory**: Uses a local Vector Database to "remember" 30+ historical company reports, ensuring every new report matches your established professional tone and remediation standards.
* **DeepSeek-R1 Reasoning**: Leverages 32B parameter models to write expansive, narrative-driven paragraphs that synthesize complex log data into executive-level intelligence.
* **JSON Forensic Vault**: Every investigation is anchored by a structured **JSON Truth Block**. This ensures 100% data integrity between raw logs, RAG context, and the final report.
* **Multi-GPU Orchestration**: Optimized for Ubuntu servers to distribute model layers across 4 GPUs, keeping the Extractor, Embedder, and Reporter models resident in VRAM for high-speed execution.
* **Hallucination Auditor**: An upgraded forensic validator that cross-references AI narratives against the JSON Truth Block to catch fabricated IPs or security claims.

---

## 🛠️ Install & Setup (GPU Server)

### Requirements
- Python 3.9+
- Ollama AI Framework
- **32GB VRAM** (Optimized for 4x 8GB GPU setups)
- NVIDIA Drivers & CUDA Toolkit

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
   Ingest your historical reports and MITRE mapping into the local vector store:
   ```bash
   python3 src/ingest_knowledge.py
   ```

4. **Verify Deployment**:
   ```bash
   python3 scripts/verify_setup.py
   ```

---

## 📖 Usage

### 1. Ignite the GPU Stack
```bash
./scripts/start_ollama.sh
```

### 2. Run Forensic Pipeline
Pass raw CSV logs. Use the `--insight` flag to guide the AI with your Tier 3 expert conclusions.
```bash
./scripts/report.sh data/input/network_logs.csv --insight "Suspected unauthorized lateral movement targeting production DB."
```

---

## 📂 The Forensic Vault (JSON Synchronized)
All results are saved to `data/output/` and share a synchronized **Run ID**:
* **`cleaned_[ID].csv`**: Sanitized log evidence (Wazuh/SonicWall).
* **`incident_[ID].json`**: The **Semantic Truth Block** (Validated Machine Facts + Human Insight).
* **`incident_report_[ID].md`**: The expansive, Tier 3 narrative report.
* **`validation_[ID].txt`**: The forensic audit identifying any AI inconsistencies.

---

## 🏗️ Modular Architecture

### Logic Flow
```text
src/
 ├── pipeline.py (Master Orchestrator - Syncs Extraction, RAG, and Reporting)
 ├── config.py (Hardware Logic - Manages GPU VRAM & NUM_CTX settings)
 ├── ingest_knowledge.py (The Librarian - Builds the Vector Database)
 │
 ├── csv_to_incident.py (Phase 1: Semantic Extraction via Qwen-7B)
 │    └── semantic_extractor.py (Produces the JSON Truth Block)
 │
 ├── knowledge_base.py (Phase 2: RAG Retrieval - Fetches historical context)
 │
 └── report_generator.py (Phase 3: Synthesis via DeepSeek-R1 32B)
      └── report_validator.py (Phase 4: JSON-Native Fact Auditing)
```

---

## 🛠️ GPU Server Optimization

| Feature | Setting | Purpose |
| :--- | :--- | :--- |
| **VRAM Pool** | 32GB (4x 8GB) | Supports DeepSeek-R1 32B without system RAM spill. |
| **Context Window** | 32,768 (NUM_CTX) | Allows reading of long logs + multiple RAG documents. |
| **Load Balancing** | OLLAMA_NUM_PARALLEL | Distributes inference across all 4 available GPUs. |
| **Reasoning** | Flash Attention | Boosts throughput for long-form narrative generation. |

---

## ⚙️ Customization

| To Change... | Edit This File |
| :--- | :--- |
| **AI Tone/Persona** | `templates/prompt_template.txt` |
| **Report Layout** | `templates/report_format.txt` |
| **Company Knowledge** | Update `INCIDENT_REPORTS` in `src/ingest_knowledge.py` |
| **Model Selection** | `.env` (Change Extractor or Reporter models) |

---

## ⚠️ Troubleshooting

* **VRAM Spills**: If inference is slow, check `nvidia-smi`. Ensure no other heavy processes are using the 4 GPUs.
* **RAG Misses**: If the report lacks company context, ensure `data/vector_db/` is populated by running the ingestion script again.
* **Thinking Tags**: DeepSeek-R1 reports are post-processed to remove `<think>` blocks. If they appear in your MD file, check the parser in `report_generator.py`.
