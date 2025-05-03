#!/usr/bin/env python3
import os
import re
import json
import time
import logging
import asyncio
from io import BytesIO
from urllib.parse import urlparse, unquote, parse_qs
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
            timeout=aiohttp.ClientTimeout(total=120),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "video/webm,video/ogg,video/*;q=0.9",
                "Referer": "https://www.terabox.com/",
                "Origin": "https://www.terabox.com"
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
        url = unquote(url)
        domains = ["terasharelink.com", "1024terabox.com", "terabox.app", "www.terabox.com"]
        for domain in domains:
            url = url.replace(domain, "terabox.com")
        return url.split('?')[0].split('#')[0]

    def _is_valid_terabox_url(self, url: str) -> bool:
        """Strict URL validation"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                "terabox.com" in parsed.netloc,
                any(parsed.path.startswith(p) for p in ("/s/", "/sharing/", "/share/", "/w/")),
                len(parsed.path.split('/')[-1]) >= 8  # Minimum ID length
            ])
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False

    async def _extract_video_from_api(self, share_id: str) -> str:
        """Use Terabox's internal API to get direct download URL"""
        api_url = f"https://www.terabox.com/api/shorturlinfo?shorturl={share_id}"
        
        async with self.session.get(api_url) as response:
            data = await response.json()
            
            if data.get("errno") != 0:
                raise ValueError("API error: " + data.get("errmsg", "Unknown error"))
            
            if not data.get("dlink"):
                raise ValueError("No download link in API response")
            
            return data["dlink"]

    async def _extract_video_from_page(self, url: str) -> str:
        """Advanced parsing for modern Terabox pages"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                
                # Method 1: Find JSON-LD data
                ld_json = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
                if ld_json:
                    try:
                        data = json.loads(ld_json.group(1))
                        if data.get("@type") == "VideoObject" and data.get("contentUrl"):
                            return data["contentUrl"]
                    except json.JSONDecodeError:
                        pass
                
                # Method 2: Find window.__DATA__
                js_data = re.search(r'window\.__DATA__\s*=\s*({.*?});', html, re.DOTALL)
                if js_data:
                    try:
                        data = json.loads(js_data.group(1))
                        if data.get("videoInfo", {}).get("video_url"):
                            return data["videoInfo"]["video_url"]
                    except json.JSONDecodeError:
                        pass
                
                # Method 3: Find direct MP4 links
                video_url = re.search(
                    r'source\s+src="(https?://[^"]+\.mp4)"',
                    html,
                    re.IGNORECASE
                )
                if video_url:
                    return video_url.group(1)
                
                raise ValueError("No video source found in page")
        except Exception as e:
            raise ValueError(f"Page parsing failed: {str(e)}")

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Smart filename extraction"""
        # From Content-Disposition
        if "content-disposition" in headers:
            try:
                cd = headers["content-disposition"]
                if "filename=" in cd:
                    fname = cd.split("filename=")[1].split(";")[0].strip('\"\'')
                    if '.' in fname:
                        return unquote(fname)
            except Exception as e:
                logger.warning(f"Content-Disposition parse failed: {e}")

        # From URL
        basename = unquote(os.path.basename(urlparse(url).path)) or "terabox_video"
        if not basename.lower().endswith(('.mp4','.mkv','.mov','.avi','.webm')):
            basename += ".mp4"
            
        return re.sub(r'[^\w\-_. ()[\]]', '', basename)[:128]

    async def _download_video(self, url: str) -> tuple:
        """Robust video downloader"""
        for attempt in range(3):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    
                    # Verify content
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
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _process_video_url(self, url: str) -> tuple:
        """Main processing pipeline with multiple fallbacks"""
        try:
            # Try direct download first
            return await self._download_video(url)
        except Exception as e:
            logger.info(f"Direct download failed ({str(e)}), trying API...")
            
            try:
                # Extract share ID and try API
                share_id = urlparse(url).path.split('/')[-1]
                api_url = await self._extract_video_from_api(share_id)
                return await self._download_video(api_url)
            except Exception as api_error:
                logger.info(f"API failed ({str(api_error)}), trying page parsing...")
                
                try:
                    # Final fallback to HTML parsing
                    video_url = await self._extract_video_from_page(url)
                    return await self._download_video(video_url)
                except Exception as parse_error:
                    raise ValueError(
                        f"All methods failed:\n"
                        f"1. Direct: {str(e)}\n"
                        f"2. API: {str(api_error)}\n"
                        f"3. Parser: {str(parse_error)}"
                    )

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎬 <b>Terabox Video Downloader</b>\n\n"
            "Send me a Terabox video link and I'll fetch it for you!\n\n"
            "⚠️ <i>Works with most public Terabox links</i>\n"
            "🔗 <i>Supported formats:</i>\n"
            "- terabox.com/s/...\n"
            "- terabox.com/sharing/...\n"
            "- terabox.com/share/..."
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process video links"""
        raw_url = update.message.text.strip()
        url = self._clean_url(raw_url)
        
        if not self._is_valid_terabox_url(url):
            await update.message.reply_text(
                "❌ <b>Invalid Link Format</b>\n\n"
                "Please send a valid Terabox link like:\n"
                "<code>https://terabox.com/s/123abcde</code>\n"
                "<code>https://www.terabox.com/sharing/xyz7890</code>",
                parse_mode="HTML"
            )
            return
        
        msg = await update.message.reply_text("🔍 Processing your link...")
        
        try:
            success, data, filename, size = await self._process_video_url(url)
            
            if not success:
                raise ValueError(data)
            
            await update.message.reply_video(
                video=InputFile(data, filename=filename),
                caption=f"🎥 {filename}",
                duration=int(size/(1024*250)) if size else None,
                supports_streaming=True,
                read_timeout=180,
                write_timeout=180
            )
            await msg.delete()
            
        except Exception as e:
            error_msg = (
                "❌ <b>Download Failed</b>\n\n"
                f"<i>Reason:</i> {str(e)}\n\n"
                "<b>Try this:</b>\n"
                "1. Open link in browser\n"
                "2. Wait for video to load completely\n"
                "3. Right-click video → <i>'Copy video address'</i>\n"
                "4. Send that direct URL to me"
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
        """Log errors"""
        logger.error(f"Update {update} caused error: {context.error}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                "⚠️ <b>Bot Error</b>\n\n"
                "Please try again later or contact support",
                parse_mode="HTML"
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting Terabox Video Downloader Bot...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            pool_timeout=120
        )

if __name__ == "__main__":
    bot = TeraboxDownloaderBot()
    bot.run()
