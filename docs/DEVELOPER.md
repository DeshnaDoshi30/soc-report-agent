# Developer Guide - Architecture & Customization (v2026)

## System Architecture

### Modular Design
The system is built as a series of independent modules that communicate through standardized "Truth Blocks" (incident files).

```
┌─────────────────────────────────────────────────────────┐
│                    pipeline.py                          │
│     (Master Orchestrator - Generates Unique Run ID)     │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
  ┌──────────────┐      ┌──────────────────┐
  │ CSV INPUT    │      │ TEXT INPUT       │
  └──────────────┘      └──────────────────┘
        │ (with Insight)      │ (with Insight)
        ↓                     ↓
  ┌──────────────────┐        │
  │ csv_to_incident  │        │
  │   ├─ processor   │        │
  │   └─ extractor   │        │
  └──────────────────┘        │
        │                     │
        └──────────┬──────────┘
                   ↓
        ┌──────────────────────┐
        │ report_generator.py  │
        │  (Calls Validator)   │
        └──────────────────────┘
                   ↓
  ┌────────────────┬───────────────┐
  │                │               │
  ↓                ↓               ↓
[Report.md]   [Facts.txt]    [Validation.txt]
(Vault Storage: All files linked by unique Timestamp ID)
```

---

## Module Descriptions

### 1. **pipeline.py** (Main Entry)
* **Purpose**: Single entry point that manages the lifecycle of an investigation.
* **Responsibility**: Generates the unique `run_id` timestamp and routes data to the correct workflow.
* **Key Logic**: Pulls default model and hardware settings from `src/config.py`.

```python
from src.pipeline import UnifiedPipeline

# Automated Run: Routes CSV or TXT automatically
pipeline = UnifiedPipeline(input_file="logs.csv", human_insight="Verified internal scan")
pipeline.run()
```

### 2. **csv_to_incident.py** (CSV Orchestrator)
* **Purpose**: Manages the conversion of raw logs into a forensic "Truth Block".
* **Logic**: Merges machine-detected facts with ephemeral **Human Insights**.
* **Non-Overwriting**: Automatically creates unique filenames using the `run_id`.

```python
from src.csv_to_incident import CSVToIncidentConverter

# Human Insight takes priority in the final text block
converter = CSVToIncidentConverter(csv_file="logs.csv", human_insight="Dev team testing.")
incident_path = converter.convert()
```

### 3. **processor.py** (Universal Cleaner)
* **Purpose**: Normalizes diverse log formats (Network, FIM, Email) into a standard SOC schema.
* **Hardware Optimized**: Uses categorical data types to prevent `MemoryError` on **8GB RAM**.

### 4. **forensic_extractor.py** (Deep Scan)
* **Purpose**: Performs regex-based "Deep Scans" on raw evidence to find hidden usernames, file paths, and permission bits (777).
* **Domain Support**: Includes logic for SPF/DKIM failures and Webshell path detection.

### 5. **report_generator.py** (Writer & Auditor)
* **Purpose**: Generates the AI report and automatically triggers the **HallucinationDetector**.
* **Authority Logic**: Instructs the LLM to treat human insights as the absolute investigative truth.

---

## Data Flow Transformations

### The "Truth Block" Synthesis (incident.txt)
Instead of just raw facts, the system now creates a prioritized hierarchy:
1.  **Primary Truth**: Ephemeral analyst insights from the command line.
2.  **Machine Data**: Automated forensics from `forensic_extractor.py`.

### The Forensic Vault Output
Every run results in three linked files in `data/output/`:
* `incident_YYYYMMDD_HHMMSS.txt` (Source Evidence)
* `incident_report_YYYYMMDD_HHMMSS.md` (AI Findings)
* `validation_YYYYMMDD_HHMMSS.txt` (Accuracy Audit)

---

## Customization & Scaling

### 1. Global Settings (src/config.py)
This is your **Single Point of Decision** for model and hardware.
* **Model**: Change `DEFAULT_MODEL` to swap between Qwen, Llama, or office-provided GPU models.
* **Hardware**: Update `OLLAMA_HOST` to point to a local CPU or a remote GPU server.

### 2. Universal Schema Mapping (src/processor.py)
The `target_columns` dictionary has been expanded to support:
* **FIM**: `File_Path`, `Permissions`, `Owner`.
* **Email**: `SPF_Status`, `DKIM_Status`, `Email_Sender`.
* **Identity**: `Source_User`, `Target_User`.

---

## Testing & Troubleshooting

### Local Module Testing
```bash
# Test the full pipeline with a Human Insight override
python src/pipeline.py logs.csv --insight "This is a confirmed pentest."

# Test only the AI Generation and Validation phases
python src/report_generator.py data/output/incident_20260320_1200.txt
```

### Troubleshooting Memory Usage
If running on **8GB RAM**, ensure `num_ctx` is set to **4096** in `report_generator.py` to prevent the Qwen model from overwhelming system memory.

### Hallucination Warnings
If the `validation_[ID].txt` report flags **CRITICAL** issues, check if the AI has invented **Financial Costs** or **CVSS Scores** that were not present in the original `incident.txt`.

---

## Version & Dependencies
* **Python**: 3.7+ (Recommended for `pathlib` and `datetime` support).
* **Pandas**: 1.x+ (Used with categorical optimization for RAM safety).
* **Ollama**: Latest (Required for local LLM orchestration).
* **Requests**: 2.28+ (Used for communication with the Ollama API).
