"""
Shared bot types and enums.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CompressionLevel(Enum):
    """Compression quality levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def quality(self) -> int:
        """Get compression quality percentage"""
        return {
            CompressionLevel.HIGH: 95,
            CompressionLevel.MEDIUM: 85,
            CompressionLevel.LOW: 70
        }[self]

    @property
    def title(self) -> str:
        """Get human-readable title"""
        return {
            CompressionLevel.HIGH: "High Quality (95%)",
            CompressionLevel.MEDIUM: "Medium Quality (85%)",
            CompressionLevel.LOW: "Low Quality (70%)"
        }[self]


class Language(Enum):
    """Supported languages"""
    EN = "en"
    DE = "de"
    FA = "fa"

    @property
    def title(self) -> str:
        return {
            Language.EN: "English",
            Language.DE: "Deutsch",
            Language.FA: "فارسی"
        }[self]


@dataclass
class ConversionResult:
    """Result of image conversion"""
    success: bool
    pdf_path: Optional[str] = None
    original_size: Optional[str] = None
    pdf_size: Optional[str] = None
    compression_used: Optional[CompressionLevel] = None
    original_format: Optional[str] = None
    image_dimensions: Optional[str] = None
    image_count: Optional[int] = None
    total_original_size: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ImageInfo:
    """Information about processed image"""
    file_path: str
    size: str
    format: str
    dimensions: Optional[str] = None
