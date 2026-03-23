# SOC Agent v2026: Simple Workflow Cheat Sheet

## 1. The "Start of Shift" Setup
Run these once at the beginning of your work session.

### Step 1: Start the AI Engine
```batch
cd scripts
start_ollama.bat
```
> **Note**: Keep this terminal window open in the background.

### Step 2: Initialize the Brain (First time only)
```batch
cd scripts
pull_model.bat qwen2.5-coder:3b
```
*Optimized for your **8GB RAM** environment*.

---

## 2. The Investigation Workflow
Every time you have a new set of logs or notes, follow this one-command path.

### Step 3: Run the Pipeline
Use the universal `report.bat`. It automatically detects if you are giving it a CSV or a TXT file.

**Option A: Standard Run (Machine Facts Only)**
```batch
report.bat logs.csv
```

**Option B: Expert Run (Human + Machine)** *This is the recommended path for the highest accuracy*.
```batch
report.bat logs.csv --insight "This is a confirmed port scan from an internal dev IP."
```

---

## 3. Where are my files? (The Forensic Vault)
Your results are saved in `data/output/`. The system **never overwrites** old data. Look for the files with the latest timestamp:

1.  **`incident_[ID].txt`**: Your raw facts and manual insights.
2.  **`incident_report_[ID].md`**: The professional security report.
3.  **`validation_[ID].txt`**: The "Truth Score" audit. Check this for hallucinations.

---

## 4. Quick Command Reference

| Goal | Command |
| :--- | :--- |
| **Start Engine** | `start_ollama.bat` |
| **List Models** | `list_models.bat` |
| **Process Logs** | `report.bat logs.csv` |
| **Override AI** | `report.bat logs.csv --insight "..."` |
| **Test Setup** | `test_setup.bat` |

---

## 5. Troubleshooting (8GB RAM Tips)

* **"Ollama Not Found"**: Install from `ollama.ai` and restart your terminal.
* **"System Lagging"**: Close Chrome or other heavy apps. The agent needs about **4GB of free RAM** to run the Qwen model comfortably.
* **"AI is Lying"**: Check the `validation_[ID].txt` file. If the AI is hallucinating, provide a more detailed `--insight` to ground it in reality.

