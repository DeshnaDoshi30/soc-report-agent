"""
Hardware Compatibility Detector
Determines which models can run based on GPU/RAM + input size
"""
import logging
import subprocess
import json
from typing import List, Dict, Tuple, Optional
import psutil

logger = logging.getLogger(__name__)

class ModelCompatibility:
    """Defines model memory requirements."""
    
    # Model name -> (VRAM needed in GB, min system RAM in GB, context window)
    MODELS = {
        "qwen2.5:7b": {"vram_gb": 5, "ram_gb": 1, "context": 2048},
        "deepseek-r1:14b": {"vram_gb": 14, "ram_gb": 2, "context": 8192},
        "deepseek-r1:8b": {"vram_gb": 8, "ram_gb": 1.5, "context": 8192},
        "deepseek-r1:7b": {"vram_gb": 7, "ram_gb": 1, "context": 8192},
        "mistral:latest": {"vram_gb": 6, "ram_gb": 1, "context": 8192},
        "llama2:latest": {"vram_gb": 5, "ram_gb": 1, "context": 4096},
        "neural-chat:latest": {"vram_gb": 4, "ram_gb": 1, "context": 4096},
    }

class HardwareDetector:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.gpu_info = self._get_gpu_info()
        self.sys_mem = self._get_system_memory()
    
    def _get_gpu_info(self) -> Dict:
        """Get GPU VRAM info from nvidia-smi."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.free',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                gpus = {}
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(', ')
                    if len(parts) == 4:
                        gpu_id, name, total, free = parts
                        gpus[int(gpu_id)] = {
                            'name': name.strip(),
                            'total_mb': float(total),
                            'free_mb': float(free)
                        }
                return gpus
        except Exception as e:
            logger.warning(f"GPU detection unavailable: {e}")
        
        return {}
    
    def _get_system_memory(self) -> Dict:
        """Get system RAM info."""
        try:
            vm = psutil.virtual_memory()
            return {
                'total_mb': vm.total / (1024 * 1024),
                'available_mb': vm.available / (1024 * 1024)
            }
        except Exception as e:
            logger.warning(f"System memory detection failed: {e}")
            return {'total_mb': 0, 'available_mb': 0}
    
    def get_available_models(self) -> List[str]:
        """Get list of models available in Ollama."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    parts = line.split()
                    if parts:
                        models.append(parts[0].split(':')[0] if ':' in parts[0] else parts[0])
                return list(set(models))  # Remove duplicates
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {e}")
        
        return []
    
    def get_total_vram(self) -> float:
        """Get total available VRAM across all GPUs in GB."""
        if not self.gpu_info:
            return 0
        
        total_free = sum(gpu['free_mb'] for gpu in self.gpu_info.values())
        return total_free / 1024
    
    def get_compatible_models(self, estimated_context_needed: int = 8000) -> List[Dict]:
        """
        Get list of models that can run with current hardware.
        
        Args:
            estimated_context_needed: Estimated context size needed (in tokens)
        
        Returns:
            List of compatible models with details
        """
        available_models = self.get_available_models()
        total_vram_gb = self.get_total_vram()
        available_ram_gb = self.sys_mem.get('available_mb', 0) / 1024
        
        compatible = []
        
        for model_name in available_models:
            # Check if model is in our known list
            if model_name in ModelCompatibility.MODELS:
                model_spec = ModelCompatibility.MODELS[model_name]
            else:
                # Try to infer from name
                if '14b' in model_name or '14B' in model_name:
                    model_spec = ModelCompatibility.MODELS['deepseek-r1:14b']
                elif '8b' in model_name or '8B' in model_name:
                    model_spec = ModelCompatibility.MODELS['deepseek-r1:8b']
                elif '7b' in model_name or '7B' in model_name:
                    model_spec = ModelCompatibility.MODELS['qwen2.5:7b']
                else:
                    continue  # Skip unknown models
            
            # Check compatibility
            vram_needed = model_spec['vram_gb']
            ram_needed = model_spec['ram_gb']
            
            if total_vram_gb >= vram_needed and available_ram_gb >= ram_needed:
                # Calculate safety margin
                vram_margin = ((total_vram_gb - vram_needed) / total_vram_gb * 100) if total_vram_gb > 0 else 0
                
                compatible.append({
                    'name': model_name,
                    'vram_needed_gb': vram_needed,
                    'vram_available_gb': round(total_vram_gb, 2),
                    'vram_margin_percent': round(vram_margin, 1),
                    'context_window': model_spec['context'],
                    'suitable_for_phase3': True if '14b' in model_name or '8b' in model_name else False
                })
        
        # Sort by VRAM needed (most capable first)
        return sorted(compatible, key=lambda x: x['vram_needed_gb'], reverse=True)
    
    def get_recommended_model(self) -> Optional[str]:
        """Get the best model for Phase 3 (report generation)."""
        models = self.get_compatible_models()
        
        # Prefer 14b > 8b > 7b for Phase 3
        for preference in ['14b', '8b', '7b']:
            for model in models:
                if preference in model['name']:
                    return model['name']
        
        return models[0]['name'] if models else None
    
    def get_hardware_summary(self) -> Dict:
        """Get hardware summary for UI display."""
        return {
            'gpu_count': len(self.gpu_info),
            'total_vram_gb': round(self.get_total_vram(), 1),
            'available_ram_gb': round(self.sys_mem.get('available_mb', 0) / 1024, 1),
            'gpus': self.gpu_info,
            'compatible_models': self.get_compatible_models()
        }
