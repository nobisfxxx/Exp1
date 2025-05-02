#!/usr/bin/env python3
import os
import time
import logging
import asyncio
from io import BytesIO
from urllib.parse import urlparse
import aiohttp
from telegram import Update, InputFile
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
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("terabox_bot.log")
    ]
)
logger = logging.getLogger(__name__)

class TeraboxDownloaderBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN")
        
        self.application = Application.builder() \
            .token(self.token) \
            .post_init(self.on_startup) \
            .post_shutdown(self.on_shutdown) \
            .build()
            
        self.session = None
        self._register_handlers()

    async def on_startup(self, app):
        """Initialize resources"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "TeraboxBot/1.0"}
        )
        logger.info("Bot started with aiohttp session")

    async def on_shutdown(self, app):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Bot stopped gracefully")

    def _validate_url(self, url: str) -> bool:
        """Validate Terabox URLs"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                any(d in parsed.netloc for d in ["terabox.com", "terasharelink.com"]),
                parsed.path.startswith("/s/")
            ])
        except Exception as e:
            logger.error(f"Invalid URL: {e}")
            return False

    async def _download_file(self, url: str) -> tuple[bool, BytesIO | str, str | None, int | None]:
        """Download file with retries"""
        for attempt in range(3):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    
                    # Get filename
                    filename = "terabox_file"
                    if "content-disposition" in response.headers:
                        cd = response.headers["content-disposition"]
                        if "filename=" in cd:
                            filename = cd.split("filename=")[1].split(";")[0].strip('\"\'')
                    
                    # Stream download
                    buffer = BytesIO()
                    async for chunk in response.content.iter_chunked(8192):
                        buffer.write(chunk)
                    
                    buffer.seek(0)
                    return (True, buffer, filename, int(response.headers.get("content-length", 0)))
                    
            except Exception as e:
                if attempt == 2:
                    return (False, f"Failed after 3 attempts: {str(e)}", None, None)
                await asyncio.sleep(2 ** attempt)
        return (False, "Unknown error", None, None)

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🚀 <b>Terabox Downloader Bot</b>\n\n"
            "Send me a public Terabox link (format: terabox.com/s/...) and I'll download it for you!"
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process Terabox links"""
        url = update.message.text.strip()
        
        if not self._validate_url(url):
            await update.message.reply_text("❌ Invalid Terabox URL format. Example: https://terabox.com/s/123abc")
            return
        
        msg = await update.message.reply_text("⏳ Downloading file...")
        
        success, data, filename, size = await self._download_file(url)
        
        if not success:
            await msg.edit_text(f"❌ Download failed: {data}")
            return
            
        try:
            await update.message.reply_document(
                document=InputFile(data, filename=filename or "terabox_file"),
                caption=f"✅ {filename}" + (f" ({size//1024//1024}MB)" if size else "")
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Upload failed: {str(e)}")
        finally:
            if isinstance(data, BytesIO):
                data.close()

    def _register_handlers(self):
        """Register command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(f"Update {update} caused error: {context.error}")

    def run(self):
        """Start the bot"""
        logger.info("Starting bot...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    bot = TeraboxDownloaderBot()
    bot.run()
