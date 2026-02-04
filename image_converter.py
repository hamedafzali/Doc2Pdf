"""
Image to PDF Converter Module
Handles conversion of various image formats to PDF
"""

import os
import img2pdf
from PIL import Image
from typing import List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageToPdfConverter:
    """Convert images to PDF format"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    
    def __init__(self):
        self.supported_formats = self.SUPPORTED_FORMATS
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
    
    def get_image_info(self, image_path: str) -> dict:
        """Get image information"""
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': os.path.getsize(image_path)
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {e}")
            return {}
    
    def convert_single_image(self, image_path: str, output_path: str = None) -> str:
        """
        Convert a single image to PDF
        
        Args:
            image_path: Path to the image file
            output_path: Path for the output PDF file (optional)
            
        Returns:
            Path to the generated PDF file
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not self.is_supported_format(image_path):
            raise ValueError(f"Unsupported image format: {image_path}")
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}.pdf"
        
        try:
            # Get image info for logging
            img_info = self.get_image_info(image_path)
            logger.info(f"Converting {image_path} ({img_info.get('format', 'unknown')}) to PDF")
            
            # Convert image to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_path, rotation=img2pdf.Rotation.ifvalid))
            
            logger.info(f"Successfully converted to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting {image_path} to PDF: {e}")
            raise
    
    def convert_multiple_images(self, image_paths: List[str], output_path: str = None) -> str:
        """
        Convert multiple images to a single PDF
        
        Args:
            image_paths: List of paths to image files
            output_path: Path for the output PDF file (optional)
            
        Returns:
            Path to the generated PDF file
        """
        if not image_paths:
            raise ValueError("No image paths provided")
        
        # Validate all images
        for img_path in image_paths:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")
            if not self.is_supported_format(img_path):
                raise ValueError(f"Unsupported image format: {img_path}")
        
        if output_path is None:
            output_path = "combined_images.pdf"
        
        try:
            logger.info(f"Converting {len(image_paths)} images to single PDF")
            
            # Convert multiple images to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_paths, rotation=img2pdf.Rotation.ifvalid))
            
            logger.info(f"Successfully converted to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting images to PDF: {e}")
            raise
    
    def batch_convert_directory(self, directory_path: str, output_dir: str = None) -> List[str]:
        """
        Convert all supported images in a directory to individual PDFs
        
        Args:
            directory_path: Path to directory containing images
            output_dir: Directory for output PDFs (optional)
            
        Returns:
            List of paths to generated PDF files
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if output_dir is None:
            output_dir = directory_path
        
        # Find all supported image files
        image_files = []
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path) and self.is_supported_format(file_path):
                image_files.append(file_path)
        
        if not image_files:
            logger.warning(f"No supported image files found in {directory_path}")
            return []
        
        converted_files = []
        logger.info(f"Found {len(image_files)} images to convert")
        
        for img_path in image_files:
            try:
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.pdf")
                
                converted_file = self.convert_single_image(img_path, output_path)
                converted_files.append(converted_file)
                
            except Exception as e:
                logger.error(f"Failed to convert {img_path}: {e}")
                continue
        
        logger.info(f"Successfully converted {len(converted_files)} images")
        return converted_files

# Convenience functions for direct usage
def convert_image_to_pdf(image_path: str, output_path: str = None) -> str:
    """Convert a single image to PDF"""
    converter = ImageToPdfConverter()
    return converter.convert_single_image(image_path, output_path)

def convert_images_to_pdf(image_paths: List[str], output_path: str = None) -> str:
    """Convert multiple images to a single PDF"""
    converter = ImageToPdfConverter()
    return converter.convert_multiple_images(image_paths, output_path)
