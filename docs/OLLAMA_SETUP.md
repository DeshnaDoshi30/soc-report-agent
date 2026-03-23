# SOC Agent v2026: Ollama & Qwen Startup Guide

## 1. Quick Start

### Step 1: Initialize the AI Server
Run this first to ensure the Ollama background service is active and the model is ready:
```bash
cd scripts
start_ollama.bat
```
* **What it does**: Checks for the Ollama service and pulls the **Qwen 2.5 Coder 3B** model if it isn't already installed.

### Step 2: Run the Forensic Pipeline
Use the universal `report.bat` to process your logs. **Recommendation**: Provide a human insight to ensure the highest accuracy.
```bash
# For CSV Logs
report.bat logs.csv --insight "Confirmed internal vulnerability scan."

# For Direct Text
report.bat incident.txt
```
* **What it does**: Automatically cleans logs, extracts facts, generates a report, and runs a hallucination audit.

---

## 2. The Forensic Vault (Output)
Unlike older versions, this system **never overwrites your work**. Every execution creates a unique set of files in `data/output/` linked by a timestamp:

* **`incident_[ID].txt`**: The "Truth Block" (Human Insights + Machine Facts).
* **`incident_report_[ID].md`**: The final formatted security report.
* **`validation_[ID].txt`**: The automated accuracy audit (Hallucination Check).

---

## 3. Configuration & Hardware

### Single Point of Decision (`src/config.py`)
All core settings are centralized. If you get **GPU access** later, you only need to change this one file:
* **DEFAULT_MODEL**: Set to `qwen2.5-coder:3b` for 8GB RAM safety.
* **OLLAMA_HOST**: Point to `localhost` or a remote office server.

### 8GB RAM Optimization
The pipeline is hard-coded with a **4096 context window** (`num_ctx`) to ensure the Qwen model runs smoothly on standard laptops without crashing.

---

## 4. Troubleshooting

### "Model Not Found"
**Problem**: The pipeline can't find the Qwen model.
* **Solution**: Run `pull_model.bat qwen2.5-coder:3b` or check your settings in `src/config.py`.

### "Connection Refused"
**Problem**: Pipeline cannot talk to Ollama.
* **Solution**: Ensure `start_ollama.bat` is running in a separate, active terminal window.

### "Hallucination Detected"
**Problem**: The `validation_[ID].txt` file flags **CRITICAL** issues.
* **Solution**: Review the report for "invented" data (like fake IP addresses or costs) that weren't in your original logs.

---

## 5. Manual Management
If you need to manage the model manually via the terminal:
```bash
# Pull the specific 3B coder model
ollama pull qwen2.5-coder:3b

# Verify the model is loaded in VRAM
ollama list

# Test the model's logic directly
ollama run qwen2.5-coder:3b "Summarize these logs..."
```

---

## 6. Pipeline Flow Summary
1.  **START**: `report.bat` triggered.
2.  **ID GEN**: Unique **Run ID** timestamp created.
3.  **CLEAN**: `processor.py` normalizes data for 8GB RAM safety.
4.  **EXTRACT**: `forensic_extractor.py` performs a Deep Scan (777 perms, SPF, etc.).
5.  **SYNTHESIZE**: Human Insights + Machine Facts merged into the "Truth Block".
6.  **GENERATE**: AI writes the report (Priority: Human Insight).
7.  **AUDIT**: `report_validator.py` scans for fabrications.
8.  **VAULT**: All files saved to `data/output/` with the unique Run ID.

