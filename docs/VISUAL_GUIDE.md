## 1. The Big Picture (Logic Flow v2026)
The system now functions as a "Thinking Vault," using historical experience to inform current investigations.

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   ANALYST INPUTS                                    ┃
┃   ├─ CSV (Raw Wazuh/SonicWall Logs)                 ┃
┃   └─ --insight "Expert Conclusion" (Authority 1)    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━┛
                                │
                                ↓
                    ┌────────────────────────┐
                    │      pipeline.py       │
                    │  (The Master Router)   │
                    │   Generates RUN ID     │
                    └────────┬───────────────┘
                             │
            ┌────────────────┴────────────────┐
            ↓                                 ↓
  ┌──────────────────┐              ┌──────────────────┐
  │ PHASE 1: SENSE   │              │ PHASE 2: REMEMBER│
  │(Semantic Extract)│              │ (RAG Retrieval)  │
  └────────┬─────────┘              └────────┬─────────┘
           │                                 │
           ↓                                 ↓
  ┌────────────────────┐            ┌────────────────────┐
  │ semantic_extractor │            │   knowledge_base   │
  │   (Qwen 2.5 7B)    │            │ (ChromaDB Vector)  │
  └────────┬───────────┘            └────────┬───────────┘
           │                                 │
           ↓                                 ↓
  ┌────────────────────┐            ┌────────────────────┐
  │  THE TRUTH BLOCK   │            │  EXPERT CONTEXT    │
  │  (incident_[ID].json)           │  (Past 30+ Reports)│
  └────────┬───────────┘            └────────┬───────────┘
           │                                 │
           └──────────┬──────────────────────┘
                      ↓
           ┌────────────────────────┐
           │ PHASE 3: REASON & WRITE│
           │  (DeepSeek-R1 32B)     │
           │   32k Context Window   │
           └──────────┬─────────────┘
                      │
                      ↓
           ┌────────────────────────┐
           │ PHASE 4: AUDIT & VAULT │
           │  (report_validator)    │
           │   JSON-Native Check    │
           └──────────┬─────────────┘
                      │
                      ↓
           ┏━━━━━━━━━━━━━━━━━━━━━━━━┓
           ┃     FORENSIC VAULT     ┃
           ┃  (data/output/[ID]/)   ┃
           ┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 2. The Upgrade: Semantic vs. Regex
Your 2026 architecture replaces "Guessing" with "Reasoning."

| Feature | Old (8GB Laptop) | New (32GB GPU Server) |
| :--- | :--- | :--- |
| **Extraction** | Regex (Keyword matching) | **Semantic** (LLM understands context) |
| **Memory** | None (Vacuum state) | **RAG** (Remembers 30+ past incidents) |
| **Reasoning** | 3B Coder (Short answers) | **DeepSeek-R1 32B** (Chain-of-Thought) |
| **Integrity** | Flat Text Truth Block | **JSON-Native Truth Block** |
| **Context** | 4,096 Tokens | **32,768 Tokens** |

---

## 3. The "Forensic Vault" Output
To ensure forensic integrity, the system saves three synchronized files in `data/output/`. These are your "Chain of Custody."

* **`incident_[ID].json`**: The **Truth Block**. A structured data anchor containing every IP, path, and human note.
* **`incident_report_[ID].md`**: The **Narrative Report**. A professional, Tier 3 document that sounds like your senior team wrote it.
* **`validation_[ID].txt`**: The **Auditor's Log**. A line-by-line verification proving the AI stayed within the facts.

---

## 4. Multi-GPU Distribution (Ubuntu Optimization)
The agent automatically spreads the workload across your **4x 8GB NVIDIA GPUs**.

* **GPU 1**: Runs the **Semantic Extractor** (Qwen 7B) and the **Embedding Model** (Nomic).
* **GPU 2-4**: Collaboratively run the **DeepSeek-R1 32B** model, splitting its 64 layers to fit within the combined VRAM.
* **Memory Residency**: All models stay loaded in VRAM, eliminating "startup lag" between the extraction and reporting phases.

---

## 5. Deployment Commands

```bash
# 1. IGNITE THE STACK
./scripts/start_ollama.sh

# 2. INITIALIZE THE BRAIN (RAG)
python3 src/ingest_knowledge.py

# 3. RUN INVESTIGATION
./scripts/report.sh logs.csv --insight "Suspected unauthorized lateral movement."

# 4. RUN DIAGNOSTICS
python3 scripts/verify_setup.py
```

---

## 6. Why this is Tier 3 Ready?
1.  **Experience**: It learns from your 30+ past reports via RAG.
2.  **Integrity**: The JSON Truth Block prevents data drift.
3.  **Reasoning**: DeepSeek-R1 provides the "Thinking" process behind every conclusion.
4.  **Hardware Aware**: It is specifically architected for your Ubuntu GPU cluster.
