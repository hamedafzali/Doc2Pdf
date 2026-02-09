#!/usr/bin/env python3
"""
Create a simple profile picture for the Doc2Pdf bot
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_profile_picture():
    """Create a profile picture for the bot"""
    # Create a 512x512 image (Telegram profile picture size)
    size = 512
    image = Image.new('RGB', (size, size), color='#2563EB')  # Telegram blue background
    
    draw = ImageDraw.Draw(image)
    
    # Draw a simple PDF icon
    # White rectangle for PDF icon
    pdf_rect = [(size//4, size//3), (3*size//4, 2*size//3)]
    draw.rectangle(pdf_rect, fill='white', outline='white', width=2)
    
    # Draw "PDF" text
    try:
        # Try to use a larger font
        font_size = size // 8
        font = ImageFont.load_default()
    except:
        font = None
    
    text = "PDF"
    if font:
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 10
        text_height = 20
    
    # Center the text
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    draw.text((text_x, text_y), text, fill='#2563EB', font=font)
    
    # Add "Doc2Pdf" text at bottom
    bottom_text = "Doc2Pdf"
    try:
        font_small = ImageFont.load_default()
    except:
        font_small = None
    
    if font_small:
        bbox_small = draw.textbbox((0, 0), bottom_text, font=font_small)
        small_width = bbox_small[2] - bbox_small[0]
        small_height = bbox_small[3] - bbox_small[1]
    else:
        small_width = len(bottom_text) * 8
        small_height = 15
    
    small_x = (size - small_width) // 2
    small_y = size - small_height - 20
    
    draw.text((small_x, small_y), bottom_text, fill='white', font=font_small)
    
    # Save the image
    image.save('profile.jpg', 'JPEG', quality=95)
    print("✅ Profile picture created: profile.jpg")
    
    # Also create a smaller version for display
    image.thumbnail((128, 128), Image.Resampling.LANCZOS)
    image.save('profile_small.jpg', 'JPEG', quality=90)
    print("✅ Small profile picture created: profile_small.jpg")

if __name__ == "__main__":
    create_profile_picture()
