"""
Office Document to PDF Converter
Uses LibreOffice (soffice) in headless mode.
"""

import os
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentToPdfConverter:
    """Convert Office documents to PDF using LibreOffice."""

    SUPPORTED_FORMATS = {'.docx', '.pptx', '.xlsx'}

    def __init__(self) -> None:
        self.supported_formats = self.SUPPORTED_FORMATS

    def is_supported_format(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats

    def _ensure_soffice(self) -> str:
        soffice_path = shutil.which('soffice')
        if not soffice_path:
            raise RuntimeError(
                "LibreOffice (soffice) not found. Install LibreOffice to enable "
                "DOCX/PPTX/XLSX conversion."
            )
        return soffice_path

    def convert_document(self, doc_path: str, output_path: Optional[str] = None) -> dict:
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Document not found: {doc_path}")
        if not self.is_supported_format(doc_path):
            raise ValueError(f"Unsupported document format: {doc_path}")

        self._ensure_soffice()

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(doc_path))[0]
            output_path = f"{base_name}.pdf"

        output_path = os.path.abspath(output_path)
        output_dir = os.path.dirname(output_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                "soffice",
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "pdf",
                "--outdir", tmpdir,
                doc_path
            ]
            logger.info("Converting document to PDF via LibreOffice")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"LibreOffice conversion failed: {result.stderr.strip() or result.stdout.strip()}"
                )

            # LibreOffice outputs with same base name
            generated = Path(tmpdir) / (Path(doc_path).stem + ".pdf")
            if not generated.exists():
                raise RuntimeError("LibreOffice did not produce a PDF output.")

            os.makedirs(output_dir, exist_ok=True)
            shutil.move(str(generated), output_path)

        original_size = os.path.getsize(doc_path)
        pdf_size = os.path.getsize(output_path)

        return {
            "success": True,
            "pdf_path": output_path,
            "original_size": original_size,
            "pdf_size": pdf_size,
            "original_format": Path(doc_path).suffix.lower(),
        }
