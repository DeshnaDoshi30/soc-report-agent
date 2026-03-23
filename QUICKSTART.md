# QUICKSTART - Forensic Vault Workflow

## Path A: Raw Logs (CSV)
Ideal for high-volume analysis on your 8GB RAM machine.
1. `cd scripts`
2. `start_ollama.bat`
3. `report.bat my_logs.csv --insight "Manual observation: Traffic looks like a port scan."`

## Path B: Direct Text (TXT)
Ideal for manual investigations or re-running reports.
1. `report.bat incident.txt`

---

## The "Forensic Vault" Result
Every run creates unique files. Your data is **never overwritten**:
* `data/output/incident_20260320_1527.txt` - The "Truth Block"
* `data/output/incident_report_20260320_1527.md` - The AI Report
* `data/output/validation_20260320_1527.txt` - Hallucination Audit

---

## Power Features
* **Human Priority**: Use `--insight "..."` to force the AI to follow your lead.
* **Hallucination Detection**: Every report is automatically audited for fake IPs, costs, or CVSS scores.
* **Single Config**: Change your model or hardware source in `src/config.py`.