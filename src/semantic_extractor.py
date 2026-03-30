import pandas as pd
import logging
import json
import ollama  
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from src import config

logger = logging.getLogger(__name__)

class IncidentSchema(BaseModel):
    primary_classification: str = Field(description="Calculated category of the incident (e.g., Phishing, Brute Force, Unauthorized Access)")
    target_ips: list[str] = Field(default_factory=list, description="List of involved IP addresses")
    file_paths: list[str] = Field(default_factory=list, description="List of involved system file paths")
    permission_bits: str = Field(default="N/A", description="Any file permissions mentioned (e.g., 777, rwxr-xr-x)")
    mitre_query: str = Field(description="A concise 3-5 word search query for a security knowledge base")
    technical_summary: str = Field(description="A 2-sentence technical summary of the activity")

class SemanticExtractor:
    def __init__(self, df: pd.DataFrame, run_id: str = "N/A", model: str | None = None):
        self.df = df
        self.run_id = run_id
        self.model = model or config.EXTRACTOR_MODEL 
        self.facts: Dict[str, Any] = {}

    def extract_all_facts(self, human_insight: str = "") -> Dict[str, Any]:
        """Extracts facts from either raw logs or narrative incident reports."""
        
        # 1. Prepare Evidence
        # If it's a text file, it will likely be 1 big row. If logs, many rows.
        is_narrative = len(self.df) <= 1
        raw_evidence = " ".join(self.df['Full_Evidence'].astype(str).head(15).tolist())
        
        # 2. Context-Aware Instructions
        input_mode = "NARRATIVE REPORT" if is_narrative else "SYSTEM LOG STREAM"
        
        json_structure = IncidentSchema.model_json_schema()
        
        prompt = f"""
        You are a Senior SOC Analyst. Analyze the following {input_mode} and extract forensic facts.
        
        REQUIRED JSON SCHEMA:
        {json.dumps(json_structure['properties'], indent=2)}

        ---
        EVIDENCE DATA ({input_mode}):
        {raw_evidence}
        
        ANALYST INPUT/HINT:
        {human_insight if human_insight else "No additional hints provided."}
        ---

        INSTRUCTIONS:
        1. Return ONLY a flat JSON object. No conversational text.
        2. If data for a field is missing (like permission_bits), use "N/A".
        3. 'mitre_query' should be optimized for a vector database search (e.g., "T1059 Command and Scripting Interpreter").
        4. In {input_mode} mode, look for {'intent and actor descriptions' if is_narrative else 'patterns in IP addresses and timestamps'}.
        """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                keep_alive=config.KEEP_ALIVE, 
                options={
                    "num_ctx": config.NUM_CTX, 
                    "temperature": 0.0 
                }
            )
            
            raw_content = response['message']['content']
            extracted_json = json.loads(raw_content)
            
            # Smart Unwrapping (Our previous fix)
            if len(extracted_json) == 1 and isinstance(list(extracted_json.values())[0], dict):
                extracted_json = list(extracted_json.values())[0]
            
            # Validate with Pydantic
            validated_data = IncidentSchema(**extracted_json)
            
            self.facts = {
                "METADATA": {
                    "run_id": self.run_id,
                    "timestamp": datetime.now().isoformat(),
                    "input_mode": input_mode,
                    "total_records_sampled": len(self.df.head(15))
                },
                "FINDINGS": validated_data.model_dump()
            }
            
            logger.info(f"✓ Semantic Extraction ({input_mode}) Complete.")
            return self.facts

        except ValidationError as ve:
            logger.error(f"❌ Schema Validation Error: {ve}")
            return {"error": "AI response did not match the forensic schema."}
        except Exception as e:
            logger.error(f"❌ Extraction Failed: {e}")
            return {"error": str(e)}

    def export_vault(self, output_path: Path):
        with open(output_path, 'w') as f:
            json.dump(self.facts, f, indent=4)
        logger.info(f"Forensic JSON vaulted: {output_path}")