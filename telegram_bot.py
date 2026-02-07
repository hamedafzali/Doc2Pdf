#!/usr/bin/env python3
"""
Refactored Telegram Bot for Image to PDF Converter
Clean, modular, and maintainable codebase
"""

import os
import tempfile
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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


class UserSession:
    """Manages user session data"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.temp_files: List[str] = []
        self.compression_setting: CompressionLevel = CompressionLevel.MEDIUM
        
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


class MessageTemplates:
    """Centralized message templates"""
    
    @staticmethod
    def welcome() -> str:
        """Welcome message"""
        return """
🖼️ **Image to PDF Converter Bot**

Welcome! I can convert your images to PDF format.

**Features:**
• Convert single images to PDF
• Combine multiple images into one PDF
• **NEW:** PDF compression options
• Supports: JPG, PNG, BMP, TIFF, GIF, WebP

**How to use:**
1. Send me one or more images
2. Use /convert to see compression options
3. Choose compression level:
   - /compress_high (95%) - Best quality
   - /compress_medium (85%) - Default
   - /compress_low (70%) - Smallest file
   - /convert_now - Use current setting
4. Download the PDF file with detailed size info

**Commands:**
/start - Show this help message
/help - Show help message
/convert - Choose compression options
/convert_now - Convert with current settings
/compress_high - Set high quality compression (95%)
/compress_medium - Set medium quality compression (85%) - Default
/compress_low - Set low quality compression (70%) - Smallest file
/clear - Clear pending images

Send me some images to get started! 📸
        """
    
    @staticmethod
    def help() -> str:
        """Help message"""
        return """
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
2. Use /convert to see compression options
3. Choose compression level or use /convert_now
4. Download the PDF file with detailed size information

**File Size Info:**
• Shows original image size
• Shows final PDF size
• Shows compression ratio when applicable

**Commands:**
/start - Start bot and see welcome message
/convert - Choose compression options
/convert_now - Convert with current settings
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
    
    @staticmethod
    def compression_options(image_count: int, current_setting: CompressionLevel) -> str:
        """Compression options message"""
        message = f"🖼️ Found {image_count} image(s) to convert\n\n"
        message += "🔧 **Choose compression level:**\n\n"
        message += "1️⃣ /compress_high - High Quality (95%)\n"
        message += "2️⃣ /compress_medium - Medium Quality (85%) - Default\n"
        message += "3️⃣ /compress_low - Low Quality (70%) - Smallest file\n"
        message += "4️⃣ /convert_now - Use current setting\n"
        message += f"Current setting: {current_setting.title}"
        return message
    
    @staticmethod
    def image_received(file_info: ImageInfo, pending_count: int) -> str:
        """Image received confirmation"""
        return (
            f"✅ Image received!\n"
            f"Format: {file_info.format}\n"
            f"Size: {file_info.size}\n"
            f"Images pending: {pending_count}\n\n"
            f"Send more images or use /convert when ready!"
        )
    
    @staticmethod
    def processing_start(image_count: int, compression: CompressionLevel) -> str:
        """Processing started message"""
        return (
            f"🔄 Converting {image_count} image(s) to PDF...\n"
            f"Compression: {compression.title}\n"
            f"This may take a moment..."
        )
    
    @staticmethod
    def conversion_success(result: ConversionResult, image_count: int) -> str:
        """Conversion success message"""
        if image_count == 1:
            return "✅ Conversion completed!"
        else:
            return f"✅ {image_count} images converted to PDF!"
    
    @staticmethod
    def file_size_info(result: ConversionResult) -> str:
        """File size information"""
        if result.image_count == 1:
            return (
                "📊 **File Size Info:**\n"
                f"📸 Original: {result.original_size}\n"
                f"📄 PDF: {result.pdf_size}\n"
                f"🔧 Compression: {result.compression_used.title}\n"
                f"📐 Format: {result.original_format}\n"
                f"📏 Dimensions: {result.image_dimensions}"
            )
        else:
            return (
                "📊 **File Size Info:**\n"
                f"📸 Total Original: {result.total_original_size}\n"
                f"📄 PDF: {result.pdf_size}\n"
                f"🔧 Compression: {result.compression_used.title}\n"
                f"🖼️ Images: {result.image_count}"
            )
    
    @staticmethod
    def conversion_error(error_message: str) -> str:
        """Conversion error message"""
        return f"❌ Error during conversion: {error_message}\nPlease try again."
    
    @staticmethod
    def no_images() -> str:
        """No images message"""
        return "❌ No images to convert!\n\nPlease send me some images first, then use /convert."
    
    @staticmethod
    def invalid_image() -> str:
        """Invalid image message"""
        return "❌ Invalid image format. Please send a valid image."
    
    @staticmethod
    def unsupported_format(file_extension: str, supported_formats: List[str]) -> str:
        """Unsupported format message"""
        return (
            f"❌ Unsupported format: {file_extension}\n"
            f"Supported formats: {', '.join(supported_formats)}"
        )
    
    @staticmethod
    def files_cleared() -> str:
        """Files cleared message"""
        return "🗑️ Cleared all pending images!"
    
    @staticmethod
    def compression_set(compression: CompressionLevel) -> str:
        """Compression set message"""
        return f"🔧 Compression set to **{compression.title}**"


class ImageToPdfBot:
    """Refactored Telegram bot for converting images to PDF"""
    
    def __init__(self, token: str):
        self.token = token
        self.converter = ImageToPdfConverter()
        self.user_sessions: Dict[int, UserSession] = {}
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.debug_dir = 'debug_output'
        
        # Create debug directory if in debug mode
        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)
        
        logger.info(f"Bot initialized. Debug mode: {self.debug_mode}")
    
    def get_user_session(self, user_id: int) -> UserSession:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id)
        return self.user_sessions[user_id]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(MessageTemplates.welcome(), parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(MessageTemplates.help(), parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command"""
        session = self.get_user_session(update.effective_user.id)
        session.clear_temp_files()
        await update.message.reply_text(MessageTemplates.files_cleared())
    
    async def set_compression(self, update: Update, context: ContextTypes.DEFAULT_TYPE, compression: CompressionLevel) -> None:
        """Set compression level and convert"""
        session = self.get_user_session(update.effective_user.id)
        session.compression_setting = compression
        
        await update.message.reply_text(MessageTemplates.compression_set(compression), parse_mode=ParseMode.MARKDOWN)
        # Auto-convert after setting compression
        await self.convert_now_command(update, context)
    
    async def set_compression_high(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set high quality compression"""
        await self.set_compression(update, context, CompressionLevel.HIGH)
    
    async def set_compression_medium(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set medium quality compression"""
        await self.set_compression(update, context, CompressionLevel.MEDIUM)
    
    async def set_compression_low(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set low quality compression"""
        await self.set_compression(update, context, CompressionLevel.LOW)
    
    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /convert command"""
        session = self.get_user_session(update.effective_user.id)
        
        if not session.get_file_count():
            await update.message.reply_text(MessageTemplates.no_images())
            return
        
        await update.message.reply_text(
            MessageTemplates.compression_options(session.get_file_count(), session.compression_setting),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def convert_now_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /convert_now command"""
        session = self.get_user_session(update.effective_user.id)
        
        if not session.get_file_count():
            await update.message.reply_text(MessageTemplates.no_images())
            return
        
        image_count = session.get_file_count()
        compression = session.compression_setting
        
        # Send processing message
        processing_message = await update.message.reply_text(
            MessageTemplates.processing_start(image_count, compression)
        )
        
        try:
            # Generate debug filename if in debug mode
            if self.debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"user_{update.effective_user.id}_{timestamp}_{image_count}images.pdf"
                debug_path = os.path.join(self.debug_dir, debug_filename)
                
                # Convert images to debug location
                if image_count == 1:
                    result = self._convert_single_image(session.temp_files[0], debug_path, compression)
                else:
                    result = self._convert_multiple_images(session.temp_files, debug_path, compression)
                
                logger.info(f"Debug mode: PDF saved to {debug_path}")
            else:
                # Normal conversion
                if image_count == 1:
                    result = self._convert_single_image(session.temp_files[0], compress=compression)
                else:
                    result = self._convert_multiple_images(session.temp_files, compress=compression)
            
            # Send results
            await self._send_conversion_results(update, result, processing_message, image_count)
            
        except Exception as e:
            logger.error(f"Error converting images: {e}")
            await processing_message.edit_text(MessageTemplates.conversion_error(str(e)))
        
        finally:
            # Clean up temporary files
            session.clear_temp_files()
    
    async def _convert_single_image(self, image_path: str, output_path: Optional[str] = None, compress: CompressionLevel = CompressionLevel.MEDIUM) -> ConversionResult:
        """Convert single image to PDF"""
        try:
            result = self.converter.convert_single_image(image_path, output_path, compress)
            return ConversionResult(
                success=True,
                pdf_path=result['pdf_path'],
                original_size=result.get('original_size'),
                pdf_size=result.get('pdf_size'),
                compression_used=compress,
                original_format=result.get('original_format'),
                image_dimensions=result.get('image_dimensions')
            )
        except Exception as e:
            logger.error(f"Error converting single image: {e}")
            return ConversionResult(success=False, error_message=str(e))
    
    async def _convert_multiple_images(self, image_paths: List[str], output_path: Optional[str] = None, compress: CompressionLevel = CompressionLevel.MEDIUM) -> ConversionResult:
        """Convert multiple images to PDF"""
        try:
            result = self.converter.convert_multiple_images(image_paths, output_path, compress)
            return ConversionResult(
                success=True,
                pdf_path=result['pdf_path'],
                total_original_size=result.get('total_original_size'),
                pdf_size=result.get('pdf_size'),
                compression_used=compress,
                image_count=result.get('image_count')
            )
        except Exception as e:
            logger.error(f"Error converting multiple images: {e}")
            return ConversionResult(success=False, error_message=str(e))
    
    async def _send_conversion_results(self, update: Update, result: ConversionResult, processing_message, image_count: int) -> None:
        """Send conversion results to user"""
        if not result.success:
            await processing_message.edit_text(MessageTemplates.conversion_error(result.error_message))
            return
        
        # Send PDF file
        await update.message.reply_document(
            document=open(result.pdf_path, 'rb'),
            caption=MessageTemplates.conversion_success(result, image_count),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update processing message
        await processing_message.edit_text(MessageTemplates.conversion_success(result, image_count))
        
        # Send file size info
        await update.message.reply_text(MessageTemplates.file_size_info(result), parse_mode=ParseMode.MARKDOWN)
        
        # Clean up PDF file after sending (only if not in debug mode)
        if not self.debug_mode:
            os.unlink(result.pdf_path)
        else:
            await update.message.reply_text(f"📁 Debug mode: PDF saved to {result.pdf_path}")
    
    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming images"""
        session = self.get_user_session(update.effective_user.id)
        
        # Get the largest photo available
        photo = update.message.photo[-1]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Download photo
            file = await context.bot.get_file(photo.file_id)
            await file.download_to_drive(temp_file.name)
            
            # Store temp file path
            session.add_temp_file(temp_file.name)
            
            # Get image info
            img_info = self._get_image_info(temp_file.name)
            if img_info:
                await update.message.reply_text(
                    MessageTemplates.image_received(img_info, session.get_file_count()),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(MessageTemplates.invalid_image())
                # Clean up invalid file
                os.unlink(temp_file.name)
                session.temp_files.remove(temp_file.name)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document uploads (images sent as files)"""
        session = self.get_user_session(update.effective_user.id)
        document = update.message.document
        
        # Check if document is an image
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await update.message.reply_text("❌ Please send only image files.")
            return
        
        # Get file extension
        file_extension = Path(document.file_name).suffix.lower()
        if file_extension not in self.converter.supported_formats:
            await update.message.reply_text(
                MessageTemplates.unsupported_format(file_extension, self.converter.supported_formats)
            )
            return
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Download document
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(temp_file.name)
            
            # Store temp file path
            session.add_temp_file(temp_file.name)
            
            # Get image info
            img_info = self._get_image_info(temp_file.name)
            if img_info:
                await update.message.reply_text(
                    MessageTemplates.image_received(img_info, session.get_file_count()),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(MessageTemplates.invalid_image())
                # Clean up invalid file
                os.unlink(temp_file.name)
                session.temp_files.remove(temp_file.name)
    
    def _get_image_info(self, image_path: str) -> Optional[ImageInfo]:
        """Get image information"""
        try:
            info = self.converter.get_image_info(image_path)
            if info:
                return ImageInfo(
                    file_path=image_path,
                    size=info.get('size', 'Unknown'),
                    format=info.get('format', 'Unknown'),
                    dimensions=info.get('dimensions', 'Unknown')
                )
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
        return None
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and hasattr(update, 'message'):
            try:
                await update.message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
            except Exception:
                pass
    
    def setup_handlers(self, application: Application) -> None:
        """Setup bot handlers"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("convert", self.convert_command))
        application.add_handler(CommandHandler("convert_now", self.convert_now_command))
        application.add_handler(CommandHandler("compress_high", self.set_compression_high))
        application.add_handler(CommandHandler("compress_medium", self.set_compression_medium))
        application.add_handler(CommandHandler("compress_low", self.set_compression_low))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        application.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document))
        
        # Error handler
        application.add_error_handler(self.error_handler)
    
    async def set_bot_commands(self, application: Application) -> None:
        """Set bot commands"""
        commands = [
            BotCommand("start", "Start bot and see welcome message"),
            BotCommand("help", "Show help message"),
            BotCommand("convert", "Choose compression options"),
            BotCommand("convert_now", "Convert with current settings"),
            BotCommand("compress_high", "Set high quality compression (95%)"),
            BotCommand("compress_medium", "Set medium quality compression (85%)"),
            BotCommand("compress_low", "Set low quality compression (70%)"),
            BotCommand("clear", "Clear all pending images")
        ]
        
        await application.bot.set_my_commands(commands)
    
    def run(self) -> None:
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


def main() -> None:
    """Main function to run the bot"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create and run bot
    bot = create_bot(token)
    bot.run()


if __name__ == '__main__':
    main()
