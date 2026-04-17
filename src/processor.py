import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, Union

# Use standard project logging
logger = logging.getLogger(__name__)

class SOCDataCleaner:
    """
    Universal SOC log cleaner optimized for 8GB RAM.
    Standardizes Wazuh/SonicWall logs for AI analysis.
    """

    def __init__(self, input_path: Union[str, Path], output_path: Union[str, Path],
                 target_columns: Optional[Dict[str, str]] = None, chunk_size: Optional[int] = None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.chunk_size = chunk_size

        # Centralized Mapping for Wazuh & SonicWall
        self.target_columns = target_columns or {
            '_source.@timestamp': 'Timestamp',
            '_source.timestamp': 'Timestamp',
            '_source.data.srcip': 'Source_IP',
            '_source.data.dstip': 'Dest_IP',
            '_source.data.protocol': 'Protocol',
            '_source.data.action': 'Action',
            '_source.rule.level': 'Alert_Level',
            '_source.rule.description': 'Description',
            '_source.full_log': 'Full_Evidence',
            '_source.syscheck.path': 'File_Path',
            '_source.syscheck.mode': 'Permissions',
            '_source.data.dstuser': 'Target_User',
            '_source.data.srcuser': 'Source_User',
            '_source.GeoLocation.country_name': 'Country'
        }

    def validate_paths(self) -> bool:
        """Ensures the vault structure is ready."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Forensic Source Missing: {self.input_path}")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        return True

    def clean_logs(self) -> pd.DataFrame:
        """Executes the universal cleaning pipeline."""
        logger.info(f"Cleaning Forensic Data: {self.input_path.name}")
        self.validate_paths()

        # Auto-detect if chunking is needed for safety
        # Large files (>10MB) should use chunking to avoid OOM on 8GB GPUs
        if self.chunk_size is None:
            file_size_mb = self.input_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 10:
                # Auto-enable chunking for large files
                self.chunk_size = 5000 if file_size_mb > 50 else 10000
                logger.info(f"🔒 Auto-enabled chunking for large file ({file_size_mb:.1f}MB): {self.chunk_size} rows/batch")

        if self.chunk_size:
            logger.info(f"💾 Memory Guard Active: Processing in chunks of {self.chunk_size}")
            chunks = [self._clean_chunk(c) for c in pd.read_csv(self.input_path, chunksize=self.chunk_size)]
            df_clean = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.read_csv(self.input_path)
            df_clean = self._clean_chunk(df)

        # Save the sanitized evidence to the vault
        df_clean.to_csv(self.output_path, index=False)
        logger.info(f"Sanitized evidence vaulted: {self.output_path.name} ({len(df_clean)} records)")
        return df_clean

    def _clean_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes logs and optimizes memory usage."""
        
        # 1. Map columns and handle deduplication
        found_sources = [src for src in self.target_columns.keys() if src in df.columns]
        selection_map = {}
        for src in found_sources:
            target = self.target_columns[src]
            if target not in selection_map:
                selection_map[target] = src
        
        df_clean = df[list(selection_map.values())].copy()
        df_clean.rename(columns={v: k for k, v in selection_map.items()}, inplace=True)

        # 2. Fill missing standard columns
        for col in set(self.target_columns.values()):
            if col not in df_clean.columns:
                df_clean[col] = None

        # 3. Optimize Data Types for 8GB RAM
        df_clean = self._optimize_types(df_clean)
        return self._handle_missing_values(df_clean)

    def _optimize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fixes timestamps and reduces memory footprint."""
        
        if 'Timestamp' in df.columns:
            # 1. Find the integer position of the 'Timestamp' column(s)
            # This returns a list of positions (e.g., [0] or [0, 5] if duplicates exist)
            ts_indices = [i for i, col in enumerate(df.columns) if col == 'Timestamp']
            
            if ts_indices:
                # 2. Extract the first matching column as a Series
                # Using a single integer inside .iloc[:, int] ALWAYS returns a Series.
                # Pylance loves this because it's no longer ambiguous.
                ts_series = df.iloc[:, ts_indices[0]]
                
                # 3. Clean and convert
                cleaned_ts = ts_series.astype(str).str.replace(' @ ', ' ', regex=False).str.strip()
                df['Timestamp'] = pd.to_datetime(cleaned_ts, errors='coerce')

        if 'Alert_Level' in df.columns:
            df['Alert_Level'] = pd.to_numeric(df['Alert_Level'], errors='coerce').fillna(0).astype(int)

        # Categorical optimization for high-volume logs on 8GB RAM
        for col in ['Protocol', 'Action', 'Country']:
            if col in df.columns:
                df[col] = df[col].astype('category')

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fills NaNs safely based on column type."""
        for col in df.columns:
            if col == 'Timestamp': continue
            
            if isinstance(df[col].dtype, pd.CategoricalDtype):
                if 'Unknown' not in df[col].cat.categories:
                    df[col] = df[col].cat.add_categories(['Unknown'])
                df[col] = df[col].fillna('Unknown')
            else:
                df[col] = df[col].fillna('N/A')
        return df