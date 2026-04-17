import sys
import logging
import argparse
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

# Standardized SOC Imports
try:
    from src import config
    from src.csv_to_incident import CSVToIncidentConverter
    from src.semantic_extractor import SemanticExtractor
    from src.knowledge_base import fetch_expert_context
    from src.report_generator import IncidentReportGenerator
    from src.hardware_utils import check_preflight, check_file_size, get_recommended_chunk_size
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
    def __init__(self, input_file: str, human_insight: str = "", model: Optional[str] = None):
        self.input_file = Path(input_file)
        self.human_insight = human_insight
        
        # Unique RUN ID: The 'Glue' for the Forensic Vault
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Run locking mechanism (prevent concurrent pipelines)
        self.lock_file = config.OUTPUT_DIR / ".pipeline.lock"
        
        # Ensure output directory exists
        self.output_dir = config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _acquire_lock(self, timeout: int = 5) -> bool:
        """
        Acquire exclusive pipeline lock (prevent concurrent runs).
        Timeout helps avoid deadlock.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.lock_file.exists():
                try:
                    self.lock_file.write_text(f"{self.run_id}\n{datetime.now().isoformat()}")
                    logger.info(f"✅ Acquired pipeline lock (Run: {self.run_id})")
                    return True
                except OSError:
                    pass
            time.sleep(0.1)
        
        # Lock timeout - another pipeline is still running
        if self.lock_file.exists():
            old_run = self.lock_file.read_text().split('\n')[0]
            logger.error(f"❌ Another pipeline is running (Run: {old_run}). Cannot proceed.")
        return False
    
    def _release_lock(self):
        """Release the pipeline lock."""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info("✅ Released pipeline lock")
        except OSError as e:
            logger.warning(f"Warning: Could not clean up lock file: {e}")

    def detect_input_type(self) -> str:
        if not self.input_file.exists():
            raise FileNotFoundError(f"Target file not found in vault: {self.input_file}")
        
        suffix = self.input_file.suffix.lower()
        if suffix == ".csv":
            return "csv"
        return "text"

    def run(self) -> bool:
        """Executes the synchronized Semantic + RAG investigation workflow."""
        
        # SAFETY GATE 1: Pre-flight checks
        is_safe, preflight_msg = check_preflight()
        if is_safe:
            logger.info(f"🚀 {preflight_msg}")
        
        # SAFETY GATE 2: File size validation
        file_safe, file_msg = check_file_size(self.input_file)
        if not file_safe:
            logger.error(f"❌ {file_msg}")
            return False
        logger.info(f"✅ {file_msg}")
        
        # SAFETY GATE 3: Prevent concurrent runs
        if not self._acquire_lock():
            return False
        
        logger.info("="*60)
        logger.info(f"SOC INVESTIGATION START | ID: {self.run_id}")
        logger.info(f"INPUT SOURCE: {self.input_file.name}")
        logger.info("="*60)
        
        try:
            input_type = self.detect_input_type()
            
            # PHASE 1: Unified Semantic Extraction 
            if input_type == "csv":
                logger.info("📊 Processing Log Evidence (CSV)...")
                json_vault_path = self._extract_from_csv()
            else:
                logger.info("📝 Processing Narrative Evidence (TXT)...")
                json_vault_path = self._extract_from_text()

            # --- PHASE 1 GATEKEEPER ---
            if not json_vault_path:
                logger.error("❌ Pipeline Halted: Phase 1 failed to produce a Truth Block.")
                return False

            with open(json_vault_path, 'r') as f:
                truth_block = json.load(f)
            
            # IMPROVEMENT: Ensure hostname is available for the cover page 
            findings = truth_block.get("FINDINGS", {})
            metadata = truth_block.get("METADATA", {})
            
            if not findings:
                logger.error("❌ Pipeline Halted: Extraction data invalid. No findings found.")
                return False

            # Extract hostname safely for the professional Word report
            hostname = metadata.get("hostname") or findings.get("hostname") or "Production Server"

            # PHASE 2: Intelligence Retrieval (RAG)
            rag_context = self._get_rag_context(truth_block)

            # PHASE 3: Lead-Level AI Synthesis (DeepSeek-R1)
            # IMPROVEMENT: Pass hostname to the generator
            logger.info(f"PHASE 3: Generating Final Report for {hostname} via DeepSeek-R1")
            result = self._trigger_generator(json_vault_path, rag_context, hostname)
            return result

        except Exception as e:
            logger.error(f"PIPELINE CRASHED: {e}")
            return False
        finally:
            # Always release lock, even on error
            self._release_lock()

    def _trigger_generator(self, incident_path: str, rag_context: str, hostname: str) -> bool:
        """Triggers the reasoning engine with synchronized context."""
        try:
            # We initialize the generator here to keep VRAM clean during extraction
            generator = IncidentReportGenerator()
            return generator.generate_report(
                incident_path=incident_path, 
                rag_context=rag_context, 
                run_id=self.run_id,
                hostname=hostname # NEW: Pass hostname for cover page 
            )
        except Exception as e:
            logger.error(f"AI Generation Failed: {e}")
            return False

    def _extract_from_csv(self) -> Optional[str]:
        """Handles Raw CSV -> Cleaning -> JSON Truth Block."""
        try:
            # Determine recommended chunk size based on file size
            file_size_mb = self.input_file.stat().st_size / (1024 * 1024)
            chunk_size = get_recommended_chunk_size(file_size_mb)
            
            if chunk_size:
                logger.info(f"💾 Enabling memory-safe chunking: {chunk_size} rows per batch")
            
            converter = CSVToIncidentConverter(
                csv_file=str(self.input_file),
                human_insight=self.human_insight,
                run_id=self.run_id,
                chunk_size=chunk_size
            )
            return converter.convert()
        except Exception as e:
            logger.error(f"CSV Workflow Failed: {e}")
            return None

    def _extract_from_text(self) -> Optional[str]:
        """Handles Raw Text -> Qwen -> JSON Truth Block."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()

            # Wrap text in a dummy DataFrame for the Extractor
            df = pd.DataFrame({'Full_Evidence': [raw_text]})
            extractor = SemanticExtractor(df, run_id=self.run_id)
            
            facts = extractor.extract_all_facts(human_insight=self.human_insight)
            
            if "error" in facts:
                return None

            output_path = config.OUTPUT_DIR / f"incident_{self.run_id}.json"
            extractor.export_vault(output_path)
            return str(output_path)
        except Exception as e:
            logger.error(f"Text Extraction Failed: {e}")
            return None

    def _get_rag_context(self, truth_block: dict) -> str:
        """Performs the RAG search using extracted findings."""
        findings = truth_block.get("FINDINGS", {})
        search_query = findings.get("mitre_query", "security incident")
        
        logger.info(f"PHASE 2: Querying Knowledge Base for: '{search_query}'")
        return fetch_expert_context(search_query)

def main():
    parser = argparse.ArgumentParser(description="SOC Agent - GPU Semantic Pipeline")
    parser.add_argument("input_file", help="Path to logs (CSV) or Incident text (TXT)")
    parser.add_argument("--insight", default="", help="Analyst's primary investigative truth")
    
    args = parser.parse_args()
    
    pipeline = UnifiedPipeline(
        input_file=args.input_file,
        human_insight=args.insight
    )
    
    success = pipeline.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()