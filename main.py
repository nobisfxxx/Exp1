from instagrapi import Client
import os
import json
import time
import logging
import sys
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
SESSION_FILE = "/app/session.json"
REPLY_MSG = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
PROXY = os.getenv("INSTA_PROXY")  # Format: http://user:pass@host:port

# ===== SESSION MANAGER =====
def create_session():
    """Generate fresh session with device fingerprint"""
    return {
        "cookies": [],
        "device_settings": {
            "app_version": "250.0.0.16.117",
            "android_version": random.randint(25, 30),
            "android_release": f"{random.randint(9, 13)}.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": random.choice(["Google", "Xiaomi", "Samsung"]),
            "device": random.choice(["Pixel 7", "Mi 11", "Galaxy S22"]),
            "phone_id": Client().generate_uuid(),
            "uuid": Client().generate_uuid()
        },
        "user_agent": "Instagram 250.0.0.16.117 Android"
    }

def reset_session():
    """Completely wipe and rebuild session file"""
    with open(SESSION_FILE, 'w') as f:
        json.dump(create_session(), f)
    logger.info("Session nuclear reset complete")

# ===== LOGIN SYSTEM =====
def login():
    """Bulletproof login with 5 retries"""
    cl = Client()
    cl.delay_range = [3, 7]
    
    for attempt in range(5):
        try:
            # Fresh session every attempt
            reset_session()
            cl.load_settings(SESSION_FILE)
            
            if PROXY:
                cl.set_proxy(PROXY)
                logger.info(f"Using proxy: {PROXY.split('@')[-1]}")

            if cl.login(USERNAME, PASSWORD):
                # Verify session works
                cl.get_timeline_feed()
                cl.dump_settings(SESSION_FILE)
                logger.info("✅ Login conquest successful")
                return cl
                
        except ChallengeRequired:
            logger.error("Manual verification needed! Check Instagram app")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Attempt {attempt+1}/5 failed: {str(e)}")
            time.sleep(attempt * 15)
    
    logger.critical("❌ All login attempts failed")
    sys.exit(1)

# ===== GROUP HANDLER =====
def get_groups(cl):
    """Safe group detection without force_refresh"""
    try:
        threads = cl.direct_threads()
        return [t for t in threads if is_valid_group(cl, t)]
    except Exception as e:
        logger.error(f"Group scan failed: {str(e)}")
        return []

def is_valid_group(cl, thread):
    """Check if thread is an active group"""
    try:
        return (
            hasattr(thread, 'users') and
            len(thread.users) > 1 and
            cl.user_id in [u.pk for u in thread.users]
        )
    except:
        return False

def reply_to_group(cl, group):
    """Send reply with safety checks"""
    try:
        messages = cl.direct_messages(thread_id=group.id, amount=1)
        if not messages or messages[-1].user_id == cl.user_id:
            return

        user = cl.user_info(messages[-1].user_id)
        cl.direct_send(
            text=REPLY_MSG.format(username=user.username),
            thread_ids=[group.id]
        )
        logger.info(f"📩 Replied to @{user.username}")
        time.sleep(random.uniform(2, 5))
        
    except Exception as e:
        logger.error(f"Reply failed: {str(e)}")
        if "not in group" in str(e).lower():
            cl.direct_threads()  # Refresh cache

# ===== MAIN BOT =====
def run_bot():
    """Main execution flow"""
    logger.info("🚀 Starting Instagram Sentinel")
    
    # Phase 1: Login
    client = login()
    
    # Phase 2: Group Monitoring
    logger.info("🔍 Beginning group surveillance")
    while True:
        try:
            groups = get_groups(client)
            logger.info(f"🎯 Active groups: {len(groups)}")
            
            for group in groups:
                reply_to_group(client, group)
            
            # Randomized sleep (45-120s)
            sleep_time = random.randint(45, 120)
            logger.info(f"💤 Sleeping for {sleep_time}s")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown initiated")
            break
        except Exception as e:
            logger.error(f"System failure: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
