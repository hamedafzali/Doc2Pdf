"""
User session management.
"""

import os
import logging
from typing import List

from bot_types import CompressionLevel, Language

logger = logging.getLogger(__name__)


class UserSession:
    """Manages user session data"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.temp_files: List[str] = []
        self.compression_setting: CompressionLevel = CompressionLevel.MEDIUM
        self.pdf_files: List[str] = []
        self.language: Language = Language.EN

    def add_temp_file(self, file_path: str):
        """Add temporary file to session"""
        self.temp_files.append(file_path)

    def clear_temp_files(self):
        """Clean up all temporary files"""
        for file_path in self.temp_files:
            try:
                os.unlink(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {e}")
        self.temp_files.clear()

    def get_file_count(self) -> int:
        """Get number of pending files"""
        return len(self.temp_files)

    def add_pdf_file(self, file_path: str):
        """Add PDF file to session"""
        self.pdf_files.append(file_path)

    def clear_pdf_files(self):
        """Clean up all pending PDF files"""
        for file_path in self.pdf_files:
            try:
                os.unlink(file_path)
            except Exception:
                pass
        self.pdf_files.clear()

    def get_pdf_count(self) -> int:
        """Get number of pending PDFs"""
        return len(self.pdf_files)
