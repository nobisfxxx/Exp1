from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired
import os
import json
import time
import random
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
SESSION_FILE = "session.json"
REPLY_MSG = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
PROXY = os.getenv("INSTA_PROXY")  # http://user:pass@host:port

# ===== DEVICE FINGERPRINT =====
def generate_device():
    """Create randomized device fingerprint"""
    return {
        "app_version": "287.0.0.19.301",
        "android_version": random.randint(28, 33),
        "android_release": f"{random.randint(9, 13)}.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": random.choice(["Google", "Samsung", "OnePlus"]),
        "device": random.choice(["Pixel 7", "Galaxy S23", "ONEPLUS A6013"]),
        "model": random.choice(["QP1A.190711.020", "SM-S901U", "ONEPLUS A6013"]),
        "cpu": random.choice(["qcom", "exynos"]),
        "phone_id": Client().generate_uuid(),
        "uuid": Client().generate_uuid()
    }

# ===== SESSION MANAGER =====
def create_session():
    """Generate fresh session with device fingerprint"""
    return {
        "cookies": [],
        "device_settings": generate_device(),
        "user_agent": "Instagram 287.0.0.19.301 Android",
        "last_login": int(time.time())
    }

def reset_session():
    """Completely reset session file"""
    with open(SESSION_FILE, 'w') as f:
        json.dump(create_session(), f)
    logger.info("Nuclear session reset complete")

# ===== CHALLENGE HANDLER =====
def handle_challenge(client, challenge_url):
    """Automate challenge resolution"""
    logger.warning(f"Attempting to solve challenge: {challenge_url}")
    try:
        # Try email verification
        if "challenge" in challenge_url:
            client.challenge_resolve(challenge_url)
            logger.info("Challenge auto-solved via email")
            return True
    except Exception as e:
        logger.error(f"Challenge failed: {str(e)}")
        return False

# ===== LOGIN SYSTEM =====
def login(client):
    """Military-grade login with challenge bypass"""
    for attempt in range(3):
        try:
            # Fresh session every attempt
            reset_session()
            client.load_settings(SESSION_FILE)
            
            if PROXY:
                client.set_proxy(PROXY)
                logger.info(f"Using proxy: {PROXY.split('@')[-1]}")

            # Critical headers
            client.set_headers({
                "X-IG-App-Locale": "en_US",
                "X-IG-Device-Locale": "en_US",
                "X-IG-Mapped-Locale": "en_US",
                "X-Pigeon-Session-Id": client.generate_uuid(),
                "X-IG-Connection-Speed": f"{random.randint(3, 20)}Mbps",
            })

            # Human-like delay
            time.sleep(random.randint(5, 15))
            
            if not client.login(USERNAME, PASSWORD):
                raise Exception("Login returned False")

            # Verify session
            client.get_timeline_feed()
            client.dump_settings(SESSION_FILE)
            logger.info("✅ Login conquest successful")
            return True
            
        except ChallengeRequired as e:
            if not handle_challenge(client, str(e)):
                logger.error("Manual verification required in Instagram app!")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Attempt {attempt+1}/3 failed: {str(e)}")
            time.sleep(attempt * 30)
    
    logger.critical("❌ Maximum login attempts reached")
    sys.exit(1)

# ===== GROUP SYSTEM =====
def get_active_groups(client):
    """Safe group detection with error handling"""
    try:
        threads = client.direct_threads()
        return [t for t in threads if is_valid_group(client, t)]
    except Exception as e:
        logger.error(f"Group scan failed: {str(e)}")
        return []

def is_valid_group(client, thread):
    """Validate group structure and membership"""
    try:
        return (
            hasattr(thread, 'users') and
            len(thread.users) > 1 and
            client.user_id in [u.pk for u in thread.users]
        )
    except:
        return False

def reply_in_group(client, group):
    """Send reply with version-safe method"""
    try:
        messages = client.direct_messages(thread_id=group.id, amount=1)
        if not messages or messages[-1].user_id == client.user_id:
            return

        user = client.user_info(messages[-1].user_id)
        client.direct_send(
            text=REPLY_MSG.format(username=user.username),
            thread_ids=[group.id]
        )
        logger.info(f"📩 Replied to @{user.username}")
        time.sleep(random.uniform(2, 5))
        
    except Exception as e:
        logger.error(f"Reply failed: {str(e)}")
        if "not in group" in str(e).lower():
            client.direct_threads()  # Refresh cache

# ===== MAIN BOT =====
def main():
    logger.info("🚀 Starting Instagram Sentinel v3.0")
    client = Client()
    client.delay_range = [3, 7]

    # Phase 1: Login
    if not login(client):
        return

    # Phase 2: Group Operations
    logger.info("🔍 Beginning group surveillance")
    while True:
        try:
            groups = get_active_groups(client)
            logger.info(f"🎯 Active groups: {len(groups)}")
            
            for group in groups:
                reply_in_group(client, group)
            
            # Randomized sleep (45-120s)
            sleep_time = random.randint(45, 120)
            logger.info(f"💤 Sleeping for {sleep_time}s")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown")
            break
        except Exception as e:
            logger.error(f"System failure: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
