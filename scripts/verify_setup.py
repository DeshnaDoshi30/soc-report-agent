import sys
import subprocess
import socket
from pathlib import Path

# --- MODULAR IMPORT FIX ---
# Ensures we can find config.py even if run from /scripts
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    import config
    import ollama
except ImportError as e:
    print(f"✗ CRITICAL: Missing dependencies. Run: pip install -r requirements.txt\nDetail: {e}")
    sys.exit(1)

def check_python_packages():
    """Verifies internal library health."""
    packages = {'ollama': 'AI Client', 'pandas': 'Data Engine', 'requests': 'Networking'}
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

def check_ollama_service():
    """Checks if the engine is responding at the configured host."""
    # Pull host from config instead of hardcoding localhost
    host_url = config.OLLAMA_HOST.replace("http://", "").split(":")
    host = host_url[0]
    port = int(host_url[1]) if len(host_url) > 1 else 11434

    print("\n" + "=" * 60 + f"\nCHECKING OLLAMA SERVICE ({config.OLLAMA_HOST})\n" + "=" * 60)
    
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"✓ Service is active on {host}:{port}")
            return True
    except (socket.error, socket.timeout):
        print(f"✗ Service unreachable at {host}:{port}")
        print("  - If local: Run start_ollama.bat")
        print("  - If office: Check VPN/Network connection")
        return False

def check_model_availability():
    """Verifies the target model is downloaded."""
    target = config.DEFAULT_MODEL
    print("\n" + "=" * 60 + f"\nCHECKING TARGET MODEL: {target}\n" + "=" * 60)
    
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        models = client.list()
        
        # Handle different Ollama library response formats
        model_list = models.models if hasattr(models, 'models') else models.get('models', [])
        
        for m in model_list:
            m_name = getattr(m, 'model', m.get('model', ''))
            if target in m_name:
                print(f"✓ Model {target} is loaded and ready.")
                return True
        
        print(f"✗ Model {target} not found.")
        print(f"  Action: Run pull_model.bat {target}")
        return False
    except Exception as e:
        print(f"✗ Could not query models: {e}")
        return False

def main():
    print(f"\nSOC Agent Setup Audit | Run ID: Diagnostic\n" + "#" * 60)
    results = {
        "Libraries": check_python_packages(),
        "Service": check_ollama_service(),
        "Model": check_model_availability()
    }
    
    print("\n" + "=" * 60 + "\nFINAL AUDIT SUMMARY\n" + "=" * 60)
    for name, passed in results.items():
        print(f"{'✓ PASS' if passed else '✗ FAIL':<10} {name}")
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())