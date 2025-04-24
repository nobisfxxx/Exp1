import time
import requests

# Your long-term Instagram access token
ACCESS_TOKEN = 'IGAAYMtqnh68pBZAFAxSlNkbHlCVnNxMTR2eWxNbVBMd2RUVC1jaWNPMmVlTW95WER1MkUtRDRudUxuMUxwcFJXRnVIblVxYjVYMzRfWVhFNk44N3hpdVp5cHVlMkpYdmc2aEJBLXg1SVo5dy1HWlRZAa0ZALSHZAFZAUMta3RuNUdyYwZDZD'

# Instagram Graph API URL for user messages
GRAPH_API_URL = 'https://graph.instagram.com'

# Reply message template
REPLY_MESSAGE = "@sender Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# Delay between replies (3 seconds)
REPLY_DELAY = 3

# Function to send reply to group messages
def send_reply(thread_id, sender_username):
    message = REPLY_MESSAGE.replace('@sender', f"@{sender_username}")
    
    # Send reply via Instagram Graph API
    url = f"{GRAPH_API_URL}/{thread_id}/messages"
    payload = {
        'message': message,
        'access_token': ACCESS_TOKEN
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Replied to {sender_username} in thread {thread_id}")
    else:
        print(f"Error replying to {sender_username} in thread {thread_id}: {response.json()}")

# Function to check if bot is kicked from the group chat
def is_kicked(thread_id):
    url = f"{GRAPH_API_URL}/{thread_id}?fields=participants&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        participants = data.get('participants', [])
        # Check if the bot is part of the participants
        for participant in participants:
            if participant.get('username') == 'lynx ka balatkari baap hu':  # Replace with your bot's username
                return False  # Not kicked
        return True  # Kicked
    else:
        print(f"Error checking if kicked from {thread_id}: {response.json()}")
        return False

# Function to fetch new group threads and reply
def auto_reply_to_groups():
    # Get all direct threads (group chats)
    url = f"{GRAPH_API_URL}/me/messages?fields=threads&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        threads = response.json().get('data', [])  # 'data' contains the threads array
        for thread in threads:
            thread_id = thread['id']
            sender_username = thread['messages'][0]['sender']['username']
            
            # Skip if bot is kicked
            if is_kicked(thread_id):
                print(f"Skipping thread {thread_id}: Bot kicked")
                continue
            
            # Send reply after a delay
            send_reply(thread_id, sender_username)
            time.sleep(REPLY_DELAY)  # Wait for 3 seconds before replying again
    else:
        print(f"Error fetching threads: {response.json()}")

if __name__ == '__main__':
    while True:
        auto_reply_to_groups()
        time.sleep(10)  # Check every 10 seconds for new threads
