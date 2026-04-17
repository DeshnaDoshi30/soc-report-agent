"""
Pre-flight Hardware Validation & Monitoring
Ensures GPU/RAM availability before pipeline starts
"""
import logging
import os
import psutil
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

def get_vram_usage() -> dict:
    """
    Attempt to get VRAM usage from nvidia-smi.
    Returns dict with GPU info or empty dict if nvidia-smi unavailable.
    """
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            gpus = {}
            for line in result.stdout.strip().split('\n'):
                parts = line.split(', ')
                if len(parts) == 4:
                    gpu_id, gpu_name, used, total = parts
                    gpus[gpu_id] = {
                        'name': gpu_name.strip(),
                        'used_mb': float(used),
                        'total_mb': float(total),
                        'free_mb': float(total) - float(used),
                        'used_pct': (float(used) / float(total) * 100) if float(total) > 0 else 0
                    }
            return gpus
    except Exception as e:
        logger.debug(f"nvidia-smi unavailable: {e}")
    return {}

def get_system_memory() -> dict:
    """Get system RAM usage."""
    try:
        vm = psutil.virtual_memory()
        return {
            'total_mb': vm.total / (1024 * 1024),
            'used_mb': vm.used / (1024 * 1024),
            'available_mb': vm.available / (1024 * 1024),
            'percent': vm.percent
        }
    except Exception as e:
        logger.warning(f"Could not get system memory: {e}")
        return {}

def check_preflight() -> Tuple[bool, str]:
    """
    Pre-flight check: Validate VRAM and system RAM availability.
    Returns (is_safe: bool, message: str)
    """
    sys_mem = get_system_memory()
    gpu_info = get_vram_usage()
    
    warnings = []
    
    # System RAM check
    if sys_mem:
        available_gb = sys_mem['available_mb'] / 1024
        if available_gb < 1.0:
            warnings.append(f"⚠️  LOW SYSTEM RAM: Only {available_gb:.1f}GB available (need ≥1GB)")
        elif available_gb < 2.0:
            warnings.append(f"⚠️  TIGHT SYSTEM RAM: Only {available_gb:.1f}GB available (recommend ≥2GB)")
        logger.info(f"📊 System RAM: {sys_mem['used_mb']:.0f}/{sys_mem['total_mb']:.0f}MB ({sys_mem['percent']:.1f}%)")
    
    # VRAM check
    if gpu_info:
        total_free_vram = sum(gpu['free_mb'] for gpu in gpu_info.values())
        logger.info(f"🎮 GPU VRAM Status:")
        for gpu_id, info in sorted(gpu_info.items()):
            logger.info(f"   GPU {gpu_id}: {info['used_mb']:.0f}/{info['total_mb']:.0f}MB "
                       f"({info['used_pct']:.1f}% used)")
        
        # DeepSeek-R1 14B needs ~14GB distributed across GPUs
        if total_free_vram < 13000:  # Less than 13GB free
            warnings.append(f"⚠️  LOW VRAM: Only {total_free_vram/1024:.1f}GB free (need ≥13GB for DeepSeek-R1)")
    else:
        logger.warning("🎮 GPU monitoring unavailable (nvidia-smi not found)")
    
    # Additional warnings
    if warnings:
        msg = "\n".join(warnings)
        logger.warning(f"⚠️  Pre-flight Warnings:\n{msg}")
        return True, msg  # Warnings but continue (not fatal)
    
    return True, "✅ Pre-flight check passed"

def check_file_size(file_path: Path) -> Tuple[bool, str]:
    """
    Check if CSV file is within safe data limits.
    Returns (is_safe: bool, message: str)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    
    # Estimate: ~100KB per row on average
    estimated_rows = (file_size_mb * 1024 * 1024) / 100000
    
    if file_size_mb > 100:
        return False, f"File too large: {file_size_mb:.1f}MB (~{estimated_rows:.0f} rows). Limit: 100MB"
    elif file_size_mb > 50:
        msg = f"Large file ({file_size_mb:.1f}MB, ~{estimated_rows:.0f} rows): Will use chunking"
        logger.warning(f"⚠️  {msg}")
        return True, msg
    elif file_size_mb > 10:
        msg = f"Medium file ({file_size_mb:.1f}MB, ~{estimated_rows:.0f} rows): Monitor memory"
        logger.info(f"ℹ️  {msg}")
        return True, msg
    
    return True, f"✅ File size OK ({file_size_mb:.1f}MB)"

def get_recommended_chunk_size(file_size_mb: float) -> int:
    """
    Calculate safe chunk size based on file size.
    Smaller chunks = more memory safe, but slower.
    """
    if file_size_mb > 50:
        return 2000  # Aggressive chunking for large files
    elif file_size_mb > 20:
        return 5000
    elif file_size_mb > 10:
        return 10000
    else:
        return None  # No chunking needed for small files
