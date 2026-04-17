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
    primary_classification: str = Field(default="Unknown Incident", description="Calculated category of the incident (e.g., Phishing, Brute Force, Unauthorized Access)")
    target_ips: list[str] = Field(default_factory=list, description="List of involved IP addresses")
    file_paths: list[str] = Field(default_factory=list, description="List of involved system file paths")
    permission_bits: str = Field(default="N/A", description="Any file permissions mentioned (e.g., 777, rwxr-xr-x)")
    mitre_query: str = Field(default="Potential Security Threat", description="A concise 3-5 word search query for a security knowledge base")
    technical_summary: str = Field(default="Suspicious activity detected in logs", description="A 2-sentence technical summary of the activity")

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
        
        prompt = f"""You are a Senior SOC Analyst. Analyze the following {input_mode} and extract forensic facts into a JSON object.

REQUIRED JSON OUTPUT STRUCTURE:
{{
  "primary_classification": "Incident category (e.g., Brute Force Attack, Unauthorized Access, Phishing, Data Exfiltration)",
  "target_ips": ["IP addresses involved in the incident"],
  "file_paths": ["File paths or directories mentioned"],
  "permission_bits": "File permissions if mentioned (e.g., 777, rwxr-xr-x) or 'N/A'",
  "mitre_query": "3-5 word MITRE ATT&CK framework search (e.g., 'T1110 Brute Force Attack')",
  "technical_summary": "2-sentence concise technical description of what happened"
}}

EVIDENCE DATA ({input_mode}):
{raw_evidence}

ANALYST HINT/CONTEXT:
{human_insight if human_insight else "Analyze the evidence objectively."}

MUST-FOLLOW RULES:
1. Return ONLY valid JSON - no markdown, no explanation, no extra text
2. All fields MUST be present in the output
3. For missing data, use:
   - Empty array [] for lists (target_ips, file_paths)
   - "N/A" for string fields that are truly missing
   - "Unknown" only if classification cannot be determined
4. primary_classification: Classify based on the evidence (Brute Force, Unauthorized Access, etc.)
5. technical_summary: Write 2 sentences describing the attack pattern and what was compromised
6. mitre_query: Reference specific MITRE ATT&CK technique IDs when possible"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                keep_alive=config.KEEP_ALIVE, 
                options={
                    "num_ctx": 2048, 
                    "num_predict": 512,
                    "temperature": 0.0,
                    "num_batch": 128 
                }
            )
            
            raw_content = response['message']['content']
            logger.info(f"[DEBUG] Raw AI Response: {raw_content[:200]}...")  # Debug output
            
            extracted_json = json.loads(raw_content)
            
            # Smart Unwrapping (Our previous fix)
            if len(extracted_json) == 1 and isinstance(list(extracted_json.values())[0], dict):
                extracted_json = list(extracted_json.values())[0]
            
            logger.info(f"[DEBUG] Parsed JSON keys: {list(extracted_json.keys())}")
            
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

        except json.JSONDecodeError as je:
            logger.error(f"❌ JSON Parsing Error: {je}")
            logger.error(f"Raw content: {raw_content[:500]}")
            return {"error": f"AI response is not valid JSON: {str(je)}"}
        except ValidationError as ve:
            logger.error(f"❌ Schema Validation Error: {ve}")
            logger.error(f"Extracted data: {extracted_json}")
            return {"error": "AI response did not match the forensic schema."}
        except Exception as e:
            logger.error(f"❌ Extraction Failed: {e}")
            return {"error": str(e)}

    def export_vault(self, output_path: Path):
        with open(output_path, 'w') as f:
            json.dump(self.facts, f, indent=4)
        logger.info(f"Forensic JSON vaulted: {output_path}")