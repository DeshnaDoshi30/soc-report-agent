# 🛡️ SOC Report Agent - User Guide (v2026)

## 1. Overview
The SOC Report Agent is a Tier 3 forensic suite designed to transform raw security logs (CSV) or manual notes (JSON/TXT) into professional, narrative-driven reports. Utilizing a **Phased Multi-Agent RAG Pipeline**, it fuses current forensic facts with historical company expertise to produce executive-level intelligence.

### High-Performance Features:
* **Sequential Actuation**: Generates reports in three distinct acts (A, B, C) to bypass VRAM bottlenecks on 8GB cards.
* **iSecurify Word Export**: Automatically generates corporate-branded `.docx` files with blue-accented headings and professional cover pages.
* **Semantic RAG Memory**: Retrieves and cites historical company reports from a local **ChromaDB** vault using **Nomic Embed**.
* **JSON-Native Truth Block**: Uses a structured forensic anchor to ensure 100% data integrity between logs and reports.

---

## 2. Quick Start (3x GTX 1070 Ubuntu Server)

### Phase 1: Initialize the "Brain"
Before running investigations, index your company's historical expertise:
1.  Open a terminal in the project root.
2.  Run: `python3 src/ingest_knowledge.py`

### Phase 2: The Investigation
**Path A: The Standard Workflow (CSV)** Use this for automated log analysis (Wazuh, SonicWall, etc.).
1.  Run: `python3 pipeline.py logs.csv --insight "Unauthorized SSH attempts on 111.90.173.220"`

**Path B: The Expert Re-Run (JSON)** Use this to re-generate a report from an existing forensic truth block.
1.  Run: `python3 pipeline.py data/output/truth_block_[ID].json`

---

## 3. The Forensic Vault (Output)
To ensure forensic integrity, the system saves four synchronized files in `data/output/` for every run, linked by a unique **Run ID** (YYYYMMDD_HHMMSS):

1.  **`truth_block_[ID].json`**: The **Semantic Truth Block**. This is the authoritative forensic anchor.
2.  **`SOC_Report_[ID].docx`**: The final **Professional Word Document** formatted with iSecurify corporate branding.
3.  **`incident_report_[ID].md`**: The raw **Markdown Narrative** containing RAG-enriched context.
4.  **`validation_[ID].txt`**: The **Accuracy Audit** identifying any data inconsistencies or fabrications.

---

## 4. Command Reference

| Command | Purpose |
| :--- | :--- |
| `python3 pipeline.py <file>` | Main entry point for investigations. |
| `--insight "text"` | **Critical**: Imparts your expert conclusions as the primary truth. |
| `ollama pull deepseek-r1:14b` | Downloads the specialized 14B reasoning model for Pascal GPUs. |
| `nvidia-smi` | Monitors VRAM distribution across your **3x 1070s**. |
| `sudo nvidia-smi -pm 1` | Enables **Persistence Mode** to prevent GPUs from "falling off the bus". |

---

## 5. Domain & Reasoning Support
The Agent leverages **DeepSeek-R1-14B** to reason across complex security domains:

* **Network Forensics**: Analyzes volume, protocols, and geo-indicators to identify intent.
* **Infrastructure (FIM)**: Evaluates the risk of world-writable (777) paths in the context of your specific app stack.
* **Strategic Resolution**: Automatically provides hardening recommendations (NIST/CIS) found in your historical database.

---

## 6. Hardware Optimization (24GB VRAM)
The system is built to scale specifically for the **3x GTX 1070** environment:

* **Phased Generation Mode**: Uses 24GB total VRAM and a **sequential flushing logic** (`KEEP_ALIVE=0`) to protect card stability.
* **Context Slicing**: Trims the JSON truth block for each phase to maximize model focus and inference speed.
* **Multi-GPU Splitting**: Automatically distributes the 14B model weights across all three 8GB cards.

---

## 7. Troubleshooting
* **"Device Handle" Errors**: If a GPU shows an "Unknown Error," reseat the card and ensure it has a **dedicated power cable** from the PSU.
* **Knowledge Gaps**: If the report lacks company "voice," ensure you have run the `ingest_knowledge.py` script recently to update the **ChromaDB** vault.
* **Stale VRAM**: If generation slows down, ensure no other background processes are using the 1070s. Use `nvidia-smi` to confirm idle status (**2MiB/8192MiB**) before starting.