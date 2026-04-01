import logging
from typing import cast
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.styles.style import _ParagraphStyle

logger = logging.getLogger(__name__)

class SOCDocxExporter:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self):
        """Sets corporate blue branding with explicit type casting and safe lookups [cite: 1-11]."""
        
        # 1. Normal Text Styling [cite: 11]
        if 'Normal' in self.doc.styles:
            style = cast(_ParagraphStyle, self.doc.styles['Normal'])
            style.font.name = 'Calibri'
            style.font.size = Pt(11)

        # 2. Title Styling (Blue Header) [cite: 1-7]
        if 'Title' in self.doc.styles:
            title_style = cast(_ParagraphStyle, self.doc.styles['Title'])
            title_style.font.name = 'Calibri'
            title_style.font.size = Pt(24)
            title_style.font.bold = True
            title_style.font.color.rgb = RGBColor(0, 32, 96) # Dark Blue

        # 3. Heading 1 Styling (Section Headers) [cite: 265-275]
        if 'Heading 1' in self.doc.styles:
            h1 = cast(_ParagraphStyle, self.doc.styles['Heading 1'])
            h1.font.name = 'Calibri'
            h1.font.size = Pt(14)
            h1.font.bold = True
            h1.font.color.rgb = RGBColor(0, 32, 96) # iSecurify Blue

    def _add_footer(self):
        """Adds the mandatory Confidentiality footer[cite: 24, 282, 516]."""
        section = self.doc.sections[0]
        footer = section.footer
        p = footer.paragraphs[0]
        p.text = "Confidential Document - For Internal Use Only"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Accessing font safely for the footer
        run = p.runs[0] if p.runs else p.add_run()
        run.font.size = Pt(9)
        run.font.italic = True

    def _add_cover_page(self, run_id: str, hostname: str):
        """Generates the professional cover page [cite: 1-24, 265-282]."""
        self.doc.add_heading('iSecurify', 0).alignment = WD_ALIGN_PARAGRAPH.LEFT
        self.doc.add_heading('SOC INVESTIGATION REPORT', level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        for _ in range(3): self.doc.add_paragraph()

        # Prepared For / By Block [cite: 10-13, 274-277]
        table = self.doc.add_table(rows=4, cols=2)
        data = [
            ("Subject:", f"Forensic Analysis of {hostname}"),
            ("Prepared For:", f"Infrastructure - {hostname}"),
            ("Prepared By:", "iSecurify - Experts in Cybersecurity Solutions"),
            ("Report ID:", run_id)
        ]
        
        for i, (key, value) in enumerate(data):
            row_cells = table.rows[i].cells
            p_key = row_cells[0].paragraphs[0]
            p_key.add_run(key).bold = True
            row_cells[1].text = value

        self.doc.add_page_break()

    def generate(self, report_text: str, run_id: str, hostname: str = "Production Server"):
        """Converts phased Markdown into a professional Word document."""
        self._add_cover_page(run_id, hostname)
        self._add_footer()

        # Content Parsing
        for block in report_text.split('\n\n'):
            block = block.strip()
            if not block: continue

            # Section Headers [cite: 27-46, 285-304]
            if block.startswith('#'):
                level = block.count('#')
                clean_text = block.replace('#', '').strip()
                self.doc.add_heading(clean_text, level=min(level, 3))
            
            # List Items / Key Findings [cite: 58-61, 312-317]
            elif block.startswith('-'):
                for line in block.split('\n'):
                    p = self.doc.add_paragraph(style='List Bullet')
                    line = line.replace('-', '').replace('**', '').strip()
                    if ':' in line:
                        key, val = line.split(':', 1)
                        p.add_run(f"{key.strip()}: ").bold = True
                        p.add_run(val.strip())
                    else:
                        p.add_run(line)
            
            # Standard Paragraphs with Justification 
            else:
                p = self.doc.add_paragraph(block)
                # Corrected enum name for 'Justified' alignment
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY 

        self.doc.save(str(self.output_path))
        logger.info(f"✓ Professional iSecurify Report Saved: {self.output_path.name}")