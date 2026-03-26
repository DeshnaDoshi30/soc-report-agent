import pandas as pd
import logging
import json
import ollama  # Using the local Ollama library
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Setup professional logging
logger = logging.getLogger(__name__)

# --- STEP 1: Define the mold (The Truth Block) ---
class IncidentSchema(BaseModel):
    primary_classification: str = Field(description="Calculated category of the incident")
    target_ips: list[str] = Field(default_factory=list)
    file_paths: list[str] = Field(default_factory=list)
    permission_bits: str = Field(default="N/A")
    mitre_query: str = Field(description="A search query for the RAG pipeline to find relevant MITRE techniques")
    technical_summary: str = Field(description="A brief technical explanation of the log findings")

class SemanticExtractor:
    def __init__(self, df: pd.DataFrame, run_id: str = "N/A", model: str = "qwen2.5:7b"):
        self.df = df
        self.run_id = run_id
        self.model = model
        self.facts: Dict[str, Any] = {}

    def extract_all_facts(self, human_insight: str = "") -> Dict[str, Any]:
        """Replaces regex signatures with LLM-based semantic extraction."""
        
        # 1. Prepare the raw evidence for the LLM
        # We sample or chunk the 'Full_Evidence' to stay within VRAM limits
        raw_evidence = " ".join(self.df['Full_Evidence'].astype(str).head(10).tolist())
        
        # 2. Construct the Semantic Prompt
        prompt = f"""
        Analyze these security logs and extract facts into the required JSON format.
        
        LOG DATA:
        {raw_evidence}
        
        ANALYST INSIGHT:
        {human_insight}
        
        INSTRUCTIONS:
        1. Identify if this is a network attack or a misconfiguration.
        2. Extract all IPs and File Paths.
        3. Generate a 'mitre_query' for a vector database search.
        4. Return ONLY valid JSON.
        """

        try:
            # 3. Call the local LLM on GPU 1
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json' # Force JSON output
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
            
            return self.facts

        except Exception as e:
            logger.error(f"Semantic Extraction Failed: {e}")
            return {"error": "Extraction failed, falling back to basic metadata."}

    def export_vault(self, output_path: Path):
        """Save the JSON Truth Block to the Forensic Vault."""
        with open(output_path, 'w') as f:
            json.dump(self.facts, f, indent=4)
        logger.info(f"Forensic JSON vaulted to: {output_path}")