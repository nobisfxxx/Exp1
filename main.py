#!/usr/bin/env python3
import os
import time
import logging
import asyncio
import signal
from io import BytesIO
from urllib.parse import urlparse
import aiohttp
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    Defaults,
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
        
        # Initialize the Application
        self.application = Application.builder() \
            .token(self.token) \
            .defaults(Defaults(
                parse_mode="HTML",
                disable_web_page_preview=True,
                block=False
            )) \
            .build()
            
        # Rate limiting dictionary
        self.user_cooldown = {}
        self.session = None

        # Register handlers
        self._register_handlers()

    async def init_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "TeraboxDownloader/1.0"}
        )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        now = time.time()
        if user_id in self.user_cooldown:
            if now - self.user_cooldown[user_id] < 5:  # 5 second cooldown
                return True
        self.user_cooldown[user_id] = now
        return False

    def _validate_url(self, url: str) -> bool:
        """Validate Terabox URLs"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                any(domain in parsed.netloc for domain in ["terabox.com", "terasharelink.com"]),
                parsed.path.startswith("/s/")
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Extract filename from headers or URL"""
        if "content-disposition" in headers:
            cd = headers["content-disposition"]
            if "filename=" in cd:
                return cd.split("filename=")[1].strip('"\'').replace(" ", "_")
        return os.path.basename(urlparse(url).path) or "terabox_file"

    async def _download_file(self, url: str) -> tuple:
        """Download file with progress tracking"""
        if not self.session:
            await self.init_session()

        try:
            async with self.session.head(url, allow_redirects=True) as head_resp:
                head_resp.raise_for_status()
                file_size = int(head_resp.headers.get("content-length", 0))
                filename = self._extract_filename(url, head_resp.headers)

            buffer = BytesIO()
            downloaded = 0
            async with self.session.get(url) as response:
                response.raise_for_status()
                
                async for chunk in response.content.iter_chunked(8192):
                    buffer.write(chunk)
                    downloaded += len(chunk)
                    
            buffer.seek(0)
            return (True, buffer, filename, file_size)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return (False, str(e), None, None)

    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚀 <b>Terabox Downloader Bot</b>\n\n"
            "Send me a public Terabox link and I'll download it for you!\n\n"
            "⚠️ <i>Only works with public links (no login required)</i>\n\n"
            "Type /help for usage instructions"
        )

    async def _help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📝 <b>How to use:</b>\n"
            "1. Find a Terabox file (must be public)\n"
            "2. Copy the share link (should look like terabox.com/s/...)\n"
            "3. Paste it here\n\n"
            "⚙️ <b>Features:</b>\n"
            "- Supports files up to 2GB (Telegram limit)\n"
            "- Auto-detects file type\n"
            "- Progress tracking\n\n"
            "⏳ <b>Rate limit:</b> 1 request every 5 seconds"
        )

    async def _message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        message = update.message
        url = message.text.strip()

        if self._check_rate_limit(user.id):
            await message.reply_text("⏳ Please wait 5 seconds between requests")
            return

        if not self._validate_url(url):
            await message.reply_text(
                "❌ Invalid Terabox URL. Must be in format:\n"
                "<code>https://terabox.com/s/...</code>\n\n"
                "Type /help for instructions"
            )
            return

        status_msg = await message.reply_text("⏳ Checking link...")

        success, result, filename, file_size = await self._download_file(url)

        if not success:
            await status_msg.edit_text(f"❌ Download failed:\n<code>{result}</code>")
            return

        max_size = 1.8 * 1024 * 1024 * 1024  # 1.8GB buffer
        if file_size > max_size:
            await status_msg.edit_text(
                f"⚠️ File too large ({file_size/1024/1024:.1f}MB). "
                f"Max supported: {max_size/1024/1024:.1f}MB"
            )
            return

        await status_msg.edit_text(f"⬆️ Uploading {filename}...")
        
        try:
            await message.reply_document(
                document=InputFile(result, filename=filename),
                caption=f"✅ {filename} ({file_size/1024/1024:.1f}MB)"
            )
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            await status_msg.edit_text(f"❌ Upload failed:\n<code>{e}</code>")
        finally:
            if hasattr(result, 'close'):
                result.close()

    def _register_handlers(self):
        """Register all handlers"""
        handlers = [
            CommandHandler("start", self._start_handler),
            CommandHandler("help", self._help_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler)
        ]
        for handler in handlers:
            self.application.add_handler(handler)

    async def run(self):
        """Run the bot with graceful shutdown"""
        await self.init_session()
        
        # Register signal handlers
        stop_event = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: stop_event.set())
        
        async with self.application:
            await self.application.start()
            logger.info("Bot is running...")
            await stop_event.wait()  # Wait until shutdown signal
            logger.info("Shutting down gracefully...")
            await self.application.stop()
            await self.close_session()
            logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        bot = TeraboxDownloaderBot()
        asyncio.run(bot.run())
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
        raise
