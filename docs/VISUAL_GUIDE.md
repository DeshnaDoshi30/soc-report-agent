# 🛡️ SOC Report Agent - Visual Guide (v2026)

## 1. The Big Picture (Logic Flow v2026)
The system functions as a "Sequential Thinking Vault," using historical experience to inform a three-act forensic narrative.

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   ANALYST INPUTS                                    ┃
┃   ├─ CSV (Raw Wazuh/SonicWall Logs)                 ┃
┃   └─ --insight "Expert Conclusion" (Authority 1)    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━┛
                                │
                                ↓
                    ┌────────────────────────┐
                    │       pipeline.py      │
                    │   (The Master Router)  │
                    │    Generates RUN ID    │
                    └────────┬───────────────┘
                             │
            ┌────────────────┴────────────────┐
            ↓                                 ↓
  ┌──────────────────┐               ┌──────────────────┐
  │ PHASE 1: SENSE   │               │ PHASE 2: REMEMBER│
  │(Semantic Extract)│               │ (RAG Retrieval)  │
  └────────┬─────────┘               └────────┬─────────┘
           │                                  │
           ↓                                  ↓
  ┌────────────────────┐             ┌────────────────────┐
  │ semantic_extractor │             │   knowledge_base   │
  │   (Qwen 2.5 7B)    │             │ (ChromaDB Vector)  │
  └────────┬───────────┘             └────────┬───────────┘
           │                                  │
           ↓                                  ↓
  ┌────────────────────┐             ┌────────────────────┐
  │  THE TRUTH BLOCK   │             │   EXPERT CONTEXT   │
  │ (truth_block_[ID]) │             │ (Past 30+ Reports) │
  └────────┬───────────┘             └────────┬───────────┘
           │                                  │
           └──────────┬──────────────────────┘
                      ↓
           ┌────────────────────────┐
           │ PHASE 3: REASON & WRITE│
           │ (DeepSeek-R1 14B)      │
           │ Phased Acts: A, B, C   │
           └──────────┬─────────────┘
                      │
                      ↓
           ┌────────────────────────┐
           │ PHASE 4: EXPORT & VAULT│
           │  (SOCDocxExporter)     │
           │ iSecurify Blue Styling │
           └──────────┬─────────────┘
                      │
                      ↓
           ┏━━━━━━━━━━━━━━━━━━━━━━━━┓
           ┃     FORENSIC VAULT     ┃
           ┃  (data/output/[ID]/)   ┃
           ┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 2. The Upgrade: Phased Reasoning vs. Regex
Your architecture replaces "Single-Shot" generation with "Phased Narrative Construction" to protect your 8GB cards.

| Feature | Old (8GB Laptop) | New (3x 1070 GPU Server) |
| :--- | :--- | :--- |
| **Extraction** | Regex (Keyword matching) | **Semantic** (LLM understands forensic intent) |
| **Memory** | None (Vacuum state) | **RAG** (Remembers 30+ past incidents) |
| **Reasoning** | 3B Coder (Short answers) | **DeepSeek-R1 14B** (Chain-of-Thought) |
| **Integrity** | Flat Text Truth Block | **JSON-Native Truth Block** |
| **Context** | 4,096 Tokens | **8,192 Tokens (NUM_CTX)** |
| **Output** | 1-Page Summary | **5-Page Narrative (.docx)** |

---

## 3. The "Forensic Vault" Output
To ensure forensic integrity, the system saves four synchronized files in `data/output/`. These represent your complete "Chain of Custody".

* **`truth_block_[ID].json`**: The **Truth Block**. A structured data anchor containing every IP, path, and validated finding.
* **`SOC_Report_[ID].docx`**: The **Client-Ready Report**. A professional Word document with iSecurify branding and a dedicated cover page.
* **`incident_report_[ID].md`**: The **Narrative Script**. The raw phased output from the DeepSeek-R1 reasoning engine.
* **`validation_[ID].txt`**: The **Auditor's Log**. A line-by-line verification proving the AI adhered to the JSON facts.

---

## 4. Multi-GPU Distribution (10-Series Optimization)
The agent automatically spreads the workload across your **3x 8GB NVIDIA GPUs** using sequential VRAM flushing.

* **Layer Splitting**: Ollama distributes the **DeepSeek-R1 14B** weights across all three cards to maintain stability.
* **Sequential Flushing**: Setting `KEEP_ALIVE=0` ensures that the **Qwen-7B** is cleared before the **DeepSeek-14B** loads, preventing OOM crashes.
* **Act-Based Generation**: By generating the report in three parts (Executive, Forensic, Strategic), the system avoids bandwidth bottlenecks on the Pascal-series architecture.

---

## 5. Deployment Commands

```bash
# 1. ENABLE PERSISTENCE MODE
sudo nvidia-smi -pm 1

# 2. INITIALIZE THE BRAIN (RAG)
python3 src/ingest_knowledge.py

# 3. RUN INVESTIGATION
python3 pipeline.py logs.csv --insight "Unauthorized SSH login attempts on 111.90.173.220"

# 4. VIEW iSECURIFY REPORT
open data/output/SOC_Report_[ID].docx
```

---

## 6. Why this is Tier 3 Ready?
1.  **Experience**: It learns from your 30+ past reports via RAG to mirror your company's tone.
2.  **Integrity**: The JSON Truth Block serves as an immutable anchor to prevent data drift.
3.  **Professionalism**: Automated `.docx` formatting ensures every report matches the blue-accented iSecurify standards.
4.  **Hardware Efficiency**: Specifically architected to achieve 5-page depth on 1070 hardware through phased memory management.

