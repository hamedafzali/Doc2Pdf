#!/usr/bin/env python3
"""
Web Manager Runner for Doc2Pdf Bot
Starts the web management interface
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the web manager"""
    logger.info("Starting Doc2Pdf Bot Web Manager...")
    
    # Check required environment variables
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Import and run the web manager
    try:
        from web_manager import app
        port = int(os.getenv('WEB_MANAGER_PORT', 5000))
        host = os.getenv('WEB_MANAGER_HOST', '0.0.0.0')
        debug = os.getenv('WEB_MANAGER_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting web manager on {host}:{port}")
        logger.info(f"Access the web interface at: http://{host}:{port}")
        
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        logger.error(f"Failed to import web manager: {e}")
        logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Error starting web manager: {e}")

if __name__ == '__main__':
    main()
