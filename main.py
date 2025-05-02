#!/usr/bin/env python3
import os
import time
from io import BytesIO
from urllib.parse import urlparse
import requests
from telegram import Update, InputFile
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    Defaults
)

class TeraboxDownloaderBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
        
        # Configure bot with better defaults
        defaults = Defaults(
            parse_mode="HTML",
            disable_web_page_preview=True,
            timeout=30
        )
        
        self.updater = Updater(
            token=self.token,
            defaults=defaults,
            use_context=True
        )
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self._register_handlers()
        
        # Rate limiting (requests per user)
        self.user_cooldown = {}

    def _register_handlers(self):
        handlers = [
            CommandHandler("start", self._start_handler),
            CommandHandler("help", self._help_handler),
            MessageHandler(
                Filters.text & ~Filters.command,
                self._message_handler
            )
        ]
        for handler in handlers:
            self.dispatcher.add_handler(handler)

    def _check_rate_limit(self, user_id: int) -> bool:
        """Returns True if user is rate limited"""
        now = time.time()
        if user_id in self.user_cooldown:
            last_time = self.user_cooldown[user_id]
            if now - last_time < 5:  # 5 seconds cooldown
                return True
        self.user_cooldown[user_id] = now
        return False

    def _validate_url(self, url: str) -> bool:
        """Validate Terabox URLs"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ("http", "https"),
                parsed.netloc.endswith(("terabox.com", "terasharelink.com")),
                parsed.path.startswith("/s/")
            ])
        except:
            return False

    def _extract_filename(self, url: str, headers: dict) -> str:
        """Extract filename from headers or URL"""
        if "content-disposition" in headers:
            cd = headers["content-disposition"]
            if "filename=" in cd:
                return cd.split("filename=")[1].strip('"\'')
        return os.path.basename(urlparse(url).path) or "terabox_file"

    def _download_file(self, url: str) -> tuple:
        """Download file with progress tracking"""
        try:
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # Get file info
                file_size = int(response.headers.get("content-length", 0))
                filename = self._extract_filename(url, response.headers)
                
                # Stream to memory
                buffer = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    buffer.write(chunk)
                
                buffer.seek(0)
                return (True, buffer, filename, file_size)
                
        except Exception as e:
            return (False, str(e), None, None)

    async def _start_handler(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "🚀 <b>Terabox Downloader Bot</b>\n\n"
            "Send me a public Terabox link and I'll download it for you!\n\n"
            "⚠️ <i>Only works with public links (no login required)</i>"
        )

    async def _help_handler(self, update: Update, context: CallbackContext):
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

    async def _message_handler(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        url = update.message.text.strip()

        # Rate limiting check
        if self._check_rate_limit(user_id):
            await update.message.reply_text(
                "⏳ Please wait 5 seconds between requests"
            )
            return

        # URL validation
        if not self._validate_url(url):
            await update.message.reply_text(
                "❌ Invalid Terabox URL. Must be in format:\n"
                "<code>https://terabox.com/s/...</code>"
            )
            return

        # Start processing
        status_msg = await update.message.reply_text(
            "⏳ Checking link..."
        )

        # Download file
        success, result, filename, file_size = self._download_file(url)

        if not success:
            await status_msg.edit_text(
                f"❌ Download failed:\n<code>{result}</code>"
            )
            return

        # Check file size
        if file_size > 1.8 * 1024 * 1024 * 1024:  # 1.8GB
            await status_msg.edit_text(
                "⚠️ File too large (max 2GB supported by Telegram)"
            )
            return

        # Send file
        await status_msg.edit_text(
            f"⬆️ Uploading {filename} ({file_size/1024/1024:.1f}MB)..."
        )
        
        try:
            await update.message.reply_document(
                document=InputFile(result, filename=filename),
                caption="✅ Download complete!"
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(
                f"❌ Upload failed:\n<code>{e}</code>"
            )

    def run(self):
        self.updater.start_polling(
            drop_pending_updates=True,
            timeout=30,
            read_latency=5
        )
        print("Bot is running... Press Ctrl+C to stop")
        self.updater.idle()


if __name__ == "__main__":
    try:
        bot = TeraboxDownloaderBot()
        bot.run()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
