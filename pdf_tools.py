"""
PDF utilities: merge and split.
"""

import os
from typing import List, Optional, Tuple

from pypdf import PdfReader, PdfWriter


class PdfTools:
    """Utility helpers for PDF operations."""

    def merge_pdfs(self, pdf_paths: List[str], output_path: Optional[str] = None) -> str:
        if not pdf_paths:
            raise ValueError("No PDF files provided")

        if output_path is None:
            output_path = "merged.pdf"

        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path

    def compress_pdf(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if output_path is None:
            base = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = f"{base}_compressed.pdf"

        import pikepdf

        with pikepdf.open(pdf_path) as pdf:
            pdf.save(output_path, optimize_streams=True, compress_streams=True)

        return output_path

    def split_pdf(self, pdf_path: str, page_ranges: Optional[List[Tuple[int, int]]] = None,
                  output_prefix: Optional[str] = None) -> List[str]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        if output_prefix is None:
            output_prefix = os.path.splitext(os.path.basename(pdf_path))[0]

        outputs = []

        if not page_ranges:
            # Default: split into one file per page
            for i in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                out_path = f"{output_prefix}_page_{i+1}.pdf"
                with open(out_path, "wb") as f:
                    writer.write(f)
                outputs.append(out_path)
            return outputs

        for start, end in page_ranges:
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range: {start}-{end} (total pages: {total_pages})")
            writer = PdfWriter()
            for i in range(start - 1, end):
                writer.add_page(reader.pages[i])
            out_path = f"{output_prefix}_{start}-{end}.pdf"
            with open(out_path, "wb") as f:
                writer.write(f)
            outputs.append(out_path)

        return outputs
