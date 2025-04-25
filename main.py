from instagrapi import Client
import os
import json
import time
import logging
import sys
from datetime import datetime

# ===== ENHANCED CONFIGURATION =====
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

class RobustInstagramBot:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [3, 7]
        self.client.set_user_agent("Instagram 219.0.0.12.117 Android")
        self._configure_device()
        
    def _configure_device(self):
        """Device fingerprint hardening"""
        self.client.set_device({
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "Xiaomi",
            "device": "mi 6",
            "phone_id": self.client.generate_uuid(),
            "uuid": self.client.generate_uuid(),
        })
        
    def login(self):
        """Smart login with session recovery"""
        try:
            if os.path.exists(SESSION_FILE):
                self.client.load_settings(SESSION_FILE)
                if self._verify_session():
                    return True
            return self._fresh_login()
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
            
    def _verify_session(self):
        """Verify session validity"""
        try:
            self.client.get_timeline_feed()
            return True
        except (LoginRequired, AttributeError):
            return False
            
    def _fresh_login(self):
        """Perform new login with challenge handling"""
        try:
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
        """Fetch groups with robust error handling"""
        try:
            # Force API refresh with timeout
            threads = self.client.direct_threads(force_refresh=True, timeout=10)
            
            if not isinstance(threads, list):
                logger.error("Invalid threads response - possible shadowban")
                return []
                
            return [t for t in threads if self._valid_group(t)]
        except Exception as e:
            logger.error(f"Group fetch failed: {str(e)}")
            return []
            
    def _valid_group(self, thread):
        """Validate group structure"""
        try:
            return (
                thread is not None and
                hasattr(thread, 'users') and
                len(thread.users) > 1 and
                self.client.user_id in [u.pk for u in thread.users]
            )
        except Exception as e:
            logger.warning(f"Group validation error: {str(e)}")
            return False
            
    def process_groups(self):
        """Process groups with enhanced safety"""
        groups = self.get_active_groups()
        logger.info(f"📊 Valid groups: {len(groups)}")
        
        for group in groups:
            try:
                # Verify group access
                if not self.client.direct_thread(group.id):
                    logger.warning(f"Lost access to group {group.id[:6]}...")
                    continue
                    
                self._process_group_messages(group)
                
            except Exception as e:
                logger.error(f"Group {group.id[:6]}... failed: {str(e)}")
                self.client.direct_threads(force_refresh=True)
                
    def _process_group_messages(self, group):
        """Handle message processing"""
        messages = self.client.direct_messages(thread_id=group.id, amount=1)
        if not messages:
            return
            
        last_msg = messages[-1]
        if last_msg.user_id == self.client.user_id:
            return
            
        user = self.client.user_info(last_msg.user_id)
        self.client.direct_send(
            REPLY_TEMPLATE.format(username=user.username),
            thread_ids=[group.id]
        )
        logger.info(f"📩 Replied to @{user.username}")
        time.sleep(3)

# ===== MAIN EXECUTION =====
def main():
    bot = RobustInstagramBot()
    
    # Login sequence
    if not bot.login():
        logger.error("❌ Permanent login failure")
        sys.exit(1)
        
    logger.info("🤖 Bot operational - Monitoring groups")
    while True:
        try:
            bot.process_groups()
            sleep_time = 60  # More conservative delay
            logger.info(f"💤 Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown")
            break
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main()
