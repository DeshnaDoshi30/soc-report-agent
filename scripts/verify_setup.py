import sys
import socket
import json
import logging
from pathlib import Path
import subprocess

# --- MODULAR IMPORT FIX ---
# Ensures we can find config.py even if run from /scripts
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    import config
    import ollama
    import chromadb
    from pydantic import BaseModel
except ImportError as e:
    print(f"✗ CRITICAL: Missing dependencies. Run: pip install -r requirements.txt\nDetail: {e}")
    sys.exit(1)

def check_python_packages():
    """Verifies library health for RAG and Semantic Extraction."""
    packages = {
        'ollama': 'AI Client', 
        'pandas': 'Data Engine', 
        'chromadb': 'Vector Database',
        'pydantic': 'Data Validation',
        'langchain': 'RAG Framework'
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

def check_gpu_status():
    """Verifies if the 4x 8GB GPU setup is visible to the OS."""
    print("\n" + "=" * 60 + "\nCHECKING GPU HARDWARE (NVIDIA-SMI)\n" + "=" * 60)
    try:
        res = subprocess.check_output(["nvidia-smi", "--list-gpus"]).decode('utf-8')
        gpu_count = len(res.strip().split('\n'))
        print(f"✓ Detected {gpu_count} GPU(s).")
        if gpu_count < 4:
            print(f"  ⚠ Warning: Architecture optimized for 4 GPUs, found {gpu_count}.")
        return True
    except Exception:
        print("✗ Could not detect NVIDIA GPUs. Ensure drivers are installed.")
        return False

def check_knowledge_base():
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

def check_multi_model_availability():
    """Verifies all three required models are loaded in Ollama."""
    required_models = [
        config.EXTRACTOR_MODEL, 
        config.EMBEDDING_MODEL, 
        config.REPORT_MODEL
    ]
    
    print("\n" + "=" * 60 + "\nCHECKING OLLAMA MODELS\n" + "=" * 60)
    
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        loaded_models = [m.model for m in client.list().models]
        
        all_present = True
        for target in required_models:
            # Check for partial match (e.g. 'qwen2.5:7b' in 'qwen2.5:7b-instruct-q4_K_M')
            if any(target in m for m in loaded_models):
                print(f"✓ {target:<20} - READY")
            else:
                print(f"✗ {target:<20} - MISSING")
                all_present = False
        
        if not all_present:
            print(f"\nAction: Run './scripts/pull_model.sh --setup-all'")
        return all_present
    except Exception as e:
        print(f"✗ Service unreachable or error querying models: {e}")
        return False

def main():
    print(f"\n🛡️ SOC Agent Semantic Stack Audit | Version: 2026\n" + "#" * 60)
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
        print("\n🚀 SYSTEM READY FOR INVESTIGATION.")
    else:
        print("\n❌ SYSTEM NOT READY. Resolve failures above.")
    
    return 0 if final_status else 1

if __name__ == "__main__":
    sys.exit(main())