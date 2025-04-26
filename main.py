from instagrapi import Client
import os
import json
import time
import logging
import random

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# ===== SESSION HANDLER =====
def create_fresh_session():
    """Generate new session with random device fingerprint"""
    return {
        "cookies": [],
        "device_settings": {
            "app_version": "250.0.0.16.117",
            "android_version": random.randint(25, 30),
            "android_release": f"{random.randint(9, 13)}.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": random.choice(["Google", "Xiaomi", "Samsung"]),
            "device": random.choice(["Pixel 5", "Redmi Note 10", "Galaxy S21"]),
            "phone_id": Client().generate_uuid(),
            "uuid": Client().generate_uuid()
        },
        "user_agent": "Instagram 250.0.0.16.117 Android"
    }

def reset_session():
    """Completely reset session file"""
    with open(SESSION_FILE, 'w') as f:
        json.dump(create_fresh_session(), f)
    logger.info("Created fresh session file")

# ===== CORE BOT =====
class InstagramBot:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [2, 5]
        
    def login(self):
        """Smart login with session recovery"""
        try:
            if not os.path.exists(SESSION_FILE):
                reset_session()
            
            self.client.load_settings(SESSION_FILE)
            if not self.client.login(USERNAME, PASSWORD):
                raise Exception("Login returned False")
                
            # Verify session works
            self.client.get_timeline_feed()
            logger.info("✅ Login successful")
            return True
            
        except ChallengeRequired:
            logger.error("🔐 Complete verification in Instagram app!")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            reset_session()
            return False

    def get_active_groups(self):
        """Safe group detection without force_refresh"""
        try:
            threads = self.client.direct_threads()
            return [t for t in threads if self._is_valid_group(t)]
        except Exception as e:
            logger.error(f"Group fetch failed: {str(e)}")
            return []

    def _is_valid_group(self, thread):
        """Check if thread is an active group"""
        try:
            return (
                hasattr(thread, 'users') and
                len(thread.users) > 1 and
                self.client.user_id in [u.pk for u in thread.users]
            )
        except:
            return False

    def reply_in_group(self, group):
        """Send reply with safety checks"""
        try:
            messages = self.client.direct_messages(thread_id=group.id, amount=1)
            if not messages or messages[-1].user_id == self.client.user_id:
                return

            user = self.client.user_info(messages[-1].user_id)
            self.client.direct_send(
                text=REPLY_TEMPLATE.format(username=user.username),
                thread_ids=[group.id]
            )
            logger.info(f"📩 Replied to @{user.username}")
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Reply failed: {str(e)}")
            if "not in group" in str(e).lower():
                self.client.direct_threads()  # Refresh cache

# ===== MAIN =====
def main():
    bot = InstagramBot()
    
    # Login with retries
    for attempt in range(3):
        if bot.login():
            break
        logger.warning(f"Retry {attempt+1}/3 in 10 seconds...")
        time.sleep(10)
    else:
        logger.error("❌ Permanent login failure")
        return

    # Main loop
    logger.info("🤖 Bot activated - Monitoring groups")
    while True:
        try:
            groups = bot.get_active_groups()
            logger.info(f"📊 Active groups: {len(groups)}")
            
            for group in groups:
                bot.reply_in_group(group)
            
            # Random sleep (30-90s)
            sleep_time = random.randint(30, 90)
            logger.info(f"💤 Sleeping for {sleep_time}s")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
