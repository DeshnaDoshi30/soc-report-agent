# 🛡️ SOC Agent v2026: Pro RAG Workflow (Ubuntu GPU)

## 1. The "Launch Sequence"
Run these at the start of your shift to warm up the **4x 8GB GPU** stack.

### Step 1: Ignite the Multi-GPU Engine
```bash
./scripts/start_ollama.sh
```
> **What’s happening**: This balances the **32B DeepSeek-R1** layers across all 4 GPUs and keeps the **Qwen Extractor** and **Nomic Embedder** resident in VRAM.

### Step 2: Sync the Librarian (If reports were added)
```bash
python3 src/ingest_knowledge.py
```
> **What’s happening**: This updates your "Semantic Memory" (ChromaDB) with any new company reports or compliance standards.

---

## 2. The Investigation Workflow
The pipeline now intelligently handles the "thinking" for you.

### Step 3: Run the Multi-Agent Pipeline
The universal `report.sh` now triggers a three-agent handoff: **Extractor → Librarian → Lead Investigator**.

**The "Standard" Narrative (Logs only)**
```bash
./scripts/report.sh logs.csv
```

**The "Tier 3" Investigation (Human + RAG)**
*This is the recommended path for executive-level reporting.*
```bash
./scripts/report.sh logs.csv --insight "Evidence of SQL injection attempts on API v2."
```

---

## 3. The Forensic Vault (Synchronized Results)
Results are saved in `data/output/` and share a synchronized **Run ID**. Every investigation is a "Case File":

| File | Forensic Role |
| :--- | :--- |
| **`incident_[ID].json`** | The **Semantic Truth Block**. The authoritative anchor of all facts. |
| **`incident_report_[ID].md`** | The **Narrative Report**. Fuses log data with historical company experience. |
| **`validation_[ID].txt`** | The **Forensic Audit**. Proves the narrative matches the JSON truth. |

---

## 4. Pro Command Reference

| Action | Command |
| :--- | :--- |
| **Full Stack Check** | `python3 scripts/verify_setup.py` |
| **Pull GPU Models** | `./scripts/pull_model.sh --setup-all` |
| **Monitor VRAM** | `nvidia-smi` (Run in a separate terminal) |
| **View AI "Thinking"** | `tail -f data/ollama_server.log` |

---

## 5. Pro Optimization (32GB VRAM Tips)

> [!IMPORTANT]
> **Semantic Memory**: If your report doesn't sound like "you," ensure you've run `ingest_knowledge.py`. The agent relies on your historical reports to match the company's voice.

* **Context Window**: The server is set to **32,768 tokens**. This allows you to process entire log files in one go without the AI "forgetting" the beginning of the file.
* **VRAM Spills**: If you see `nvidia-smi` showing nearly 32GB used, that's perfect. It means the models are fully resident in the GPUs for maximum speed.
* **Audit High-Severity**: If the validation log shows high-severity flags, the AI may have tried to "fill in the gaps" where logs were missing. Ground it by adding more detail to your `--insight`.
