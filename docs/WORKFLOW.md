# 🛡️ SOC Agent v2026: Phased RAG Workflow (3x GTX 1070)

## 1. The "Launch Sequence"
Run these at the start of your shift to optimize the **3x 8GB GPU** (24GB total) stack.

### Step 1: Ignite the Sequential Engine
```bash
# Enable persistence mode to stabilize Pascal architecture
sudo nvidia-smi -pm 1

# Set global flush to clear VRAM between investigation acts
export OLLAMA_KEEP_ALIVE=0
ollama serve
```
> **What’s happening**: This configures Ollama to split the **14B DeepSeek-R1** layers across all three GPUs while ensuring a total VRAM flush after each phased act (A, B, and C) to prevent memory fragmentation.

### Step 2: Sync the Librarian
```bash
python3 src/ingest_knowledge.py
```
> **What’s happening**: This updates your **ChromaDB** "Semantic Memory" with your 30+ historical iSecurify reports to ensure the AI matches the company's "voice" and remediation standards.

---

## 2. The Investigation Workflow
The pipeline uses **Phased Reasoning** to achieve 5-page report depth without hitting 10-series bandwidth bottlenecks.

### Step 3: Run the Unified Pipeline
The `pipeline.py` master orchestrator triggers a synchronized four-agent handoff: **Cleaner → Extractor → Librarian → Phased Reporter**.

**The "Tier 3" Investigation (Human + RAG)**
*This is the recommended path for executive-level iSecurify Word output.*
```bash
python3 pipeline.py logs.csv --insight "Unauthorized SSH login attempts on 111.90.173.220"
```

---

## 3. The Forensic Vault (Synchronized Results)
Results are saved in `data/output/` and share a synchronized **Run ID**. Every investigation is a complete "Forensic Case File":

| File | Forensic Role |
| :--- | :--- |
| **`truth_block_[ID].json`** | The **Forensic Anchor**. Structured JSON data containing all IPs, paths, and validated facts. |
| **`SOC_Report_[ID].docx`** | The **Executive Export**. Professional Word document with iSecurify blue styling and cover page. |
| **`incident_report_[ID].md`** | The **Phased Narrative**. Raw DeepSeek-R1 reasoning script across Acts A, B, and C. |
| **`validation_[ID].txt`** | The **Forensic Audit**. Proves the narrative matches the original JSON truth. |

---

## 4. Pro Command Reference

| Action | Command |
| :--- | :--- |
| **Hardware Health** | `nvidia-smi` (Monitor VRAM distribution across the 3 cards) |
| **Pull 14B Model** | `ollama pull deepseek-r1:14b` |
| **Verify RAG Memory** | `python3 scripts/verify_setup.py` |
| **Persistence Reset** | `sudo nvidia-smi -r` (If a GPU "falls off the bus") |

---

## 5. Pro Optimization (24GB VRAM Tips)

> [!IMPORTANT]
> **Sequential Flushing**: On 10-series cards, VRAM bandwidth is the bottleneck. By using `KEEP_ALIVE=0`, we ensure Act B (Forensics) has full access to GPU memory without "leftovers" from Act A slowing down inference.

* **Context Window (NUM_CTX)**: Optimized at **8,192 tokens**. This is the "Sweet Spot" for your 24GB capacity—sufficient for deep RAG injection without risking OOM crashes.
* **iSecurify Branding**: Ensure the `hostname` is present in your logs; `pipeline.py` extracts this for the **SOCDocxExporter** to populate the professional cover page.
* **Power Stability**: Monitor the **TDP** (Power Usage) in `nvidia-smi`. If inference causes a card to disconnect, ensure each 1070 has a **dedicated power rail** from your PSU rather than a shared pigtail cable.