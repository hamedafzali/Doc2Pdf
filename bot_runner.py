#!/usr/bin/env python3
"""
Telegram Bot Runner for Image to PDF Converter
Launches the Telegram bot with proper configuration
"""

import os
import sys
import logging
from dotenv import load_dotenv

from telegram_bot import create_bot

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=numeric_level
    )

def main():
    """Main bot runner"""
    # Load environment variables
    load_dotenv()
    
    # Get bot token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please:")
        print("1. Copy .env.example to .env")
        print("2. Add your bot token to .env file")
        print("3. Get token from @BotFather on Telegram")
        sys.exit(1)
    
    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    
    # Create and run bot
    try:
        print("Starting Image to PDF Telegram Bot...")
        print(f"Log level: {log_level}")
        
        bot = create_bot(bot_token)
        bot.run()
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
