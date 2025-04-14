import json
import time
from cy_device_spoofing import optimize_message_check  # Import Cython function

# --- CONFIG ---
DEFAULT_REPLY_MESSAGE = "oii massage maat kar warna nob kke haters ki maa shod ke feekkk dunga"
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work weelll?.. If not make changes to the script.. till then boii boii boss"
STOP_COMMAND = "stop the bot on this gc"
RESUME_COMMAND = "resume the bot on this gc"
PASSWORD_REQUEST = "Okay, boss. What's the password?"
VALID_PASSWORD = "17092004"
STOP_FILE = "stopped_threads.json"
REPLY_TRACK_FILE = "replied_messages.json"

# Initialize the session
# (Assuming you use requests or an API client)
from requests import Session

session = Session()

# Load cookies (same as before)
def load_cookies():
    if os.path.exists(SESSION_COOKIES_FILE):
        with open(SESSION_COOKIES_FILE, "r") as f:
            return json.load(f)
    return {}

# Handle incoming messages
def auto_reply_all_groups():
    while True:
        try:
            messages = get_new_messages()  # Get new messages (simulate API)

            for msg in messages:
                thread_id = msg['thread_id']
                message_id = msg['message_id']
                text = msg['text'].lower()
                username = msg['username']

                if message_id == last_replied.get(thread_id):
                    continue  # Skip already replied messages

                if thread_id in stopped_threads:
                    continue  # Skip stopped threads

                # Using the Cython function to check the command in the message
                command = optimize_message_check(text)

                if command == "stop":
                    handle_stop(thread_id)
                    continue
                elif command == "resume":
                    handle_resume(thread_id)
                    continue
                elif TRIGGER_PHRASE in text:
                    send_message(thread_id, TRIGGER_RESPONSE)
                    print(f"Triggered response to @{username}")
                else:
                    reply = f"@{username} {DEFAULT_REPLY_MESSAGE}"
                    send_message(thread_id, reply)
                    print(f"Roasted @{username}")

                last_replied[thread_id] = message_id
                save_last_replied()

            time.sleep(2)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(5)

# Send message (simulated)
def send_message(thread_id, message):
    print(f"Sending message to {thread_id}: {message}")

# Simulated message fetch
def get_new_messages():
    return [
        {"thread_id": "12345", "message_id": "1", "text": "hoi nobi is here", "username": "user1"},
        {"thread_id": "12345", "message_id": "2", "text": "what's up?", "username": "user2"}
    ]

if __name__ == "__main__":
    auto_reply_all_groups()
