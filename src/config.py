import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables if present
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
EXTRACTOR_MODEL = os.getenv("EXTRACTOR_MODEL", "qwen2.5:7b")
if not EXTRACTOR_MODEL:
    EXTRACTOR_MODEL = "qwen2.5:7b"

# 2. Embedder: Nomic (Uses <1GB VRAM)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
if not EMBEDDING_MODEL:
    EMBEDDING_MODEL = "nomic-embed-text"

# 3. Writer: DeepSeek-R1 (Uses ~19GB VRAM)
# Note: 32B fits in 24GB, but only if Qwen is flushed out first!
REPORT_MODEL = os.getenv("REPORT_MODEL", "deepseek-r1:32b")
if not REPORT_MODEL:
    REPORT_MODEL = "deepseek-r1:32b"

# --- SEQUENTIAL PROCESSING SETTINGS ---
# '0' tells Ollama to UNLOAD the model from GPUs immediately after use.
# This makes room for the next model so they don't fight for VRAM.
KEEP_ALIVE = 0 

# --- PERFORMANCE ---
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 600)) # 10 mins for deep reasoning
NUM_CTX = 16384  # 16k is safer for 24GB VRAM to avoid 'Out of Memory' crashes

# --- FORENSIC VAULT ---
REPORT_TEMPLATE = TEMPLATES_DIR / "report_format.txt"