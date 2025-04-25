from instagrapi import Client
import time

# Login to Instagram
def login(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        print("✅ Login successful!")
        return cl
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

# Auto-reply in group chats
def auto_reply_in_groups(cl, reply_message):
    while True:
        try:
            # Get active group chats
            threads = cl.direct_threads()
            for thread in threads:
                if len(thread.users) > 1:  # Check if it's a group chat
                    last_msg = thread.messages[-1]
                    sender_username = last_msg.user.username
                    
                    # Custom reply with mention
                    custom_reply = f"@{sender_username} {reply_message}"
                    
                    # Send reply
                    cl.direct_send(custom_reply, thread_id=thread.id)
                    print(f"📩 Replied to @{sender_username} in group chat.")
                    
                    time.sleep(2)  # 2-second delay (avoid rate limits)
        except Exception as e:
            print(f"⚠ Error: {e}")
            time.sleep(60)  # Wait 1 min if error occurs

if __name__ == "__main__":
    # ⚠ Replace with your credentials (use environment variables in Railway!)
    USERNAME = "your_instagram_username"
    PASSWORD = "your_instagram_password"
    REPLY_MSG = "Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

    # Start the bot
    client = login(USERNAME, PASSWORD)
    if client:
        auto_reply_in_groups(client, REPLY_MSG)
