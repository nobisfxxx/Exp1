from instagrapi import Client
import os
import time

# Load session or login fresh
def load_or_login(username, password, session_file="session.json"):
    cl = Client()
    
    # Try loading session
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, password)  # Will use session if valid
            print("✅ Session loaded successfully!")
            return cl
        except Exception as e:
            print(f"❌ Session expired/invalid. Logging in fresh: {e}")
            os.remove(session_file)  # Delete invalid session
    
    # Fresh login & save session
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)  # Save session
        print("✅ New login & session saved!")
        return cl
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

# Auto-reply logic (same as before)
def auto_reply_in_groups(cl, reply_message):
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if len(thread.users) > 1:  # Group chat
                    last_msg = thread.messages[-1]
                    sender_username = last_msg.user.username
                    custom_reply = f"@{sender_username} {reply_message}"
                    cl.direct_send(custom_reply, thread_id=thread.id)
                    print(f"📩 Replied to @{sender_username}")
                    time.sleep(2)  # Delay
        except Exception as e:
            print(f"⚠ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # ⚠ Use environment variables (Railway secrets)
    USERNAME = os.getenv("INSTA_USERNAME")  # Set in Railway dashboard
    PASSWORD = os.getenv("INSTA_PASSWORD")
    REPLY_MSG = "Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

    client = load_or_login(USERNAME, PASSWORD)
    if client:
        auto_reply_in_groups(client, REPLY_MSG)
