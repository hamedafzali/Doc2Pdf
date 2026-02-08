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
✅ Telegram bot with interactive compression
✅ Web-based management interface (separated)

## Next Goals (Feature-Focused)

1. Convert Other Document Types (Priority)
   - Add PDF output from Office docs (DOCX, PPTX, XLSX).
   - Add PDF output from text/markdown (TXT, MD).
   - Add PDF output from HTML/URL input.
   - Add clear user messaging for unsupported formats.

2. New User-Facing Features
   - Add /merge to combine multiple PDFs into one.
   - Add /split to split a PDF into pages or page ranges.
   - Add /compress_pdf to reduce size of existing PDFs.
   - Add /ocr to make scanned PDFs searchable.

3. Media Enhancements
   - Add image rotation/crop before conversion.
   - Add page size selection (A4, Letter, Auto).
   - Add watermark and header/footer options.

4. Sharing and Output Options
   - Add output naming templates (date, user, title).
   - Add zip delivery for multiple outputs.
   - Add a shareable download link option.

## Project Structure

```
Doc2Pdf/
├── Core Application
│   ├── image_converter.py      # Core PDF conversion logic
│   ├── telegram_bot.py         # Telegram bot interface
│   ├── main.py                # CLI interface
│   └── bot_runner.py           # Bot entry point
├── Web Management Interface (Separated)
│   └── See: https://github.com/hamedafzali/AdvancedContainerManager
├── Docker & Deployment
│   ├── Dockerfile              # Container definition
│   └── docker-compose.yml       # Bot deployment
├── Configuration
│   ├── .env.example           # Environment template
│   └── requirements.txt        # Python dependencies
└── Documentation
    ├── PROJECT.md              # This file
    └── README.md               # User documentation
```

## Container Management

The web-based container management interface has been separated into its own repository:

### 🚀 Advanced Container Manager

**Repository**: https://github.com/hamedafzali/AdvancedContainerManager

**Features**:

- Professional web-based container management
- Real-time metrics and monitoring
- Web terminal access inside containers
- Multi-project Git repository management
- Modern UI with real-time updates
- REST API for all operations

**Quick Start**:

```bash
git clone https://github.com/hamedafzali/AdvancedContainerManager
cd AdvancedContainerManager
pip install -r requirements.txt
python advanced_manager.py
```

**Access**: http://localhost:5003

### 📋 Separation Benefits

- **Focused Development**: Each repository has a clear purpose
- **Independent Updates**: Manager can be updated without affecting bot
- **Reusable**: Manager can manage other projects, not just Doc2Pdf
- **Professional**: Enterprise-grade container management platform

## How It Works

### 🔄 Complete System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Web Manager    │    │     Docker      │
│     Bot         │◄──►│   Interface      │◄──►│   Container     │
│                 │    │                  │    │                 │
│ • Image to PDF  │    │ • Start/Stop     │    │ • Bot Process   │
│ • Compression   │    │ • Logs View      │    │ • File System   │
│ • File Info     │    │ • Rebuild        │    │ • Networking    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         └────────────────────────┴────────────────────────┘
                            User Interaction
```

### 📱 User Interaction Flow

#### **1. Telegram Bot Flow**

```
User sends images → Bot stores temporarily → User chooses compression → Bot converts → Returns PDF + file info
```

#### **2. Web Manager Flow**

```
Admin accesses web UI → View container status → Control bot → Monitor logs → Rebuild if needed
```

### 🏗️ Component Breakdown

#### **Core Components**

**1. image_converter.py**

- **Purpose**: Core PDF conversion engine
- **Key Classes**: `ImageToPdfConverter`
- **Features**:
  - Single/multiple image conversion
  - Compression (High/Medium/Low quality)
  - File size calculation and formatting
  - Image information extraction
- **Dependencies**: Pillow, img2pdf, io

**2. telegram_bot.py**

- **Purpose**: Telegram bot interface
- **Key Classes**: `ImageToPdfBot`
- **Features**:
  - Image/document handling
  - Interactive compression selection
  - File size information display
  - User session management
- **Dependencies**: python-telegram-bot, logging

**3. main.py**

- **Purpose**: Command-line interface
- **Features**:
  - Single image conversion
  - Batch directory processing
  - CLI arguments and options

#### **Web Management Components**

**4. web_manager.py**

- **Purpose**: Flask web application for bot management
- **Key Classes**: `BotManager`
- **Features**:
  - Docker container control
  - Real-time status monitoring
  - Log streaming
  - Image rebuilding
- **Dependencies**: Flask, docker-py

**5. Web UI Components**

- **dashboard.html**: Main management interface
- **logs.html**: Real-time log viewer
- **JavaScript files**: Interactive functionality and API calls

#### **Deployment Components**

**6. Docker Configuration**

- **Dockerfile**: Multi-purpose container image
- **docker-compose.yml**: Bot deployment
- **docker-compose-manager.yml**: Web manager deployment

### 🔄 Data Flow

#### **Telegram Bot Processing**

```
1. User sends image(s) via Telegram
2. Bot downloads to temporary storage
3. User triggers /convert command
4. Bot shows compression options menu
5. User selects compression level
6. Bot processes images with compression
7. Bot generates PDF with file size info
8. Bot sends PDF + detailed information
9. Bot cleans up temporary files
```

#### **Web Manager Operations**

```
1. Admin accesses web interface (port 5000)
2. Web app connects to Docker socket
3. Admin views container status (real-time)
4. Admin performs actions (start/stop/restart)
5. Web app manages Docker containers
6. Admin views real-time logs
7. Admin can rebuild image if needed
```

### 🔧 Configuration System

#### **Environment Variables**

```bash
# Core Configuration
TELEGRAM_BOT_TOKEN=token    # Bot authentication
LOG_LEVEL=INFO             # Logging verbosity
DEBUG_MODE=false           # File retention for debugging

# Web Manager Configuration
WEB_MANAGER_HOST=0.0.0.0   # Web server binding
WEB_MANAGER_PORT=5000       # Web server port
WEB_MANAGER_DEBUG=false      # Flask debug mode
```

#### **Compression Settings**

```python
COMPRESSION_QUALITY = {
    'high': 95,    # Best quality, larger files
    'medium': 85,  # Good balance (default)
    'low': 70      # Smallest files, lower quality
}
```

### 🐳 Container Architecture

#### **Multi-Mode Container**

The single Docker image can run in two modes:

1. **Bot Mode** (default):

   ```bash
   docker run doc2pdf-bot python bot_runner.py
   ```

2. **Web Manager Mode**:
   ```bash
   docker run doc2pdf-bot python web_runner.py
   ```

#### **Docker Socket Integration**

```
Web Manager Container
       │
       ▼
/var/run/docker.sock (mounted)
       │
       ▼
Docker Daemon
       │
       ▼
Bot Container (managed)
```

### 📊 State Management

#### **Bot State**

- **User Sessions**: Temporary files per user
- **Compression Settings**: Per-user preferences
- **File Cleanup**: Automatic after conversion

#### **Web Manager State**

- **Container Status**: Real-time monitoring
- **Log Streaming**: Live from Docker API
- **Auto-refresh**: 5-second intervals

### 🔒 Security Architecture

#### **Isolation**

- **Bot Container**: Runs as non-root user
- **Web Manager**: Limited Docker socket access
- **File System**: Proper permissions and cleanup

#### **Data Flow Security**

```
Telegram → Bot (encrypted) → Temp Files → PDF → User (encrypted)
Web UI → HTTPS (recommended) → Docker API → Container Control
```

### 🚀 Deployment Scenarios

#### **1. Bot Only Deployment**

```bash
docker-compose up -d
# Runs bot container only
# Bot accessible via Telegram
```

#### **2. Web Manager Deployment**

```bash
docker-compose -f docker-compose-manager.yml up -d
# Runs web manager container
# Bot managed via web interface
# Access at http://server:5000
```

#### **3. Development Mode**

```bash
pip install -r requirements.txt
python bot_runner.py  # or web_runner.py
# Local development with hot reload
```

### 📈 Monitoring & Logging

#### **Log Levels**

- **DEBUG**: Detailed processing information
- **INFO**: General operation status
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures

#### **Metrics Tracked**

- **File sizes**: Before/after compression
- **Conversion times**: Performance monitoring
- **User actions**: Bot interaction patterns
- **Container health**: Docker status checks

This architecture provides a complete, scalable solution for image-to-PDF conversion with professional management capabilities.

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
