from instapy import InstaPy
import time
import os

# Environment variables (could be set in Railway for production)
session_id = os.getenv("SESSION_ID")
csrf_token = os.getenv("CSRFTOKEN")
user_id = os.getenv("DS_USER_ID")

# Initialize InstaPy session
session = InstaPy(username=session_id, password='dummy', headless_browser=True)

# Setting cookies for login
session.set_session_cookies({
    'sessionid': session_id,
    'csrftoken': csrf_token,
    'ds_user_id': user_id
})

# Start InstaPy session
session.login()

# Function to handle replying to the latest message in group chats
def reply_to_latest_message():
    try:
        # Get the most recent messages from your direct threads
        threads = session.get_direct_threads()

        if not threads:
            print("No threads found.")
            return

        # Get the most recent message in the first thread
        latest_message = threads[0]['messages'][0]

        sender = latest_message['user']['username']
        message_content = latest_message['text']

        # Reply only if the message is within the last 60 seconds
        if time.time() - latest_message['timestamp'] < 60:
            # Craft the reply (e.g., a roast message)
            reply_message = f"@{sender} Oii massage maat kar warga nobi aa jaega"
            print(f"Replying to {sender}: {reply_message}")

            # Send the reply to the thread
            session.send_direct_message([reply_message], threads[0]['thread_id'])
        else:
            print("No recent messages to reply to.")
    except Exception as e:
        print(f"Error while replying: {e}")

# Main loop to keep the bot running
while True:
    reply_to_latest_message()
    time.sleep(3)  # Delay between checking for new messages (to avoid spamming)
