import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# --- OS-AGNOSTIC PATHING ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
SAVED_DIR = DATA_DIR / "saved"
TEMPLATES_DIR = BASE_DIR / "templates"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Ensure all forensic vault and RAG directories exist
for folder in [INPUT_DIR, OUTPUT_DIR, SAVED_DIR, TEMPLATES_DIR, VECTOR_DB_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# --- MODEL & HARDWARE SETTINGS (3-GPU OPTIMIZED) ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# 1. Extractor: Qwen (Uses ~5GB VRAM)
EXTRACTOR_MODEL = "qwen2.5:7b" 

# 2. Embedder: Nomic (Uses <1GB VRAM)
EMBEDDING_MODEL = "nomic-embed-text"

# 3. Reporter: DeepSeek-R1-14B (Optimized for 10-Series Bandwidth)
# 14B Distilled provides the best 'Reasoning-to-Speed' ratio for 3x 1070s.
REPORT_MODEL = "deepseek-r1:14b"

# --- SEQUENTIAL VRAM MANAGEMENT ---
# '0' ensures that models are flushed immediately. 
# This prevents OOM errors when switching from Qwen to DeepSeek.
KEEP_ALIVE = 0 

# --- INFERENCE PARAMETERS (5-PAGE TARGET) ---
REQUEST_TIMEOUT = 900  
NUM_CTX = 8192         # Sufficient for RAG + JSON context window
NUM_PREDICT = 2048     # Allowed output PER PHASE (Total ~6k tokens)
REPORT_TEMP = 0.6      # Slightly increased for more descriptive 'iSecurify' tone
REPEAT_PENALTY = 1.15  # Prevents repetitive technical loops

# --- PHASED TEMPLATE ARCHITECTURE ---
# Replaced 'report_format.txt' with the new modular suite
GLOBAL_HEADER = TEMPLATES_DIR / "global_header.txt"
PHASE_A = TEMPLATES_DIR / "phase_a.txt"
PHASE_B = TEMPLATES_DIR / "phase_b.txt"
PHASE_C = TEMPLATES_DIR / "phase_c.txt"