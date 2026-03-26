import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Union

# Use project-standard logging
logger = logging.getLogger(__name__)

class HallucinationDetector:
    """
    Forensic Auditor for SOC Reports.
    Now optimized to parse structured JSON Truth Blocks and detect AI fabrications.
    """
    
    # Patterns to flag suspicious AI fabrications
    HALLUCINATION_INDICATORS = {
        'financial_fabrication': {
            'patterns': [r'\$[\d,]+.*(?:cost|expense|remediation|impact)', r'financial.*(?:impact|loss|cost)'],
            'severity': 'CRITICAL', 'description': 'Financial claims without source data'
        },
        'cvss_fabrication': {
            'patterns': [r'CVSS\s+[\d.]+', r'CVE-\d+-\d+'],
            'severity': 'CRITICAL', 'description': 'CVSS/CVE claims without source data'
        },
        'attribution_fabrication': {
            'patterns': [r'nation[\-\s]state', r'APT[\d]+', r'advanced.*threat.*actor'],
            'severity': 'CRITICAL', 'description': 'Attribution without evidence'
        }
    }
    
    def __init__(self, source_json_str: str):
        """Initializes the auditor using the structured JSON Truth Block."""
        self.findings: List[Dict[str, Any]] = []
        
        try:
            # Parse the Truth Block
            data = json.loads(source_json_str)
            
            # Extract Known Assets directly from the JSON fields (No more regex guessing!)
            # We pull from the 'affected_scope' and 'forensic_indicators' blocks
            scope = data.get("affected_scope", {})
            indicators = data.get("forensic_indicators", {})
            net_meta = indicators.get("network_metadata", {})

            self.known_ips = set(scope.get("target_ips", [])) | \
                             set(net_meta.get("source_ips", [])) | \
                             set(net_meta.get("destination_ips", []))
            
            self.known_paths = set(scope.get("file_paths", []))
            
            # Capture the specific permission bits identified by the Extractor
            self.known_perms = {indicators.get("permission_bits", "N/A")}
            
            logger.info(f"Auditor initialized with {len(self.known_ips)} IPs and {len(self.known_paths)} Paths from JSON.")

        except json.JSONDecodeError:
            logger.warning("Auditor fallback: Source is not JSON. Using basic regex extraction.")
            self.known_ips = set(re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})', source_json_str))
            self.known_paths = set(re.findall(r'(?:/[a-zA-Z0-9._/-]+|\b[A-Z]:\\[a-zA-Z0-9._\\]+)', source_json_str))
            self.known_perms = set(re.findall(r'(777|rwxrwxrwx|world-writable)', source_json_str.lower()))

    def check_report(self, report_text: str) -> List[Dict[str, Any]]:
        """Scans for classic AI fabrications (Cost, CVSS, Attribution)."""
        issues = []
        for h_type, config in self.HALLUCINATION_INDICATORS.items():
            for pattern in config['patterns']:
                for match in re.finditer(pattern, report_text, re.IGNORECASE):
                    issue = {
                        'type': h_type,
                        'severity': config['severity'],
                        'description': config['description'],
                        'matched_text': match.group(0)
                    }
                    self.findings.append(issue)
                    issues.append(issue)
        
        # Add data consistency checks to the findings
        issues.extend(self.check_data_consistency(report_text))
        return issues

    def check_data_consistency(self, report_text: str) -> List[Dict[str, Any]]:
        """Validates report content against the immutable JSON Truth Block."""
        consistency_issues = []
        
        # 1. Validate IPs mentioned in the report
        report_ips = set(re.findall(r'\d{1,3}(?:\.\d{1,3}){3}', report_text))
        for ip in report_ips:
            # Ignore common noise/internal ranges
            if ip.startswith(('127.', '0.0.')): continue
            
            if ip not in self.known_ips:
                consistency_issues.append(self._log_issue(
                    'hallucinated_ip', 'HIGH', f'IP {ip} is mentioned but is NOT in the forensic source.', ip
                ))

        # 2. Validate File Paths
        report_paths = set(re.findall(r'(?:/[a-zA-Z0-9._/-]+|\b[A-Z]:\\[a-zA-Z0-9._\\]+)', report_text))
        for path in report_paths:
            # Filter out very short strings that might be false positives
            if len(path) > 5 and path not in self.known_paths:
                consistency_issues.append(self._log_issue(
                    'hallucinated_path', 'HIGH', f'File path {path} was not found in the original logs.', path
                ))

        # 3. Validate Permissions Logic
        if any(p in report_text.lower() for p in ['777', 'rwxrwxrwx', 'world-writable']):
            # If the report claims insecure perms, they MUST be in the JSON Truth Block
            if not any(p in str(self.known_perms).lower() for p in ['777', 'rwxrwxrwx', 'world-writable']):
                consistency_issues.append(self._log_issue(
                    'perm_fabrication', 'HIGH', 'Report claims 777 permissions but source data shows secure state.', '777'
                ))

        return consistency_issues

    def _log_issue(self, i_type: str, severity: str, description: str, text: str) -> Dict[str, Any]:
        issue = {
            'type': i_type, 'severity': severity, 'description': description, 'matched_text': text
        }
        self.findings.append(issue)
        return issue

    def generate_validation_report(self, output_path: Union[str, Path]):
        """Generates the forensic audit file for the Vault."""
        output_path = Path(output_path)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== FORENSIC VALIDATION AUDIT (JSON VERIFIED) ===\n")
                f.write(f"Status: {'⚠ ISSUES DETECTED' if self.findings else '✓ CLEAN'}\n\n")
                
                f.write("--- AUTHORITATIVE ASSETS (FROM JSON TRUTH) ---\n")
                f.write(f"Verified IPs: {', '.join(self.known_ips) if self.known_ips else 'None'}\n")
                f.write(f"Verified Paths: {', '.join(self.known_paths) if self.known_paths else 'None'}\n")
                f.write(f"Verified Perms: {', '.join(self.known_perms) if self.known_perms else 'None'}\n\n")
                
                if self.findings:
                    f.write(f"DETECTION LOG ({len(self.findings)} issues):\n")
                    f.write("-" * 40 + "\n")
                    for i, issue in enumerate(self.findings, 1):
                        f.write(f"{i}. [{issue['severity']}] {issue['type']}: {issue['matched_text']}\n")
                        f.write(f"   {issue['description']}\n\n")
                else:
                    f.write("RESULT: No hallucinations or data inconsistencies detected.\n")
        except Exception as e:
            logger.error(f"Audit Export Failed: {e}")