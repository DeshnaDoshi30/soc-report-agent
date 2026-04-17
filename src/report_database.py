"""
Report History Database Manager
Stores metadata about all generated reports in SQLite
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class ReportDatabase:
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "reports.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                run_id TEXT UNIQUE NOT NULL,
                hostname TEXT NOT NULL,
                primary_classification TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',
                model_used TEXT,
                processing_time_seconds REAL,
                summary TEXT,
                file_paths TEXT,
                tags TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✓ Report database initialized")
    
    def add_report(self, run_id: str, hostname: str, classification: str = "", 
                   model_used: str = "", processing_time: float = 0, 
                   summary: str = "", file_paths: Dict = None, tags: str = "") -> bool:
        """Add a completed report to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            file_paths_json = json.dumps(file_paths) if file_paths else "{}"
            
            cursor.execute('''
                INSERT INTO reports 
                (id, run_id, hostname, primary_classification, status, model_used, 
                 processing_time_seconds, summary, file_paths, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id,  # Use run_id as id
                run_id,
                hostname,
                classification,
                'completed',
                model_used,
                processing_time,
                summary[:500] if summary else "",  # First 500 chars
                file_paths_json,
                tags
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✓ Report added to database: {run_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add report: {e}")
            return False
    
    def get_all_reports(self, limit: int = 50) -> List[Dict]:
        """Fetch all reports, newest first."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM reports 
                ORDER BY created_date DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to fetch reports: {e}")
            return []
    
    def get_report(self, run_id: str) -> Optional[Dict]:
        """Fetch a specific report by run_id."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM reports WHERE run_id = ?', (run_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to fetch report: {e}")
            return None
    
    def search_reports(self, query: str, field: str = "hostname") -> List[Dict]:
        """Search reports by hostname, classification, or tags."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if field == "hostname":
                cursor.execute(
                    'SELECT * FROM reports WHERE hostname LIKE ? ORDER BY created_date DESC',
                    (f"%{query}%",)
                )
            elif field == "classification":
                cursor.execute(
                    'SELECT * FROM reports WHERE primary_classification LIKE ? ORDER BY created_date DESC',
                    (f"%{query}%",)
                )
            elif field == "tags":
                cursor.execute(
                    'SELECT * FROM reports WHERE tags LIKE ? ORDER BY created_date DESC',
                    (f"%{query}%",)
                )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM reports')
            total = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT COUNT(DISTINCT hostname) FROM reports'
            )
            unique_hosts = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT AVG(processing_time_seconds) FROM reports WHERE processing_time_seconds > 0'
            )
            avg_time = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_reports': total,
                'unique_hosts': unique_hosts,
                'avg_processing_time': avg_time or 0
            }
        except Exception as e:
            logger.error(f"❌ Stats query failed: {e}")
            return {}
    
    def delete_report(self, run_id: str) -> bool:
        """Delete a report from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM reports WHERE run_id = ?', (run_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Report deleted: {run_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete report: {e}")
            return False
