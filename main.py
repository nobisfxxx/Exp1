from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
import os
import time
import random
import json
from datetime import datetime

# ===== CONFIGURATION =====
USERNAME = os.getenv("INSTA_USERNAME")  # Set in Railway/Heroku
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# Safety limits
MIN_DELAY = 2  # seconds between actions
MAX_DELAY = 5
CHECK_INTERVAL = 30  # seconds between group checks

# ===== CORE BOT =====
class InstagramBot:
    def __init__(self):
        self.cl = Client()
        self.setup_client()
        self.replied_msg_ids = set()  # Prevent duplicate replies

    def setup_client(self):
        """Configure client with realistic settings"""
        self.cl.delay_range = [MIN_DELAY, MAX_DELAY]
        self.cl.set_user_agent("Instagram 219.0.0.12.117 Android")
        self.cl.set_device({
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "ONEPLUS A6013"
        })

    def login(self):
        """Handle login with session persistence"""
        try:
            if os.path.exists(SESSION_FILE):
                self.cl.load_settings(SESSION_FILE)
                self.cl.login(USERNAME, PASSWORD)  # Refresh session
                print("✅ Session refreshed")
            else:
                self.cl.login(USERNAME, PASSWORD)
                self.cl.dump_settings(SESSION_FILE)
                print("✅ New session created")

            # Verify login
            self.cl.get_timeline_feed()
            return True
            
        except ChallengeRequired:
            print("🔐 Challenge required! Check your Instagram app")
        except Exception as e:
            print(f"❌ Login failed: {type(e).__name__}: {str(e)}")
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        return False

    def fetch_groups(self):
        """Get all active group chats"""
        try:
            return self.cl.direct_threads(thread_types=["group"])
        except Exception as e:
            print(f"⚠ Error fetching groups: {str(e)}")
            return []

    def should_reply(self, thread, last_msg):
        """Check if we should reply to this message"""
        return (last_msg.user_id != self.cl.user_id  # Not our own message
                and last_msg.id not in self.replied_msg_ids  # Not already replied
                and len(thread.users) > 2)  # Actual group (not 1:1)

    def send_reply(self, thread, last_msg):
        """Send reply with mention"""
        try:
            user = self.cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            
            self.cl.direct_send(reply_text, thread_id=thread.id)
            self.replied_msg_ids.add(last_msg.id)
            
            print(f"{datetime.now()} - Replied to @{user.username}")
            self.log_activity(thread.id, user.username)
            
        except Exception as e:
            print(f"⚠ Reply failed: {str(e)}")

    def log_activity(self, thread_id, username):
        """Record actions to avoid duplicates"""
        with open("activity.log", "a") as f:
            f.write(f"{datetime.now()},{thread_id},{username}\n")

    def run(self):
        """Main bot loop"""
        if not self.login():
            return False

        print("🤖 Bot started - Ctrl+C to stop")
        while True:
            try:
                groups = self.fetch_groups()
                print(f"🔍 Found {len(groups)} active groups")

                for thread in groups:
                    if thread.messages:
                        last_msg = thread.messages[-1]
                        if self.should_reply(thread, last_msg):
                            self.send_reply(thread, last_msg)
                            time.sleep(random.randint(MIN_DELAY, MAX_DELAY))

                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                print("🛑 Stopping bot...")
                break
            except Exception as e:
                print(f"💥 Critical error: {str(e)}")
                time.sleep(60)  # Wait before retrying

# ===== START BOT =====
if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()
