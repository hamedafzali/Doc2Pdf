# Web Manager for Doc2Pdf Bot

A web-based management interface for your Doc2Pdf Telegram bot that allows you to easily manage the Docker container without manual commands.

## Features

### 🎯 Bot Management
- **Start/Stop/Restart** the bot with one click
- **View real-time status** with container information
- **Rebuild Docker image** without manual commands
- **Automatic container creation** when starting

### 📊 Monitoring
- **Live status updates** every 5 seconds
- **Container information** (ID, image, creation time)
- **Health checks** and error reporting
- **Visual status indicators** with animations

### 📋 Log Management
- **Real-time log viewing** with configurable line limits
- **Auto-refresh** option for live monitoring
- **Download logs** as text files
- **Clear and refresh** functionality

### 🎨 Modern UI
- **Responsive design** for desktop and mobile
- **Dark theme logs** for better readability
- **Smooth animations** and transitions
- **Intuitive controls** with clear feedback

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your bot token

# Start the web manager
docker-compose -f docker-compose-manager.yml up -d

# Access the web interface
# Open http://localhost:5000 in your browser
```

### Option 2: Manual Docker Run

```bash
# Build the image
docker build -t doc2pdf-bot .

# Run the web manager
docker run -d \
  --name doc2pdf-web-manager \
  --restart unless-stopped \
  -p 5000:5000 \
  -e TELEGRAM_BOT_TOKEN=your_bot_token_here \
  -e DEBUG_MODE=false \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/debug_output:/app/debug_output \
  doc2pdf-bot python web_runner.py
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_bot_token_here

# Run the web manager
python web_runner.py
```

## Usage

### 1. Dashboard
- **View bot status** at a glance
- **Control buttons** for start/stop/restart
- **Quick stats** showing container information
- **Real-time updates** every 5 seconds

### 2. Bot Control
- **Start Bot**: Creates and starts the container if not running
- **Stop Bot**: Stops the running container
- **Restart Bot**: Stops and starts the container
- **Rebuild**: Rebuilds the Docker image and restarts

### 3. Logs Page
- **View container logs** in real-time
- **Configure line limits** (50, 100, 200, 500)
- **Auto-refresh** option for live monitoring
- **Download logs** as timestamped text files

## Configuration

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE=false                  # Keep PDF files for debugging
WEB_MANAGER_HOST=0.0.0.0          # Web server host
WEB_MANAGER_PORT=5000             # Web server port
WEB_MANAGER_DEBUG=false           # Flask debug mode
```

### Docker Requirements

The web manager needs access to the Docker socket to manage containers:
```bash
-v /var/run/docker.sock:/var/run/docker.sock
```

## Security Notes

### 🔒 Important Security Considerations

1. **Docker Socket Access**: The web manager needs Docker socket access to manage containers
2. **Network Exposure**: The web interface is exposed on port 5000 by default
3. **Authentication**: No built-in authentication (consider adding reverse proxy with auth)
4. **Environment Variables**: Bot token is exposed in container environment

### 🔧 Security Recommendations

1. **Use Reverse Proxy**: Add Nginx/Apache with authentication
2. **Limit Network Access**: Bind to localhost if not needed externally
3. **Use Secrets**: Consider using Docker secrets for sensitive data
4. **Regular Updates**: Keep Docker and dependencies updated

## Troubleshooting

### Common Issues

1. **Docker Socket Permission Error**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Or run with sudo
   ```

2. **Port Already in Use**
   ```bash
   # Change port in .env
   WEB_MANAGER_PORT=5001
   ```

3. **Container Not Found**
   - Use the "Start Bot" button to create the container
   - Check Docker is running: `docker version`

4. **Logs Not Showing**
   - Check if bot container is running
   - Verify Docker socket access
   - Check web manager logs

### Debug Mode

Enable debug mode for more detailed logging:
```bash
WEB_MANAGER_DEBUG=true
LOG_LEVEL=DEBUG
```

## API Endpoints

The web manager provides REST API endpoints:

- `GET /api/status` - Get container status
- `POST /api/start` - Start container
- `POST /api/stop` - Stop container  
- `POST /api/restart` - Restart container
- `POST /api/rebuild` - Rebuild image
- `GET /api/logs?lines=100` - Get container logs

## Development

### Project Structure
```
templates/
├── dashboard.html    # Main dashboard
└── logs.html         # Logs viewer

static/js/
├── dashboard.js      # Dashboard functionality
└── logs.js           # Logs functionality

web_manager.py       # Flask web application
web_runner.py        # Entry point script
```

### Adding New Features

1. **New API Endpoints**: Add to `web_manager.py`
2. **New Pages**: Add HTML templates and JavaScript
3. **Styling**: Uses Tailwind CSS for modern design
4. **Icons**: Uses Lucide icons for consistency

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Verify Docker configuration
4. Check environment variables
