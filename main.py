from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
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

# Configuration
USERNAME = os.getenv("INSTA_USERNAME") or "your_username"
PASSWORD = os.getenv("INSTA_PASSWORD") or "your_password"
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Your message here"

# ===== SAFE SESSION HANDLING =====
def create_fresh_session():
    """Create a new session with proper structure"""
    device = {
        "app_version": "320.0.0.0.0",
        "android_version": 33,
        "android_release": "13.0",
        "phone_manufacturer": "OnePlus",
        "phone_device": "ONEPLUS A5010",
        "phone_model": "ONEPLUS 5T",
        "device_id": f"android-{random.randint(10**15, (10**16)-1)}"
    }
    
    session_data = {
        "cookies": [],
        "last_login": int(time.time()),
        "device_settings": device,
        "user_agent": "Instagram 320.0.0.0.0 Android (33/13.0; OnePlus; ONEPLUS 5T; qcom; en_US; 380dpi)"
    }
    
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

def validate_session_structure():
    """Ensure session file has correct structure"""
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Session is not a dictionary")
            if "cookies" not in data:
                raise ValueError("Missing cookies in session")
        return True
    except Exception as e:
        logger.warning(f"Invalid session: {str(e)}")
        return False

# ===== ROBUST API HANDLER =====
def safe_request(cl, func, *args, max_retries=3, **kwargs):
    """Wrapper for safe API calls with proper typing"""
    for attempt in range(max_retries):
        try:
            response = func(*args, **kwargs)
            
            # Explicit type checking
            if func.__name__ == "direct_threads" and not isinstance(response, list):
                raise TypeError(f"Expected list, got {type(response)}")
                
            if response is None:
                raise ValueError("API returned None")
                
            return response
            
        except (ClientError, TypeError, AttributeError) as e:
            wait = min((2 ** attempt) + random.random(), 15)
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed ({func.__name__}): {str(e)}")
            time.sleep(wait)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    
    logger.error(f"Permanent failure in {func.__name__}")
    return None

# ===== MAIN BOT FUNCTIONS =====
def initialize_client():
    """Initialize client with proper session handling"""
    if not os.path.exists(SESSION_FILE) or not validate_session_structure():
        create_fresh_session()
    
    cl = Client()
    cl.delay_range = [3, 7]  # Human-like delays
    
    try:
        cl.load_settings(SESSION_FILE)
        if not cl.login(USERNAME, PASSWORD):
            raise Exception("Login returned False")
            
        # Verify session is working
        feed = safe_request(cl, cl.get_timeline_feed)
        if not feed:
            raise Exception("Failed to fetch timeline")
            
        cl.dump_settings(SESSION_FILE)
        return cl
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        # Create fresh session for next attempt
        create_fresh_session()
        return None

def process_groups(cl):
    """Safe group processing with type checking"""
    try:
        threads = safe_request(cl, cl.direct_threads)
        if not threads or not isinstance(threads, list):
            return False

        groups = [t for t in threads if hasattr(t, 'users') and len(t.users) > 1]
        if not groups:
            logger.info("No active groups available")
            return False

        for group in groups:
            try:
                if not hasattr(group, 'id'):
                    continue

                messages = safe_request(cl, cl.direct_messages, thread_id=group.id, amount=3)
                if not messages or not isinstance(messages, list):
                    continue

                last_msg = messages[-1] if messages else None
                if not last_msg or not hasattr(last_msg, 'user_id'):
                    continue

                if last_msg.user_id == cl.user_id:
                    continue

                user = safe_request(cl, cl.user_info, last_msg.user_id)
                if not user or not hasattr(user, 'username'):
                    continue

                reply_text = REPLY_TEMPLATE.format(username=user.username)
                time.sleep(random.uniform(5.0, 10.0))
                
                sent = safe_request(cl, cl.direct_send, text=reply_text, thread_ids=[group.id])
                if sent:
                    logger.info(f"Replied to @{user.username}")
                else:
                    logger.warning("Failed to send reply")
                
            except Exception as e:
                logger.error(f"Group processing error: {str(e)}")
            
            time.sleep(random.randint(10, 20))
        
        return True
        
    except Exception as e:
        logger.error(f"Group processing failed: {str(e)}")
        return False

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting Instagram bot")
    
    # Initialize client with retries
    client = None
    for attempt in range(3):
        client = initialize_client()
        if client:
            break
        time.sleep(10)
    
    if not client:
        logger.error("❌ Failed to initialize client after 3 attempts")
        exit(1)
        
    # Main operation loop
    failures = 0
    try:
        while failures < 3:
            try:
                if not process_groups(client):
                    failures += 1
                    logger.warning(f"Temporary failure ({failures}/3)")
                else:
                    failures = 0
                
                cooldown = random.randint(180, 480)
                logger.info(f"⏳ Next check in {cooldown//60}m {cooldown%60}s")
                time.sleep(cooldown)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"Operation error: {str(e)}")
                failures += 1
                time.sleep(300)
        
        if failures >= 3:
            logger.error("🔴 Too many consecutive failures - restart needed")
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
    finally:
        logger.info("🏁 Bot stopped")
