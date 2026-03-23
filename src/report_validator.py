import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Union

# Use project-standard logging
logger = logging.getLogger(__name__)

class HallucinationDetector:
    """
    Forensic Auditor for SOC Reports.
    Detects AI fabrications by comparing the report against the 'Truth Block'.
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
    
    def __init__(self, facts_text: str):
        """Initializes the auditor with the 'Truth Block' evidence."""
        self.facts_text = facts_text
        self.findings: List[Dict[str, Any]] = []
        
        # Extract Known Assets for Cross-Referencing
        self.known_ips = set(re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})', facts_text))
        self.known_paths = set(re.findall(r'(?:/[a-zA-Z0-9._/-]+|\b[A-Z]:\\[a-zA-Z0-9._\\]+)', facts_text))
        self.known_perms = set(re.findall(r'(777|rwxrwxrwx|world-writable)', facts_text.lower()))
        self.known_domains = set(re.findall(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', facts_text))

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
        return issues

    def check_data_consistency(self, report_text: str) -> List[Dict[str, Any]]:
        """Validates IPs, File Paths, and Permissions against the truth block."""
        consistency_issues = []
        
        # 1. Validate Public IPs (Ignoring common internal ranges)
        report_ips = set(re.findall(r'\d{1,3}(?:\.\d{1,3}){3}', report_text))
        for ip in report_ips:
            if ip.startswith(('10.', '192.168.', '172.16.', '127.')): 
                continue
            if ip not in self.known_ips:
                consistency_issues.append(self._log_issue(
                    'unknown_ip', 'HIGH', f'IP {ip} is mentioned but missing from source facts.', ip
                ))

        # 2. Validate File Paths
        report_paths = set(re.findall(r'(?:/[a-zA-Z0-9._/-]+|\b[A-Z]:\\[a-zA-Z0-9._\\]+)', report_text))
        for path in report_paths:
            if path not in self.known_paths and len(path) > 5:
                consistency_issues.append(self._log_issue(
                    'unknown_path', 'HIGH', f'File path {path} not found in logs/insights.', path
                ))

        # 3. Validate Permissions
        if any(p in report_text.lower() for p in ['777', 'rwxrwxrwx', 'world-writable']):
            if not self.known_perms:
                consistency_issues.append(self._log_issue(
                    'config_fabrication', 'HIGH', 'Report claims insecure permissions not present in facts.', '777'
                ))

        return consistency_issues

    def _log_issue(self, i_type: str, severity: str, description: str, text: str) -> Dict[str, Any]:
        issue = {
            'type': i_type, 'severity': severity, 'description': description, 'matched_text': text
        }
        self.findings.append(issue)
        return issue

    def generate_validation_report(self, output_path: Union[str, Path]):
        """Generates a forensic audit file for the Vault."""
        output_path = Path(output_path)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== FORENSIC VALIDATION AUDIT ===\n")
                f.write(f"Status: {'⚠ ISSUES DETECTED' if self.findings else '✓ CLEAN'}\n\n")
                
                f.write("--- KNOWN ASSETS (FROM TRUTH BLOCK) ---\n")
                f.write(f"IPs: {', '.join(self.known_ips) if self.known_ips else 'None'}\n")
                f.write(f"Paths: {len(self.known_paths)} identified\n")
                f.write(f"Perms: {', '.join(self.known_perms) if self.known_perms else 'None'}\n\n")
                
                if self.findings:
                    f.write(f"DETECTION LOG ({len(self.findings)} issues):\n")
                    f.write("-" * 40 + "\n")
                    for i, issue in enumerate(self.findings, 1):
                        f.write(f"{i}. [{issue['severity']}] {issue['type']}: {issue['matched_text']}\n")
                        f.write(f"   {issue['description']}\n\n")
                else:
                    f.write("RESULT: No hallucinations or inconsistencies detected.\n")
            logger.info(f"Audit report successfully vaulted: {output_path.name}")
        except Exception as e:
            logger.error(f"Audit Export Failed: {e}")