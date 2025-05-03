#!/usr/bin/env python3
import os
import re
import json
import time
import logging
import asyncio
from io import BytesIO
from urllib.parse import urlparse, unquote
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
            timeout=aiohttp.ClientTimeout(total=120),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "video/webm,video/ogg,video/*;q=0.9",
                "Referer": "https://www.terabox.com/",
                "Origin": "https://www.terabox.com",
                "Sec-Fetch-Dest": "video",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
        )
        logger.info("Bot started with browser-like headers")

    async def on_shutdown(self, app):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Bot shutdown complete")

    def _clean_url(self, url: str) -> str:
        """Standardize Terabox URLs"""
        url = unquote(url)
        domains = ["terasharelink.com", "1024terabox.com", "terabox.app"]
        for domain in domains:
            url = url.replace(domain, "terabox.com")
        return url.split('?')[0].split('#')[0]

    def _is_valid_terabox_url(self, url: str) -> bool:
        """Validate Terabox URLs"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                "terabox.com" in parsed.netloc,
                any(parsed.path.startswith(p) for p in ("/s/", "/sharing/", "/w/")),
                len(parsed.path.split('/')[-1]) >= 8
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    async def _get_direct_video_url(self, url: str) -> str:
        """Get direct video URL through Terabox's API"""
        share_id = urlparse(url).path.split('/')[-1]
        api_url = f"https://www.terabox.com/api/shorturlinfo?shorturl={share_id}"
        
        async with self.session.get(api_url) as response:
            data = await response.json()
            if data.get("errno") != 0:
                raise ValueError("API error: " + data.get("errmsg", "Invalid response"))
            return data["dlink"]

    async def _download_video(self, url: str) -> tuple:
        """Download video with verification"""
        try:
            async with self.session.get(url) as response:
                # Verify content is video
                content_type = response.headers.get('Content-Type', '').lower()
                if not any(x in content_type for x in ['video/', 'octet-stream']):
                    first_chunk = await response.content.read(512)
                    if b'html' in first_chunk.lower():
                        raise ValueError("Received HTML instead of video")
                    response.content._buffer = first_chunk + await response.content.read()
                
                # Stream download
                buffer = BytesIO()
                file_size = int(response.headers.get('content-length', 0))
                filename = self._extract_filename(url, response.headers)
                
                async for chunk in response.content.iter_chunked(8192):
                    buffer.write(chunk)
                
                buffer.seek(0)
                return (True, buffer, filename, file_size)
        except Exception as e:
            raise ValueError(f"Download failed: {str(e)}")

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Extract filename from headers or URL"""
        # From Content-Disposition
        if "content-disposition" in headers:
            try:
                cd = headers["content-disposition"]
                if "filename=" in cd:
                    return cd.split("filename=")[1].split(";")[0].strip('\"\'')
            except Exception:
                pass
        
        # From URL
        basename = os.path.basename(urlparse(url).path) or "terabox_video.mp4"
        if not basename.lower().endswith(('.mp4','.mkv','.mov','.avi')):
            basename += ".mp4"
        return re.sub(r'[^\w\-_. ]', '', basename)

    async def _process_url(self, url: str) -> tuple:
        """Process URL through all available methods"""
        try:
            # Method 1: Try direct download
            return await self._download_video(url)
        except Exception as e1:
            logger.info(f"Direct failed: {str(e1)}")
            
            try:
                # Method 2: Use API
                direct_url = await self._get_direct_video_url(url)
                return await self._download_video(direct_url)
            except Exception as e2:
                logger.info(f"API failed: {str(e2)}")
                raise ValueError(f"All methods failed:\n1. {str(e1)}\n2. {str(e2)}")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎬 <b>Terabox Video Downloader</b>\n\n"
            "Send me a Terabox video link and I'll download it for you!\n\n"
            "⚠️ <i>Works with most public links (terabox.com/s/...)</i>"
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process video links"""
        raw_url = update.message.text.strip()
        url = self._clean_url(raw_url)
        
        if not self._is_valid_terabox_url(url):
            await update.message.reply_text(
                "❌ Invalid Terabox link format!\n"
                "Example valid link:\n"
                "<code>https://terabox.com/s/123abcde</code>",
                parse_mode="HTML"
            )
            return
        
        msg = await update.message.reply_text("🔍 Processing your link...")
        
        try:
            success, data, filename, size = await self._process_url(url)
            
            if not success:
                raise ValueError(data)
            
            await update.message.reply_video(
                video=InputFile(data, filename=filename),
                caption=f"🎥 {filename}",
                duration=int(size/(1024*250)) if size else None,
                supports_streaming=True,
                read_timeout=120,
                write_timeout=120
            )
            await msg.delete()
            
        except Exception as e:
            await msg.edit_text(
                f"❌ <b>Download Failed</b>\n\n"
                f"{str(e)}\n\n"
                "<b>Workaround:</b>\n"
                "1. Open link in browser\n"
                "2. Right-click video → 'Copy video address'\n"
                "3. Send that URL to me",
                parse_mode="HTML"
            )
        finally:
            if 'data' in locals() and data:
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
        logger.error(f"Update {update} caused error: {context.error}", exc_info=True)

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
