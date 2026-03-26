# 🚀 QUICKSTART - Semantic RAG & Forensic Vault

## 🏗️ Phase 1: One-Time "Brain" Initialization
Before your first investigation, you must build your local knowledge base from your 30+ historical reports.
1. `cd scripts`
2. `./pull_model.sh --setup-all` (Downloads Qwen, Nomic, and DeepSeek-R1)
3. `python3 ../src/ingest_knowledge.py` (Indexes your company expertise into ChromaDB)

## ⚡ Phase 2: The Investigation Loop
Follow this path for daily log analysis on your **4x 8GB GPU** stack.

### Path A: Raw Log Analysis (CSV)
1. `./start_ollama.sh` (Ignites the multi-GPU service)
2. `./report.sh logs.csv --insight "Analyst Note: Possible lateral movement to API backend."`

### Path B: Knowledge-Only Synthesis (TXT/JSON)
Ideal for re-running reports using existing forensic truth blocks.
1. `./report.sh incident_20260320_1527.json`

---

## 📂 The "Forensic Vault" Results
Every run creates a synchronized set of files linked by a unique **Run ID**. Your data is **never overwritten**:
* **`incident_[ID].json`**: The Semantic Truth Block (Verified Facts).
* **`incident_report_[ID].md`**: The Long-Form Narrative AI Report (DeepSeek-R1).
* **`validation_[ID].txt`**: The JSON-Native Hallucination Audit.

---

## 🛠️ Expert Power Features
* **Semantic Memory**: The agent automatically searches your past reports to match your company's professional tone.
* **Human-in-the-Loop**: Use the `--insight` flag to ensure your expert conclusions override machine logic.
* **GPU Orchestration**: The system automatically distributes the **32B model** across your 4 GPUs for maximum reasoning speed.
* **Diagnostic Check**: If something feels off, run `python3 scripts/verify_setup.py`.

