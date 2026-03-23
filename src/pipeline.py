import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Centralized SOC Config
try:
    import config
    from csv_to_incident import CSVToIncidentConverter
    from report_generator import IncidentReportGenerator
except ImportError as e:
    print(f"CRITICAL ERROR: Project structure invalid or missing dependencies: {e}")
    sys.exit(1)

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class UnifiedPipeline:
    def __init__(self, input_file: str, human_insight: str = "", model: Optional[str] = None, host: Optional[str] = None):
        
        self.input_file = Path(input_file)
        self.human_insight = human_insight
        
        # Priority: Command Line > .env/Config
        self.model = model or config.DEFAULT_MODEL
        self.host = host or config.OLLAMA_HOST
        
        # UNIQUE RUN ID: The 'Glue' for the Forensic Vault
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use centralized vault path from config
        self.output_dir = config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_input_type(self) -> str:
        """Identifies if the input is a raw CSV or pre-synthesized TXT."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Target file not found in vault: {self.input_file}")
        
        suffix = self.input_file.suffix.lower()
        if suffix == ".csv":
            return "csv"
        elif suffix in [".txt", ".md", ""]:
            return "text"
        else:
            raise ValueError(f"Unsupported forensic source type: {suffix}")

    def run(self) -> bool:
        """Executes the synchronized investigation workflow."""
        logger.info("="*60)
        logger.info(f"SOC INVESTIGATION START | ID: {self.run_id}")
        logger.info(f"MODEL: {self.model} | HOST: {self.host}")
        logger.info("="*60)
        
        try:
            input_type = self.detect_input_type()
            
            if input_type == "csv":
                return self._process_csv_workflow()
            else:
                # Direct AI analysis of existing text evidence
                return self._trigger_generator(str(self.input_file))
        except Exception as e:
            logger.error(f"PIPELINE CRASHED: {e}")
            return False

    def _process_csv_workflow(self) -> bool:
        """Handles Raw CSV -> Fact Extraction -> AI Synthesis."""
        logger.info(f"PHASE 1: Extracting forensic facts from {self.input_file.name}")
        try:
            converter = CSVToIncidentConverter(
                csv_file=str(self.input_file),
                human_insight=self.human_insight,
                run_id=self.run_id 
            )
            incident_path = converter.convert()
            
            if not incident_path:
                return False
                
            logger.info(f"SUCCESS: Evidence vaulted to {Path(incident_path).name}")
            logger.info("PHASE 2: Generating Lead-Level AI Report")
            return self._trigger_generator(incident_path)
            
        except Exception as e:
            logger.error(f"Forensic Extraction Failed: {e}")
            return False

    def _trigger_generator(self, incident_path: str) -> bool:
        """Triggers the AI reasoning engine and synchronizes vault IDs."""
        try:
            generator = IncidentReportGenerator(
                model=self.model,
                ollama_host=self.host
            )
            # Ensure the report name matches the Run ID for traceability
            return generator.generate_report(incident_path, run_id=self.run_id)
        except Exception as e:
            logger.error(f"AI Generation Failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="SOC Agent - Master Pipeline")
    parser.add_argument("input_file", help="Path to logs (CSV) or Incident text (TXT)")
    parser.add_argument("--insight", default="", help="Analyst's primary investigative truth")
    parser.add_argument("--model", help=f"Override model (Current: {config.DEFAULT_MODEL})")
    parser.add_argument("--host", help=f"Override host (Current: {config.OLLAMA_HOST})")
    
    args = parser.parse_args()
    
    pipeline = UnifiedPipeline(
        input_file=args.input_file,
        human_insight=args.insight,
        model=args.model,
        host=args.host
    )
    
    success = pipeline.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()