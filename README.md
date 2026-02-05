# Doc2Pdf Bot

A powerful Telegram bot that converts images to PDF with compression options.

## 🚀 Features

### Core Functionality

- **Image to PDF Conversion**: Convert single images or multiple images to PDF
- **Multiple Formats**: Supports JPG, PNG, BMP, TIFF, GIF, WebP
- **Compression Options**: Three quality levels (High 95%, Medium 85%, Low 70%)
- **File Size Information**: Shows original and final file sizes
- **Batch Processing**: Combine multiple images into one PDF
- **Interactive Interface**: Easy-to-use Telegram bot interface

### Advanced Features

- **Smart Compression**: Choose between quality and file size
- **Real-time Processing**: Get instant feedback on your conversions
- **Debug Mode**: Save PDFs locally for testing
- **Clean Architecture**: Well-structured, maintainable codebase
- **Error Handling**: Robust error handling and user feedback

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get from @BotFather)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd Doc2Pdf

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

# Run the bot
python bot_runner.py
```

### Docker Deployment

```bash
# Build the image
docker build -t doc2pdf-bot .

# Run the bot
docker run -d \
  --name doc2pdf-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  doc2pdf-bot
```

### Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your bot token

# Run with Docker Compose
docker-compose up -d
```

## 📋 Usage

### Basic Commands

- `/start` - Show welcome message and instructions
- `/help` - Display help information
- `/convert` - Show compression options for pending images
- `/convert_now` - Convert images with current settings
- `/compress_high` - Set high quality (95%) and convert
- `/compress_medium` - Set medium quality (85%) and convert
- `/compress_low` - Set low quality (70%) and convert
- `/clear` - Clear all pending images

### Workflow

1. **Send Images**: Send one or more images to the bot
2. **Choose Compression**: Use `/convert` to see options or set compression directly
3. **Convert**: Bot automatically converts after setting compression or use `/convert_now`
4. **Download**: Receive the PDF file with detailed size information

### Compression Options

- **High Quality (95%)**: Best image quality, larger file size
- **Medium Quality (85%)**: Good balance, default option
- **Low Quality (70%)**: Smallest file size, acceptable quality

## 🔧 Configuration

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
DEBUG_MODE=false          # Enable debug mode to save PDFs locally
LOG_LEVEL=INFO           # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Debug Mode

Enable debug mode to save PDF files locally for testing:

```bash
DEBUG_MODE=true
```

PDFs will be saved to the `debug_output/` directory.

## 🐳 Docker Configuration

### Dockerfile

The Dockerfile creates a minimal, secure container:

- Based on Python 3.13-slim
- Non-root user for security
- Health checks for monitoring
- Proper signal handling

### Docker Compose

Includes:

- Automatic restart policy
- Environment variable configuration
- Volume mounts for debug output
- Health checks

## 📊 Architecture

### Code Structure

```
Doc2Pdf/
├── telegram_bot.py          # Main bot implementation
├── bot_runner.py            # Entry point and configuration
├── image_converter.py       # Core conversion logic
├── main.py                  # CLI interface
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml       # Service orchestration
├── .env.example            # Environment template
└── README.md               # This file
```

### Key Classes

- **ImageToPdfBot**: Main bot class with Telegram handlers
- **ImageToPdfConverter**: Core conversion logic
- **UserSession**: Manages user-specific data and temporary files
- **CompressionLevel**: Enum for compression options
- **MessageTemplates**: Centralized message templates

## 🔍 Supported Formats

### Input Formats

- **Images**: JPG/JPEG, PNG, BMP, TIFF, GIF, WebP
- **Documents**: Images sent as document files

### Output Format

- **PDF**: Standard PDF format with optional compression

## 📈 Performance

### Optimization Features

- **Efficient Memory Usage**: Automatic cleanup of temporary files
- **Parallel Processing**: Fast image processing
- **Smart Compression**: Balance between quality and size
- **Error Recovery**: Robust error handling

### File Size Reduction

Typical compression results:

- **High Quality**: ~5-15% reduction
- **Medium Quality**: ~15-30% reduction
- **Low Quality**: ~30-50% reduction

## 🛡️ Security

### Security Features

- **Non-root Container**: Runs as non-privileged user
- **Input Validation**: Validates all file types and formats
- **Temporary File Cleanup**: Automatic cleanup of temporary files
- **Error Handling**: Prevents information leakage in errors

### Best Practices

- Use environment variables for sensitive data
- Regular updates of dependencies
- Monitor logs for unusual activity
- Use HTTPS for web interfaces (if applicable)

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding

```bash
# Check bot token
echo $TELEGRAM_BOT_TOKEN

# Check logs
python bot_runner.py

# Verify bot permissions with @BotFather
```

#### Conversion Errors

```bash
# Check supported formats
python -c "from image_converter import ImageToPdfConverter; print(ImageToPdfConverter().supported_formats)"

# Test conversion manually
python main.py input.jpg output.pdf
```

#### Docker Issues

```bash
# Check container logs
docker logs doc2pdf-bot

# Check container status
docker ps

# Restart container
docker restart doc2pdf-bot
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true LOG_LEVEL=DEBUG python bot_runner.py
```

## 📚 API Reference

### Telegram Bot Commands

- **start()**: Handle /start command
- **help_command()**: Handle /help command
- **convert_command()**: Show compression options
- **convert_now_command()**: Convert with current settings
- **set*compression*\*()**: Set compression levels
- **handle_image()**: Process image uploads
- **handle_document()**: Process document uploads

### Core Functions

- **convert_single_image()**: Convert single image to PDF
- **convert_multiple_images()**: Convert multiple images to PDF
- **get_image_info()**: Get image metadata

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd Doc2Pdf

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your bot token

# Run tests (if available)
python -m pytest

# Run bot
python bot_runner.py
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings for all public functions
- Keep functions small and focused
- Use meaningful variable names

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- **Documentation**: Check this README and inline documentation
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join our Telegram group for discussions
- **Email**: support@doc2pdf-bot.com

## 🚀 Roadmap

### Upcoming Features

- [ ] Batch processing from URLs
- [ ] Custom watermarks
- [ ] PDF password protection
- [ ] Image preprocessing (rotation, crop)
- [ ] Multiple language support
- [ ] Web interface for bot management
- [ ] Analytics and usage statistics
- [ ] API rate limiting
- [ ] User authentication
- [ ] Custom templates

### Version History

- **v2.0.0** - Refactored codebase with compression options
- **v1.5.0** - Added multiple image support
- **v1.0.0** - Initial release with basic conversion

---

**Doc2Pdf Bot** - Fast, reliable image to PDF conversion on Telegram! 📸➡️📄
