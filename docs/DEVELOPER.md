# Developer Guide - Semantic RAG Architecture (v2026)

## System Architecture

### Multi-Agent Orchestration
The system utilizes a "Chain of Reasoning" where specialized models handle extraction, retrieval, and synthesis, communicating via a structured **JSON Truth Block**.

```text
┌───────────────────────────────────────────────────────────┐
│                      pipeline.py                          │
│     (Master Orchestrator - Syncs Extraction & RAG)        │
└──────────┬─────────────────────────────┬──────────────────┘
           │                             │
    ┌──────┴───────┐             ┌───────┴───────┐
    │  KNOWLEDGE   │             │   INCIDENT    │
    │  INGESTION   │             │   PIPELINE    │
    └──────┬───────┘             └───────┬───────┘
           │                             │
 [ingest_knowledge.py]         [csv_to_incident.py]
           ↓                    (Processor + Semantic Extractor)
 [CHROMA VECTOR DB]                      ↓
           │                   [incident_ID.json] (Truth Block)
           │                             │
           └──────────────┬──────────────┘
                          ↓
               [knowledge_base.py] (RAG)
             (Retrieves historical context)
                          ↓
               [report_generator.py]
             (DeepSeek-R1 reasoning engine)
                          ↓
    ┌─────────────┬───────┴───────┬─────────────┐
    ↓             ↓               ↓             ↓
[Report.md]  [Truth.json]  [Validation.txt] [Audit.log]
```

---

## Module Descriptions

### 1. **pipeline.py** (The General)
* **Purpose**: Coordinates the multi-agent handoffs.
* **Logic**: It triggers the **Semantic Extractor**, pulls a `mitre_query` from the resulting JSON, calls the **Knowledge Base** for context, and finally invokes the **Report Generator**.
* **Model Residency**: Configured to keep all three models (Qwen, Nomic, DeepSeek) resident in VRAM simultaneously.

### 2. **semantic_extractor.py** (The Fact-Finder)
* **Intelligence**: Uses **Qwen2.5-7B** to reason through raw log evidence.
* **Output**: Produces a **Pydantic-validated JSON** object.
* **Benefit**: Unlike regex, it understands the *intent* of a log entry (e.g., distinguishing between a failed login and a brute force attack).

### 3. **knowledge_base.py** (The Librarian)
* **Purpose**: Performs semantic search against **ChromaDB**.
* **Context injection**: Fetches the top 3 most relevant past reports or hardening guides to provide "Expert Experience" to the writer.

### 4. **report_generator.py** (The Lead Investigator)
* **Intelligence**: Uses **DeepSeek-R1 (32B)** with a **32k context window**.
* **Reasoning**: It processes the JSON facts and RAG context through a "Chain of Thought" (`<think>` tags) to produce Tier 3 narrative paragraphs.

---

## Data Flow & Forensic Integrity

### The JSON "Truth Block" (incident.json)
The system has moved from flat text to a structured schema. This is the **Forensic Anchor** of the investigation:
```json
{
  "metadata": {"run_id": "20260326_1500", "severity": 8},
  "affected_scope": {"target_ips": ["10.51.10.7"], "file_paths": ["/var/www/html/"]},
  "forensic_indicators": {"permission_bits": "777", "protocols": ["TCP/22"]},
  "human_intelligence": {"analyst_notes": "Suspected pentest."}
}
```

### The 32GB VRAM Optimization
To maximize your **4x 8GB GPU** stack, the system enforces:
* **Layer Splitting**: DeepSeek-R1 layers are distributed across GPUs 0-3.
* **Flash Attention**: Enabled via environment variables to handle long-form reports.
* **Model Orchestration**: `OLLAMA_MAX_LOADED_MODELS=3` prevents VRAM swapping during the RAG lookup phase.

---

## Customization & Scaling

### 1. Expanding the Knowledge Base
To update the agent's expertise, add new report snippets to `src/ingest_knowledge.py` and re-run:
```bash
python3 src/ingest_knowledge.py
```

### 2. Adjusting the "Persona" (templates/)
* **`prompt_template.txt`**: Change this to modify the AI's "voice" (e.g., making it more compliance-focused for PCI DSS audits).
* **`report_format.txt`**: Edit this to change the Markdown structure without touching the Python code.

---

## Testing & Diagnostics

### System Health Check
Run the diagnostic tool to verify GPUs, Vector DB, and Model status:
```bash
python3 scripts/verify_setup.py
```

### Manual RAG Testing
You can test the Librarian's retrieval accuracy independently:
```python
from src.knowledge_base import fetch_expert_context
print(fetch_expert_context("How do we handle world-writable SQL files?"))
```

---

## Version & Hardware Requirements
* **OS**: Ubuntu 22.04+ (Recommended for NVIDIA driver stability).
* **VRAM**: 32GB (Required for DeepSeek-R1 32B + Qwen-7B residency).
* **ChromaDB**: Latest (Used for local vector storage).
* **Ollama**: v0.1.x+ (Required for `format="json"` support).
