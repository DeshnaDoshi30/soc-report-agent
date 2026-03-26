# 🛡️ SOC Report Agent - User Guide (v2026)

## 1. Overview
The SOC Report Agent is a Tier 3 forensic suite designed to transform raw security logs (CSV) or manual notes (JSON/TXT) into professional, narrative-driven reports. Utilizing a **Multi-Agent RAG Pipeline**, it fuses current forensic facts with historical company expertise to produce executive-level intelligence.

### High-Performance Features:
* **Semantic RAG Memory**: Automatically retrieves and cites historical company reports from a local **ChromaDB** vault.
* **JSON-Native Truth Block**: Uses a structured forensic anchor to ensure 100% data integrity between logs and reports.
* **Deep Reasoning**: Powered by **DeepSeek-R1**, providing "Chain-of-Thought" analysis of security risks.
* **Hallucination Auditor**: A JSON-verified validator that cross-references AI narratives against original forensic indicators.

---

## 2. Quick Start (Ubuntu GPU Server)

### Phase 1: Initialize the "Brain"
Before running investigations, you must index your company's historical expertise:
1. Open a terminal in the project root.
2. Run: `python3 src/ingest_knowledge.py`

### Phase 2: The Investigation
**Path A: The Standard Workflow (CSV)** Use this for automated log analysis (Wazuh, SonicWall, etc.).
1. Run: `./scripts/report.sh logs.csv --insight "Suspected unauthorized lateral movement."`

**Path B: The Expert Re-Run (JSON)** Use this to re-generate a report from an existing forensic truth block.
1. Run: `./scripts/report.sh data/output/incident_[ID].json`

---

## 3. The Forensic Vault (Output)
To ensure forensic integrity, the system saves three synchronized files in `data/output/` for every run, linked by a unique **Run ID** (YYYYMMDD_HHMMSS):

1.  **`incident_[ID].json`**: The **Semantic Truth Block**. This is the authoritative forensic anchor.
2.  **`incident_report_[ID].md`**: The final **Tier 3 Narrative Report** containing RAG-enriched context.
3.  **`validation_[ID].txt`**: The **Accuracy Audit** identifying any data inconsistencies or fabrications.

---

## 4. Command Reference

| Command | Purpose |
| :--- | :--- |
| `./scripts/report.sh <file>` | Main entry point for investigations. |
| `--insight "text"` | **Critical**: Imparts your expert conclusions as the primary truth. |
| `./scripts/start_ollama.sh` | Ignites the service with **4x 8GB GPU** load balancing. |
| `./scripts/pull_model.sh --setup-all` | Downloads the full Qwen, Nomic, and DeepSeek stack. |
| `python3 scripts/verify_setup.py` | Runs a full diagnostic of GPUs, models, and RAG health. |

---

## 5. Domain & Reasoning Support
The Agent leverages **DeepSeek-R1** to reason across complex security domains:

* **Network Forensics**: Analyzes volume, protocols, and geo-indicators to identify intent.
* **Infrastructure (FIM)**: Evaluates the risk of world-writable (777) paths in the context of your specific app stack.
* **Compliance (RAG)**: Automatically maps findings to **ISO 27001** or **PCI DSS** standards if found in your historical database.

---

## 6. Hardware Optimization
The system is built to scale across different environments:

* **Pro GPU Mode (Default)**: Uses 32GB VRAM and a **32,768 context window** for deep, multi-log analysis.
* **Laptop Mode (Fallback)**: Automatically switches to **Qwen-3B** and a **4,096 context window** if set in the `.env` file to protect 8GB RAM machines.

---

## 7. Troubleshooting
* **VRAM Spills**: If the system slows down on the server, run `nvidia-smi` to ensure all 4 GPUs are visible and not shared with other processes.
* **Knowledge Gaps**: If the report lacks company "voice," ensure you have run the `ingest_knowledge.py` script recently.
* **Audit Alerts**: If `validation_[ID].txt` flags "CRITICAL" issues, the AI has likely hallucinated an IP or a security claim not present in the original logs.
