#!/usr/bin/env python3
import os
import re
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
            raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")
        
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
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "video/webm,video/ogg,video/*;q=0.9"
            }
        )
        logger.info("Bot started with enhanced session headers")

    async def on_shutdown(self, app):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Bot shutdown complete")

    def _clean_url(self, url: str) -> str:
        """Standardize Terabox URLs"""
        url = (url.replace("terasharelink.com", "terabox.com")
                  .replace("1024terabox.com", "terabox.com")
                  .replace("terabox.app", "terabox.com"))
        return url.split('?')[0].split('#')[0]

    def _is_valid_terabox_url(self, url: str) -> bool:
        """Strict URL validation"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                "terabox.com" in parsed.netloc,
                any(parsed.path.startswith(p) for p in ("/s/", "/sharing/")),
                not parsed.path.endswith(('.js','.css','.html'))
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Smart filename extraction"""
        if "content-disposition" in headers:
            try:
                cd = headers["content-disposition"]
                if "filename=" in cd:
                    fname = cd.split("filename=")[1].split(";")[0].strip('\"\'')
                    if '.' in fname:
                        return fname
            except Exception:
                pass
        
        basename = os.path.basename(urlparse(url).path) or "terabox_video"
        if not basename.lower().endswith(('.mp4','.mkv','.mov','.avi')):
            basename += ".mp4"
        return re.sub(r'[^\w\-_. ]', '', basename)

    async def _get_real_video_url(self, url: str) -> str:
        """Resolve redirects to find actual video"""
        async with self.session.head(url, allow_redirects=True) as resp:
            final_url = str(resp.url)
            
            # Fixed parentheses in this condition
            if (any(x in final_url for x in ['.mp4','.mkv','.mov']) or 
                'video/' in resp.headers.get('Content-Type','')):
                return final_url
            
            raise ValueError("No video found after redirect")

    async def _download_video(self, url: str) -> tuple:
        """Robust video downloader"""
        try:
            video_url = await self._get_real_video_url(url)
            
            async with self.session.get(video_url) as response:
                response.raise_for_status()
                
                if 'video/' not in response.headers.get('Content-Type',''):
                    raise ValueError("Not a video file")
                
                buffer = BytesIO()
                file_size = int(response.headers.get('content-length', 0))
                filename = self._extract_filename(video_url, response.headers)
                
                async for chunk in response.content.iter_chunked(8192):
                    buffer.write(chunk)
                
                buffer.seek(0)
                return (True, buffer, filename, file_size)
                
        except Exception as e:
            return (False, str(e), None, None)

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎬 <b>Terabox Video Downloader</b>\n\n"
            "Send me a Terabox video link (must contain /s/ or /sharing/) "
            "and I'll fetch the video for you!\n\n"
            "⚠️ <i>Only works with public video links</i>"
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process video links"""
        raw_url = update.message.text.strip()
        url = self._clean_url(raw_url)
        
        if not self._is_valid_terabox_url(url):
            await update.message.reply_text(
                "❌ Invalid Terabox video link!\n"
                "Example valid format:\n"
                "<code>https://terabox.com/s/123abc</code>"
            )
            return
        
        msg = await update.message.reply_text("🔍 Checking video link...")
        
        success, data, filename, size = await self._download_video(url)
        
        if not success:
            await msg.edit_text(f"❌ Failed: {data}\n\nTry the link in your browser first.")
            return
            
        try:
            await update.message.reply_video(
                video=InputFile(data, filename=filename),
                caption=f"📹 {filename}",
                duration=int(size/(1024*250)) if size else None,
                supports_streaming=True,
                read_timeout=60,
                write_timeout=60
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"📤 Upload failed: {str(e)}")
        finally:
            if data:
                data.close()

    def _register_handlers(self):
        """Register all handlers"""
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler)
        )
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(f"Error: {context.error}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                f"⚠️ Error occurred: {str(context.error)[:200]}"
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting Terabox Video Downloader Bot...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    bot = TeraboxDownloaderBot()
    bot.run()
