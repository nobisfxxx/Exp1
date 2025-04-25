from instagrapi import Client
import time
import os

def load_or_login(username, password, session_file="session.json"):
    cl = Client()
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            print("✅ Session loaded successfully!")
            return cl
        except Exception as e:
            print(f"❌ Session expired. Logging in fresh: {e}")
            os.remove(session_file)
    
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        print("✅ New login & session saved!")
        return cl
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def auto_reply_in_groups(cl, reply_message):
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if len(thread.users) > 1:  # Group chat
                    last_msg = thread.messages[-1]
                    # NEW: Proper way to get sender info
                    user_id = last_msg.user_id
                    user_info = cl.user_info(user_id)
                    sender_username = user_info.username
                    
                    custom_reply = f"@{sender_username} {reply_message}"
                    cl.direct_send(custom_reply, thread_id=thread.id)
                    print(f"📩 Replied to @{sender_username}")
                    time.sleep(2)
        except Exception as e:
            print(f"⚠ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    USERNAME = "INSTA_USERNAME"  # Or use os.getenv()
    PASSWORD = "INSTA_PASSWORD"
    REPLY_MSG = "Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

    client = load_or_login(USERNAME, PASSWORD)
    if client:
        auto_reply_in_groups(client, REPLY_MSG)
