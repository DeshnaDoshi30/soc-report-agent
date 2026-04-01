import json
import logging
import ollama  
from pathlib import Path
from typing import Optional, Dict, Any
from src import config
from src.report_validator import HallucinationDetector
from src.docx_exporter import SOCDocxExporter

logger = logging.getLogger(__name__)

class IncidentReportGenerator:
    def __init__(self, model: Optional[str] = None):
        self.model = model or config.REPORT_MODEL
        self.template_dir = config.TEMPLATES_DIR
        self.output_dir = config.OUTPUT_DIR
        
        # Load the Permanent iSecurify Header
        self.global_header = self._load_template("global_header.txt")

    def _load_template(self, name: str) -> str:
        path = self.template_dir / name
        return path.read_text(encoding='utf-8') if path.exists() else ""

    def _trim_json_for_phase(self, full_json: Dict, phase: str) -> str:
        """Slices JSON safely to reduce context load on 1070 GPUs."""
        # Use .get() with a default empty dict {} to prevent NoneType errors
        metadata = full_json.get("METADATA", {})
        findings = full_json.get("FINDINGS", {})

        if phase == "A":
            # Metadata & High-level Classification for the Brief [cite: 72-84]
            trimmed = {
                "METADATA": metadata,
                "FINDINGS": {
                    "primary_classification": findings.get("primary_classification", "Unknown"),
                    "technical_summary": findings.get("technical_summary", "No summary available")
                }
            }
            return json.dumps(trimmed, indent=2)
            
        elif phase == "B":
            # Technical Findings & IPs for the Deep-Dive [cite: 161-178]
            return json.dumps(findings, indent=2)
            
        else:
            # RAG & Analyst Insights for the Resolution [cite: 196-253]
            trimmed = {
                "human_insight": full_json.get("human_insight", "No analyst notes provided."),
                "mitre_technique": findings.get("mitre_query", "N/A")
            }
            return json.dumps(trimmed, indent=2)

    def _call_ai_phase(self, phase_prompt: str, json_context: str, rag_context: str, bridge: str = "") -> str:
        """Executes a single generation phase with VRAM flushing."""
        full_instruction = f"{self.global_header}\n\n{phase_prompt}\n\n"
        if bridge:
            full_instruction += f"### PREVIOUS PROGRESS (CONTINUITY BRIDGE):\n{bridge}\n\n"
        
        full_instruction += f"### PRIMARY INCIDENT TRUTH (TRIMMED):\n{json_context}\n\n"
        full_instruction += f"### EXPERT CONTEXT (RAG):\n{rag_context}"

        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': full_instruction}],
            keep_alive=0, # Crucial for 10-series VRAM flushing
            options={
                "num_ctx": config.NUM_CTX,
                "temperature": config.REPORT_TEMP,
                "num_predict": 2048 # High token count for 5-page depth
            }
        )
        raw_content = response['message']['content']
        # Strip DeepSeek-R1 Thinking tags
        return raw_content.split("</think>")[-1].strip() if "</think>" in raw_content else raw_content

    def generate_report(self, incident_path: str, rag_context: str, run_id: str, hostname: str = "Production Server") -> bool:
        try:
            # 1. Load Source Data
            incident_data = json.loads(Path(incident_path).read_text(encoding='utf-8'))
            master_report = []

            # PHASE A: The Brief (Sections 1-3) [cite: 49-93]
            logger.info("ACT 1: Generating Executive Brief...")
            phase_a_out = self._call_ai_phase(
                self._load_template("phase_a.txt"),
                self._trim_json_for_phase(incident_data, "A"),
                rag_context
            )
            master_report.append(phase_a_out)

            # Create Bridge for Continuity
            bridge = f"Established incident as {incident_data.get('FINDINGS', {}).get('primary_classification')}. Summary: {phase_a_out[:300]}..."

            # PHASE B: Forensic Deep-Dive (Sections 4-5) [cite: 161-195]
            logger.info("ACT 2: Generating Forensic Deep-Dive...")
            phase_b_out = self._call_ai_phase(
                self._load_template("phase_b.txt"),
                self._trim_json_for_phase(incident_data, "B"),
                rag_context,
                bridge=bridge
            )
            master_report.append(phase_b_out)

            # PHASE C: The Resolution (Sections 6-10) [cite: 196-263]
            logger.info("ACT 3: Generating Resolution & Strategy...")
            phase_c_out = self._call_ai_phase(
                self._load_template("phase_c.txt"),
                self._trim_json_for_phase(incident_data, "C"),
                rag_context,
                bridge=f"Findings established. Impact assessed as high risk."
            )
            master_report.append(phase_c_out)

            # 2. Finalize & Export
            final_markdown = "\n\n".join(master_report)
            
            md_path = self.output_dir / f"incident_report_{run_id}.md"
            md_path.write_text(final_markdown, encoding='utf-8')

            # 3. Update the Exporter call to pass the hostname
            docx_path = self.output_dir / f"SOC_Report_{run_id}.docx"
            SOCDocxExporter(docx_path).generate(
                report_text=final_markdown, 
                run_id=run_id, 
                hostname=hostname # <--- Pass the extracted hostname here
            )

            # ... (Audit logic remains the same) ...

            return True

        except Exception as e:
            logger.error(f"Sequential Generation Failed: {e}")
            return False