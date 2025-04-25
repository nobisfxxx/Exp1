from instagrapi import Client
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

# ===== ENHANCED GROUP VALIDATION =====
def get_valid_groups(cl):
    """Safely fetch groups and filter invalid/kicked ones"""
    try:
        all_threads = cl.direct_threads()
        valid_groups = []
        
        for thread in all_threads:
            # Skip invalid/None objects
            if not thread:
                continue
                
            # Check if bot is still in the group
            try:
                users = getattr(thread, 'users', [])
                if len(users) > 1 and cl.user_id in [u.pk for u in users]:
                    valid_groups.append(thread)
                else:
                    logger.warning(f"Left/kicked from group: {thread.id}")
            except Exception as e:
                logger.error(f"Group validation failed: {str(e)}")
        
        return valid_groups
    except Exception as e:
        logger.error(f"Group fetch failed: {str(e)}")
        return []

# ===== ERROR-RESISTANT PROCESSING =====
def process_groups(cl):
    """Handle groups with removed/kicked scenarios"""
    groups = get_valid_groups(cl)
    
    if not groups:
        logger.info("No active groups - bot not added to any groups")
        return
        
    for group in groups:
        try:
            # Double-check group validity
            if not group or not group.id:
                continue
                
            logger.info(f"Processing group: {group.id[:6]}...")
            
            # Get messages safely
            messages = cl.direct_messages(thread_id=group.id, amount=1)
            if not messages:
                continue
                
            last_msg = messages[-1]
            if last_msg.user_id == cl.user_id:
                continue
                
            # Send reply
            user = cl.user_info(last_msg.user_id)
            cl.direct_send(
                REPLY_TEMPLATE.format(username=user.username),
                thread_ids=[group.id]
            )
            logger.info(f"Replied to @{user.username}")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Group {group.id[:6]}... failed: {str(e)}")
            if "not in group" in str(e).lower():
                logger.info("Bot removed from group - updating session")
                cl.direct_threads(force_refresh=True)  # Clear cache

# ===== MAIN CODE ===== 
# [Keep the login/session management from previous versions]
# [Add this to your existing login flow]
