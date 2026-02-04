#!/usr/bin/env python3
"""
Main application for Image to PDF Converter
Provides CLI interface and prepares for Telegram bot integration
"""

import argparse
import os
import sys
from pathlib import Path
from image_converter import ImageToPdfConverter, convert_image_to_pdf, convert_images_to_pdf

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Convert images to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg                    # Convert single image
  %(prog)s image.jpg -o output.pdf      # Convert with custom output name
  %(prog)s *.jpg                        # Convert multiple images to one PDF
  %(prog)s --batch /path/to/images      # Convert directory of images
        """
    )
    
    parser.add_argument('images', nargs='*', help='Image file(s) to convert')
    parser.add_argument('-o', '--output', help='Output PDF file path')
    parser.add_argument('--batch', metavar='DIRECTORY', help='Convert all images in directory')
    parser.add_argument('--list-formats', action='store_true', help='List supported image formats')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.list_formats:
        converter = ImageToPdfConverter()
        print("Supported image formats:")
        for fmt in sorted(converter.supported_formats):
            print(f"  {fmt}")
        return
    
    if args.batch:
        # Batch conversion mode
        converter = ImageToPdfConverter()
        try:
            converted_files = converter.batch_convert_directory(args.batch)
            if converted_files:
                print(f"Successfully converted {len(converted_files)} images:")
                for file in converted_files:
                    print(f"  {file}")
            else:
                print("No images found to convert")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.images:
        # Single or multiple image conversion
        try:
            if len(args.images) == 1:
                # Single image conversion
                output_path = convert_image_to_pdf(args.images[0], args.output)
                print(f"Converted: {args.images[0]} -> {output_path}")
            else:
                # Multiple images to single PDF
                output_path = convert_images_to_pdf(args.images, args.output)
                print(f"Combined {len(args.images)} images -> {output_path}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\nNo input provided. Use --help for usage information.")

if __name__ == "__main__":
    main()
