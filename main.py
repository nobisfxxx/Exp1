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
PROXY = os.getenv("INSTA_PROXY")  # Optional: http://user:pass@host:port

# ===== NUCLEAR SESSION HANDLER =====
class SessionWeapon:
    @staticmethod
    def create_warhead():
        """Generate new device fingerprint"""
        return {
            "app_version": "250.0.0.16.117",
            "android_version": random.randint(25, 30),
            "android_release": f"{random.randint(9, 13)}.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": random.choice(["Google", "Xiaomi", "Samsung"]),
            "device": random.choice(["Pixel 7 Pro", "Mi 11", "Galaxy S23"]),
            "phone_id": Client().generate_uuid(),
            "uuid": Client().generate_uuid(),
        }

    @classmethod
    def nuke_session(cls):
        """Complete session reset"""
        session_data = {
            "cookies": [],
            "device_settings": cls.create_warhead(),
            "user_agent": "Instagram 250.0.0.16.117 Android",
            "last_login": int(time.time())
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f)
        logger.info("Nuclear session detonation complete")

# ===== WARRIOR LOGIN SYSTEM =====
class LoginCommander:
    def __init__(self):
        self.cl = Client()
        self.attempt = 0
        self.max_attempts = 5

    def conquer_login(self):
        """Military-grade login sequence"""
        while self.attempt < self.max_attempts:
            try:
                SessionWeapon.nuke_session()
                self.cl.load_settings(SESSION_FILE)
                
                if PROXY:
                    self.cl.set_proxy(PROXY)
                    logger.info(f"Activated proxy: {PROXY.split('@')[-1]}")
                
                self._rotate_fingerprint()
                logger.info(f"Assault attempt {self.attempt+1}/{self.max_attempts}")
                
                if self.cl.login(USERNAME, PASSWORD):
                    self._validate_conquest()
                    return True
                    
            except ChallengeRequired:
                logger.error("MANUAL VERIFICATION REQUIRED! Check Instagram app")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Assault failed: {str(e)}")
                self.attempt += 1
                time.sleep(self.attempt * 15)
                
        logger.critical("Login fortress impenetrable - Mission aborted")
        sys.exit(1)

    def _rotate_fingerprint(self):
        """Change device fingerprint"""
        new_device = SessionWeapon.create_warhead()
        self.cl.set_device(new_device)
        logger.info(f"New fingerprint: {new_device['device']}")

    def _validate_conquest(self):
        """Verify login success"""
        try:
            self.cl.get_timeline_feed()
            self.cl.dump_settings(SESSION_FILE)
            logger.info("Territory secured - Login validated")
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise

# ===== GROUP TROOPER =====
class GroupBattalion:
    def __init__(self, client):
        self.cl = client
        self.replied_ids = set()

    def recon_groups(self):
        """Advanced group reconnaissance"""
        try:
            threads = self.cl.direct_threads(force_refresh=True)
            return [t for t in threads if self._is_hostile_territory(t)]
        except Exception as e:
            logger.error(f"Recon failed: {str(e)}")
            return []

    def _is_hostile_territory(self, thread):
        """Identify valid groups"""
        try:
            return (
                thread and
                len(getattr(thread, 'users', [])) > 1 and
                self.cl.user_id in [u.pk for u in thread.users]
            )
        except Exception as e:
            logger.error(f"Target analysis failed: {str(e)}")
            return False

    def engage_target(self, group):
        """Execute message strike"""
        try:
            messages = self.cl.direct_messages(thread_id=group.id, amount=1)
            if not messages:
                return

            last_msg = messages[-1]
            if last_msg.id in self.replied_ids:
                return

            user = self.cl.user_info(last_msg.user_id)
            strike_msg = REPLY_MSG.format(username=user.username)
            
            self.cl.direct_send(
                text=strike_msg,
                thread_ids=[group.id]
            )
            self.replied_ids.add(last_msg.id)
            logger.info(f"Target engaged: @{user.username}")
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            logger.error(f"Strike failed: {str(e)}")
            if "not in group" in str(e).lower():
                logger.warning("Evacuating compromised territory")
                self.cl.direct_threads(force_refresh=True)

# ===== MISSION CONTROL =====
def main_operation():
    logger.info("🚀 Initiating Operation Instagram Dominance")
    
    # Phase 1: Login Conquest
    commander = LoginCommander()
    if not commander.conquer_login():
        return
    
    # Phase 2: Group Warfare
    battalion = GroupBattalion(commander.cl)
    logger.info("🔥 Combat systems engaged - Scanning battlefields")
    
    while True:
        try:
            groups = battalion.recon_groups()
            logger.info(f"🎯 Targets acquired: {len(groups)}")
            
            for group in groups:
                battalion.engage_target(group)
                
            # Strategic retreat interval
            sleep_duration = random.randint(45, 120)
            logger.info(f"🛌 Tactical pause: {sleep_duration}s")
            time.sleep(sleep_duration)
            
        except KeyboardInterrupt:
            logger.info("🕊️ Peace treaty signed - Shutting down")
            break
        except Exception as e:
            logger.error(f"Battlefield chaos: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main_operation()
