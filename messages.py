"""
Message templates and localization.
"""

from bot_types import Language


class MessageTemplates:
    """Centralized message templates"""

    STRINGS = {
        "welcome": {
            Language.EN: (
                "🖼️ **Image to PDF Converter Bot**\n\n"
                "Welcome! I can convert your files to PDF.\n\n"
                "**Features:**\n"
                "• Images → PDF\n"
                "• Office docs → PDF (DOCX, PPTX, XLSX)\n"
                "• Text/Markdown → PDF (TXT, MD)\n"
                "• HTML/URL → PDF\n"
                "• PDF tools (merge, split, compress, OCR)\n\n"
                "Use the command menu to get started."
            ),
            Language.DE: (
                "🖼️ **Bild-zu-PDF Bot**\n\n"
                "Willkommen! Ich kann Dateien in PDF umwandeln.\n\n"
                "**Funktionen:**\n"
                "• Bilder → PDF\n"
                "• Office-Dokumente → PDF (DOCX, PPTX, XLSX)\n"
                "• Text/Markdown → PDF (TXT, MD)\n"
                "• HTML/URL → PDF\n"
                "• PDF-Tools (Zusammenführen, Teilen, Komprimieren, OCR)\n\n"
                "Nutze das Befehlsmenü, um zu starten."
            ),
            Language.FA: (
                "🖼️ **ربات تبدیل به PDF**\n\n"
                "خوش آمدید! می‌توانم فایل‌ها را به PDF تبدیل کنم.\n\n"
                "**امکانات:**\n"
                "• تصویر → PDF\n"
                "• اسناد آفیس → PDF (DOCX, PPTX, XLSX)\n"
                "• متن/مارک‌داون → PDF (TXT, MD)\n"
                "• HTML/URL → PDF\n"
                "• ابزارهای PDF (ادغام، تقسیم، فشرده‌سازی، OCR)\n\n"
                "برای شروع از منوی دستورات استفاده کنید."
            ),
        },
        "help": {
            Language.EN: (
                "📖 **Help**\n\n"
                "**Supported:** JPG/PNG/BMP/TIFF/GIF/WebP, DOCX/PPTX/XLSX, TXT/MD, HTML/HTM, PDF\n\n"
                "**PDF Tools:** /merge /split /compress_pdf /ocr\n"
                "**URL:** /url2pdf https://example.com\n"
                "**Language:** /lang en|de|fa\n"
            ),
            Language.DE: (
                "📖 **Hilfe**\n\n"
                "**Unterstützt:** JPG/PNG/BMP/TIFF/GIF/WebP, DOCX/PPTX/XLSX, TXT/MD, HTML/HTM, PDF\n\n"
                "**PDF-Tools:** /merge /split /compress_pdf /ocr\n"
                "**URL:** /url2pdf https://example.com\n"
                "**Sprache:** /lang en|de|fa\n"
            ),
            Language.FA: (
                "📖 **راهنما**\n\n"
                "**پشتیبانی:** JPG/PNG/BMP/TIFF/GIF/WebP, DOCX/PPTX/XLSX, TXT/MD, HTML/HTM, PDF\n\n"
                "**ابزارهای PDF:** /merge /split /compress_pdf /ocr\n"
                "**URL:** /url2pdf https://example.com\n"
                "**زبان:** /lang en|de|fa\n"
            ),
        },
        "lang_set": {
            Language.EN: "✅ Language set to English.",
            Language.DE: "✅ Sprache auf Deutsch eingestellt.",
            Language.FA: "✅ زبان روی فارسی تنظیم شد.",
        },
        "lang_usage": {
            Language.EN: "Usage: /lang en|de|fa",
            Language.DE: "Verwendung: /lang en|de|fa",
            Language.FA: "نحوه استفاده: /lang en|de|fa",
        },
        "no_pdfs": {
            Language.EN: "❌ No PDFs pending. Send PDF files first.",
            Language.DE: "❌ Keine PDFs vorhanden. Bitte zuerst PDFs senden.",
            Language.FA: "❌ هیچ PDFی موجود نیست. ابتدا PDF بفرستید.",
        },
        "files_cleared": {
            Language.EN: "🗑️ Cleared all pending files!",
            Language.DE: "🗑️ Alle ausstehenden Dateien wurden gelöscht!",
            Language.FA: "🗑️ همه فایل‌های در صف پاک شد!",
        },
        "url_usage": {
            Language.EN: "Usage: /url2pdf https://example.com",
            Language.DE: "Verwendung: /url2pdf https://example.com",
            Language.FA: "نحوه استفاده: /url2pdf https://example.com",
        },
        "ocr_usage": {
            Language.EN: "Usage: /ocr [language]\nExample: /ocr eng",
            Language.DE: "Verwendung: /ocr [language]\nBeispiel: /ocr deu",
            Language.FA: "نحوه استفاده: /ocr [language]\nمثال: /ocr fas",
        },
    }

    @classmethod
    def t(cls, key: str, lang: Language, **kwargs) -> str:
        text = cls.STRINGS.get(key, {}).get(lang) or cls.STRINGS.get(key, {}).get(Language.EN, "")
        if kwargs:
            return text.format(**kwargs)
        return text

    @staticmethod
    def compression_options(image_count: int, current_setting) -> str:
        message = f"🖼️ Found {image_count} image(s) to convert\n\n"
        message += "🔧 **Choose compression level:**\n\n"
        message += "1️⃣ /compress_high - High Quality (95%)\n"
        message += "2️⃣ /compress_medium - Medium Quality (85%) - Default\n"
        message += "3️⃣ /compress_low - Low Quality (70%) - Smallest file\n"
        message += "4️⃣ /convert_now - Use current setting\n"
        message += f"Current setting: {current_setting.title}"
        return message

    @staticmethod
    def image_received(file_info, pending_count: int) -> str:
        return (
            f"✅ Image received!\n"
            f"Format: {file_info.format}\n"
            f"Size: {file_info.size}\n"
            f"Images pending: {pending_count}\n\n"
            f"Send more images or use /convert when ready!"
        )

    @staticmethod
    def processing_start(image_count: int, compression) -> str:
        return (
            f"🔄 Converting {image_count} image(s) to PDF...\n"
            f"Compression: {compression.title}\n"
            f"This may take a moment..."
        )

    @staticmethod
    def conversion_success(result, image_count: int) -> str:
        if image_count == 1:
            return "✅ Conversion completed!"
        return f"✅ {image_count} images converted to PDF!"

    @staticmethod
    def file_size_info(result) -> str:
        if result.image_count == 1:
            return (
                "📊 **File Size Info:**\n"
                f"📸 Original: {result.original_size}\n"
                f"📄 PDF: {result.pdf_size}\n"
                f"🔧 Compression: {result.compression_used.title}\n"
                f"📐 Format: {result.original_format}\n"
                f"📏 Dimensions: {result.image_dimensions}"
            )
        return (
            "📊 **File Size Info:**\n"
            f"📸 Total Original: {result.total_original_size}\n"
            f"📄 PDF: {result.pdf_size}\n"
            f"🔧 Compression: {result.compression_used.title}\n"
            f"🖼️ Images: {result.image_count}"
        )

    @staticmethod
    def conversion_error(error_message: str) -> str:
        return f"❌ Error during conversion: {error_message}\nPlease try again."

    @staticmethod
    def no_images() -> str:
        return "❌ No images to convert!\n\nPlease send me some images first, then use /convert."

    @staticmethod
    def invalid_image() -> str:
        return "❌ Invalid image format. Please send a valid image."

    @staticmethod
    def unsupported_format(file_extension: str, supported_formats) -> str:
        return (
            f"❌ Unsupported format: {file_extension}\n"
            f"Supported formats: {', '.join(supported_formats)}"
        )

    @staticmethod
    def compression_set(compression) -> str:
        return f"🔧 Compression set to **{compression.title}**"

    @staticmethod
    def pdf_received(file_name: str, pending_count: int) -> str:
        return f"✅ PDF received: {file_name}\nPDFs pending: {pending_count}\nUse /merge or /split."

    @staticmethod
    def document_received(file_name: str) -> str:
        return f"✅ Document received: {file_name}\nConverting to PDF..."

    @staticmethod
    def document_success(original_size: str, pdf_size: str) -> str:
        return (
            "✅ Document converted to PDF!\n"
            f"📄 Original: {original_size}\n"
            f"📄 PDF: {pdf_size}"
        )

    @staticmethod
    def document_error(error_message: str) -> str:
        return f"❌ Document conversion failed: {error_message}"
