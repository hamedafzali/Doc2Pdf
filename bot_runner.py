#!/usr/bin/env python3
"""
Telegram Bot Runner for Image to PDF Converter
Launches the Telegram bot with proper configuration
"""

import os
import sys
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
    """Main function to run the bot"""
    logger.info("Starting Doc2Pdf Telegram Bot...")
    
    # Check required environment variables
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Import and run the refactored bot
    try:
        from telegram_bot import create_bot
        
        # Create and run bot
        bot = create_bot(telegram_token)
        logger.info("Bot started successfully!")
        bot.run()
        
    except ImportError as e:
        logger.error(f"Failed to import bot: {e}")
        logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == '__main__':
    main()
