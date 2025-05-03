#!/usr/bin/env python3
import os
import re
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
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "video/webm,video/ogg,video/*;q=0.9",
                "Referer": "https://www.terabox.com/"
            }
        )
        logger.info("Bot started with enhanced session headers")

    async def on_shutdown(self, app):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Bot shutdown complete")

    def _clean_url(self, url: str) -> str:
        """Standardize Terabox URLs and remove tracking"""
        url = unquote(url)  # Decode URL-encoded characters
        domains = ["terasharelink.com", "1024terabox.com", "terabox.app"]
        for domain in domains:
            url = url.replace(domain, "terabox.com")
        return url.split('?')[0].split('#')[0]

    def _is_valid_terabox_url(self, url: str) -> bool:
        """Strict URL validation with improved checks"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                any(d in parsed.netloc for d in ["terabox.com", "www.terabox.com"]),
                any(parsed.path.startswith(p) for p in ("/s/", "/sharing/", "/share/")),
                not parsed.path.endswith(('.js','.css','.html','.php')),
                len(parsed.path.split('/')[-1]) > 5  # Minimum ID length
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    async def _extract_video_from_page(self, url: str) -> str:
        """Advanced HTML parsing to find embedded videos"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                
                # Method 1: Find JSON-encoded video URLs
                json_matches = re.findall(r'"video_url":"(https?://[^"]+\.mp4)"', html)
                if json_matches:
                    return json_matches[0].replace('\\/', '/')
                
                # Method 2: Find standard video tags
                video_src = re.search(
                    r'<video[^>]+src="(https?://[^"]+\.(?:mp4|mkv|mov|webm))"',
                    html,
                    re.IGNORECASE
                )
                if video_src:
                    return video_src.group(1)
                
                # Method 3: Find download buttons
                download_btn = re.search(
                    r'href="(https?://[^"]+\.(?:mp4|mkv|mov|webm))"[^>]*download',
                    html,
                    re.IGNORECASE
                )
                if download_btn:
                    return download_btn.group(1)
                
                raise ValueError("No video source found in page")
        except Exception as e:
            raise ValueError(f"Page parsing failed: {str(e)}")

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Smart filename extraction with multiple fallbacks"""
        # From Content-Disposition
        if "content-disposition" in headers:
            try:
                cd = headers["content-disposition"]
                if "filename=" in cd:
                    fname = cd.split("filename=")[1].split(";")[0].strip('\"\'')
                    if '.' in fname:  # Has extension
                        return unquote(fname)  # Decode URL-encoded filenames
            except Exception as e:
                logger.warning(f"Content-Disposition parse failed: {e}")

        # From URL path
        path = urlparse(url).path
        basename = unquote(os.path.basename(path)) or "terabox_video"
        
        # Ensure video extension
        if not basename.lower().endswith(('.mp4','.mkv','.mov','.avi','.webm')):
            basename += ".mp4"
            
        # Sanitize filename
        return re.sub(r'[^\w\-_. ()[\]]', '', basename)[:128]  # Limit length

    async def _download_video(self, url: str) -> tuple:
        """Robust video downloader with retries"""
        for attempt in range(3):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    
                    # Verify content type
                    content_type = response.headers.get('Content-Type', '').lower()
                    if not any(x in content_type for x in ['video/', 'octet-stream']):
                        first_bytes = await response.content.read(512)
                        if b'html' in first_bytes.lower():
                            raise ValueError("Received HTML instead of video")
                        response.content._buffer = first_bytes + await response.content.read()
                    
                    # Stream download
                    buffer = BytesIO()
                    file_size = int(response.headers.get('content-length', 0))
                    filename = self._extract_filename(url, response.headers)
                    
                    async for chunk in response.content.iter_chunked(8192):
                        buffer.write(chunk)
                    
                    buffer.seek(0)
                    return (True, buffer, filename, file_size)
                    
            except Exception as e:
                if attempt == 2:  # Final attempt
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _process_video_url(self, url: str) -> tuple:
        """Main video processing pipeline"""
        try:
            # Try direct download first
            return await self._download_video(url)
        except Exception as e:
            logger.info(f"Direct download failed ({str(e)}), trying page extraction...")
            try:
                # Fallback to HTML parsing
                video_url = await self._extract_video_from_page(url)
                return await self._download_video(video_url)
            except Exception as ee:
                raise ValueError(f"All methods failed:\n1. {str(e)}\n2. {str(ee)}")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎬 <b>Terabox Video Downloader</b>\n\n"
            "Send me a Terabox video link and I'll fetch it for you!\n\n"
            "⚠️ <i>Works with most public Terabox links</i>\n"
            "🔗 <i>Formats: terabox.com/s/... or terabox.com/sharing/...</i>"
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process video links with comprehensive error handling"""
        raw_url = update.message.text.strip()
        url = self._clean_url(raw_url)
        
        if not self._is_valid_terabox_url(url):
            await update.message.reply_text(
                "❌ <b>Invalid Terabox Link</b>\n\n"
                "Valid examples:\n"
                "• <code>https://terabox.com/s/123abc</code>\n"
                "• <code>https://www.terabox.com/sharing/xyz789</code>"
            )
            return
        
        msg = await update.message.reply_text("🔍 Analyzing link...")
        
        try:
            success, data, filename, size = await self._process_video_url(url)
            
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
            error_msg = (
                "❌ <b>Download Failed</b>\n\n"
                f"<i>Reason:</i> {str(e)}\n\n"
                "<b>Try this:</b>\n"
                "1. Open link in browser\n"
                "2. Wait for video to load\n"
                "3. Right-click video → 'Copy video address'\n"
                "4. Send that URL to me"
            )
            await msg.edit_text(error_msg, parse_mode="HTML")
            
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
        """Log errors and notify user"""
        logger.error(f"Error: {context.error}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "⚠️ <b>Bot Error</b>\n\n"
                f"<code>{str(context.error)[:300]}</code>\n\n"
                "Please try again later",
                parse_mode="HTML"
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting Terabox Video Downloader Bot...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            pool_timeout=60
        )

if __name__ == "__main__":
    bot = TeraboxDownloaderBot()
    bot.run()
