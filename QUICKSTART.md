# 🚀 QUICKSTART - Phased RAG & Forensic Vault

## 🏗️ Phase 1: One-Time "Brain" Initialization
Before your first investigation, you must build your local knowledge base from your 30+ historical reports.
1. `ollama pull deepseek-r1:14b` (Optimized reasoning model for 10-series GPUs).
2. `ollama pull qwen2.5:7b` (High-speed forensic extractor).
3. `python3 src/ingest_knowledge.py` (Indexes your company expertise into ChromaDB).

## ⚡ Phase 2: The Investigation Loop
Follow this path for daily log analysis on your **3x 8GB GPU** stack.

### Path A: Raw Log Analysis (CSV)
1. `export OLLAMA_KEEP_ALIVE=0` (Enables sequential VRAM flushing between acts).
2. `python3 pipeline.py logs.csv --insight "Unauthorized SSH login attempts on 111.90.173.220"`.

### Path B: Knowledge-Only Synthesis (JSON)
Ideal for re-running reports using existing forensic truth blocks.
1. `python3 pipeline.py data/output/truth_block_20260320_1527.json`.

---

## 📂 The "Forensic Vault" Results
Every run creates a synchronized set of files linked by a unique **Run ID**. Your data is **never overwritten**:
* **`SOC_Report_[ID].docx`**: The professional **iSecurify Word Document** with corporate branding.
* **`truth_block_[ID].json`**: The **Semantic Truth Block** (The immutable forensic anchor).
* **`incident_report_[ID].md`**: The Phased Narrative AI Report across **Acts A, B, and C**.
* **`validation_[ID].txt`**: The Forensic Accuracy Audit.

---

## 🛠️ Expert Power Features
* **Phased Generation**: The system writes the report in three acts to achieve **5-page depth** without hitting 10-series VRAM limits.
* **Semantic Memory**: The agent automatically searches your past reports to match iSecurify's professional tone.
* **Human-in-the-Loop**: Use the `--insight` flag to ensure your expert conclusions override machine logic.
* **GPU Orchestration**: The system automatically distributes the **14B model** across your 3 GPUs for maximum reasoning speed.
* **Diagnostic Check**: If something feels off, run `python3 scripts/verify_setup.py`.