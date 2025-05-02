#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TeraboxDownloaderBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
        
        # Initialize Application with polling
        self.application = Application.builder() \
            .token(self.token) \
            .build()
        
        # Register handlers
        self._register_handlers()
        
        # Log token for verification (first 5 and last 5 chars)
        logger.info(f"Bot token: {self.token[:5]}...{self.token[-5:]}")
        
    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"Start command from {user.full_name} (ID: {user.id})")
        
        await update.message.reply_text(
            f"👋 Hello {user.full_name}!\n\n"
            "I'm your Terabox downloader bot. Send me a Terabox link to get started."
        )

    async def _message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all text messages"""
        user = update.effective_user
        text = update.message.text
        
        logger.info(f"Message from {user.full_name}: {text}")
        
        # Simple echo for testing
        await update.message.reply_text(
            f"🔍 You sent: {text}\n\n"
            "This bot will eventually download Terabox files.\n"
            "Currently in testing mode."
        )

    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(f"Update {update} caused error: {context.error}")

    def _register_handlers(self):
        """Register all handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_handler))
        
        # Message handler - processes all text messages that aren't commands
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler)
        )
        
        # Error handler
        self.application.add_error_handler(self._error_handler)

    def run(self):
        """Run the bot until interrupted"""
        logger.info("Starting bot in polling mode...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    try:
        bot = TeraboxDownloaderBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Bot failed: {e}")
        raise
