"""
Text/Markdown to PDF Converter
Uses ReportLab for simple text rendering.
"""

import os
import logging
import textwrap
from pathlib import Path
from typing import Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)


class TextToPdfConverter:
    """Convert text and markdown files to PDF."""

    SUPPORTED_FORMATS = {'.txt', '.md'}

    def __init__(self) -> None:
        self.supported_formats = self.SUPPORTED_FORMATS

    def is_supported_format(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats

    def convert_text(self, text_path: str, output_path: Optional[str] = None) -> dict:
        if not os.path.exists(text_path):
            raise FileNotFoundError(f"Text file not found: {text_path}")
        if not self.is_supported_format(text_path):
            raise ValueError(f"Unsupported text format: {text_path}")

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(text_path))[0]
            output_path = f"{base_name}.pdf"

        output_path = os.path.abspath(output_path)

        with open(text_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        self._render_text_to_pdf(content, output_path)

        return {
            "success": True,
            "pdf_path": output_path,
            "original_size": os.path.getsize(text_path),
            "pdf_size": os.path.getsize(output_path),
            "original_format": Path(text_path).suffix.lower(),
        }

    def _render_text_to_pdf(self, content: str, output_path: str) -> None:
        page_width, page_height = LETTER
        margin = 0.75 * inch
        font_name = "Times-Roman"
        font_size = 11
        leading = 14

        usable_width = page_width - (2 * margin)
        max_chars = int(usable_width / (font_size * 0.6))
        max_chars = max(40, max_chars)

        c = canvas.Canvas(output_path, pagesize=LETTER)
        c.setFont(font_name, font_size)

        y = page_height - margin
        for raw_line in content.splitlines():
            line = raw_line.rstrip("\n")
            if not line:
                y -= leading
            else:
                wrapped = textwrap.wrap(line, width=max_chars) or [""]
                for segment in wrapped:
                    if y < margin:
                        c.showPage()
                        c.setFont(font_name, font_size)
                        y = page_height - margin
                    c.drawString(margin, y, segment)
                    y -= leading

        c.save()
