import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# --- OS-AGNOSTIC PATHING ---
# Resolves the root directory of your SOC Agent project
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
SAVED_DIR = DATA_DIR / "saved"
TEMPLATES_DIR = BASE_DIR / "templates"

# --- RAG & KNOWLEDGE BASE PATHS ---
# New directory for your local ChromaDB vector store
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Ensure all forensic vault and RAG directories exist
for folder in [INPUT_DIR, OUTPUT_DIR, SAVED_DIR, TEMPLATES_DIR, VECTOR_DB_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# --- MODEL & HARDWARE SETTINGS (GPU OPTIMIZED) ---
# We now use a three-model orchestration approach
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# 1. Extractor: Small & Fast for log-to-JSON parsing (GPU 1)
EXTRACTOR_MODEL = os.getenv("EXTRACTOR_MODEL", "qwen2.5:7b")

# 2. Embedder: Lightweight for Vector DB indexing (GPU 1 or 2)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# 3. Writer/Lead Investigator: The "Brain" for the final report (GPU 3 & 4)
REPORT_MODEL = os.getenv("REPORT_MODEL", "deepseek-r1:32b")

# --- PERFORMANCE ---
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 300)) # Increased for 32B model reasoning
NUM_CTX = 32768  # Expanded context window for long logs and RAG injection

# --- FORENSIC VAULT ---
# Path to your professional report format template
REPORT_TEMPLATE = TEMPLATES_DIR / "report_format.txt"