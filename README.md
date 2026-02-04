# Image to PDF Converter

A Python application that converts images to PDF format with support for both standalone usage and Telegram bot integration.

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Doc2Pdf
```

2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### CLI Usage

#### Single Image Conversion

```bash
python main.py image.jpg
python main.py image.jpg -o output.pdf
```

#### Multiple Images to Single PDF

```bash
python main.py image1.jpg image2.jpg image3.png
```

#### Batch Directory Conversion

```bash
python main.py --batch /path/to/images
```

#### List Supported Formats

```bash
python main.py --list-formats
```

### Telegram Bot Setup

1. **Create a Telegram Bot:**
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Follow instructions to get your bot token

2. **Configure Environment:**

   ```bash
   cp .env.example .env
   # Edit .env and add your bot token
   ```

3. **Run the Bot:**
   ```bash
   python bot_runner.py
   ```

#### Bot Commands

- `/start` - Start bot and see welcome message
- `/help` - Show help message
- `/convert` - Convert received images to PDF
- `/clear` - Clear all pending images

#### Bot Usage

1. Send one or more images to the bot
2. Use `/convert` when ready
3. Download the PDF file

## Supported Image Formats

- JPG/JPEG
- PNG
- BMP
- TIFF
- GIF
- WebP

## Features

- High-quality lossless conversion
- Single image to PDF
- Multiple images to single PDF
- Batch directory processing
- CLI interface
- **Telegram bot integration**
- Automatic file cleanup
- User-friendly interface

## Project Structure

```
Doc2Pdf/
├── requirements.txt          # Python dependencies
├── image_converter.py        # Core conversion module
├── main.py                   # CLI application
├── telegram_bot.py          # Telegram bot implementation
├── bot_runner.py            # Bot launcher script
├── .env.example             # Environment configuration template
├── PROJECT.md               # Project documentation
└── README.md                # User documentation
```

## Docker Deployment

### Quick Start with Docker Compose

1. **Clone and setup:**

   ```bash
   git clone https://github.com/hamedafzali/Doc2Pdf.git
   cd Doc2Pdf
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your bot token
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Manual Docker Build

1. **Build the image:**

   ```bash
   docker build -t doc2pdf-bot .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name doc2pdf-bot \
     --restart unless-stopped \
     -e TELEGRAM_BOT_TOKEN=your_token_here \
     -e DEBUG_MODE=true \
     -v $(pwd)/debug_output:/app/debug_output \
     doc2pdf-bot
   ```

### Docker Management

- **View logs:** `docker-compose logs -f`
- **Stop bot:** `docker-compose down`
- **Restart bot:** `docker-compose restart`
- **Debug output:** Check `debug_output/` directory

### Docker Features

- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for monitoring
- **Volume mounting** for persistent debug output
- **Environment variable configuration**

## Requirements

- Python 3.7+ (for local development)
- Docker & Docker Compose (for containerized deployment)
- Telegram Bot Token (for bot functionality)
- See requirements.txt for package dependencies

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - optional

## Development

The project is structured with modular components:

- Core conversion logic in `image_converter.py`
- CLI interface in `main.py`
- Telegram bot in `telegram_bot.py`
- Bot launcher in `bot_runner.py`
