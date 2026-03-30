import pandas as pd
import logging
import json
import ollama  
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError # Added ValidationError
from src import config

logger = logging.getLogger(__name__)

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
        self.model = model or config.EXTRACTOR_MODEL 
        self.facts: Dict[str, Any] = {}

    def extract_all_facts(self, human_insight: str = "") -> Dict[str, Any]:
        """Extracts facts with robust JSON unwrapping logic."""
        
        raw_evidence = " ".join(self.df['Full_Evidence'].astype(str).head(10).tolist())
        
        # IMPROVEMENT 1: Explicit Schema Instructions
        # We tell the AI exactly what keys we need.
        json_structure = IncidentSchema.model_json_schema()
        
        prompt = f"""
        Analyze these security logs and extract facts into the following JSON format.
        
        REQUIRED SCHEMA:
        {json.dumps(json_structure['properties'], indent=2)}

        LOG DATA:
        {raw_evidence}
        
        ANALYST INSIGHT:
        {human_insight}
        
        INSTRUCTIONS:
        1. Return ONLY the JSON object.
        2. Do NOT wrap the JSON in any top-level keys like 'analysis' or 'incident'.
        3. Identify if this is a network attack or a misconfiguration.
        4. Generate a 'mitre_query' for RAG search.
        """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                keep_alive=config.KEEP_ALIVE, 
                options={
                    "num_ctx": config.NUM_CTX, 
                    "temperature": 0.0 # Lower temperature for stricter JSON
                }
            )
            
            raw_content = response['message']['content']
            extracted_json = json.loads(raw_content)
            
            # IMPROVEMENT 2: Smart Unwrapping
            # If the AI ignores instructions and wraps the JSON, we "unwrap" it.
            if len(extracted_json) == 1 and isinstance(list(extracted_json.values())[0], dict):
                key = list(extracted_json.keys())[0]
                logger.warning(f"⚠️ AI wrapped JSON in '{key}' key. Auto-unwrapping...")
                extracted_json = extracted_json[key]
            
            # Validate with Pydantic
            validated_data = IncidentSchema(**extracted_json)
            
            self.facts = {
                "METADATA": {
                    "run_id": self.run_id,
                    "timestamp": datetime.now().isoformat(),
                    "total_records": len(self.df)
                },
                "FINDINGS": validated_data.model_dump() # Pydantic v2 standard
            }
            
            logger.info(f"✓ Semantic Extraction Complete. Model flushed.")
            return self.facts

        except ValidationError as ve:
            logger.error(f"❌ Schema Validation Error: {ve}")
            return {"error": "AI returned JSON, but it didn't match the required SOC schema."}
        except Exception as e:
            logger.error(f"❌ Semantic Extraction Failed: {e}")
            return {"error": f"Critical extraction failure: {str(e)}"}

    def export_vault(self, output_path: Path):
        with open(output_path, 'w') as f:
            json.dump(self.facts, f, indent=4)
        logger.info(f"Forensic JSON vaulted to: {output_path}")