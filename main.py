from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import logging
import sys
from datetime import datetime

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "/app/session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# ===== SESSION MANAGER =====
def validate_session_structure():
    """Ensure session file has correct structure"""
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return all(key in data for key in ['cookies', 'device_settings', 'user_agent'])
    except:
        return False

def reset_session():
    """Create fresh session file with device fingerprint"""
    new_session = {
        "cookies": [],
        "device_settings": {
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "Xiaomi",
            "device": "mi 6"
        },
        "user_agent": "Instagram 219.0.0.12.117 Android"
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(new_session, f)

# ===== CORE FUNCTIONALITY =====
class InstagramBot:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [3, 7]
        
    def login(self):
        """Smart login with session recovery"""
        try:
            if validate_session_structure():
                self.client.load_settings(SESSION_FILE)
                self._verify_session()
                logger.info("✅ Session login successful")
                return True
            else:
                return self._fresh_login()
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def _verify_session(self):
        """Confirm session is still valid"""
        try:
            self.client.get_timeline_feed()
        except (LoginRequired, AttributeError):
            logger.warning("Session expired - refreshing")
            self._fresh_login()

    def _fresh_login(self):
        """Perform new login and save session"""
        try:
            reset_session()
            self.client.load_settings(SESSION_FILE)
            self.client.login(USERNAME, PASSWORD)
            self.client.dump_settings(SESSION_FILE)
            logger.info("✅ Fresh login successful")
            return True
        except ChallengeRequired:
            logger.error("🔐 Complete verification in Instagram app!")
            return False
        except Exception as e:
            logger.error(f"Fresh login failed: {str(e)}")
            return False

    def get_active_groups(self):
        """Safely fetch groups with error handling"""
        try:
            threads = self.client.direct_threads()
            return [t for t in threads if self._is_valid_group(t)]
        except Exception as e:
            logger.error(f"Group fetch failed: {str(e)}")
            return []

    def _is_valid_group(self, thread):
        """Check if thread is a group and bot is still member"""
        try:
            return (
                thread and
                len(getattr(thread, 'users', [])) > 1 and
                self.client.user_id in [u.pk for u in thread.users]
            )
        except Exception as e:
            logger.warning(f"Group validation error: {str(e)}")
            return False

    def process_group(self, group):
        """Handle message processing for a single group"""
        try:
            messages = self.client.direct_messages(thread_id=group.id, amount=1)
            if not messages:
                return

            last_msg = messages[-1]
            if last_msg.user_id == self.client.user_id:
                return

            user = self.client.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            
            self.client.direct_send(
                text=reply_text,
                thread_ids=[group.id]
            )
            logger.info(f"📩 Replied to @{user.username}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Group error: {str(e)}")
            if "not in group" in str(e).lower():
                logger.info("Removed from group - updating session")
                self.client.direct_threads(force_refresh=True)

# ===== MAIN FLOW =====
def main():
    bot = InstagramBot()
    
    # Login with retries
    for attempt in range(3):
        if bot.login():
            break
        logger.warning(f"Retry {attempt+1}/3 in 30 seconds...")
        time.sleep(30)
    else:
        logger.error("❌ Permanent login failure")
        sys.exit(1)

    # Main loop
    logger.info("🤖 Bot operational - Monitoring groups")
    while True:
        try:
            groups = bot.get_active_groups()
            logger.info(f"📊 Active groups: {len(groups)}")
            
            for group in groups:
                bot.process_group(group)
            
            # Randomized delay to avoid detection
            sleep_time = 45 + (len(groups) * 5)
            logger.info(f"💤 Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown")
            break
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
