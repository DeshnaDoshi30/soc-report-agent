# Developer Guide - Phased Forensic RAG Architecture (v2026)

## System Architecture

### Multi-Act Forensic Orchestration
The system utilizes a "Sequential Chain of Reasoning." To respect VRAM limits while achieving 5-page report depth, models are loaded, utilized for a specific "Act," and then flushed.

```text
┌───────────────────────────────────────────────────────────┐
│                    pipeline.py                            │
│     (Master Orchestrator - Syncs Extraction & RAG)        │
└──────────┬─────────────────────────────┬──────────────────┘
           │                             │
    ┌──────┴───────┐             ┌───────┴───────┐
    │  KNOWLEDGE   │             │   INCIDENT    │
    │  INGESTION   │             │   PIPELINE    │
    └──────┬───────┘             └───────┬───────┘
           │                             │
 [ingest_knowledge.py]         [csv_to_incident.py] / [pipeline.py]
           ↓                    (Cleaner + Semantic Extractor)
 [CHROMA VECTOR DB]                      ↓
           │                  [truth_block_ID.json] (Truth Block)
           │                             │
           └──────────────┬──────────────┘
                          ↓
                [knowledge_base.py] (RAG)
              (Retrieves historical context)
                          ↓
                [report_generator.py] 
             (Phased 14B Reasoning Engine)
           (Act A: Brief | Act B: Forensic | Act C: Strategy)
                          ↓
    ┌─────────────┬───────┴───────┬─────────────┐
    ↓             ↓               ↓             ↓
[Report.md] [SOC_Report.docx] [Truth.json] [Audit.log]
```

---

## Module Descriptions

### 1. **pipeline.py** (The General)
* **Purpose**: Manages the high-level investigation state.
* **Logic**: Orchestrates the handoff from **Qwen-7B** (Extraction) to **ChromaDB** (RAG) and finally **DeepSeek-14B** (Reporting).
* **VRAM Guard**: Ensures hostname and metadata are passed through to the final Docx exporter.

### 2. **semantic_extractor.py** (The Fact-Finder)
* **Intelligence**: Uses **Qwen2.5-7B** for forensic parsing.
* **Logic**: Differentiates between **NARRATIVE** and **LOG** inputs to adjust extraction intent.
* **Output**: Pydantic-validated **JSON Truth Block**.

### 3. **report_generator.py** (The Lead Investigator)
* **Intelligence**: **DeepSeek-R1 (14B)**.
* **Phased Reasoning**: Instead of a single call, it executes three distinct acts (**Phase A, B, and C**) to bypass the "10-series bottleneck" and achieve a 4-5 page narrative depth.
* **Memory Bridge**: Passes a summary of the previous act to the next to maintain forensic continuity.

### 4. **docx_exporter.py** (The Publisher)
* **Purpose**: Converts Markdown into iSecurify-branded Word documents.
* [cite_start]**Design**: Implements blue-accented headings (RGB 0, 32, 96), a professional cover page, and a mandatory "Confidential" footer.

---

## Data Flow & Forensic Integrity

### The JSON "Truth Block" (`truth_block_[run_id].json`)
This structured object prevents AI hallucination by anchoring all phases to verified data.
```json
{
  "METADATA": {"run_id": "20260401_1500", "hostname": "EMBERVEIL"},
  "FINDINGS": {
    "primary_classification": "Unauthorized SSH Access",
    "target_ips": ["111.90.173.220"],
    "permission_bits": "777",
    "mitre_query": "T1110.001 Password Brute Forceing"
  }
}
```

### The 24GB VRAM Optimization (3x 1070)
To maximize the 8GB VRAM per card, the system enforces:
* **Sequential Flushing**: `KEEP_ALIVE=0` is set in all Ollama calls to ensure the GPU is 100% empty between the Extractor and Reporter phases.
* **Context Slicing**: The `_trim_json_for_phase` method sends only the necessary data segments to the AI, keeping the KV cache lean and fast.

---

## Customization & Scaling

### 1. Phased Prompt Engineering (`templates/`)
* **`global_header.txt`**: The permanent iSecurify persona and narrative guardrails.
* **`phase_a/b/c.txt`**: Detailed objectives for the Brief, Forensic Deep-Dive, and Strategic Resolution.

### 2. Branding & Design
Modify `src/docx_exporter.py` to adjust typography, RGB color schemes, or cover page tables to match evolving company document standards.

---

## Version & Hardware Requirements
* **VRAM**: 24GB (3x 8GB recommended; utilizes layer splitting).
* **Models**: `deepseek-r1:14b`, `qwen2.5:7b`, `nomic-embed-text`.
* **Python**: 3.10+ (requires `python-docx`, `pydantic`, and `pandas`).