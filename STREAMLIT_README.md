# 🛡️ Streamlit Web UI for SOC Report Agent

Professional web interface for forensic report generation without touching the CLI pipeline.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📋 Features

### ✅ Smart Model Selection
- Automatically detects GPU/RAM availability
- Shows only compatible models based on your hardware
- Displays safety margins and context windows
- Pre-selects optimal model for Phase 3

### ✅ Hardware Monitoring
- Real-time GPU VRAM checking
- System RAM availability display
- Model compatibility validation
- Prevents incompatible model selection

### ✅ Clean Report Organization
- Auto-archives reports in `data/archive/YYYY-MM-DD/run_id/`
- SQLite database for metadata tracking
- Easy report history browsing and searching
- No more messy output folder

### ✅ Professional Interface
- Responsive two-column layout
- Real-time status updates
- One-click report downloads
- Previous reports accessible anytime

---

## 🎯 Workflow

### Step 1: Configure (Optional)
- Set custom Ollama host in sidebar (default: `http://localhost:11434`)
- View current hardware status

### Step 2: Generate Report
1. Upload CSV/TXT forensic logs
2. Enter analyst insights (optional)
3. Select model from dropdown
4. Click "Generate Report"
5. Watch real-time progress

### Step 3: Download Results
Once complete:
- Download DOCX report (professional formatting)
- Download Markdown (raw narrative)
- Download JSON (truth block + findings)

### Step 4: Browse History
- View all previous reports by date
- Search by hostname or classification
- Quick re-download functionality

---

## 📁 File Organization

```
data/
├── reports.db                          ← SQLite metadata
├── output/                             ← Temp (auto-archived)
└── archive/
    ├── 2026-04-17/
    │   ├── 20260417_055151/
    │   │   ├── SOC_Report_20260417_055151.docx
    │   │   ├── incident_report_20260417_055151.md
    │   │   ├── incident_20260417_055151.json
    │   │   ├── truth_block_20260417_055151.json
    │   │   └── metadata.json
    │   └── 20260417_053045/
    │       ├── SOC_Report_20260417_053045.docx
    │       └── ...
    └── 2026-04-16/
        └── ...
```

---

## 🔧 Configuration

### Ollama Host
Edit in Streamlit UI sidebar or set environment variable:
```bash
export OLLAMA_HOST=http://your-gpu-server:11434
```

### Database
- Location: `data/reports.db`
- Auto-created on first run
- Searchable by hostname, classification, tags

### Archive
- Location: `data/archive/`
- Auto-created with date-based folders
- Each report gets its own subfolder with metadata

---

## 📊 Module Descriptions

### `app.py` - Main Streamlit Interface
- Tabbed interface (Generate, History, About)
- Hardware status display
- Model selection with validation
- Real-time progress monitoring

### `src/report_database.py` - SQLite Manager
```python
db = ReportDatabase()
db.add_report(run_id, hostname, classification, model_used, time, summary, file_paths)
reports = db.get_all_reports(limit=50)
stats = db.get_stats()
```

### `src/hardware_detector.py` - GPU/RAM Detection
```python
detector = HardwareDetector(ollama_host)
models = detector.get_compatible_models()  # Only suitable models
summary = detector.get_hardware_summary()   # GPU/RAM status
recommended = detector.get_recommended_model()
```

### `src/report_organizer.py` - File Archive Manager
```python
organizer = ReportOrganizer()
organizer.archive_report(run_id, hostname, classification)
report = organizer.get_archived_report(run_id)
reports = organizer.list_archived_reports(limit=20)
docx_path = organizer.get_docx_path(run_id)
```

---

## 🚀 Running on Linux Server (SSH)

### Option 1: Local Tunnel
```bash
# On server
streamlit run app.py --server.port 8501

# On your laptop
ssh -L 8501:localhost:8501 user@server-ip
# Then open: http://localhost:8501
```

### Option 2: Public Access (Secure)
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
# Access from: http://server-ip:8501
```

---

## ⚙️ Advanced Usage

### Customize Hardware Limits
Edit `src/hardware_detector.py`:
```python
MODELS = {
    "your-model": {"vram_gb": 14, "ram_gb": 2, "context": 8192}
}
```

### Add Custom Models
Models are auto-detected from `ollama list`. Just pull them:
```bash
ollama pull your-model:latest
# It appears in Streamlit dropdown automatically
```

### Search Reports
In Report History tab, use search by:
- Hostname
- Classification
- Date range (manual filtering)

---

## 🐛 Troubleshooting

### "No compatible models found"
- Check: `ollama list` (models available?)
- Check GPU: `nvidia-smi` (VRAM available?)
- Restart Ollama: `ollama serve`

### "Connection refused"
- Check Ollama host in sidebar
- Verify: `curl http://ollama-host:11434/api/tags`

### Files not archiving
- Check write permissions on `data/` folder
- Ensure `data/archive/` exists: `mkdir -p data/archive`

### Database locked
- Close Streamlit app
- Delete `data/reports.db` (starts fresh)
- Restart

---

## 📈 Database Queries

```python
from src.report_database import ReportDatabase

db = ReportDatabase()

# All reports
all_reports = db.get_all_reports()

# Search by hostname
reports = db.search_reports("production-server", field="hostname")

# Get stats
stats = db.get_stats()
print(f"Total: {stats['total_reports']}, Avg Time: {stats['avg_processing_time']}s")

# Delete old report
db.delete_report(run_id)
```

---

## 🎨 Customization Tips

### Change Color Scheme
Edit CSS in `app.py`:
```python
# Change brand blue:
BRAND_BLUE = RGBColor(0, 32, 96)  # Dark blue
ACCENT_BLUE = RGBColor(31, 78, 121)  # Medium blue
```

### Add Custom Filters
In Report History tab, add:
```python
date_filter = st.date_input("Filter by date")
# Then filter reports before displaying
```

---

## 📝 Notes

- ✅ Original pipeline untouched (runs as-is)
- ✅ All new code isolated in utils
- ✅ Database auto-created on first run
- ✅ Archive structure maintained for company compatibility
- ✅ Professional frontend for client presentations

---

## Support Log

If issues occur, check logs:
```bash
# Stream logs while running
streamlit run app.py --logger.level=debug
```

---

**Version**: 2026 | **Project**: Final Year Engineering | **Status**: Production Ready
