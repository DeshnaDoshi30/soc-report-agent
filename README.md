# 🛡️ SOC Incident Report Agent - Forensic Vault Edition (v2026)

Generate professional, Tier 3 security incident reports from CSV logs or incident text using local AI. This system is specifically engineered for **8GB RAM** environments and is **Cross-Platform Ready** for seamless transition between Windows laptops and Ubuntu GPU servers.

---

## 🚀 Key Features
* **Forensic Vault**: Every investigation is synchronized by a unique **Run ID**. Cleaned data, extracted facts, and AI reports are linked, ensuring a perfect audit trail.
* **Human-in-the-Loop**: Senior Analyst insights provided via CLI take absolute priority over automated machine logs in the AI's reasoning.
* **Hallucination Auditor**: A built-in forensic validator scans reports for fabricated IPs, costs, or CVSS scores not present in the "Truth Block."
* **Universal Log Routing**: Handles Network attacks, File Integrity (FIM/777) alerts, and Email Security (SPF/DKIM) through a unified schema.

---

## 🛠️ Install & Setup (5 Minutes)

### Requirements
- Python 3.9+
- Ollama AI Framework
- **8GB RAM** (Optimized for local 3B/8B parameter models)

### Installation Steps
1. **Prepare Environment**:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate | Ubuntu: source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Secrets**:
   Copy `.env.example` to **`.env`** and set your target model and Ollama host.

3. **Verify Setup**:
   ```bash
   python scripts/verify_setup.py
   ```

---

## 📖 Usage

### 1. Start AI Engine
```bash
# Windows
scripts\start_ollama.bat

# Ubuntu
./scripts/start_ollama.sh
```

### 2. Run Forensic Pipeline
Pass raw CSV logs or existing incident text. Use the `--insight` flag to impart your expert conclusions to the AI.
```bash
# Windows
scripts\report.bat logs.csv --insight "Confirmed internal pentest activity."

# Ubuntu
./scripts/report.sh logs.csv --model llama3:8b
```

---

## 📂 The Forensic Vault (Synchronized Output)
All results are saved to `data/output/` and share a synchronized **Run ID** for traceability:
* **`cleaned_[ID].csv`**: The sanitized, memory-optimized log evidence.
* **`incident_[ID].txt`**: The "Truth Block" (Merged Human Insight + Machine Facts).
* **`incident_report_[ID].md`**: The formatted, Lead-level AI report.
* **`validation_[ID].txt`**: The forensic audit identifying any AI fabrications.

---

## 🏗️ Modular Architecture & Project Structure

The project is designed with a **Separation of Concerns** principle. Every module has a single responsibility, making it easy to swap models or add new forensic signatures without breaking the core pipeline.

### Logic Flow
```text
src/
 ├── pipeline.py (Master Orchestrator - Generates Run ID & Syncs Modules)
 ├── config.py (Single Point of Truth - Manages .env & Global Paths)
 │
 ├── csv_to_incident.py (The Context Merger)
 │    ├── processor.py (Universal Cleaner - 8GB RAM safe, Handles Chunking)
 │    └── forensic_extractor.py (Signature Scanner - Extracts IPs, Paths, & Perms)
 │
 └── report_generator.py (The Writer - Ingests Templates & Logic)
      └── report_validator.py (The Internal Auditor - Scans for Hallucinations)
```

### File Hierarchy
```text
SOC-REPORT-AGENT/
├── data/                 # The Forensic Vault
│   ├── input/            # Raw log storage
│   ├── output/           # Synchronized Run ID results (.md, .txt, .csv)
│   └── saved/            # Archived investigations
├── docs/                 # Extensive Documentation
│   ├── ARCHITECTURE.md   # Deep dive into the system logic
│   ├── USER_GUIDE.md     # How to use the CLI flags
│   └── WORKFLOW.md       # Visualizing the Forensic Pipeline
├── scripts/              # Cross-Platform Execution Layer
│   ├── report.bat/.sh    # Unified Entry Points (Win/Linux)
│   ├── start_ollama.bat/.sh # Ignition scripts
│   └── verify_setup.py   # Automated Diagnostic Tool
├── src/                  # Core Source Code
├── templates/            # Report Blueprints & AI Personas
├── .env.example          # Template for local hardware settings
└── requirements.txt      # Dependency manifest
```

---

## 🛠️ Cross-Platform Execution (Dual-Mode)

The agent is built to be **Environment Agnostic**. Use the twin scripts in the `scripts/` folder to ensure identical behavior on your laptop or a high-powered GPU server.

| Feature | Windows (Local Laptop) | Linux (Ubuntu GPU Server) |
| :--- | :--- | :--- |
| **Ignition** | `scripts\start_ollama.bat` | `./scripts/start_ollama.sh` |
| **Intelligence** | `scripts\pull_model.bat` | `./scripts/pull_model.sh` |
| **Investigation** | `scripts\report.bat <file>` | `./scripts/report.sh <file>` |
| **Diagnostics** | `python scripts/verify_setup.py` | `python3 scripts/verify_setup.py` |

---

## ⚙️ Customization & Portability

| To Change... | Edit This File |
| :--- | :--- |
| **Model/Hardware** | `.env` or `src/config.py` (e.g., set to Office GPU IP) |
| **Log Schema** | `src/processor.py` (Add new CSV column mappings) |
| **Detection Rules** | `src/forensic_extractor.py` (Add new regex signatures) |
| **Report Layout** | `templates/report_format.txt` (Change headers/sections) |

---

## 📚 Support Documentation
* **Project Logic**: See [ARCHITECTURE.md](./docs/ARCHITECTURE.md)
* **User Workflow**: See [USER_GUIDE.md](./docs/USER_GUIDE.md)
* **Deployment**: See [OLLAMA_SETUP.md](./docs/OLLAMA_SETUP.md)

---

## ⚠️ Troubleshooting

* **Ubuntu Permissions**: If scripts won't run on Linux, run `chmod +x scripts/*.sh`.
* **RAM Optimization**: The agent uses a **4096 context window** via `num_ctx`. If you experience crashes on 8GB RAM, ensure the `SOC_MODEL` in `.env` is set to a 3B parameter model.
* **Vault Warnings**: If `validation_[ID].txt` shows "CRITICAL" issues, the AI has likely hallucinated data. Review the source facts in `incident_[ID].txt`.
