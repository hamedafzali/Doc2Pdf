"""
Image to PDF Converter Module
Handles conversion of various image formats to PDF
"""

import os
import img2pdf
from PIL import Image
from typing import List, Union, Optional
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageToPdfConverter:
    """Convert images to PDF format"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    COMPRESSION_QUALITY = {
        'high': 95,    # Best quality, larger file
        'medium': 85,  # Good balance
        'low': 70      # Smaller file, lower quality
    }
    
    def __init__(self):
        self.supported_formats = self.SUPPORTED_FORMATS
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def get_file_info(self, file_path: str) -> dict:
        """Get comprehensive file information"""
        try:
            file_size = os.path.getsize(file_path)
            return {
                'file_size': file_size,
                'file_size_formatted': self.format_file_size(file_size),
                'file_path': file_path
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
    
    def compress_image(self, image_path: str, quality: str = 'medium') -> str:
        """Compress image and return path to compressed image"""
        if quality not in self.COMPRESSION_QUALITY:
            quality = 'medium'
        
        try:
            with Image.open(image_path) as img:
                # Convert RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create compressed image in memory
                compressed_buffer = io.BytesIO()
                img.save(compressed_buffer, 
                       format='JPEG', 
                       quality=self.COMPRESSION_QUALITY[quality],
                       optimize=True)
                compressed_buffer.seek(0)
                
                # Save compressed image to temp file
                temp_path = image_path.replace('.', '_compressed.')
                with open(temp_path, 'wb') as f:
                    f.write(compressed_buffer.getvalue())
                
                original_size = os.path.getsize(image_path)
                compressed_size = os.path.getsize(temp_path)
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                logger.info(f"Image compressed: {self.format_file_size(original_size)} -> {self.format_file_size(compressed_size)} ({compression_ratio:.1f}% reduction)")
                
                return temp_path
                
        except Exception as e:
            logger.error(f"Error compressing image {image_path}: {e}")
            return image_path  # Return original if compression fails
    
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
    
    def convert_single_image(self, image_path: str, output_path: str = None, compress: str = None) -> dict:
        """
        Convert a single image to PDF
        
        Args:
            image_path: Path to the image file
            output_path: Path for the output PDF file (optional)
            compress: Compression quality ('high', 'medium', 'low') (optional)
            
        Returns:
            Dictionary with conversion results including file sizes
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not self.is_supported_format(image_path):
            raise ValueError(f"Unsupported image format: {image_path}")
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}.pdf"
        
        # Get original image info
        original_info = self.get_image_info(image_path)
        original_file_info = self.get_file_info(image_path)
        
        # Compress image if requested
        working_image_path = image_path
        if compress:
            working_image_path = self.compress_image(image_path, compress)
        
        try:
            logger.info(f"Converting {image_path} ({original_info.get('format', 'unknown')}) to PDF")
            
            # Convert image to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(working_image_path, rotation=img2pdf.Rotation.ifvalid))
            
            # Get PDF file info
            pdf_info = self.get_file_info(output_path)
            
            # Clean up compressed image if created
            if compress and working_image_path != image_path:
                os.unlink(working_image_path)
            
            result = {
                'success': True,
                'pdf_path': output_path,
                'original_size': original_file_info.get('file_size_formatted', 'Unknown'),
                'pdf_size': pdf_info.get('file_size_formatted', 'Unknown'),
                'original_format': original_info.get('format', 'Unknown'),
                'image_dimensions': original_info.get('size', 'Unknown'),
                'compression_used': compress or 'none'
            }
            
            logger.info(f"Successfully converted to {output_path} ({result['pdf_size']})")
            return result
            
        except Exception as e:
            logger.error(f"Error converting {image_path} to PDF: {e}")
            # Clean up compressed image if created
            if compress and working_image_path != image_path:
                try:
                    os.unlink(working_image_path)
                except:
                    pass
            raise
    
    def convert_multiple_images(self, image_paths: List[str], output_path: str = None, compress: str = None) -> dict:
        """
        Convert multiple images to a single PDF
        
        Args:
            image_paths: List of paths to image files
            output_path: Path for the output PDF file (optional)
            compress: Compression quality ('high', 'medium', 'low') (optional)
            
        Returns:
            Dictionary with conversion results including file sizes
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
        
        # Calculate total original size
        total_original_size = 0
        working_image_paths = []
        
        try:
            logger.info(f"Converting {len(image_paths)} images to single PDF")
            
            # Process each image
            for img_path in image_paths:
                # Get original file info
                original_file_info = self.get_file_info(img_path)
                total_original_size += original_file_info.get('file_size', 0)
                
                # Compress image if requested
                if compress:
                    compressed_path = self.compress_image(img_path, compress)
                    working_image_paths.append(compressed_path)
                else:
                    working_image_paths.append(img_path)
            
            # Convert multiple images to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(working_image_paths, rotation=img2pdf.Rotation.ifvalid))
            
            # Get PDF file info
            pdf_info = self.get_file_info(output_path)
            
            # Clean up compressed images
            if compress:
                for compressed_path in working_image_paths:
                    if compressed_path != img_path and os.path.exists(compressed_path):
                        os.unlink(compressed_path)
            
            result = {
                'success': True,
                'pdf_path': output_path,
                'total_original_size': self.format_file_size(total_original_size),
                'pdf_size': pdf_info.get('file_size_formatted', 'Unknown'),
                'image_count': len(image_paths),
                'compression_used': compress or 'none'
            }
            
            logger.info(f"Successfully converted {len(image_paths)} images to {output_path} ({result['pdf_size']})")
            return result
            
        except Exception as e:
            logger.error(f"Error converting images to PDF: {e}")
            # Clean up compressed images on error
            if compress:
                for compressed_path in working_image_paths:
                    if os.path.exists(compressed_path) and compressed_path != img_path:
                        try:
                            os.unlink(compressed_path)
                        except:
                            pass
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

    def ocr_image(self, image_path: str, language: str = "eng") -> str:
        """
        Extract text from an image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            language: OCR language code (default: 'eng' for English)
            
        Returns:
            Extracted text as string
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            import pytesseract
            from PIL import Image
        except ImportError as e:
            raise RuntimeError(f"OCR dependencies not available: {e}. Install pytesseract and ensure Tesseract is installed.")
        
        try:
            # Set TESSDATA_PREFIX environment variable for Tesseract
            os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'
            
            # Open image
            image = Image.open(image_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, lang=language)
            
            logger.info(f"OCR completed for {image_path}, extracted {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error performing OCR on {image_path}: {e}")
            raise RuntimeError(f"OCR failed: {str(e)}")

# Convenience functions for direct usage
def convert_image_to_pdf(image_path: str, output_path: str = None, compress: str = None) -> dict:
    """Convert a single image to PDF"""
    converter = ImageToPdfConverter()
    return converter.convert_single_image(image_path, output_path, compress)

def convert_images_to_pdf(image_paths: List[str], output_path: str = None, compress: str = None) -> dict:
    """Convert multiple images to a single PDF"""
    converter = ImageToPdfConverter()
    return converter.convert_multiple_images(image_paths, output_path, compress)
