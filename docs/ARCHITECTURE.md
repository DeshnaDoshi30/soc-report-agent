# 🛡️ Architecture & Data Flow (v2026 - Semantic RAG Edition)

## 1. The Evolutionary Leap: From Keywords to Reasoning
The previous iteration relied on static regex signatures and limited context, often missing the "story" within the logs. The v2026 architecture introduces **Semantic Intelligence** and **Historical Experience**.
* **Beyond Regex**: Replaced rigid keyword matching with a **Semantic Extractor** (Qwen-7B) that understands intent.
* **Knowledge Retrieval (RAG)**: The agent no longer works in a vacuum. It queries a local **ChromaDB** "memory" of 30+ historical reports to match company style and remediation standards.
* **Deep Reasoning**: Utilizes **DeepSeek-R1 (32B)** to perform "Chain-of-Thought" analysis, providing the "Why" behind security risks rather than just the "What".

## 2. The Tier 3 Forensic Vault (JSON-Native)
We have upgraded the "Truth Block" from a flat text file to a structured **JSON Schema**. This ensures 100% data integrity throughout the multi-stage pipeline.
* **JSON Truth Block**: Acts as the immutable forensic anchor. Every IP, path, and permission is validated before the report is written.
* **Non-Repudiation**: Every run generates a unique **Run ID**, archiving the raw logs, the extracted JSON, and the final narrative in a synchronized vault.

---

## 3. Modular Orchestration (The Multi-Agent Stack)

| Module | Forensic Role | Intelligence Layer |
| :--- | :--- | :--- |
| **`semantic_extractor.py`** | **The Fact-Finder**: Turns raw logs into a structured JSON "Truth Block." | **Qwen 2.5 (7B)** |
| **`knowledge_base.py`** | **The Librarian**: Fetches relevant past incidents and MITRE techniques (RAG). | **Nomic Embed Text** |
| **`report_generator.py`** | **The Lead Investigator**: Synthesizes facts and experience into a narrative. | **DeepSeek-R1 (32B)** |
| **`report_validator.py`** | **The Internal Auditor**: Cross-references the narrative against the JSON Truth. | **Pydantic/Regex** |
| **`ingest_knowledge.py`** | **The Archivist**: Indexes historical company reports into ChromaDB. | **Vector Logic** |

---

## 4. Advanced Data Flow (The Intelligence Loop)

### Path: Raw Log to Executive Intelligence
```text
Raw Logs (CSV) + Human Insight (CLI)
      ↓
[processor.py] -> Normalizes Wazuh/SonicWall logs (Memory Optimized)
      ↓
[semantic_extractor.py] -> (GPU 1) Reasons through 'Full_Evidence' to produce JSON
      ↓
[incident_ID.json] -> THE TRUTH BLOCK (Immutable Facts)
      ↓
[knowledge_base.py] -> (GPU 1/2) Searches ChromaDB for "Similar Past Incidents"
      ↓
[report_generator.py] -> (GPU 3/4) Synthesis: DeepSeek-R1 (JSON + RAG + Prompt)
      ↓
[report_validator.py] -> Automated JSON-Native Audit (Fabrication Check)
      ↓
OUTPUT VAULT (data/output/)
├─ incident_20260320.json      (The Forensic Evidence)
├─ incident_report_20260320.md (The Tier 3 Narrative Report)
└─ validation_20260320.txt     (The Auditor's Verdict)
```

---

## 5. Hardware Optimization (32GB VRAM Architecture)
Designed for high-performance Ubuntu servers with **4x 8GB GPUs**, the system enforces:
* **Layer Distribution**: Offloads the 64+ layers of DeepSeek-R1 across all 4 GPUs to prevent system RAM bottlenecks.
* **Expanded Context (32k)**: The `NUM_CTX` is set to 32,768, allowing the agent to simultaneously "read" multiple past reports and thousands of log entries.
* **Flash Attention**: Enabled to accelerate inference and reduce the VRAM footprint of the 32B model.
* **Model Residency**: `OLLAMA_MAX_LOADED_MODELS=3` ensures all agents (Qwen, Nomic, DeepSeek) stay in VRAM for zero-latency switching.

---

## 6. Key Scientific Improvements
* ✅ **Semantic Consistency**: RAG ensures reports align with company history.
* ✅ **Reasoning Depth**: DeepSeek-R1 provides Tier 3 professional analysis.
* ✅ **Validation Rigor**: JSON-native auditing eliminates false-positive hallucination flags.
* ✅ **Future Proof**: The modular "Agent" structure allows for swapping models (e.g., Llama 4 or DeepSeek-V3) by editing a single `.env` variable.
