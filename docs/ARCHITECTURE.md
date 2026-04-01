# 🛡️ Architecture & Data Flow (v2026 - Phased RAG Edition)

## 1. The Evolutionary Leap: Phased Reasoning
The v2026 architecture introduces **Phased Narrative Generation** to overcome the bandwidth limitations of 10-series hardware. Instead of a single-shot generation, the agent writes the report in three distinct "Acts" (A, B, and C).
* **Beyond Regex**: Replaced rigid keyword matching with a **Semantic Extractor** (Qwen-7B) that understands forensic intent.
* **Knowledge Retrieval (RAG)**: Queries a local **ChromaDB** to inject historical company expertise and hardening standards into every section.
* **Tier 3 Depth**: Utilizes **DeepSeek-R1 (14B)** to perform forensic analysis across 4-5 pages, providing the "Why" behind security risks.

## 2. The Tier 3 Forensic Vault (JSON-Native)
The **JSON Truth Block** serves as the immutable anchor for the entire investigation.
* **Forensic Anchor**: Every IP, timestamp, and technical finding is validated against a structured schema before any narrative is generated.
* **Non-Repudiation**: Unique **Run IDs** synchronize raw logs, the JSON Truth Block, and the final iSecurify-branded Word document for full auditability.

---

## 3. Modular Orchestration (The Multi-Agent Stack)

| Module | Forensic Role | Intelligence Layer |
| :--- | :--- | :--- |
| **`semantic_extractor.py`** | **The Fact-Finder**: Converts raw evidence into the JSON Truth Block. | **Qwen 2.5 (7B)** |
| **`knowledge_base.py`** | **The Librarian**: Performs semantic RAG searches for context injection. | **Nomic Embed Text** |
| **`report_generator.py`** | **The Lead Investigator**: Executes phased narrative synthesis (Acts A, B, C). | **DeepSeek-R1 (14B)** |
| **`docx_exporter.py`** | **The Publisher**: Generates corporate blue iSecurify Word reports. | **python-docx** |

---

## 4. Advanced Data Flow (The Sequential Pipeline)

### Path: Raw Log to Professional Word Export
```text
Raw Logs (CSV) + Human Insight (CLI)
      ↓
[processor.py] -> Normalizes Wazuh/SonicWall logs (Memory Optimized)
      ↓
[semantic_extractor.py] -> (GPU 0) Reasons through evidence to produce JSON Truth
      ↓
[TRUTH BLOCK] -> Immutable Forensic Data (VRAM FLUSH: KEEP_ALIVE=0)
      ↓
[knowledge_base.py] -> (GPU 1) Searches ChromaDB for "Similar Past Incidents"
      ↓
[report_generator.py] -> (GPU 0-2) Phased Synthesis (A -> B -> C)
      ├─ PHASE A: Executive Brief
      ├─ PHASE B: Forensic Deep-Dive
      └─ PHASE C: Strategic Resolution
      ↓
[docx_exporter.py] -> Finalizes Professional iSecurify Report (Blue Accents)
      ↓
OUTPUT VAULT (data/output/)
├─ truth_block_ID.json   (The Evidence)
├─ incident_report_ID.md (The Raw Narrative)
└─ SOC_Report_ID.docx    (The Client-Ready Document)
```

---

## 5. Hardware Optimization (24GB VRAM Architecture)
Specifically engineered for **3x 8GB GTX 1070s**, the system enforces:
* **Sequential Actuation**: `KEEP_ALIVE=0` ensures the Extractor (Qwen) is fully flushed before the Reporter (DeepSeek) loads, preventing OOM crashes.
* **Phased VRAM Flushing**: Memory is cleared between report acts (A, B, and C) to prevent fragmentation and allow for high-density reasoning.
* **Context Slicing**: `NUM_CTX=8192` combined with the `_trim_json_for_phase` helper maximizes model attention on critical forensic data.
* **Layer Distribution**: Ollama automatically splits the 14B model weights across all 3 GPUs to maintain stability.

---

## 6. Key Scientific Improvements
* ✅ **VRAM Efficiency**: Phased logic allows 14B models to run on 8GB cards without quality loss.
* ✅ **Narrative Depth**: Act-based generation consistently achieves 4-5 page report length.
* ✅ **Corporate Compliance**: Automated Docx styling matches the 2026 iSecurify blue-accent standards.
* ✅ **Truth Grounding**: JSON-native anchoring eliminates AI hallucinations in forensic sections.