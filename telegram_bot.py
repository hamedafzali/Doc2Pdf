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

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from image_converter import ImageToPdfConverter
from document_converter import DocumentToPdfConverter
from text_converter import TextToPdfConverter
from pdf_tools import PdfTools
from html_converter import HtmlToPdfConverter
from bot_types import CompressionLevel, Language, ConversionResult, ImageInfo
from sessions import UserSession
from messages import MessageTemplates

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ImageToPdfBot:
    """Refactored Telegram bot for converting images to PDF"""
    
    def __init__(self, token: str):
        self.token = token
        self.converter = ImageToPdfConverter()
        self.doc_converter = DocumentToPdfConverter()
        self.text_converter = TextToPdfConverter()
        self.pdf_tools = PdfTools()
        self.html_converter = HtmlToPdfConverter()
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
        session = self.get_user_session(update.effective_user.id)
        await update.message.reply_text(
            MessageTemplates.t("welcome", session.language),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        session = self.get_user_session(update.effective_user.id)
        await update.message.reply_text(
            MessageTemplates.t("help", session.language),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command"""
        session = self.get_user_session(update.effective_user.id)
        session.clear_temp_files()
        session.clear_pdf_files()
        await update.message.reply_text(MessageTemplates.t("files_cleared", session.language))

    async def set_language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set user language"""
        session = self.get_user_session(update.effective_user.id)
        if not context.args:
            await update.message.reply_text(MessageTemplates.t("lang_usage", session.language))
            return

        lang_arg = context.args[0].lower()
        lang_map = {"en": Language.EN, "de": Language.DE, "fa": Language.FA}
        if lang_arg not in lang_map:
            await update.message.reply_text(MessageTemplates.t("lang_usage", session.language))
            return

        session.language = lang_map[lang_arg]
        await update.message.reply_text(MessageTemplates.t("lang_set", session.language))
    
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

    async def merge_pdfs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Merge all pending PDFs into one"""
        session = self.get_user_session(update.effective_user.id)
        if not session.get_pdf_count():
            await update.message.reply_text(MessageTemplates.t("no_pdfs", session.language))
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "merged.pdf")
            try:
                merged_path = self.pdf_tools.merge_pdfs(session.pdf_files, output_path)
                await update.message.reply_document(
                    document=open(merged_path, "rb"),
                    caption="✅ PDFs merged successfully!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error merging PDFs: {e}")
                await update.message.reply_text(f"❌ Merge failed: {e}")
            finally:
                session.clear_pdf_files()

    async def split_pdf_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Split the last received PDF into one file per page"""
        session = self.get_user_session(update.effective_user.id)
        if not session.get_pdf_count():
            await update.message.reply_text(MessageTemplates.t("no_pdfs", session.language))
            return

        source_pdf = session.pdf_files[-1]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_prefix = os.path.join(temp_dir, "split")
            try:
                outputs = self.pdf_tools.split_pdf(source_pdf, output_prefix=output_prefix)
                for out_path in outputs:
                    await update.message.reply_document(
                        document=open(out_path, "rb"),
                        caption="✅ Split page",
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as e:
                logger.error(f"Error splitting PDF: {e}")
                await update.message.reply_text(f"❌ Split failed: {e}")
            finally:
                session.clear_pdf_files()

    async def compress_pdf_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Compress the last received PDF"""
        session = self.get_user_session(update.effective_user.id)
        if not session.get_pdf_count():
            await update.message.reply_text(MessageTemplates.t("no_pdfs", session.language))
            return

        source_pdf = session.pdf_files[-1]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "compressed.pdf")
            try:
                compressed_path = self.pdf_tools.compress_pdf(source_pdf, output_path)
                await update.message.reply_document(
                    document=open(compressed_path, "rb"),
                    caption="✅ PDF compressed successfully!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error compressing PDF: {e}")
                await update.message.reply_text(f"❌ Compression failed: {e}")
            finally:
                session.clear_pdf_files()

    async def url_to_pdf_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Convert a URL to PDF"""
        if not context.args:
            session = self.get_user_session(update.effective_user.id)
            await update.message.reply_text(MessageTemplates.t("url_usage", session.language))
            return

        url = context.args[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "webpage.pdf")
            try:
                result = self.html_converter.convert_url(url, output_path)
                await update.message.reply_document(
                    document=open(result["pdf_path"], "rb"),
                    caption="✅ URL converted to PDF!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error converting URL: {e}")
                await update.message.reply_text(f"❌ URL conversion failed: {e}")

    async def ocr_pdf_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Run OCR on the last received PDF"""
        session = self.get_user_session(update.effective_user.id)
        if not session.get_pdf_count():
            await update.message.reply_text(MessageTemplates.t("no_pdfs", session.language))
            return

        language = "eng"
        if context.args:
            language = context.args[0]
        else:
            session = self.get_user_session(update.effective_user.id)
            default_map = {Language.EN: "eng", Language.DE: "deu", Language.FA: "fas"}
            language = default_map.get(session.language, "eng")

        source_pdf = session.pdf_files[-1]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "ocr.pdf")
            try:
                ocr_path = self.pdf_tools.ocr_pdf(source_pdf, output_path, language=language)
                await update.message.reply_document(
                    document=open(ocr_path, "rb"),
                    caption="✅ OCR completed!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error running OCR: {e}")
                await update.message.reply_text(f"❌ OCR failed: {e}")
            finally:
                session.clear_pdf_files()
    
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

    async def handle_non_image_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-image documents (Office and text/markdown)"""
        document = update.message.document

        if not document or not document.file_name:
            await update.message.reply_text("❌ Invalid document.")
            return

        file_extension = Path(document.file_name).suffix.lower()
        if file_extension == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                file = await context.bot.get_file(document.file_id)
                await file.download_to_drive(temp_file.name)
                session = self.get_user_session(update.effective_user.id)
                session.add_pdf_file(temp_file.name)
                await update.message.reply_text(
                    MessageTemplates.pdf_received(document.file_name, session.get_pdf_count())
                )
            return

        converter = None
        if file_extension in self.doc_converter.supported_formats:
            converter = self.doc_converter
        elif file_extension in self.text_converter.supported_formats:
            converter = self.text_converter
        elif file_extension in self.html_converter.supported_formats:
            converter = self.html_converter
        else:
            supported = list(
                self.doc_converter.supported_formats
                | self.text_converter.supported_formats
                | self.html_converter.supported_formats
            )
            await update.message.reply_text(
                MessageTemplates.unsupported_format(file_extension, supported)
            )
            return

        await update.message.reply_text(MessageTemplates.document_received(document.file_name))

        with tempfile.TemporaryDirectory() as temp_dir:
            doc_path = os.path.join(temp_dir, document.file_name)
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(doc_path)

            try:
                output_pdf = os.path.join(temp_dir, f"{Path(document.file_name).stem}.pdf")
                if isinstance(converter, DocumentToPdfConverter):
                    result = converter.convert_document(doc_path, output_pdf)
                elif isinstance(converter, HtmlToPdfConverter):
                    result = converter.convert_html_file(doc_path, output_pdf)
                else:
                    result = converter.convert_text(doc_path, output_pdf)
                original_size = self.converter.format_file_size(result["original_size"])
                pdf_size = self.converter.format_file_size(result["pdf_size"])

                await update.message.reply_document(
                    document=open(result["pdf_path"], "rb"),
                    caption="✅ Document converted to PDF!",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(
                    MessageTemplates.document_success(original_size, pdf_size),
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error converting document: {e}")
                await update.message.reply_text(MessageTemplates.document_error(str(e)))
    
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
        application.add_handler(CommandHandler("lang", self.set_language_command))
        application.add_handler(CommandHandler("merge", self.merge_pdfs_command))
        application.add_handler(CommandHandler("split", self.split_pdf_command))
        application.add_handler(CommandHandler("compress_pdf", self.compress_pdf_command))
        application.add_handler(CommandHandler("url2pdf", self.url_to_pdf_command))
        application.add_handler(CommandHandler("ocr", self.ocr_pdf_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        application.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document))
        application.add_handler(MessageHandler(filters.Document.ALL & ~filters.Document.IMAGE, self.handle_non_image_document))
        
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
            BotCommand("merge", "Merge pending PDFs"),
            BotCommand("split", "Split last PDF into pages"),
            BotCommand("compress_pdf", "Compress last PDF"),
            BotCommand("url2pdf", "Convert URL to PDF"),
            BotCommand("ocr", "OCR last PDF"),
            BotCommand("lang", "Set language (en/de/fa)"),
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
