import json
import logging
import ollama  # Using native library for better GPU/Context management
from pathlib import Path
from typing import Optional
import config
from report_validator import HallucinationDetector

# Setup professional logging
logger = logging.getLogger(__name__)

class IncidentReportGenerator:
    def __init__(self, model: Optional[str] = None, ollama_host: Optional[str] = None):
        """
        AI Reasoning Engine optimized for DeepSeek-R1 and GPU Hardware.
        Handles JSON Truth Blocks and RAG Context injection.
        """
        self.model = model or config.REPORT_MODEL
        self.host = ollama_host or config.OLLAMA_HOST
        self.template_dir = config.TEMPLATES_DIR
        self.output_dir = config.OUTPUT_DIR

    def _load_template(self, name: str) -> str:
        path = self.template_dir / name
        return path.read_text(encoding='utf-8') if path.exists() else ""

    def generate_report(self, incident_path: str, rag_context: str, run_id: str) -> bool:
        """
        Synthesizes the final report using the JSON Truth Block and retrieved Knowledge.
        """
        try:
            # 1. Load the Semantic Truth Block (JSON)
            incident_data = json.loads(Path(incident_path).read_text(encoding='utf-8'))
            
            # 2. Load Templates
            system_prompt = self._load_template("prompt_template.txt")
            report_format = self._load_template("report_format.txt")

            # 3. Construct the Lead-Level Authority Prompt
            # We provide the AI with 'Truth' (JSON) + 'Experience' (RAG)
            full_prompt = f"""
            {system_prompt}

            ### 1. EXPERT CONTEXT (RAG)
            Use the following historical reports and compliance guides to inform your tone and recommendations:
            {rag_context}

            ### 2. PRIMARY INCIDENT TRUTH (JSON)
            Extract the specific facts from this validated forensic data:
            {json.dumps(incident_data, indent=2)}

            ### 3. REQUIRED REPORT STRUCTURE
            Follow this format exactly:
            {report_format}

            STRICT INSTRUCTION: 
            - Do not mention 'JSON' or 'RAG' in the report. 
            - Match the professional Tier 3 tone of your historical context.
            - Prioritize 'Analyst Notes' found in the JSON data.
            """

            logger.info(f"Generating Lead-Level Report with {self.model} (Context: {config.NUM_CTX})")
            
            # 4. AI Generation (Optimized for 32GB VRAM)
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': full_prompt}],
                options={
                    "num_ctx": config.NUM_CTX,
                    "temperature": 0.3 # Low temp for factual reporting
                }
            )
            
            raw_report = response['message']['content']

            # 5. POST-PROCESSING: Handle DeepSeek-R1 'Think' tags
            # We strip the internal reasoning block for the final professional output
            if "<think>" in raw_report:
                report_content = raw_report.split("</think>")[-1].strip()
            else:
                report_content = raw_report

            # 6. VAULT STORAGE
            report_path = self.output_dir / f"incident_report_{run_id}.md"
            report_path.write_text(report_content, encoding='utf-8')
            
            print(f"✓ Professional Report Vaulted: {report_path.name}")

            # 7. VALIDATION PHASE
            # We pass the original JSON string for the detector to audit
            self._validate_results(report_content, json.dumps(incident_data), run_id)

            return True 

        except Exception as e:
            logger.error(f"DeepSeek Reasoning Pipeline Failed: {e}")
            return False

    def _validate_results(self, report_content: str, source_text: str, run_id: str):
        print(f"--- [Audit Phase] Validating Intelligence Accuracy ---")
        detector = HallucinationDetector(source_text)
        issues = detector.check_report(report_content)
        
        val_name = f"validation_{run_id}.txt"
        val_path = self.output_dir / val_name
        detector.generate_validation_report(str(val_path))

        if issues:
            print(f"⚠ ALERT: {len(issues)} potential hallucinations found in Vault.")
        else:
            print("✓ AUDIT PASSED: Intelligence is factually consistent.")