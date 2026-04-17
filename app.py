"""
SOC Report Agent — Streamlit Web UI
Navy + slate enterprise theme for internal SOC analyst use.
Run: streamlit run app.py
"""

import streamlit as st
import sys
import logging
from pathlib import Path
import time
import os

sys.path.insert(0, str(Path(__file__).parent))

from src.hardware_detector import HardwareDetector
from src.report_database import ReportDatabase
from src.report_organizer import ReportOrganizer
from src.pipeline import UnifiedPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="iSecurify · SOC Report Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --navy-950: #060F1C;
    --navy-900: #0B1E35;
    --navy-800: #112848;
    --navy-700: #163258;
    --blue-500: #1D6FEB;
    --blue-400: #3B8BFF;
    --blue-100: rgba(29,111,235,0.10);
    --blue-border: rgba(29,111,235,0.20);
    --slate-50:  #F7F9FC;
    --slate-100: #EEF2F7;
    --slate-200: #DDE3ED;
    --slate-400: #8898B0;
    --slate-600: #4A5A70;
    --slate-800: #1C2B3A;
    --success:   #16A34A;
    --warning:   #CA8A04;
    --error:     #DC2626;
    --mono: 'IBM Plex Mono', 'Courier New', monospace;
    --sans: 'IBM Plex Sans', system-ui, sans-serif;
}

/* ── Base ── */
html, body, [class*="css"] { font-family: var(--sans) !important; }
.main .block-container {
    background: var(--slate-50);
    max-width: 100%;
    padding: 0.8rem 1.2rem 1.2rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--navy-900) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 215px !important;
    max-width: 230px !important;
}
section[data-testid="stSidebar"] * { color: #A8BACE !important; font-family: var(--sans) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #E4EDF6 !important; }
section[data-testid="stSidebar"] .stMetric         { background: rgba(255,255,255,0.04) !important; border-radius: 6px; padding: 8px 10px; }
section[data-testid="stSidebar"] .stMetric label   { color: #6A7F96 !important; font-size: 10px !important; font-weight: 700 !important; }
section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] { color: #E4EDF6 !important; font-family: var(--mono) !important; font-size: 16px !important; font-weight: 800 !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: #A8BACE !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    border-radius: 5px;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #7A93AC !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-align: left !important;
    padding: 6px 10px !important;
    border-radius: 5px !important;
    width: 100% !important;
    transition: background 0.15s, color 0.15s;
    letter-spacing: 0.3px;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(29,111,235,0.15) !important;
    color: #93C5FD !important;
    font-weight: 800 !important;
}

/* Active nav item — applied via a wrapper class we inject */
.nav-active .stButton > button {
    background: rgba(29,111,235,0.15) !important;
    color: #7EC8FF !important;
    font-weight: 600 !important;
}

/* ── Wordmark ── */
.wordmark {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 4px;
    padding: 0.6rem 0;
    margin-bottom: 0.8rem;
    border: none;
}
.wordmark-name {
    font-family: var(--sans);
    font-size: 32px;
    font-weight: 800;
    color: var(--navy-900);
    letter-spacing: -0.5px;
    margin: 0;
}
.wordmark-tag {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #fff;
    background: var(--blue-500);
    border: none;
    border-radius: 4px;
    padding: 3px 12px;
}

/* ── Page title ── */
.page-title {
    font-family: var(--sans);
    font-size: 13px;
    font-weight: 700;
    color: var(--slate-600);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}
.page-divider {
    border: none;
    border-top: 1px solid var(--slate-200);
    margin: 4px 0 8px;
}

/* ── Expander (section card) ── */
.streamlit-expanderHeader {
    background: var(--navy-800) !important;
    border: 1px solid var(--navy-700) !important;
    border-radius: 6px !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #fff !important;
    padding: 10px 14px !important;
}
.streamlit-expanderHeader:hover { background: var(--navy-700) !important; border-color: var(--blue-500) !important; }
.streamlit-expanderContent {
    border: 1px solid var(--navy-700) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    background: #fff !important;
    padding: 12px 14px !important;
}
div[data-testid="stExpander"] { margin-bottom: 6px; }

/* ── Buttons ── */
.stButton > button {
    background: var(--navy-800) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    padding: 8px 16px !important;
    transition: background 0.15s;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.stButton > button:hover { background: var(--blue-500) !important; }

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    border: 1px solid var(--navy-700) !important;
    border-radius: 6px !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--navy-800) !important;
    background: #fff !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--blue-500) !important;
    box-shadow: 0 0 0 3px rgba(29,111,235,0.12) !important;
}
.stFileUploader {
    border: 1px dashed var(--slate-200) !important;
    border-radius: 7px !important;
    background: #fff !important;
}

/* ── Metrics in main area ── */
.main [data-testid="metric-container"] {
    background: var(--navy-800);
    border: 1px solid var(--navy-700);
    border-radius: 6px;
    padding: 8px 12px;
}
.main [data-testid="metric-container"] label { font-size: 10px !important; color: #A8BACE !important; font-family: var(--mono) !important; font-weight: 700 !important; }
.main [data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 16px !important; color: #fff !important; font-weight: 700 !important; }

/* ── Step indicators ── */
.steps-wrap { display:flex; align-items:center; padding: 12px 0; }
.step-node  { display:flex; flex-direction:column; align-items:center; flex: 0 0 auto; }
.step-circle {
    width: 34px; height: 34px;
    border-radius: 50%;
    border: 2px solid var(--slate-200);
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--mono); font-size: 12px; font-weight: 600;
    color: var(--slate-400);
    transition: all 0.3s;
}
.step-circle.active  { border-color: var(--blue-500); background: var(--blue-100); color: var(--blue-500); box-shadow: 0 0 0 4px rgba(29,111,235,0.10); }
.step-circle.done    { border-color: var(--success); background: var(--success); color: #fff; }
.step-circle.error   { border-color: var(--error);   background: var(--error);   color: #fff; }
.step-label  { font-family: var(--sans); font-size: 10px; font-weight: 800; color: var(--navy-800); margin-top: 4px; white-space:nowrap; }
.step-sub    { font-family: var(--mono); font-size: 9px; color: var(--blue-500); white-space:nowrap; font-weight: 600; }
.step-line   { flex: 1; height: 2px; background: var(--slate-200); margin: 0 6px; margin-bottom: 18px; transition: background 0.3s; min-width: 40px; }
.step-line.done   { background: var(--success); }
.step-line.active { background: linear-gradient(90deg, var(--success) 0%, var(--blue-400) 100%); }

/* ── Alerts ── */
.stAlert { border-radius: 6px !important; font-family: var(--sans) !important; font-size: 12px !important; font-weight: 700 !important; }

/* ── Download buttons ── */
.stDownloadButton > button {
    background: var(--navy-800) !important;
    color: #fff !important;
    border: 1px solid var(--navy-700) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 8px 12px !important;
}
.stDownloadButton > button:hover { background: var(--blue-500) !important; }

hr { border-color: var(--slate-200) !important; }

/* ── Caption / small text ── */
.stCaption { font-family: var(--mono) !important; font-size: 11px !important; color: var(--slate-600) !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "generate"
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None


# ── Services (cached) ─────────────────────────────────────────────────────────
@st.cache_resource
def get_services():
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return {
        "detector": HardwareDetector(ollama_host),
        "db":       ReportDatabase(),
        "organizer": ReportOrganizer(),
    }


# ── Step indicator renderer ───────────────────────────────────────────────────
def render_steps(phases: dict):
    """
    phases = {
        1: {"label": "Extraction",  "sub": "Qwen 7B",   "status": "idle"|"active"|"done"|"error"},
        2: {"label": "Embedding",   "sub": "Nomic",      "status": ...},
        3: {"label": "Report Gen",  "sub": "DeepSeek-R1","status": ...},
    }
    """
    items = list(phases.items())
    parts = []

    for i, (num, p) in enumerate(items):
        s = p["status"]
        css = {"active": "active", "done": "done", "error": "error"}.get(s, "")
        icon = "✓" if s == "done" else ("✕" if s == "error" else str(num))

        parts.append(f"""
        <div class="step-node">
            <div class="step-circle {css}">{icon}</div>
            <div class="step-label">{p['label']}</div>
            <div class="step-sub">{p['sub']}</div>
        </div>""")

        if i < len(items) - 1:
            line_css = "done" if s == "done" else ("active" if s == "active" else "")
            parts.append(f'<div class="step-line {line_css}"></div>')

    html = "<div class='steps-wrap'>" + "".join(parts) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Pages ─────────────────────────────────────────────────────────────────────
def page_generate(services):
    detector = services["detector"]
    db       = services["db"]
    organizer = services["organizer"]
    hw       = detector.get_hardware_summary()

    # Section: Input Data
    with st.expander("📂 Input Data", expanded=True):
        input_file = st.file_uploader(
            "Upload forensic log file",
            type=["csv", "txt"],
            help="CSV or TXT exported from SIEM / endpoint agent",
            label_visibility="collapsed",
        )
        if input_file:
            st.caption(f"✓ **{input_file.name}** — {len(input_file.getvalue()):,} bytes")

    # Section: Analyst Context
    with st.expander("🧑‍💻 Analyst Context", expanded=True):
        analyst_insight = st.text_area(
            "Observations",
            placeholder="e.g. Suspected lateral movement. Process hollowing observed.",
            height=60,
            label_visibility="collapsed",
        )

    # Section: Model Selection
    compatible_models = detector.get_compatible_models()
    available_models  = detector.get_available_models()

    with st.expander("🤖 Model Selection", expanded=True):
        if not available_models:
            st.error("No models detected in Ollama. Run `ollama pull <model>` and restart.")
        elif not compatible_models:
            st.warning("Models found but none compatible with current hardware profile.")
        else:
            phase3_models = [m for m in compatible_models if m.get("suitable_for_phase3")]
            if phase3_models:
                labels = {
                    f"{m['name']} · {m.get('vram_needed_gb', '?')}GB": m["name"]
                    for m in phase3_models
                }
                chosen_label = st.selectbox(
                    "Phase 3 model",
                    options=list(labels.keys()),
                    label_visibility="collapsed",
                )
                # ── BUG FIX: store and use session state consistently ──
                st.session_state.selected_model = labels[chosen_label]

                m0 = phase3_models[0]
                c1, c2, c3 = st.columns(3)
                c1.metric("VRAM", f"{m0.get('vram_available_gb', '?')}GB")
                c2.metric("Context", f"{m0.get('context_window', '?')}")
                c3.metric("Safety", f"{m0.get('vram_margin_percent', 0):.0f}%")
            else:
                st.warning("No Phase 3 models available. 14B or 8B model required.")

        with st.expander("🔍 Debug: detection details", expanded=False):
            st.json({
                "available":        available_models,
                "compatible_count": len(compatible_models),
                "gpu_count":        hw["gpu_count"],
                "total_vram_gb":    hw["total_vram_gb"],
            })

    # Run button
    st.markdown("<div style='margin: 8px 0;'>", unsafe_allow_html=True)
    run_clicked = st.button("🚀 GENERATE REPORT", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Pipeline ──
    if not run_clicked:
        return

    if not input_file:
        st.error("Upload a log file before running.")
        return

    # ── BUG FIX: read from session_state, not a local variable ──
    sel_model = st.session_state.selected_model
    if not sel_model:
        st.error("Select a model in the Model Selection section.")
        return

    temp_file = Path("/tmp") / f"soc_{input_file.name}"
    temp_file.write_bytes(input_file.getvalue())

    steps_ph  = st.empty()
    status_ph = st.empty()

    phases = {
        1: {"label": "Extraction", "sub": "Qwen 7B",    "status": "idle"},
        2: {"label": "Embedding",  "sub": "Nomic",       "status": "idle"},
        3: {"label": "Report Gen", "sub": "DeepSeek-R1", "status": "idle"},
    }

    def set_phases(s1, s2, s3):
        phases[1]["status"] = s1
        phases[2]["status"] = s2
        phases[3]["status"] = s3
        with steps_ph.container():
            render_steps(phases)

    try:
        set_phases("active", "idle", "idle")
        status_ph.info("Phase 1 — Extracting indicators and facts from log data…")

        pipeline = UnifiedPipeline(
            input_file=str(temp_file),
            human_insight=analyst_insight,
            model=sel_model,
        )

        start = time.time()

        # Phase 2 — embedding (pipeline.run() handles all three internally;
        # we update the indicators at logical checkpoints around the single call)
        set_phases("done", "active", "idle")
        status_ph.info("Phase 2 — Building embeddings and retrieving context…")

        success = pipeline.run()
        elapsed = time.time() - start

        if success:
            set_phases("done", "done", "done")
            status_ph.success(f"Report generated in {elapsed:.1f}s")

            report_path = organizer.archive_report(pipeline.run_id, "Analysis Host", "")
            if report_path:
                # ── BUG FIX: use sel_model (resolved from session state) ──
                db.add_report(
                    pipeline.run_id,
                    "Analysis Host",
                    model_used=sel_model,
                    processing_time=elapsed,
                    summary="Report generated successfully",
                )

                st.markdown("---")
                st.markdown(
                    f"<span style='font-family:var(--mono);font-size:12px;color:var(--slate-400)'>Run ID: "
                    f"<b style='color:var(--navy-800)'>{pipeline.run_id}</b></span>",
                    unsafe_allow_html=True,
                )

                docx_p = report_path / f"SOC_Report_{pipeline.run_id}.docx"
                md_p   = report_path / f"incident_report_{pipeline.run_id}.md"
                json_p = report_path / f"incident_{pipeline.run_id}.json"

                d1, d2, d3, _ = st.columns([1, 1, 1, 2])
                if docx_p.exists():
                    d1.download_button("📄 DOCX",     docx_p.read_bytes(), f"SOC_Report_{pipeline.run_id}.docx",     key="dl_docx")
                if md_p.exists():
                    d2.download_button("📝 Markdown", md_p.read_text(),    f"incident_report_{pipeline.run_id}.md",  key="dl_md")
                if json_p.exists():
                    d3.download_button("📑 JSON",     json_p.read_text(),  f"incident_{pipeline.run_id}.json",       key="dl_json")
        else:
            set_phases("done", "done", "error")
            status_ph.error("Pipeline failed at report generation phase.")

    except Exception as exc:
        status_ph.error(f"Unexpected error: {exc}")
        logger.exception("Pipeline error")
    finally:
        if temp_file.exists():
            temp_file.unlink()


def page_history(services):
    organizer = services["organizer"]

    col_a, col_b, col_c = st.columns([1.2, 2, 0.8])
    with col_a:
        st.selectbox("Filter by", ["All", "Hostname", "Classification"], label_visibility="collapsed")
    with col_b:
        st.text_input("Search", placeholder="Search reports…", label_visibility="collapsed")
    with col_c:
        st.button("Search", use_container_width=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    reports = organizer.list_archived_reports(limit=20)
    if not reports:
        st.info("No reports archived yet. Generate your first report to get started.")
        return

    for report in reports:
        host = report.get("hostname", "Unknown Host")
        date = report.get("archived_date", "N/A")
        with st.expander(f"📊  {host}  ·  {date}", expanded=False):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(
                    f"**Run ID:** `{report['run_id']}`  \n"
                    f"**Classification:** {report.get('primary_classification', 'N/A')}  \n"
                    f"**Date:** {date}"
                )
            with c2:
                files = report.get("files", {})
                if files:
                    st.markdown("**Files available:**")
                    for ft in files:
                        st.caption(f"· {ft}")

            files = report.get("files", {})
            d1, d2, d3 = st.columns(3)

            soc_file = files.get("SOC", "")
            if soc_file:
                p = Path(__file__).parent / "data" / soc_file
                if p.exists():
                    d1.download_button("📄 DOCX", p.read_bytes(), key=f"docx_{report['run_id']}")

            inc_file = files.get("incident", "")
            if inc_file:
                p = Path(__file__).parent / "data" / inc_file
                if p.exists():
                    d2.download_button("📝 Markdown", p.read_text(), key=f"md_{report['run_id']}")
                    if p.with_suffix(".json").exists():
                        d3.download_button("📑 JSON", p.with_suffix(".json").read_text(), key=f"json_{report['run_id']}")


def page_about():
    st.markdown("""
    **iSecurify SOC Report Agent** automates forensic investigation log analysis
    and produces professional, structured reports for review.

    | Component | Technology |
    |---|---|
    | Fact Extraction | Qwen 2.5 7B |
    | Embedding | Nomic Embed Text |
    | Report Generation | DeepSeek-R1 |
    | Knowledge Base | ChromaDB (RAG) |
    | Interface | Streamlit |

    **Pipeline overview:**
    Upload forensic logs → Extract indicators (Phase 1) →
    Build embeddings & retrieve context (Phase 2) →
    Generate 5-page report (Phase 3) → Export DOCX / MD / JSON

    All processing runs locally. No data leaves the machine.
    Archives stored at `data/archive/YYYY-MM-DD/<run_id>/`.
    """)
    st.caption("Version: 2026  ·  Final Year Engineering Project")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    services = get_services()
    detector  = services["detector"]
    db        = services["db"]
    hw        = detector.get_hardware_summary()
    stats     = db.get_stats()

    # ── Sidebar ──
    with st.sidebar:
        # Wordmark
        st.markdown("""
        <div style="padding:12px 6px 12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:12px;">
            <span style="font-family:'IBM Plex Sans',sans-serif; font-size:14px; font-weight:800; color:#E4EDF6; letter-spacing:-0.3px;">
                iSecurify
            </span>
            <span style="font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:800; letter-spacing:1px;
                         text-transform:uppercase; color:#fff;
                         background:#1D6FEB; border:none;
                         border-radius:3px; padding:2px 6px; margin-left:6px; vertical-align:middle;">
                SOC
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Navigation label
        st.markdown(
            "<p style='font-size:10px;font-weight:800;letter-spacing:1.2px;"
            "text-transform:uppercase;color:#60A5FA;margin:0 0 8px 4px'>Navigation</p>",
            unsafe_allow_html=True
        )

        nav_items = {
            "generate": "⚡ Generate",
            "history":  "📋 History",
            "about":    "ℹ️ About",
        }
        # ── BUG FIX: sidebar buttons drive routing via session_state + st.rerun() ──
        # No query params, no broken conditionals.
        for key, label in nav_items.items():
            # Highlight active page by wrapping in a div with the nav-active class
            if st.session_state.page == key:
                st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()
            if st.session_state.page == key:
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0'>",
            unsafe_allow_html=True
        )

        # Hardware
        st.markdown(
            "<p style='font-size:10px;font-weight:800;letter-spacing:1.2px;"
            "text-transform:uppercase;color:#60A5FA;margin:0 0 8px 4px'>Hardware</p>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        c1.metric("GPUs",  hw["gpu_count"])
        c2.metric("VRAM",  f"{hw['total_vram_gb']}GB")
        st.metric("RAM",   f"{hw['available_ram_gb']}GB free")

        if hw["gpu_count"] == 0:
            st.caption("⚠️ No GPU detected — inference will use system RAM.")

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0'>",
            unsafe_allow_html=True
        )

        # DB stats
        st.markdown(
            "<p style='font-size:10px;font-weight:800;letter-spacing:1.2px;"
            "text-transform:uppercase;color:#60A5FA;margin:0 0 8px 4px'>Stats</p>",
            unsafe_allow_html=True
        )
        st.caption(f"Reports: **{stats.get('total_reports', 0)}**")
        st.caption(f"Hosts: **{stats.get('unique_hosts', 0)}**")
        st.caption(f"Avg time: **{stats.get('avg_processing_time', 0):.1f}s**")

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0'>",
            unsafe_allow_html=True
        )

        # Config
        st.markdown(
            "<p style='font-size:10px;font-weight:800;letter-spacing:1.2px;"
            "text-transform:uppercase;color:#60A5FA;margin:0 0 6px 4px'>Config</p>",
            unsafe_allow_html=True
        )
        st.text_input(
            "Ollama host",
            value=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            label_visibility="collapsed",
        )

    # ── Main content ──
    # Brand header (centered, large)
    st.markdown("""
    <div style='text-align: center; padding: 0.4rem 0; margin-bottom: 0.6rem;'>
        <h1 style='margin: 0; font-size: 40px; font-weight: 800; color: var(--navy-900); letter-spacing: -0.5px;'>
            SOC Report Agent
        </h1>
        <p style='margin: 2px 0 0 0; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--blue-500);'>
            🛡️ iSecurify Forensic Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Route
    if st.session_state.page == "generate":
        page_generate(services)
    elif st.session_state.page == "history":
        page_history(services)
    elif st.session_state.page == "about":
        page_about()


if __name__ == "__main__":
    main()