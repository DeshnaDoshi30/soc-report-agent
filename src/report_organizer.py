"""
Report Organizer & Archiver
Manages report file organization and archiving
"""
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ReportOrganizer:
    """Organizes report files into clean archive structure."""
    
    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent / "data"
        
        self.base_path = base_path
        self.output_dir = base_path / "output"
        self.archive_dir = base_path / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def archive_report(self, run_id: str, hostname: str, 
                       primary_classification: str = "") -> Optional[Path]:
        """
        Move report files from output/ to organized archive structure.
        
        Structure:
        archive/
        ├── 2026-04-17/
        │   ├── 20260417_055151/
        │   │   ├── SOC_Report_20260417_055151.docx
        │   │   ├── incident_report_20260417_055151.md
        │   │   ├── incident_20260417_055151.json
        │   │   ├── truth_block_20260417_055151.json
        │   │   └── metadata.json
        """
        try:
            # Create date-based folder
            date_str = datetime.now().strftime("%Y-%m-%d")
            date_folder = self.archive_dir / date_str
            
            # Create report-specific folder
            report_folder = date_folder / run_id
            report_folder.mkdir(parents=True, exist_ok=True)
            
            # List of files to move
            files_to_move = [
                f"SOC_Report_{run_id}.docx",
                f"incident_report_{run_id}.md",
                f"incident_{run_id}.json",
                f"truth_block_{run_id}.json",
                f"cleaned_{run_id}.csv",
                f"validation_{run_id}.txt"
            ]
            
            moved_files = {}
            
            # Move files from output to archive
            for filename in files_to_move:
                src = self.output_dir / filename
                if src.exists():
                    dst = report_folder / filename
                    shutil.move(str(src), str(dst))
                    moved_files[filename.split('_')[0]] = str(dst.relative_to(self.base_path))
                    logger.info(f"✓ Archived: {filename}")
            
            # Create metadata.json for quick lookup
            metadata = {
                'run_id': run_id,
                'hostname': hostname,
                'primary_classification': primary_classification,
                'archived_date': date_str,
                'archived_time': datetime.now().isoformat(),
                'files': moved_files
            }
            
            metadata_file = report_folder / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            
            logger.info(f"✓ Report archived: {report_folder}")
            return report_folder
        
        except Exception as e:
            logger.error(f"❌ Failed to archive report: {e}")
            return None
    
    def get_archived_report(self, run_id: str) -> Optional[Dict]:
        """Fetch archived report metadata."""
        try:
            for date_folder in sorted(self.archive_dir.iterdir(), reverse=True):
                if date_folder.is_dir():
                    report_folder = date_folder / run_id
                    metadata_file = report_folder / "metadata.json"
                    
                    if metadata_file.exists():
                        metadata = json.loads(metadata_file.read_text())
                        metadata['folder'] = str(report_folder)
                        return metadata
            
            return None
        except Exception as e:
            logger.error(f"❌ Failed to fetch archived report: {e}")
            return None
    
    def list_archived_reports(self, limit: int = 50) -> list:
        """List all archived reports, newest first."""
        try:
            reports = []
            
            for date_folder in sorted(self.archive_dir.iterdir(), reverse=True):
                if date_folder.is_dir():
                    for report_folder in sorted(date_folder.iterdir(), reverse=True):
                        if report_folder.is_dir():
                            metadata_file = report_folder / "metadata.json"
                            if metadata_file.exists():
                                metadata = json.loads(metadata_file.read_text())
                                metadata['folder'] = str(report_folder)
                                reports.append(metadata)
                                
                                if len(reports) >= limit:
                                    return reports
            
            return reports
        except Exception as e:
            logger.error(f"❌ Failed to list archived reports: {e}")
            return []
    
    def delete_archived_report(self, run_id: str) -> bool:
        """Delete an archived report and its folder."""
        try:
            for date_folder in self.archive_dir.iterdir():
                if date_folder.is_dir():
                    report_folder = date_folder / run_id
                    if report_folder.exists():
                        shutil.rmtree(report_folder)
                        logger.info(f"✓ Deleted archived report: {run_id}")
                        return True
            
            logger.warning(f"Report not found: {run_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete archived report: {e}")
            return False
    
    def get_docx_path(self, run_id: str) -> Optional[Path]:
        """Get path to DOCX file for a report."""
        report_data = self.get_archived_report(run_id)
        if report_data and 'files' in report_data and 'SOC' in report_data['files']:
            return self.base_path / report_data['files']['SOC']
        
        return None
    
    def get_all_files(self, run_id: str) -> Dict[str, Path]:
        """Get all file paths for a report."""
        report_data = self.get_archived_report(run_id)
        if report_data and 'files' in report_data:
            return {k: self.base_path / v for k, v in report_data['files'].items()}
        
        return {}
