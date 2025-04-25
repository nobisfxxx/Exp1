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

USERNAME = os.getenv("INSTA_USERNAME") or "your_username"
PASSWORD = os.getenv("INSTA_PASSWORD") or "your_password"
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Your reply here"

# ===== TYPE-SAFE API HANDLER =====
def safe_api_call(cl, func, *args, **kwargs):
    """Wrapper that verifies response types"""
    try:
        response = func(*args, **kwargs)
        
        # Special handling for known endpoints
        if func.__name__ == "direct_threads" and not isinstance(response, list):
            raise TypeError(f"Expected list, got {type(response)}")
            
        if func.__name__ == "direct_thread" and not hasattr(response, 'id'):
            raise ValueError("Invalid thread response")
            
        return response
        
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        raise

# ===== ENHANCED GROUP PROCESSING =====
def process_groups(cl):
    try:
        # Type-checked API call
        threads = safe_api_call(cl, cl.direct_threads)
        if not isinstance(threads, list):
            logger.error("Invalid threads response")
            return False

        groups = []
        for t in threads:
            if hasattr(t, 'users') and isinstance(t.users, list) and len(t.users) > 1:
                groups.append(t)
                
        if not groups:
            logger.info("No active groups found")
            return False

        for group in groups:
            try:
                # Verify group object structure
                if not hasattr(group, 'id'):
                    continue
                    
                # Safe message retrieval
                messages = safe_api_call(cl, cl.direct_messages, 
                                      thread_id=group.id, amount=3)
                if not isinstance(messages, list):
                    continue

                if not messages:
                    continue

                # Validate message structure
                last_msg = messages[-1]
                if not hasattr(last_msg, 'user_id'):
                    continue
                    
                if last_msg.user_id == cl.user_id:
                    continue

                # Safe user info retrieval
                user = safe_api_call(cl, cl.user_info, last_msg.user_id)
                if not hasattr(user, 'username'):
                    continue

                # Send with human-like delay
                reply_text = REPLY_TEMPLATE.format(username=user.username)
                time.sleep(random.uniform(5.0, 10.0))
                
                send_result = safe_api_call(cl, cl.direct_send,
                                         text=reply_text, 
                                         thread_ids=[group.id])
                if send_result:
                    logger.info(f"Replied to @{user.username}")
                else:
                    logger.warning("Send returned False")
                    
            except Exception as e:
                logger.error(f"Message processing error: {str(e)}")
                time.sleep(30)
            
            time.sleep(random.randint(10, 20))
        
        return True
        
    except Exception as e:
        logger.error(f"Group processing failed: {str(e)}")
        return False

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting type-safe Instagram bot")
    
    # Initialize client (from previous examples)
    cl = Client()
    try:
        cl.load_settings(SESSION_FILE)
        if not cl.login(USERNAME, PASSWORD):
            raise Exception("Login failed")
            
        # Main loop
        failures = 0
        while failures < 3:
            try:
                if not process_groups(cl):
                    failures += 1
                    logger.warning(f"Temporary failure ({failures}/3)")
                    time.sleep(60)
                else:
                    failures = 0
                    time.sleep(random.randint(120, 300))
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop error: {str(e)}")
                failures += 1
                time.sleep(300)
                
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
    finally:
        logger.info("🏁 Bot stopped")
