# SOC Report Agent - User Guide (v2026)

## 1. Overview
The SOC Report Agent is a Tier 3 forensic tool designed to convert raw security logs (CSV) or manual incident notes (TXT) into professional, fact-based reports. It uses the **Qwen 2.5 Coder** model, optimized to run locally on machines with **8GB RAM**.

### Key Features:
* **Forensic Vault**: Every investigation is saved with a unique timestamp. No data is ever overwritten.
* **Human-in-the-Loop**: Analyst insights provided via the command line take priority over machine-detected logs.
* **Universal Routing**: Automatically handles Wazuh logs, FIM (File Integrity) alerts, and Email Security (SPF/DKIM) failures.
* **Hallucination Detection**: Every report is audited against source facts to prevent the AI from inventing IPs or costs.

---

## 2. Quick Start

### Path A: I have Raw CSV Logs
Use this for bulk analysis of automated alerts.
1. Open a terminal in `scripts/`.
2. Run: `report.bat my_logs.csv`

### Path B: I have Manual Incident Notes
Use this to format your own investigation notes.
1. Run: `report.bat incident.txt`

### Path C: The "Expert" Workflow (Recommended)
Provide your manual conclusions to guide the AI's final report.
1. Run: `report.bat logs.csv --insight "Confirmed internal vulnerability scan by the IT team."`

---

## 3. The Forensic Vault (Output)
To ensure forensic integrity, the system saves three distinct files for every run in `data/output/`. These are linked by a unique **Run ID** (YYYYMMDD_HHMMSS):

1.  **`incident_[ID].txt`**: The "Truth Block" containing merged human and machine facts.
2.  **`incident_report_[ID].md`**: The final formatted AI report.
3.  **`validation_[ID].txt`**: The accuracy audit identifying any potential AI fabrications.

---

## 4. Command Reference

| Command | Purpose |
| :--- | :--- |
| `report.bat <file>` | Main command to generate a report. |
| `--insight "text"` | **Critical**: Imparts human expert conclusions to the AI. |
| `--model <name>` | Overrides the default model (e.g., `--model llama3`). |
| `start_ollama.bat` | Starts the local AI server. |
| `list_models.bat` | Shows models currently installed on your machine. |

---

## 5. Domain Support
The Agent is pre-trained to recognize specific security domains:

* **Network Attacks**: Brute force, port scans, and IP blocking.
* **Configuration (FIM)**: World-writable (777) permissions and suspicious file paths (e.g., webshells).
* **Policy/Email**: SPF, DKIM, and DMARC failures, as well as unauthorized internal access.

---

## 6. Customization
The system is designed with a **Single Point of Decision** model:

* **Hardware/Model**: Edit `src/config.py` to change the local model name or to point to an office GPU server.
* **AI Tone**: Edit `templates/prompt_template.txt` to adjust how strictly the AI follows the logs.
* **Report Style**: Edit `templates/report_format.txt` to change headers or sections.

---

## 7. Troubleshooting
* **RAM Issues**: If the system slows down, ensure no other heavy apps are running. The Agent is capped at a 4096 context window to protect your **8GB RAM**.
* **Hallucination Warnings**: If `validation_[ID].txt` shows high-severity issues, check if the AI invented a cost or a nation-state actor.
* **Ollama Errors**: Ensure `start_ollama.bat` is running in a separate window before starting the pipeline.