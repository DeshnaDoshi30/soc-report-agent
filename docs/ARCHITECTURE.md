# Architecture & Data Flow (v2026 - Forensic Vault Edition)

## 1. The Core Problem
Previously, the system was a linear, overwriting script that lacked forensic integrity.
* **Overwriting Risk**: Every new run deleted the previous report.
* **Machine-Only Logic**: The AI guessed conclusions without human expert guidance.
* **Accuracy Gaps**: There was no automated check to see if the AI was "hallucinating" data.

## 2. The Tier 3 Solution
I upgraded the system into a **Modular Forensic Vault**. It doesn't just generate reports; it builds a historical archive of every investigation.

### ✓ Forensic Integrity (The Vault)
* **Unique Run IDs**: Every execution generates a unique timestamp (e.g., `20260320_1527`) used for all output files.
* **Non-Overwriting**: Previous investigations are preserved, creating a permanent chain of custody.

### ✓ Human-in-the-Loop Priority
* **Primary Truth**: Analysts can provide ephemeral insights via the `--insight` flag.
* **Authority Logic**: The AI is strictly instructed to prioritize human conclusions over automated machine logs.

### ✓ Automated Auditing
* **Hallucination Detection**: A post-generation audit checks for fake IPs, invented costs, or fabrications.

---

## 3. Modular Architecture (The "Brain" & "Guard")

| Module | Forensic Role |
| :--- | :--- |
| **`config.py`** | **Single Point of Decision**: Centralized model and hardware settings. |
| **`pipeline.py`** | **Master Synchronizer**: Generates the Run ID and routes the investigation. |
| **`processor.py`** | **Universal Cleaner**: Normalizes Network, FIM, and Email logs for 8GB RAM safety. |
| **`forensic_extractor.py`** | **Deep Scanner**: Extracts hidden usernames, file paths, and 777 permissions. |
| **`report_generator.py`** | **The Writer**: Synthesizes the "Truth Block" into a markdown report. |
| **`report_validator.py`** | **The Auditor**: Scans for inconsistencies and fabrications. |

---

## 4. Advanced Data Flow

### Path: CSV to Forensic Vault
```
Raw Logs (CSV) + Human Insight (CLI)
      ↓
[processor.py] -> Normalizes to Universal Schema (Network/FIM/Email)
      ↓
[forensic_extractor.py] -> Deep Scans for 777 perms, Webshells, and SPF failures
      ↓
[incident_ID.txt] -> The "Truth Block" (Human Insight + Machine Facts)
      ↓
[report_generator.py] -> AI synthesis using Qwen 2.5 Coder (4096 context)
      ↓
[report_validator.py] -> Automated Accuracy Audit
      ↓
OUTPUT VAULT (data/output/)
├─ incident_20260320.txt        (The Evidence)
├─ incident_report_20260320.md  (The AI Report)
└─ validation_20260320.txt      (The Audit Log)
```

---

## 5. Hardware Optimization (8GB RAM)
To ensure stability on local hardware, the following optimizations are enforced:
* **Categorical Encoding**: Reduces memory footprint for high-volume IP logs.
* **Context Capping**: The LLM is restricted to a 4096-token window to prevent system crashes.
* **Ollama Orchestration**: Offloads model management to the Ollama backend for better VRAM handling.
* **Environment Agnostic**: Uses Pathlib and config.py to automatically switch between Windows paths (\) and Linux paths (/), allowing the code to run on an 8GB laptop or an Ubuntu GPU server with zero changes.

---

## 6. Key Improvements (Summary)
* ✅ **Versioning**: Every report is unique; no data loss.
* ✅ **Accuracy**: Built-in hallucination detection.
* ✅ **Authority**: Expert human insights take precedence.
* ✅ **Universal**: One pipeline for Network, File, and Email security.

---
