from instagrapi import Client
import os
import json
import time
import random
import logging

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"
REPLY_MSG = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

class MessageTracker:
    def __init__(self):
        self.sent_messages = set()
    
    def add(self, message_id):
        self.sent_messages.add(message_id)
    
    def contains(self, message_id):
        return message_id in self.sent_messages

tracker = MessageTracker()

# ===== CORE BOT =====
class InstagramBot:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [3, 7]
        
    def login(self):
        try:
            if os.path.exists(SESSION_FILE):
                self.client.load_settings(SESSION_FILE)
            
            logger.debug("Attempting login...")
            login_result = self.client.login(USERNAME, PASSWORD)
            
            if not login_result:
                raise Exception("Login returned False")
            
            logger.info("✅ Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def process_groups(self):
        """Full message processing with debug logs"""
        try:
            logger.debug("Fetching threads...")
            threads = self.client.direct_threads()
            logger.debug(f"Raw threads data: {threads}")
            
            valid_groups = []
            for t in threads:
                if self._is_valid_group(t):
                    valid_groups.append(t)
                    logger.debug(f"Valid group: {t.id} | Users: {[u.username for u in t.users]}")
            
            logger.info(f"📊 Active groups: {len(valid_groups)}")
            
            for group in valid_groups:
                self._process_group(group)
                
        except Exception as e:
            logger.error(f"Group processing failed: {str(e)}")

    def _is_valid_group(self, thread):
        """Detailed group validation"""
        try:
            if not hasattr(thread, 'users'):
                logger.debug("Invalid thread: missing users attribute")
                return False
                
            users = thread.users
            if len(users) <= 1:
                logger.debug(f"Thread {thread.id} is not a group (only {len(users)} users)")
                return False
                
            if self.client.user_id not in [u.pk for u in users]:
                logger.debug(f"Bot not in group {thread.id}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Group validation error: {str(e)}")
            return False

    def _process_group(self, group):
        """Message handling with reply tracking"""
        try:
            logger.debug(f"Processing group {group.id}")
            
            messages = self.client.direct_messages(thread_id=group.id, amount=5)
            if not messages:
                logger.debug("No messages in group")
                return
                
            last_msg = messages[-1]
            logger.debug(f"Last message: ID={last_msg.id} | User={last_msg.user_id} | Text={last_msg.text[:50]}...")
            
            if tracker.contains(last_msg.id):
                logger.debug("Already replied to this message")
                return
                
            if last_msg.user_id == self.client.user_id:
                logger.debug("Skipping own message")
                return
                
            user = self.client.user_info(last_msg.user_id)
            reply_text = REPLY_MSG.format(username=user.username)
            
            logger.debug(f"Sending reply: {reply_text}")
            self.client.direct_send(text=reply_text, thread_id=group.id)
            tracker.add(last_msg.id)
            
            logger.info(f"📩 Successfully replied to @{user.username}")
            time.sleep(random.randint(2, 5))
            
        except Exception as e:
            logger.error(f"Group processing error: {str(e)}")

# ===== MAIN =====
def main():
    bot = InstagramBot()
    
    if not bot.login():
        logger.error("❌ Permanent login failure")
        return
    
    logger.info("🤖 Bot activated - Starting message scan")
    while True:
        try:
            bot.process_groups()
            sleep_time = random.randint(45, 120)
            logger.info(f"💤 Sleeping for {sleep_time}s")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown")
            break
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
