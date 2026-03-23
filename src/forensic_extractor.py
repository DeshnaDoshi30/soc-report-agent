import pandas as pd
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup professional logging
logger = logging.getLogger(__name__)

class ForensicExtractor:
    # Modular Security Signatures
    # Add new patterns here for Web Defense, Data Exfiltration, etc.
    SIGNATURES = {
        'config_vuln': r'(777|rwxrwxrwx|world-writable)',
        'webshell_indicators': r'(eval\(|base64_decode|system\(|passthru\()',
        'sql_injection': r'(SELECT.*FROM|UNION.*SELECT|OR.*1=1)',
        'xss_attempt': r'(<script>|alert\(|onerror=)',
        'network_gateway': r'fw=(\d{1,3}(?:\.\d{1,3}){3})',
        'source_mac': r'srcMac=([a-fA-F0-9:]{17})'
    }

    def __init__(self, df: pd.DataFrame, run_id: str = "N/A"):
        self.df = df
        self.run_id = run_id
        self.facts: Dict[str, Any] = {
            'METADATA': {
                'run_id': self.run_id,
                'total_records': len(self.df),
                'timestamp': datetime.now().isoformat(),
            },
            'EVENTS': []
        }

    def extract_all_facts(self) -> Dict[str, Any]:
        """Runs the deep scan across all security domains."""
        self._deep_scan_signatures()  # Modular scan
        self._extract_ip_facts()     
        self._extract_temporal_facts() 
        self._extract_severity_facts() 
        return self.facts

    def _deep_scan_signatures(self):
        """Plugin-style architecture for pattern matching."""
        if 'Full_Evidence' not in self.df.columns:
            return

        # Prepare evidence text efficiently
        evidence_text = " ".join(self.df['Full_Evidence'].astype(str).to_numpy().flatten()).lower()
        
        if not evidence_text.strip():
            return

        # Iterate through the modular signature library
        for sig_type, pattern in self.SIGNATURES.items():
            matches = re.findall(pattern, evidence_text)
            if matches:
                # Deduplicate and limit to top findings
                unique_matches = list(set(matches))[:3]
                self.facts['EVENTS'].append({
                    'fact': f"Detected {sig_type.replace('_', ' ').upper()}: {', '.join(map(str, unique_matches))}",
                    'type': sig_type
                })

        # Specialized Asset Targeting (File Paths)
        path_pattern = r'(?:/[a-zA-Z0-9._/-]+|\b[A-Z]:\\[a-zA-Z0-9._\\]+)'
        paths = re.findall(path_pattern, evidence_text)
        if paths:
            top_paths = pd.Series(paths).value_counts().head(3).index.tolist()
            self.facts['EVENTS'].append({
                'fact': f"Targeted Assets/Paths: {', '.join(top_paths)}",
                'type': 'asset_target'
            })

    def _extract_ip_facts(self):
        """Maps Top 5 Source/Destination relationships."""
        for col in ['Source_IP', 'Dest_IP']:
            if col in self.df.columns:
                counts = self.df[col].value_counts().head(5)
                for ip, count in counts.items():
                    ip_str = str(ip)
                    if ip_str.lower() not in ['unknown', 'n/a', 'nan', 'none']:
                        self.facts['EVENTS'].append({
                            'fact': f"{col} {ip_str}: {count} occurrences", 
                            'type': 'network_stat'
                        })

    def _extract_temporal_facts(self):
        """Standardizes timestamps for the AI reporter."""
        if 'Timestamp' in self.df.columns:
            ts_data = self.df['Timestamp'].astype(str).str.replace(' @ ', ' ', regex=False)
            ts = pd.to_datetime(ts_data, errors='coerce').dropna()
            if not ts.empty:
                start_time = ts.min().strftime('%Y-%m-%d %H:%M:%S')
                end_time = ts.max().strftime('%Y-%m-%d %H:%M:%S')
                self.facts['EVENTS'].append({'fact': f"Log Timeline: {start_time} to {end_time}", 'type': 'temporal'})

    def _extract_severity_facts(self):
        """Extracts peak risk levels safely."""
        if 'Alert_Level' in self.df.columns:
            levels = pd.to_numeric(self.df['Alert_Level'], errors='coerce').dropna()
            if not levels.empty:
                self.facts['EVENTS'].append({
                    'fact': f"Peak Risk Level Detected: {levels.max()}", 
                    'type': 'severity'
                })

    def export_facts_as_text(self, output_path: Path, human_insight: str = ""):
        """Exports unique incident text with Pathlib support."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"--- PRIMARY INVESTIGATIVE TRUTH (HUMAN INSIGHT) ---\n")
                f.write(f"RUN_ID: {self.run_id}\n")
                f.write(f"NOTE: {human_insight if human_insight else 'No analyst notes provided.'}\n\n")
                f.write(f"--- SECONDARY MACHINE DATA (AUTOMATED) ---\n")
                
                for i, event in enumerate(self.facts['EVENTS'], 1):
                    f.write(f"{i}. {event['fact']}\n")
            logger.info(f"Forensic facts successfully vaulted to: {output_path}")
        except Exception as e:
            logger.error(f"Vault Export Failed: {e}")