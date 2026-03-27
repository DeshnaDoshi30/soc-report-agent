import pandas as pd
import logging
import json
import ollama  
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import src.config as config # Import your updated 3-GPU config

# Setup professional logging
logger = logging.getLogger(__name__)

# --- STEP 1: Define the mold (The Truth Block) ---
class IncidentSchema(BaseModel):
    primary_classification: str = Field(description="Calculated category of the incident")
    target_ips: list[str] = Field(default_factory=list)
    file_paths: list[str] = Field(default_factory=list)
    permission_bits: str = Field(default="N/A")
    mitre_query: str = Field(description="A search query for the RAG pipeline")
    technical_summary: str = Field(description="A brief technical explanation")

class SemanticExtractor:
    def __init__(self, df: pd.DataFrame, run_id: str = "N/A", model: str | None = None):
        self.df = df
        self.run_id = run_id
        # Uses config.EXTRACTOR_MODEL (qwen2.5:7b) by default
        self.model = model or config.EXTRACTOR_MODEL 
        self.facts: Dict[str, Any] = {}

    def extract_all_facts(self, human_insight: str = "") -> Dict[str, Any]:
        """Replaces regex with LLM extraction + Sequential VRAM Flush."""
        
        # 1. Prepare raw evidence (head(10) to stay safe on VRAM)
        raw_evidence = " ".join(self.df['Full_Evidence'].astype(str).head(10).tolist())
        
        # 2. Construct the Semantic Prompt
        prompt = f"""
        Analyze these security logs and extract facts into JSON.
        
        LOG DATA:
        {raw_evidence}
        
        ANALYST INSIGHT:
        {human_insight}
        
        INSTRUCTIONS:
        1. Identify if this is a network attack or a misconfiguration.
        2. Extract all IPs and File Paths.
        3. Generate a 'mitre_query' for RAG search.
        4. Return ONLY valid JSON.
        """

        try:
            # 3. Call the local LLM with SEQUENTIAL FLUSHING
            # keep_alive=config.KEEP_ALIVE (0) clears the GPU immediately after this call.
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                keep_alive=config.KEEP_ALIVE, # <--- CLEARS GPU FOR DEEPSEEK
                options={
                    "num_ctx": config.NUM_CTX, # Uses 16384 from config
                    "temperature": 0.1
                }
            )
            
            # 4. Parse into our Truth Block
            extracted_json = json.loads(response['message']['content'])
            validated_data = IncidentSchema(**extracted_json)
            
            self.facts = {
                "METADATA": {
                    "run_id": self.run_id,
                    "timestamp": datetime.now().isoformat(),
                    "total_records": len(self.df)
                },
                "FINDINGS": validated_data.dict()
            }
            
            logger.info(f"✓ Semantic Extraction Complete. Model {self.model} flushed from VRAM.")
            return self.facts

        except Exception as e:
            logger.error(f"Semantic Extraction Failed: {e}")
            return {"error": "Extraction failed, falling back to basic metadata."}

    def export_vault(self, output_path: Path):
        """Save the JSON Truth Block to the Forensic Vault."""
        with open(output_path, 'w') as f:
            json.dump(self.facts, f, indent=4)
        logger.info(f"Forensic JSON vaulted to: {output_path}")