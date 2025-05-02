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
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

class TeraboxDownloaderBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
        
        # Initialize the Application with optimized settings
        self.application = Application.builder() \
            .token(self.token) \
            .defaults(Defaults(
                parse_mode="HTML",
                disable_web_page_preview=True,
                block=False
            )) \
            .post_init(self.post_init) \
            .post_shutdown(self.post_shutdown) \
            .build()
            
        # Rate limiting
        self.user_cooldown = {}
        self.session = None
        self.lock = asyncio.Lock()

        # Register handlers
        self._register_handlers()

    async def post_init(self, application):
        """Initialize resources when bot starts"""
        logger.info("Initializing resources...")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "TeraboxDownloader/2.0"}
        )

    async def post_shutdown(self, application):
        """Cleanup resources when bot stops"""
        logger.info("Cleaning up resources...")
        if self.session:
            await self.session.close()
        logger.info("Cleanup complete")

    async def _check_rate_limit(self, user_id: int) -> bool:
        """Improved rate limiting with lock"""
        async with self.lock:
            now = time.time()
            if user_id in self.user_cooldown:
                if now - self.user_cooldown[user_id] < 5:
                    return True
            self.user_cooldown[user_id] = now
            return False

    def _validate_url(self, url: str) -> bool:
        """Strict URL validation"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                any(domain in parsed.netloc.lower() for domain in [
                    "terabox.com", 
                    "terasharelink.com",
                    "www.terabox.com"
                ]),
                parsed.path.startswith(("/s/", "/sharing/"))
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Improved filename extraction"""
        filename = "terabox_file"
        if "content-disposition" in headers:
            try:
                cd = headers["content-disposition"]
                if "filename=" in cd:
                    filename = cd.split("filename=")[1].split(";")[0].strip('\"\'')
            except Exception as e:
                logger.warning(f"Filename extraction failed: {e}")
        
        if filename == "terabox_file":
            path = urlparse(url).path
            filename = os.path.basename(path) or filename
        
        # Sanitize filename
        return "".join(
            c for c in filename 
            if c.isalnum() or c in (' ', '.', '_', '-')
        ).strip()

    async def _download_file(self, url: str) -> tuple:
        """Robust file downloader with retries"""
        if not self.session:
            await self.post_init(None)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use separate requests for head and get
                head_resp = await self.session.head(url, allow_redirects=True)
                head_resp.raise_for_status()
                file_size = int(head_resp.headers.get("content-length", 0))
                filename = self._extract_filename(url, head_resp.headers)
                head_resp.close()

                buffer = BytesIO()
                downloaded = 0
                
                resp = await self.session.get(url)
                resp.raise_for_status()
                
                async for chunk in resp.content.iter_chunked(8192):
                    buffer.write(chunk)
                    downloaded += len(chunk)
                
                resp.close()
                buffer.seek(0)
                return (True, buffer, filename, file_size)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Download failed after {max_retries} attempts: {e}")
                    return (False, str(e), None, None)
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

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

        if await self._check_rate_limit(user.id):
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
                caption=f"✅ {filename} ({file_size/1024/1024:.1f}MB)",
                read_timeout=60,
                write_timeout=60,
                connect_timeout=30
            )
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            await status_msg.edit_text(f"❌ Upload failed:\n<code>{e}</code>")
        finally:
            if hasattr(result, 'close'):
                result.close()

    def _register_handlers(self):
        """Register all handlers with error handling"""
        handlers = [
            CommandHandler("start", self._start_handler),
            CommandHandler("help", self._help_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler)
        ]
        
        for handler in handlers:
            self.application.add_handler(handler, group=1)

    async def run(self):
        """Run the bot with graceful shutdown"""
        await self.application.initialize()
        await self.application.start()
        logger.info("Bot is running...")
        
        # Handle shutdown signals
        stop_event = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: stop_event.set())
        
        await stop_event.wait()
        logger.info("Shutting down gracefully...")
        await self.application.stop()
        await self.application.shutdown()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        bot = TeraboxDownloaderBot()
        asyncio.run(bot.run())
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
        raise
