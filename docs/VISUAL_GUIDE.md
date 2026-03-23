# Visual Guide - SOC Agent v2026

## 1. The Big Picture (Logic Flow)
The system acts as a "Forensic Vault," ensuring every investigation is unique and verified.

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   ANALYST INPUTS                                    ┃
┃   ├─ CSV (Raw Logs)                                 ┃
┃   ├─ TXT (Incident Notes)                           ┃
┃   └─ --insight "Expert Conclusion" (Priority 1)     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━┛
                                │
                                ↓
                    ┌────────────────────────┐
                    │      pipeline.py       │
                    │  (The Master Router)   │
                    │   Creates UNIQUE ID    │
                    └────────┬───────────────┘
                             │
            ┌────────────────┴────────────────┐
            ↓                                 ↓
  ┌──────────────────┐               ┌──────────────────┐
  │   CSV Workflow   │               │  Text Workflow   │
  └──────────────────┘               └──────────────────┘
            │                                 │
            ↓                                 ↓
  ┌────────────────────┐            ┌────────────────────┐
  │    processor.py    │            │  report_generator  │
  │ (Universal Schema) │            │ (Direct Ingestion) │
  └────────────────────┘            └────────────────────┘
            │                                 │
            ↓                                 │
  ┌────────────────────┐            ┌────────────────────┐
  │ forensic_extractor │            │   "THE TRUTH BLOCK"│
  │ (FIM/Network/Email)│            │   (incident_[ID])  │
  └────────────────────┘            └────────────────────┘
            │                                 │
            └──────────┬──────────────────────┘
                       ↓
            ┌────────────────────────┐
            │   report_generator.py  │
            │  (Ollama / Qwen 2.5)   │
            └──────────┬─────────────┘
                       │
                       ↓
            ┌────────────────────────┐
            │  report_validator.py   │
            │   (The Truth Audit)    │
            └──────────┬─────────────┘
                       │
                       ↓
            ┏━━━━━━━━━━━━━━━━━━━━━━━━┓
            ┃     FORENSIC VAULT     ┃
            ┃  (Unique Timestamped)  ┃
            ┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 2. Path 1: From Raw Logs to Verified Report
The CSV chain is optimized for your **8GB RAM** environment.

### STEP 1: Normalization (processor.py)
* **Input**: Messy Wazuh/ELK logs.
* **Action**: Fixes `@` timestamps and maps Network/FIM/Email fields to a **Universal Schema**.

### STEP 2: Deep Scan (forensic_extractor.py)
* **Action**: Regex scanning for **777 permissions**, webshell paths, and **SPF/DKIM** failures.

### STEP 3: The Truth Block (incident_[ID].txt)
* **Action**: Merges Machine Facts with your **Human Insights**.
* **Constraint**: Human insights are placed at the top as the "Primary Truth".

---

## 3. Path 2: Direct Analyst Ingestion
If you already have a text file of findings, the Agent skips the logs and focuses on formatting and auditing your investigation.

---

## 4. The "Forensic Vault" Output
Every run creates a permanent, non-overwriting record in `data/output/`:

| File | Purpose |
| :--- | :--- |
| **`incident_20260320.txt`** | The raw evidence and analyst notes used for the run. |
| **`incident_report_20260320.md`** | The professional markdown report written by Qwen. |
| **`validation_20260320.txt`** | The audit log proving the AI didn't hallucinate data. |

---

## 5. Control Center (config.py)
A single file manages your entire hardware stack:
* **Local Use**: Points to `localhost` for CPU-based work on your laptop.
* **Office GPU**: Change one line to point to a high-power remote server.

---

## 6. Commands Summary

```bash
# UNIVERSAL COMMAND
report.bat <input> --insight "Your expert conclusion"

# SETUP
start_ollama.bat    # Starts AI Engine
pull_model.bat      # Downloads Qwen (first time)
```

---

## 7. Why this architecture is Tier 3?
1.  **Versioning**: It preserves historical data automatically.
2.  **Accuracy**: It audits itself for hallucinations.
3.  **Authority**: It yields to human expert conclusions.
4.  **Efficiency**: It handles 5,000+ logs on an 8GB laptop without crashing.
```
