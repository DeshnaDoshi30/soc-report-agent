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
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
for folder in [INPUT_DIR, OUTPUT_DIR, TEMPLATES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# --- MODEL & HARDWARE SETTINGS ---
# Priorities: .env setting > config.py default
DEFAULT_MODEL = os.getenv("SOC_MODEL", "qwen2.5-coder:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- PERFORMANCE ---
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 120))

# --- FORENSIC VAULT ---
# Path to your report format template
REPORT_TEMPLATE = TEMPLATES_DIR / "report_format.txt"