"""
SOC Report Agent - Streamlit Web UI
Professional interface for forensic report generation
Run: streamlit run app.py
"""
import streamlit as st
import sys
import logging
from pathlib import Path
from datetime import datetime
import time
import subprocess
import os
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.hardware_detector import HardwareDetector
from src.report_database import ReportDatabase
from src.report_organizer import ReportOrganizer
from src.pipeline import UnifiedPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="iSecurify SOC Report Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main { max-width: 1400px; margin: 0 auto; }
    .header-blue { color: #001F4F; font-weight: bold; }
    .success-box { 
        background-color: #E8F5E9; 
        padding: 1rem; 
        border-left: 4px solid #4CAF50;
        border-radius: 4px;
    }
    .warning-box { 
        background-color: #FFF3E0; 
        padding: 1rem; 
        border-left: 4px solid #FF9800;
        border-radius: 4px;
    }
    .error-box { 
        background-color: #FFEBEE; 
        padding: 1rem; 
        border-left: 4px solid #F44336;
        border-radius: 4px;
    }
    /* Light theme and layout overrides */
    body {
        background-color: #ffffff;
        color: #222222;
    }
    /* Top row: title centered, nav at right */
    .top-row { display:flex; align-items:center; justify-content:center; position:relative; padding:12px 0; }
    .top-row .title { flex:1; text-align:center; }
    .top-row .nav { position:absolute; right:20px; top:8px; }
    .nav-btn { background:#1E90FF; color:#fff; padding:8px 12px; margin-left:8px; border-radius:8px; text-decoration:none; font-weight:600; }
    .nav-btn:hover { opacity:0.95; }
    /* Make main Streamlit buttons larger and blue */
    .stButton>button {
        background-color: #1E90FF !important;
        color: white !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    /* TextArea and FileUploader width harmonization */
    textarea, .stFileUploader { width:100% !important; }
    .stTextArea textarea { min-height: 160px !important; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

def initialize_services():
    """Initialize detectors and databases."""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    return {
        'detector': HardwareDetector(ollama_host),
        'db': ReportDatabase(),
        'organizer': ReportOrganizer()
    }

def main():
    # Header (centered) - removed logo and top divider per UI request
    st.markdown(
        "<div style='text-align:center; margin-top:8px'>\n"
        "<h1 class='header-blue'>🛡️ iSecurify SOC Report Agent</h1>\n"
        "<div style='font-style:italic; color:#555;'>Professional Forensic Investigation & Report Generation</div>\n"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Initialize services
    services = initialize_services()
    detector = services['detector']
    db = services['db']
    organizer = services['organizer']
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Ollama Host
        ollama_host = st.text_input(
            "Ollama Host",
            value=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            help="Ollama server address"
        )
        
        # Hardware Status
        st.markdown("### 🎮 Hardware Status")
        hw_summary = detector.get_hardware_summary()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("GPU Count", hw_summary['gpu_count'])
            st.metric("Available VRAM", f"{hw_summary['total_vram_gb']} GB")
        with col2:
            st.metric("Available RAM", f"{hw_summary['available_ram_gb']} GB")
        
        # Warning if GPU detection failed
        if hw_summary['gpu_count'] == 0:
            st.warning("""
            ⚠️ **GPU detection unavailable**
            
            This is OK if:
            - nvidia-smi isn't in PATH
            - System has enough RAM for models
            - Ollama handles GPU automatically
            
            Models will still work if system RAM is sufficient.
            """)
        
        st.markdown("### 📊 Database Stats")
        stats = db.get_stats()
        st.write(f"**Total Reports:** {stats.get('total_reports', 0)}")
        st.write(f"**Unique Hosts:** {stats.get('unique_hosts', 0)}")
        st.write(f"**Avg Time:** {stats.get('avg_processing_time', 0):.1f}s")
    
    # Top navigation (title centered, nav buttons at top-right using query params)
    # Use a safe fallback if `experimental_get_query_params` is not available in this Streamlit build
    get_qparams = getattr(st, 'experimental_get_query_params', None)
    if callable(get_qparams):
        try:
            params = get_qparams()
        except Exception:
            params = {}
    else:
        params = {}

    qpage = params.get('page', [None])[0] if params else None
    if qpage:
        st.session_state.page = qpage
    if 'page' not in st.session_state:
        st.session_state.page = 'generate'

    st.markdown(
        "<div class='top-row'>"
        "<div class='title'><h1 class='header-blue' style='margin:0;'>🛡️ iSecurify SOC Report Agent</h1><div style='font-style:italic; color:#555;'>Professional Forensic Investigation & Report Generation</div></div>"
        "<div class='nav'>"
        "<a class='nav-btn' href='?page=generate'>Generate Report</a>"
        "<a class='nav-btn' href='?page=history'>Report History</a>"
        "<a class='nav-btn' href='?page=about'>About</a>"
        "</div></div>", unsafe_allow_html=True
    )

    # Page content
    if st.session_state.page == 'generate':
        st.markdown("<h2 style='text-align:center; margin-top:6px;'>Generate New Forensic Report</h2>", unsafe_allow_html=True)

        # Two-column layout: Input Data (left) and Analyst (right)
        col1, col2 = st.columns([1,1])

        with col1:
            st.markdown("### 📂 Input Data")
            
            # File selection
            input_file = st.file_uploader(
                "Select CSV log file",
                type=['csv', 'txt'],
                help="Upload forensic log data (CSV or TXT)"
            )
            
            if input_file:
                st.success(f"✓ File loaded: {input_file.name}")
            
        # Analyst insight on the right column
        with col2:
            st.markdown("### 🧑‍💻 Analyst Insight")
            analyst_insight = st.text_area(
                "Analyst Insight (Optional)",
                placeholder="Enter initial observations or hypothesis...",
                height=160,
                help="Provide context to guide the AI analysis"
            )

        # Centered Run Pipeline button below both columns (bigger styled button)
        st.markdown("<div style='text-align:center; margin-top:18px;'>", unsafe_allow_html=True)
        run_col1, run_col2, run_col3 = st.columns([1,2,1])
        with run_col2:
            if st.button("🚀 Generate Report", key="run_generate"):
                st.session_state._trigger_run = True
        st.markdown("</div>", unsafe_allow_html=True)

        # Placeholder for model selection - moved to bottom of page and rendered later
        # We'll collect compatible/available models now for later rendering
        compatible_models = detector.get_compatible_models()
        available_models = detector.get_available_models()
        model_options = {}
        selected_model = None
        
        # Run logic triggered by centered button
        status_placeholder = st.empty()
        if st.session_state.get('_trigger_run'):
            # reset trigger
            st.session_state._trigger_run = False

            if not input_file:
                st.error("❌ Please select an input file first")
            else:
                st.session_state.running = True
                temp_file = Path("/tmp") / f"temp_{input_file.name}"
                temp_file.write_bytes(input_file.getvalue())
                try:
                    with status_placeholder.container():
                        st.info("🔄 Pipeline running...")

                    # If no model selected in session, try to pick first compatible phase3
                    sel_model = st.session_state.get('selected_model')
                    if not sel_model and compatible_models:
                        phase3_models = [m for m in compatible_models if m.get('suitable_for_phase3')]
                        if phase3_models:
                            sel_model = phase3_models[0]['name']

                    if not sel_model:
                        status_placeholder.error("❌ No model selected or compatible. Please select a model from the Model Selection panel below.")
                    else:
                        start_time = time.time()
                        pipeline = UnifiedPipeline(
                            input_file=str(temp_file),
                            human_insight=analyst_insight,
                            model=sel_model
                        )
                        success = pipeline.run()
                        processing_time = time.time() - start_time

                        if success:
                            status_placeholder.success(f"✅ Report generated in {processing_time:.1f}s")
                            report_path = organizer.archive_report(pipeline.run_id, "Analysis Host", "")
                            if report_path:
                                db.add_report(pipeline.run_id, "Analysis Host", model_used=selected_model, processing_time=processing_time, summary="Report generated successfully")
                                st.markdown("#### 📊 Report Generated!")
                                st.success(f"Run ID: `{pipeline.run_id}`")
                                docx_path = report_path / f"SOC_Report_{pipeline.run_id}.docx"
                                md_path = report_path / f"incident_report_{pipeline.run_id}.md"
                                json_path = report_path / f"incident_{pipeline.run_id}.json"
                                col_d1, col_d2, col_d3 = st.columns(3)
                                with col_d1:
                                    if docx_path.exists():
                                        st.download_button("📄 Download DOCX", docx_path.read_bytes(), f"SOC_Report_{pipeline.run_id}.docx")
                                with col_d2:
                                    if md_path.exists():
                                        st.download_button("📝 Download MD", md_path.read_text(), f"incident_report_{pipeline.run_id}.md")
                                with col_d3:
                                    if json_path.exists():
                                        st.download_button("📑 Download JSON", json_path.read_text(), f"incident_{pipeline.run_id}.json")
                        else:
                            status_placeholder.error("❌ Pipeline failed")
                except Exception as e:
                    status_placeholder.error(f"❌ Error: {str(e)}")
                finally:
                    st.session_state.running = False
                    if temp_file.exists():
                        temp_file.unlink()
        # --- Model Selection panel (moved to bottom of page, centered) ---
        st.markdown("<hr style='margin-top:24px;margin-bottom:12px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>👩‍💻 Model Selection</h3>", unsafe_allow_html=True)
        # center the selectbox and info cards
        sel_c1, sel_c2, sel_c3 = st.columns([1,2,1])
        with sel_c2:
            with st.expander("🔍 Debug: Model Detection"):
                st.write(f"**Available models from Ollama:** {available_models}")
                st.write(f"**Compatible models count:** {len(compatible_models)}")
                st.write(f"**GPU Info:** {hw_summary['gpu_count']} GPUs, {hw_summary['total_vram_gb']}GB VRAM")

            if not available_models:
                st.error("❌ No models found in Ollama. See sidebar instructions to install/start Ollama.")
            elif not compatible_models:
                st.error("❌ Models found but none compatible with current hardware.")
            else:
                phase3_models = [m for m in compatible_models if m.get('suitable_for_phase3')]
                if phase3_models:
                    model_options = {f"{m['name']} ({m.get('vram_needed_gb','?')}GB VRAM)": m['name'] for m in phase3_models}
                    selected_label = st.selectbox("Select Model for Report Generation (Phase 3)", options=list(model_options.keys()))
                    # store the selected model name for the run
                    st.session_state.selected_model = model_options.get(selected_label)
                    # show details centered
                    info_a, info_b, info_c = st.columns(3)
                    with info_a:
                        st.info(f"🎯 VRAM: {phase3_models[0].get('vram_available_gb','?')}GB available")
                    with info_b:
                        st.info(f"📏 Context: {phase3_models[0].get('context_window','?')} tokens")
                    with info_c:
                        st.info(f"✅ Safety: {phase3_models[0].get('vram_margin_percent',0):.1f}% margin")
                else:
                    st.warning("⚠️ Compatible models available but none are suitable for Phase 3 (14B/8B required).")
    
    if st.session_state.page == 'history':
        st.markdown("## 📋 Report History")
        
        # Search/filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_type = st.selectbox("Search by:", ["All", "Hostname", "Classification"])
        with col2:
            search_query = st.text_input("Search query")
        with col3:
            if st.button("🔍 Search"):
                pass
        
        st.divider()
        
        # Get reports
        reports = organizer.list_archived_reports(limit=20)
        
        if reports:
            for report in reports:
                with st.expander(f"📊 {report.get('hostname', 'Unknown')} - {report.get('archived_date', 'N/A')}"):
                    col1, col2 = st.columns([0.7, 0.3])
                    
                    with col1:
                        st.write(f"**Run ID:** `{report['run_id']}`")
                        st.write(f"**Classification:** {report.get('primary_classification', 'N/A')}")
                        st.write(f"**Date:** {report.get('archived_date', 'N/A')}")
                    
                    with col2:
                        files = report.get('files', {})
                        if files:
                            st.write("**Available Files:**")
                            for file_type in files:
                                st.write(f"• {file_type}")
                    
                    # Download options
                    st.markdown("**Downloads:**")
                    col_d1, col_d2, col_d3 = st.columns(3)
                    
                    if 'SOC' in report.get('files', {}):
                        docx_path = Path(__file__).parent / "data" / report['files']['SOC']
                        if docx_path.exists():
                            with col_d1:
                                st.download_button(
                                    "📄 DOCX",
                                    docx_path.read_bytes(),
                                    key=f"docx_{report['run_id']}"
                                )
                    
                    if 'incident' in report.get('files', {}):
                        md_path = Path(__file__).parent / "data" / report['files']['incident']
                        if md_path.exists():
                            with col_d2:
                                st.download_button(
                                    "📝 Markdown",
                                    md_path.read_text(),
                                    key=f"md_{report['run_id']}"
                                )
                    
                    if 'incident_20' in str(report.get('files', {})):
                        json_path = Path(__file__).parent / "data" / report['files'].get('incident', '')
                        if json_path.exists():
                            with col_d3:
                                st.download_button(
                                    "📑 JSON",
                                    json_path.read_text(),
                                    key=f"json_{report['run_id']}"
                                )
        else:
            st.info("No reports found. Generate your first report to get started!")
    
    if st.session_state.page == 'about':
        st.markdown("## About iSecurify SOC Report Agent")
        
        st.markdown("""
        ### 🎯 Purpose
        Automated forensic investigation and professional SOC report generation using AI-powered analysis.
        
        ### ⚙️ Technology Stack
        - **Extraction**: Qwen 2.5 7B (semantic fact extraction)
        - **Embedding**: Nomic Embed Text (knowledge retrieval)
        - **Reasoning**: DeepSeek-R1 (phased report generation)
        - **RAG**: ChromaDB (knowledge base search)
        - **UI**: Streamlit (modern web interface)
        
        ### 🚀 How It Works
        1. **Analyze**: Upload forensic logs (CSV/TXT)
        2. **Extract**: Qwen identifies key indicators and classifications
        3. **Retrieve**: ChromaDB injects historical context
        4. **Generate**: DeepSeek writes professional 5-page report
        5. **Export**: Download formatted DOCX with corporate branding
        
        ### 📊 Report Format
        - Executive summary
        - Technical deep-dive
        - Strategic recommendations
        - Professional iSecurify branding
        - Confidentiality footer
        
        ### 🔐 Data Protection
        - All files archived in `data/archive/YYYY-MM-DD/run_id/`
        - SQLite database for report history
        - Local processing (no cloud uploads)
        
        *Version: 2026 | Project: Final Year Engineering | Company Ready*
        """)

if __name__ == "__main__":
    main()
