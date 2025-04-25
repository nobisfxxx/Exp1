from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import time
import random
import logging
from datetime import datetime

# ===== SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot_debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "/app/session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# ===== BOT CLASS =====
class GroupReplyBot:
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [3, 7]
        self.replied_ids = set()
        self._configure_client()

    def _configure_client(self):
        """Set realistic device parameters"""
        self.cl.set_user_agent("Instagram 219.0.0.12.117 Android")
        self.cl.set_device({
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2",
            "dpi": "480dpi",
            "resolution": "1080x1920"
        })

    def login(self):
        """Handle session/auth with detailed logging"""
        try:
            if os.path.exists(SESSION_FILE):
                self.cl.load_settings(SESSION_FILE)
                logger.info("Loaded existing session")
            else:
                logger.warning("No session file found")

            self.cl.login(USERNAME, PASSWORD)
            self.cl.dump_settings(SESSION_FILE)
            logger.info("Login successful")
            return True
            
        except ChallengeRequired:
            logger.error("Complete verification in Instagram app!")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            return False

    def get_active_groups(self):
        """Fetch group chats with error handling"""
        try:
            groups = self.cl.direct_threads(thread_types=["group"])
            logger.info(f"Found {len(groups)} groups")
            return groups
        except Exception as e:
            logger.error(f"Failed to fetch groups: {str(e)}")
            return []

    def process_group(self, group):
        """Handle messages in a single group"""
        try:
            group_id = group.id
            logger.debug(f"Processing group {group_id}")

            messages = self.cl.direct_messages(group_id)
            if not messages:
                logger.debug("No messages in group")
                return

            last_msg = messages[-1]
            if last_msg.id in self.replied_ids:
                return

            if last_msg.user_id == self.cl.user_id:
                logger.debug("Ignoring own message")
                return

            user = self.cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            
            self.cl.direct_send(reply_text, thread_id=group_id)
            self.replied_ids.add(last_msg.id)
            
            logger.info(f"Replied to @{user.username} in group {group_id}")
            time.sleep(random.randint(2, 5))

        except Exception as e:
            logger.error(f"Group {group_id} error: {str(e)}")

    def run(self):
        """Main execution loop"""
        if not self.login():
            return

        logger.info("Bot started - Monitoring groups")
        while True:
            try:
                groups = self.get_active_groups()
                for group in groups:
                    self.process_group(group)
                
                # Reset replied IDs every hour
                if time.time() % 3600 < 10:
                    self.replied_ids.clear()
                    logger.info("Cleared reply history")

                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                logger.info("Bot stopped manually")
                break
            except Exception as e:
                logger.error(f"Critical error: {str(e)}")
                time.sleep(60)

# ===== EXECUTION =====
if __name__ == "__main__":
    bot = GroupReplyBot()
    bot.run()
