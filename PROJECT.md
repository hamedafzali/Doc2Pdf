# Doc2Pdf - Image to PDF Converter

## Project Overview

A Python application that converts images to PDF format with support for both standalone usage and Telegram bot integration.

## Features

- Convert single images to PDF
- Combine multiple images into one PDF
- Batch convert entire directories
- Support for multiple image formats (JPG, PNG, BMP, TIFF, GIF, WebP)
- CLI interface for easy usage
- **Telegram bot integration** ✅

## Current Status

✅ Core image conversion functionality implemented
✅ CLI interface created

## Project Structure

```
Doc2Pdf/
├── requirements.txt          # Python dependencies
├── image_converter.py        # Core conversion module
├── main.py                   # CLI application
├── telegram_bot.py          # Telegram bot implementation
├── bot_runner.py            # Bot launcher script
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore            # Docker ignore file
├── .env.example             # Environment configuration template
├── PROJECT.md               # Project documentation
└── README.md                # User documentation
```

## Dependencies

- Pillow: Image processing
- img2pdf: High-quality PDF generation
- python-telegram-bot: Telegram integration
- python-dotenv: Environment configuration

## Usage Examples

### CLI Usage

```bash
# Single Image Conversion
python main.py image.jpg
python main.py image.jpg -o output.pdf

# Multiple Images to Single PDF
python main.py image1.jpg image2.jpg image3.png

# Batch Directory Conversion
python main.py --batch /path/to/images

# List Supported Formats
python main.py --list-formats
```

### Telegram Bot Usage

```bash
# Setup
1. Copy .env.example to .env
2. Add bot token from @BotFather
3. Install dependencies: pip install -r requirements.txt
4. Run bot: python bot_runner.py

# Bot Commands
/start - Start bot and see welcome message
/help - Show help message
/convert - Convert received images to PDF
/clear - Clear all pending images
```

## Telegram Bot Features

- Handles image uploads (photos and documents)
- Processes multiple images into single PDF
- Automatic file cleanup
- User-friendly interface with markdown formatting
- Error handling and validation
- Command menu integration

## Next Steps

1. Production deployment setup
2. Bot scalability improvements
3. Image optimization options
4. PDF metadata handling
5. Web interface (optional)
6. Docker containerization

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - optional
- `DEBUG_MODE`: Keep PDF files in debug_output folder (true/false) - optional

## Debug Mode

When `DEBUG_MODE=true`, the bot will:

- Save converted PDFs to `debug_output/` folder
- Use timestamped filenames: `user_{userID}_{timestamp}_{count}images.pdf`
- Keep PDF files for debugging instead of deleting them
- Show debug file path to user after conversion

### Debug Folder Structure

```
debug_output/
├── user_123456789_20260204_161200_1images.pdf
├── user_987654321_20260204_161300_3images.pdf
└── ...
```

## Technical Notes

- Uses img2pdf for lossless conversion
- Maintains original image quality
- Supports various image formats
- Logging implemented for debugging
- Temporary file management
- Environment-based configuration
