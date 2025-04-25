from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import logging
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

# ===== SESSION MANAGEMENT =====
def validate_session():
    """Ensure session file structure is valid"""
    required_keys = ["cookies", "last_login", "device_settings", "user_agent"]
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            if not all(key in data for key in required_keys):
                raise ValueError("Invalid session structure")
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        logger.warning("Resetting corrupted session file")
        reset_session_file()

def reset_session_file():
    """Create fresh valid session structure"""
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": {
                "app_version": "219.0.0.12.117",
                "android_version": 25,
                "android_release": "7.1.2"
            },
            "user_agent": "Instagram 219.0.0.12.117 Android"
        }, f)

# ===== CORE FUNCTIONALITY =====
def login_client():
    """Robust login with session recovery"""
    validate_session()
    
    cl = Client()
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        
        # Verify session activity
        cl.get_timeline_feed()
        logger.info("✅ Login successful")
        return cl
    except (LoginRequired, AttributeError):
        logger.warning("Session expired - fresh login")
        return fresh_login()
    except ChallengeRequired:
        logger.error("🔐 Complete verification in Instagram app!")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
    return None

def fresh_login():
    """Force new login and session creation"""
    cl = Client()
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        return cl
    except Exception as e:
        logger.error(f"Fresh login failed: {str(e)}")
        return None

def debug_group_info(cl):
    """Log detailed group chat information"""
    try:
        groups = cl.direct_threads(thread_types=["group"])
        logger.info(f"📦 Found {len(groups)} group chats")
        
        for idx, group in enumerate(groups):
            logger.info(f"""
            === GROUP {idx+1} ===
            ID: {group.id}
            Title: {group.title}
            Users: {[u.username for u in group.users]}
            Last Activity: {datetime.fromtimestamp(group.last_activity//1000)}
            Message Count: {len(group.messages)}
            ======================
            """)
            
            # Test message sending capability
            try:
                cl.direct_send("🔧 Bot debug message", thread_id=group.id)
                logger.info("✅ Successfully sent test message")
            except Exception as e:
                logger.error(f"❌ Failed to send test message: {str(e)}")
                
        return groups
    except Exception as e:
        logger.error(f"Group debug failed: {str(e)}")
        return []

def process_groups(cl):
    """Main group processing logic with detailed logging"""
    logger.info("🔍 Starting group scan")
    
    groups = debug_group_info(cl)
    if not groups:
        logger.warning("No groups found! Ensure account is added to groups")
        return

    for group in groups:
        try:
            logger.info(f"🔄 Processing group: {group.id}")
            
            messages = cl.direct_messages(thread_id=group.id, amount=5)
            logger.info(f"📩 Found {len(messages)} messages in group")
            
            if not messages:
                logger.info("💤 No messages to process")
                continue
                
            last_msg = messages[-1]
            logger.info(f"""
            ⚡ LAST MESSAGE DETAILS
            ID: {last_msg.id}
            From: {last_msg.user_id}
            Text: {last_msg.text[:50]}...
            Timestamp: {datetime.fromtimestamp(last_msg.timestamp//1000)}
            """)
            
            if last_msg.user_id == cl.user_id:
                logger.info("🤖 Skipping own message")
                continue
                
            user = cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            
            logger.info(f"✉️ Attempting reply to @{user.username}")
            cl.direct_send(reply_text, thread_id=group.id)
            logger.info("✅ Reply sent successfully")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Group processing error: {str(e)}")
            time.sleep(5)

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Initializing bot")
    
    client = None
    for attempt in range(3):
        client = login_client()
        if client:
            break
        logger.warning(f"Retrying login ({attempt+1}/3)")
        time.sleep(10)
    
    if not client:
        logger.error("❌ Permanent login failure")
        exit(1)
        
    # Verify account status
    try:
        user_info = client.user_info(client.user_id)
        logger.info(f"""
        🔑 ACCOUNT STATUS
        Username: {user_info.username}
        Followers: {user_info.follower_count}
        Following: {user_info.following_count}
        Private: {user_info.is_private}
        """)
    except Exception as e:
        logger.error(f"Account check failed: {str(e)}")
    
    # Main loop
    while True:
        process_groups(client)
        logger.info("⏳ Next check in 30 seconds...")
        time.sleep(30)
