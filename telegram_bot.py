"""
Telegram Bot for Image to PDF Converter
Handles image uploads and converts them to PDF
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional
import asyncio
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from image_converter import ImageToPdfConverter

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ImageToPdfBot:
    """Telegram bot for converting images to PDF"""
    
    def __init__(self, token: str):
        self.token = token
        self.converter = ImageToPdfConverter()
        self.user_temp_files = {}  # Track temporary files per user
        self.user_compression_settings = {}  # Track compression settings per user
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.debug_dir = 'debug_output'
        
        # Create debug directory if in debug mode
        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🖼️ **Image to PDF Converter Bot**

Welcome! I can convert your images to PDF format.

**Features:**
• Convert single images to PDF
• Combine multiple images into one PDF
• **NEW:** PDF compression options
• Supports: JPG, PNG, BMP, TIFF, GIF, WebP

**How to use:**
1. Send me one or more images
2. Set compression (optional): /compress_high, /compress_medium, /compress_low
3. Use /convert when ready
4. I'll send you the PDF file with size info

**Commands:**
/start - Show this help message
/help - Show help message
/convert - Convert received images to PDF
/compress_high - High quality (95%)
/compress_medium - Medium quality (85%) - Default
/compress_low - Low quality (70%) - Smallest file
/clear - Clear pending images

Send me some images to get started! 📸
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📖 **Help - Image to PDF Converter**

**Supported Formats:**
• JPG/JPEG
• PNG
• BMP
• TIFF
• GIF
• WebP

**Compression Options:**
• /compress_high - Best quality (95%) - Larger files
• /compress_medium - Good balance (85%) - Default
• /compress_low - Smallest files (70%) - Lower quality

**Usage:**
1. Send one or more images
2. Set compression level (optional)
3. Type /convert to process them
4. Download the PDF file

**File Size Info:**
• Shows original image size
• Shows final PDF size
• Shows compression ratio when applicable

**Commands:**
/start - Start bot and see welcome message
/convert - Convert images to PDF
/compress_high - Set high quality compression
/compress_medium - Set medium quality compression
/compress_low - Set low quality compression
/clear - Clear all pending images
/help - Show this help message

**Tips:**
• Send multiple images to combine them into one PDF
• Images are processed in the order you send them
• Use compression for smaller file sizes
• Temporary files are automatically cleaned up
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def set_compression_high(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set compression to high quality"""
        user_id = update.effective_user.id
        self.user_compression_settings[user_id] = 'high'
        await update.message.reply_text("🔧 Compression set to **High Quality (95%)**\nBest quality, larger file size.", parse_mode=ParseMode.MARKDOWN)
    
    async def set_compression_medium(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set compression to medium quality"""
        user_id = update.effective_user.id
        self.user_compression_settings[user_id] = 'medium'
        await update.message.reply_text("🔧 Compression set to **Medium Quality (85%)**\nGood balance of quality and size.", parse_mode=ParseMode.MARKDOWN)
    
    async def set_compression_low(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set compression to low quality"""
        user_id = update.effective_user.id
        self.user_compression_settings[user_id] = 'low'
        await update.message.reply_text("🔧 Compression set to **Low Quality (70%)**\nSmallest file size, lower quality.", parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        # Clean up temporary files for this user
        if user_id in self.user_temp_files:
            for file_path in self.user_temp_files[user_id]:
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {e}")
            
            del self.user_temp_files[user_id]
        
        await update.message.reply_text("🗑️ Cleared all pending images!")
    
    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming images"""
        user_id = update.effective_user.id
        
        # Initialize user temp files list if needed
        if user_id not in self.user_temp_files:
            self.user_temp_files[user_id] = []
        
        # Get the largest photo available
        photo = update.message.photo[-1]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Download photo
            file = await context.bot.get_file(photo.file_id)
            await file.download_to_drive(temp_file.name)
            
            # Store temp file path
            self.user_temp_files[user_id].append(temp_file.name)
            
            # Check if it's a valid image
            try:
                img_info = self.converter.get_image_info(temp_file.name)
                if img_info:
                    await update.message.reply_text(
                        f"✅ Image received!\n"
                        f"Format: {img_info.get('format', 'Unknown')}\n"
                        f"Size: {img_info.get('size', 'Unknown')}\n"
                        f"Images pending: {len(self.user_temp_files[user_id])}\n\n"
                        f"Send more images or use /convert when ready!"
                    )
                else:
                    await update.message.reply_text("❌ Invalid image format. Please send a valid image.")
                    # Clean up invalid file
                    os.unlink(temp_file.name)
                    self.user_temp_files[user_id].remove(temp_file.name)
                    
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                await update.message.reply_text("❌ Error processing image. Please try again.")
                # Clean up on error
                os.unlink(temp_file.name)
                if temp_file.name in self.user_temp_files[user_id]:
                    self.user_temp_files[user_id].remove(temp_file.name)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads (images sent as files)"""
        user_id = update.effective_user.id
        document = update.message.document
        
        # Check if document is an image
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await update.message.reply_text("❌ Please send only image files.")
            return
        
        # Initialize user temp files list if needed
        if user_id not in self.user_temp_files:
            self.user_temp_files[user_id] = []
        
        # Get file extension
        file_extension = Path(document.file_name).suffix.lower()
        if file_extension not in self.converter.supported_formats:
            await update.message.reply_text(
                f"❌ Unsupported format: {file_extension}\n"
                f"Supported formats: {', '.join(self.converter.supported_formats)}"
            )
            return
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Download document
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(temp_file.name)
            
            # Store temp file path
            self.user_temp_files[user_id].append(temp_file.name)
            
            # Check if it's a valid image
            try:
                img_info = self.converter.get_image_info(temp_file.name)
                if img_info:
                    await update.message.reply_text(
                        f"✅ Image received!\n"
                        f"File: {document.file_name}\n"
                        f"Format: {img_info.get('format', 'Unknown')}\n"
                        f"Size: {img_info.get('size', 'Unknown')}\n"
                        f"Images pending: {len(self.user_temp_files[user_id])}\n\n"
                        f"Send more images or use /convert when ready!"
                    )
                else:
                    await update.message.reply_text("❌ Invalid image file. Please send a valid image.")
                    # Clean up invalid file
                    os.unlink(temp_file.name)
                    self.user_temp_files[user_id].remove(temp_file.name)
                    
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                await update.message.reply_text("❌ Error processing image. Please try again.")
                # Clean up on error
                os.unlink(temp_file.name)
                if temp_file.name in self.user_temp_files[user_id]:
                    self.user_temp_files[user_id].remove(temp_file.name)
    
    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /convert command"""
        user_id = update.effective_user.id
        
        # Check if user has pending images
        if user_id not in self.user_temp_files or not self.user_temp_files[user_id]:
            await update.message.reply_text(
                "❌ No images to convert!\n\n"
                "Please send me some images first, then use /convert."
            )
            return
        
        image_count = len(self.user_temp_files[user_id])
        compression = self.user_compression_settings.get(user_id, 'medium')
        
        # Send processing message
        processing_message = await update.message.reply_text(
            f"🔄 Converting {image_count} image(s) to PDF...\n"
            f"Compression: {compression.title()} quality\n"
            f"This may take a moment..."
        )
        
        try:
            # Generate debug filename if in debug mode
            if self.debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"user_{user_id}_{timestamp}_{image_count}images.pdf"
                debug_path = os.path.join(self.debug_dir, debug_filename)
                
                # Convert images to debug location
                if image_count == 1:
                    # Single image conversion
                    result = self.converter.convert_single_image(self.user_temp_files[user_id][0], debug_path, compression)
                else:
                    # Multiple images conversion
                    result = self.converter.convert_multiple_images(self.user_temp_files[user_id], debug_path, compression)
                
                pdf_path = result['pdf_path']
                logger.info(f"Debug mode: PDF saved to {debug_path}")
            else:
                # Normal conversion
                if image_count == 1:
                    # Single image conversion
                    result = self.converter.convert_single_image(self.user_temp_files[user_id][0], compress=compression)
                else:
                    # Multiple images conversion
                    result = self.converter.convert_multiple_images(self.user_temp_files[user_id], compress=compression)
                
                pdf_path = result['pdf_path']
            
            # Create file size info message
            if image_count == 1:
                size_info = f"📊 **File Size Info:**\n"
                size_info += f"📸 Original: {result['original_size']}\n"
                size_info += f"📄 PDF: {result['pdf_size']}\n"
                size_info += f"🔧 Compression: {result['compression_used'].title()}\n"
                size_info += f"📐 Format: {result['original_format']}\n"
                size_info += f"📏 Dimensions: {result['image_dimensions']}"
            else:
                size_info = f"📊 **File Size Info:**\n"
                size_info += f"📸 Total Original: {result['total_original_size']}\n"
                size_info += f"📄 PDF: {result['pdf_size']}\n"
                size_info += f"🔧 Compression: {result['compression_used'].title()}\n"
                size_info += f"🖼️ Images: {result['image_count']}"
            
            # Send PDF file with size info
            await update.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption=f"✅ Converted {image_count} image(s) to PDF!\n\n{size_info}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update processing message
            await processing_message.edit_text("✅ Conversion completed!")
            
            # Clean up PDF file after sending (only if not in debug mode)
            if not self.debug_mode:
                os.unlink(pdf_path)
            else:
                await update.message.reply_text(f"📁 Debug mode: PDF saved to {debug_path}")
            
        except Exception as e:
            logger.error(f"Error converting images: {e}")
            await processing_message.edit_text(
                f"❌ Error during conversion: {str(e)}\n"
                f"Please try again."
            )
        
        finally:
            # Clean up user's temporary files
            if user_id in self.user_temp_files:
                for file_path in self.user_temp_files[user_id]:
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        logger.error(f"Error cleaning up file {file_path}: {e}")
                
                del self.user_temp_files[user_id]
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and hasattr(update, 'message'):
            try:
                await update.message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
            except Exception:
                pass
    
    def setup_handlers(self, application: Application):
        """Setup bot handlers"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("convert", self.convert_command))
        application.add_handler(CommandHandler("compress_high", self.set_compression_high))
        application.add_handler(CommandHandler("compress_medium", self.set_compression_medium))
        application.add_handler(CommandHandler("compress_low", self.set_compression_low))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        application.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document))
        
        # Error handler
        application.add_error_handler(self.error_handler)
    
    async def set_bot_commands(self, application: Application):
        """Set bot commands"""
        commands = [
            BotCommand("start", "Start bot and see welcome message"),
            BotCommand("help", "Show help message"),
            BotCommand("convert", "Convert images to PDF"),
            BotCommand("compress_high", "Set high quality compression (95%)"),
            BotCommand("compress_medium", "Set medium quality compression (85%)"),
            BotCommand("compress_low", "Set low quality compression (70%)"),
            BotCommand("clear", "Clear all pending images")
        ]
        
        await application.bot.set_my_commands(commands)
    
    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.token).build()
        
        # Setup handlers
        self.setup_handlers(application)
        
        # Set bot commands
        application.job_queue.run_once(
            lambda context: asyncio.create_task(self.set_bot_commands(application)),
            when=1
        )
        
        logger.info("Starting Image to PDF Bot...")
        application.run_polling()

def create_bot(token: str) -> ImageToPdfBot:
    """Create bot instance"""
    return ImageToPdfBot(token)
