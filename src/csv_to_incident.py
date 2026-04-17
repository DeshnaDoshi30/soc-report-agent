import logging
from pathlib import Path
from typing import Optional
from src import config
from src.processor import SOCDataCleaner
from src.semantic_extractor import SemanticExtractor 

# Professional logging setup
logger = logging.getLogger(__name__)

class CSVToIncidentConverter:
    def __init__(self, csv_file: str, human_insight: str = "", run_id: Optional[str] = None, chunk_size: Optional[int] = None):
        """
        Orchestrates CSV -> Cleaned Data -> Semantic Fact Extraction.
        Syncs with the global Run ID for the JSON-based Forensic Vault.
        
        Args:
            csv_file: Path to input CSV
            human_insight: Analyst's guidance for extraction
            run_id: Unique run identifier for vault sync
            chunk_size: Number of rows per chunk (None = no chunking, uses default for large files)
        """
        self.csv_file = Path(csv_file)
        self.human_insight = human_insight
        
        # Use the provided Run ID from the Unified Pipeline
        self.run_id = run_id or "legacy_run"
        
        # Memory management: chunk_size helps with large files
        # If not specified, processor will handle defaults
        self.chunk_size = chunk_size
        
        # Use centralized Vault paths from config
        self.output_dir = config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Unique timestamped filenames for the vault
        self.cleaned_csv = self.output_dir / f"cleaned_{self.run_id}.csv"
        
        # UPGRADE: Truth Block is now JSON for RAG compatibility
        self.incident_json = self.output_dir / f"incident_{self.run_id}.json"

    def convert(self) -> str:
        """Executes the conversion pipeline and returns the JSON vault path."""
        try:
            # 1. CLEANING PHASE
            logger.info(f"Initiating Log Cleaning for Run: {self.run_id}")
            cleaner = SOCDataCleaner(
                input_path=self.csv_file,
                output_path=self.cleaned_csv,
                chunk_size=self.chunk_size  # Pass chunk_size for memory safety
            )
            df_clean = cleaner.clean_logs()
            
            if df_clean.empty:
                logger.error("Vault Error: Cleaning resulted in an empty dataset.")
                return ""

            # 2. SEMANTIC EXTRACTION PHASE
            # We use the EXTRACTOR_MODEL (Qwen 7B) on GPU 1 for reasoning
            logger.info(f"PHASE 1: Extracting semantic facts using {config.EXTRACTOR_MODEL}")
            extractor = SemanticExtractor(
                df_clean, 
                run_id=self.run_id, 
                model=config.EXTRACTOR_MODEL
            )
            
            # The extractor now ingests Human Insight to guide its reasoning
            facts = extractor.extract_all_facts(human_insight=self.human_insight)
            
            if "error" in facts:
                logger.error(f"Extraction Error: {facts['error']}")
                return ""

            # 3. JSON VAULT STORAGE
            # Export the Truth Block as structured JSON for the RAG and Reporter stages
            extractor.export_vault(output_path=self.incident_json)
            
            logger.info(f"Investigation facts successfully vaulted to JSON: {self.incident_json.name}")
            return str(self.incident_json)

        except Exception as e:
            logger.error(f"Incident Conversion Failed: {e}")
            return ""

if __name__ == "__main__":
    # Handled by UnifiedPipeline in production
    pass