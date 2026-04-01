import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, cast

# --- MODULAR IMPORT FIX ---
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from src import config
    import ollama
    import pandas
    import chromadb
    from pydantic import BaseModel
except ImportError as e:
    print(f"✗ CRITICAL: Missing dependencies. Run: pip install -r requirements.txt\nDetail: {e}")
    sys.exit(1)

def check_python_packages() -> bool:
    """Verifies library health including the new Docx exporter."""
    packages = {
        'ollama': 'AI Client', 
        'pandas': 'Data Engine', 
        'chromadb': 'Vector Database',
        'pydantic': 'Data Validation',
        'docx': 'Word Exporter (python-docx)'
    }
    print("=" * 60 + "\nCHECKING PYTHON LIBRARIES\n" + "=" * 60)
    
    missing = []
    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:<15} - {desc}")
        except ImportError:
            print(f"✗ {pkg:<15} - MISSING")
            missing.append(pkg)
    return not bool(missing)

def check_gpu_status() -> bool:
    """Verifies the 3x 1070 GPU setup is visible."""
    print("\n" + "=" * 60 + "\nCHECKING GPU HARDWARE (NVIDIA-SMI)\n" + "=" * 60)
    try:
        res = subprocess.check_output(["nvidia-smi", "--list-gpus"]).decode('utf-8')
        gpu_count = len(res.strip().split('\n'))
        print(f"✓ Detected {gpu_count} GPU(s).")
        
        # Optimized for your specific 3x 1070 setup
        if gpu_count == 3:
            print("✓ Hardware configuration matches 3-GPU Phased Architecture.")
        elif gpu_count < 3:
            print(f"  ⚠ Warning: Expected 3 GPUs for optimal 14B splitting, found {gpu_count}.")
        
        return gpu_count >= 1
    except Exception:
        print("✗ Could not detect NVIDIA GPUs. Check physical seating and drivers.")
        return False

def check_knowledge_base() -> bool:
    """Checks if the RAG 'Brain' has been initialized."""
    print("\n" + "=" * 60 + "\nCHECKING KNOWLEDGE BASE (RAG)\n" + "=" * 60)
    db_path = Path(config.VECTOR_DB_DIR)
    
    if db_path.exists() and any(db_path.iterdir()):
        print(f"✓ Vector DB found at {db_path}")
        return True
    else:
        print(f"✗ Vector DB is empty or missing at {db_path}")
        print("  Action: Run 'python3 src/ingest_knowledge.py' first.")
        return False

def check_multi_model_availability() -> bool:
    """Verifies all three required models are loaded in Ollama."""
    # Defensive check: ensure config values are strings to satisfy linter
    required_models: List[str] = [
        str(config.EXTRACTOR_MODEL), 
        str(config.EMBEDDING_MODEL), 
        str(config.REPORT_MODEL)
    ]
    
    print("\n" + "=" * 60 + "\nCHECKING OLLAMA MODELS\n" + "=" * 60)
    
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        response = client.list()
        
        # Robustly extract model names, filtering out any None values
        loaded_models: List[str] = [
            str(m.model) for m in response.models if m.model is not None
        ]
        
        all_present = True
        for target in required_models:
            # Type-safe membership check
            if any(target in m for m in loaded_models):
                print(f"✓ {target:<20} - READY")
            else:
                print(f"✗ {target:<20} - MISSING")
                all_present = False
        
        if not all_present:
            print(f"\nAction: Run 'ollama pull {config.REPORT_MODEL}'")
        return all_present
    except Exception as e:
        print(f"✗ Service unreachable or error querying models: {e}")
        return False

def main():
    print(f"\n🛡️ iSecurify Phased Stack Audit | Version: 2026\n" + "#" * 60)
    results = {
        "Libraries": check_python_packages(),
        "Hardware": check_gpu_status(),
        "Knowledge": check_knowledge_base(),
        "Models": check_multi_model_availability()
    }
    
    print("\n" + "=" * 60 + "\nFINAL DEPLOYMENT SUMMARY\n" + "=" * 60)
    for name, passed in results.items():
        print(f"{'✓ PASS' if passed else '✗ FAIL':<10} {name}")
    
    final_status = all(results.values())
    if final_status:
        print("\n🚀 SYSTEM READY FOR PHASED INVESTIGATION.")
    else:
        print("\n❌ SYSTEM NOT READY. Resolve failures above.")
    
    return 0 if final_status else 1

if __name__ == "__main__":
    sys.exit(main())