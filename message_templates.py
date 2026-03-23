"""
Message templates for the Telegram bot
Centralized message management for consistency
"""

class MessageTemplates:
    """Centralized message templates"""
    
    @staticmethod
    def welcome() -> str:
        """Welcome message"""
        return (
            "🎉 *Welcome to Doc2Pdf Bot!* 🎉\n\n"
            "📸 *Convert images to PDF instantly*\n\n"
            "🔧 *Features:*\n"
            "• High-quality conversion\n"
            "• Multiple image support\n"
            "• Compression options\n"
            "• OCR functionality\n"
            "• PDF tools\n\n"
            "📝 *How to use:*\n"
            "1. Send images (JPEG, PNG, etc.)\n"
            "2. Use /convert when ready\n"
            "3. Choose compression level\n\n"
            "❓ *Need help?* Use /help"
        )
    
    @staticmethod
    def help() -> str:
        """Help message"""
        return (
            "🔧 *Doc2Pdf Bot Commands*\n\n"
            "📸 *Conversion Commands:*\n"
            "• /convert - Convert with current settings\n"
            "• /convert_now - Convert immediately\n"
            "• /compress_high - Set high quality (95%)\n"
            "• /compress_medium - Set medium quality (85%)\n"
            "• /compress_low - Set low quality (70%)\n\n"
            "📄 *PDF Tools:*\n"
            "• /merge - Merge PDFs\n"
            "• /split - Split PDF into pages\n"
            "• /compress_pdf - Compress existing PDF\n"
            "• /ocr - Make PDF searchable\n"
            "• /ocr_image - Extract text from the last image (optional language)\n\n"
            "🌐 *Other Features:*\n"
            "• /url2pdf - Convert URL to PDF\n"
            "• /clear - Clear all pending files\n\n"
            "❓ *Need more help?* Contact support!"
        )
    
    @staticmethod
    def files_cleared() -> str:
        """Files cleared message"""
        return "✅ All files cleared! Ready for new conversions."

    @staticmethod
    def pdf_received(file_name: str, pending_count: int) -> str:
        """PDF received message"""
        return (
            f"✅ PDF received: {file_name}\n"
            f"PDFs pending: {pending_count}\n"
            "Use /compress_pdf, /merge, /split, or /ocr."
        )

    @staticmethod
    def no_pdfs() -> str:
        """No PDFs message"""
        return "❌ No PDFs found. Please send a PDF first."

    @staticmethod
    def document_received(file_name: str) -> str:
        """Document received message"""
        return f"✅ Document received: {file_name}\nConverting to PDF..."

    @staticmethod
    def document_success(original_size: str, pdf_size: str) -> str:
        """Document conversion success message"""
        return (
            "✅ Document converted to PDF!\n"
            f"Original: {original_size}\n"
            f"PDF: {pdf_size}"
        )

    @staticmethod
    def document_error(error_message: str) -> str:
        """Document conversion error message"""
        return f"❌ Document conversion failed: {error_message}"
    
    @staticmethod
    def no_images() -> str:
        """No images message"""
        return "❌ No images found. Please send images first."

    @staticmethod
    def invalid_image() -> str:
        """Invalid image message"""
        return "❌ Invalid image format. Please send a valid image."

    @staticmethod
    def unsupported_format(file_extension: str, supported_formats) -> str:
        """Unsupported format message"""
        return (
            f"❌ Unsupported format: {file_extension}\n"
            f"Supported formats: {', '.join(sorted(supported_formats))}"
        )

    @staticmethod
    def image_received(file_info, pending_count: int) -> str:
        """Image received confirmation"""
        return (
            f"✅ Image received!\n"
            f"Format: {file_info.format}\n"
            f"Size: {file_info.size}\n"
            f"Images pending: {pending_count}\n\n"
            "Send more images or use /convert when ready."
        )
    
    @staticmethod
    def processing_start(image_count: int, compression) -> str:
        """Processing started message"""
        return f"🔄 Converting {image_count} image(s) to PDF...\n🔧 Compression: {compression.title}"
    
    @staticmethod
    def conversion_success(result, image_count: int) -> str:
        """Conversion success message"""
        if image_count == 1:
            return "✅ Conversion completed!"
        else:
            return f"✅ {image_count} images converted to PDF!"
    
    @staticmethod
    def conversion_error(error_message: str) -> str:
        """Conversion error message"""
        return f"❌ Error during conversion: {error_message}\nPlease try again."
    
    @staticmethod
    def file_size_info(result) -> str:
        """File size information"""
        if result.original_size and result.pdf_size:
            original_mb = result.original_size / (1024 * 1024)
            pdf_mb = result.pdf_size / (1024 * 1024)
            compression_ratio = ((result.original_size - result.pdf_size) / result.original_size) * 100 if result.original_size > result.pdf_size else 0
            
            compression_title = result.compression_used.title if result.compression_used else "Unknown"
            
            return (
                f"📊 *File Size Information:*\n"
                f"📥 Original: {original_mb:.2f} MB\n"
                f"📦 PDF: {pdf_mb:.2f} MB\n"
                f"🗜️ Compression: {compression_ratio:.1f}% smaller"
                f"🔧 Compression: {compression_title}\n"
            )
        return "📊 File size information unavailable"
    
    @staticmethod
    def compression_options(image_count: int, current_setting) -> str:
        """Compression options message"""
        message = f"🖼️ Found {image_count} image(s) to convert\n\n"
        message += "🔧 **Choose compression level:**\n\n"
        message += "1️⃣ /compress_high - High Quality (95%)\n"
        message += "2️⃣ /compress_medium - Medium Quality (85%) - Default\n"
        message += "3️⃣ /compress_low - Low Quality (70%) - Smallest file\n"
        message += "4️⃣ /convertnow - Use current setting\n"
        message += f"\nCurrent setting: {current_setting.title}"
        return message
    
    @staticmethod
    def compression_set(compression) -> str:
        """Compression set message"""
        return f"🔧 Compression set to **{compression.title}**"
    
    @staticmethod
    def ocr_usage() -> str:
        """OCR usage message"""
        return "Usage: /ocr [language]\nExample: /ocr eng\n\nSupported languages: eng (English), fra (French), deu (German), spa (Spanish), ita (Italian), por (Portuguese), rus (Russian), chi_sim (Chinese Simplified), jpn (Japanese)"
    
    @staticmethod
    def ocr_image_usage() -> str:
        """OCR image usage message"""
        return "Usage: /ocr_image [language]\nExample: /ocr_image eng\n\nLanguage is optional - defaults to English (eng) if not specified.\n\nSupported languages: eng (English), fra (French), deu (German), spa (Spanish), ita (Italian), por (Portuguese), rus (Russian), chi_sim (Chinese Simplified), jpn (Japanese)"
