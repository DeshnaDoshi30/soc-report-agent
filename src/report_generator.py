import requests
import json
import logging
from pathlib import Path
from typing import Optional
import config  #
from report_validator import HallucinationDetector

# Setup professional logging
logger = logging.getLogger(__name__)

class IncidentReportGenerator:
    def __init__(self, model: Optional[str] = None, ollama_host: Optional[str] = None):
        """
        AI Reasoning Engine for SOC Reports.
        Syncs with centralized config for Model and Host.
        """
        self.model = model or config.DEFAULT_MODEL
        self.host = ollama_host or config.OLLAMA_HOST
        self.template_dir = config.TEMPLATES_DIR
        self.output_dir = config.OUTPUT_DIR

    def _load_template(self, name: str) -> str:
        """Loads modular templates with Pathlib safety."""
        path = self.template_dir / name
        if not path.exists():
            logger.warning(f"Template missing in vault: {name}")
            return ""
        return path.read_text(encoding='utf-8')

    def generate_report(self, incident_path: str, run_id: str) -> bool:
        """Generates a vaulted report and triggers hallucination detection."""
        try:
            # 1. Gather Evidence and Instructions
            incident_text = Path(incident_path).read_text(encoding='utf-8')
            system_prompt = self._load_template("prompt_template.txt")
            report_format = self._load_template("report_format.txt")

            # 2. Construct the Authority Prompt (Human Priority)
            full_prompt = (
                f"{system_prompt}\n\n"
                f"STRICT INSTRUCTION: The 'PRIMARY INVESTIGATIVE TRUTH' below "
                f"comes from a Human Lead. Prioritize human insight over machine logs.\n\n"
                f"REPORT STRUCTURE:\n{report_format}\n\n"
                f"INPUT DATA:\n{incident_text}"
            )

            logger.info(f"Requesting analysis from {self.model} at {self.host}")
            
            # 3. AI Generation (Context Optimized for 8GB RAM)
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"num_ctx": 4096} 
                },
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            report_content = response.json().get('response', '')

            # 4. VAULT PROTECTION: Save Report with synchronized Run ID
            report_name = f"incident_report_{run_id}.md"
            report_path = self.output_dir / report_name
            report_path.write_text(report_content, encoding='utf-8')
            
            print(f"✓ AI Report Vaulted: {report_path.name}")

            # 5. VALIDATION PHASE
            self._validate_results(report_content, incident_text, run_id)

            return True 

        except Exception as e:
            logger.error(f"AI Generation Pipeline Failed: {e}")
            return False

    def _validate_results(self, report_content: str, source_text: str, run_id: str):
        """Internal Auditor: Scans for fabrications and inconsistencies."""
        print(f"--- [Audit Phase] Validating Intelligence Accuracy ---")
        
        detector = HallucinationDetector(source_text)
        issues = detector.check_report(report_content)
        ip_issues = detector.check_data_consistency(report_content)
        all_detections = issues + ip_issues

        # Save Validation Log to Vault
        val_name = f"validation_{run_id}.txt"
        val_path = self.output_dir / val_name
        detector.generate_validation_report(str(val_path))

        if all_detections:
            print(f"⚠ ALERT: {len(all_detections)} potential hallucinations found.")
            print(f"  Check Vault Log: {val_name}")
        else:
            print("✓ AUDIT PASSED: Intelligence is factually consistent.")