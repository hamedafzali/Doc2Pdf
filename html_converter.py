"""
HTML/URL to PDF Converter
Uses wkhtmltopdf.
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class HtmlToPdfConverter:
    """Convert HTML files or URLs to PDF using wkhtmltopdf."""

    SUPPORTED_FORMATS = {'.html', '.htm'}

    def __init__(self) -> None:
        self.supported_formats = self.SUPPORTED_FORMATS

    def _ensure_wkhtmltopdf(self) -> str:
        wkhtmltopdf_path = shutil.which('wkhtmltopdf')
        if not wkhtmltopdf_path:
            raise RuntimeError("wkhtmltopdf not found. Install it to enable HTML/URL conversion.")
        return wkhtmltopdf_path

    def is_supported_format(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats

    def convert_html_file(self, html_path: str, output_path: Optional[str] = None) -> dict:
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        if not self.is_supported_format(html_path):
            raise ValueError(f"Unsupported HTML format: {html_path}")

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(html_path))[0]
            output_path = f"{base_name}.pdf"

        output_path = os.path.abspath(output_path)
        self._ensure_wkhtmltopdf()

        cmd = ["wkhtmltopdf", html_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "wkhtmltopdf failed")

        return {
            "success": True,
            "pdf_path": output_path,
            "original_size": os.path.getsize(html_path),
            "pdf_size": os.path.getsize(output_path),
            "original_format": Path(html_path).suffix.lower(),
        }

    def convert_url(self, url: str, output_path: Optional[str] = None) -> dict:
        if output_path is None:
            output_path = "webpage.pdf"

        output_path = os.path.abspath(output_path)
        self._ensure_wkhtmltopdf()

        cmd = ["wkhtmltopdf", url, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "wkhtmltopdf failed")

        return {
            "success": True,
            "pdf_path": output_path,
            "pdf_size": os.path.getsize(output_path),
            "original_format": "url",
        }
