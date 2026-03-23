import logging
from pathlib import Path
from typing import Optional
import config  #
from processor import SOCDataCleaner
from forensic_extractor import ForensicExtractor

# Professional logging setup
logger = logging.getLogger(__name__)

class CSVToIncidentConverter:
    def __init__(self, csv_file: str, human_insight: str = "", run_id: Optional[str] = None):
        """
        Orchestrates CSV -> Cleaned Data -> Fact Synthesis.
        Syncs with the global Run ID for the Forensic Vault.
        """
        self.csv_file = Path(csv_file)
        self.human_insight = human_insight
        
        # Use the provided Run ID from the Unified Pipeline
        self.run_id = run_id or "legacy_run"
        
        # Use centralized Vault paths from config
        self.output_dir = config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Unique timestamped filenames for the vault
        self.cleaned_csv = self.output_dir / f"cleaned_{self.run_id}.csv"
        self.incident_txt = self.output_dir / f"incident_{self.run_id}.txt"

    def convert(self) -> str:
        """Executes the conversion pipeline and returns the vault path."""
        try:
            # 1. CLEANING PHASE
            logger.info(f"Initiating Log Cleaning for Run: {self.run_id}")
            cleaner = SOCDataCleaner(
                input_path=self.csv_file,
                output_path=self.cleaned_csv
            )
            df_clean = cleaner.clean_logs()
            
            if df_clean.empty:
                logger.error("Vault Error: Cleaning resulted in an empty dataset.")
                return ""

            # 2. EXTRACTION PHASE
            # Pass the Run ID to the extractor for internal metadata tracking
            extractor = ForensicExtractor(df_clean, run_id=self.run_id)
            facts = extractor.extract_all_facts()
            
            # 3. VAULT STORAGE: Export the Truth Block
            # Uses the Pathlib output_path parameter from our refactored extractor
            extractor.export_facts_as_text(
                output_path=self.incident_txt, 
                human_insight=self.human_insight
            )
            
            logger.info(f"Investigation facts successfully vaulted: {self.incident_txt.name}")
            return str(self.incident_txt)

        except Exception as e:
            logger.error(f"Incident Conversion Failed: {e}")
            return ""

if __name__ == "__main__":
    # Handled by UnifiedPipeline in production
    pass