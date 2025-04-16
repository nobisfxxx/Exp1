import requests
import json
import time

# Define the base URL and endpoint for Instagram's direct API
base_url = "https://i.instagram.com/api/v1/"

# Your cookies (replace these with your actual cookies)
cookies = {
    "sessionid": "4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw",
    "ds_user_id": "4815764655",
    "csrftoken": "CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf",
    "ig_did": "01ECD94D-82CA-4A2B-B39C-21F48E6309E0",
    "mid": "Z_-yPwABAAGrQkPVuZUxYwTPbtND",
    "rur": "\"PRN\\0544815764655\\0541776349673:01f7385137ffcf50a687c6886f6e244ab2159c7a3c25def40ac7b42d88596c926d5dd4ce\"",
    "datr": "PrL_ZxaJ-fbBXO66IDH9loFw",
    "dpr": "2.5",
    "wd": "432x850"
}

# Custom headers to match a real Instagram request (important for avoiding detection)
headers = {
    "User-Agent": "Instagram 272.0.0.18.84 Android (34/14; 480dpi; 1080x2400; INFINIX; GT10Pro; GT 10 Pro; mt6893; en_US)",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Instagram-AJAX": "1",
    "X-CSRFToken": cookies["csrftoken"]
}

# Fetch active groups
def get_active_groups(cookies, headers):
    url = f"{base_url}direct_v2/inbox/"
    response = requests.get(url, cookies=cookies, headers=headers)
    
    print(f"Fetching active groups... Status code: {response.status_code}")  # Debugging output
    if response.status_code == 200:
        data = response.json()
        active_groups = []
        for thread in data.get('inbox', {}).get('threads', []):
            if 'thread_id' in thread and thread['is_group'] and thread['users']:
                # Check if bot is a member
                bot_is_member = any(user['pk'] == cookies['ds_user_id'] for user in thread['users'])
                if bot_is_member:
                    active_groups.append(thread['thread_id'])
        return active_groups
    else:
        print(f"Failed to fetch active groups. Response: {response.text}")  # Debugging output
        return []

# Send message to a group
def send_message_to_group(thread_id, message, cookies, headers):
    url = f"{base_url}direct_v2/threads/{thread_id}/broadcast/text/"
    payload = {
        "text": message
    }
    response = requests.post(url, data=json.dumps(payload), cookies=cookies, headers=headers)
    
    if response.status_code == 200:
        print(f"Message sent to group {thread_id}")
    else:
        print(f"Failed to send message to group {thread_id}: {response.text}")

# Main function
def main():
    active_groups = get_active_groups(cookies, headers)
    
    if not active_groups:
        print("No active groups to reply to.")
        return

    # Define the reply message template
    message_template = "@{sender} Oii massage maat kar warga nobi aa jaega"
    
    for group in active_groups:
        # Get the latest thread data to reply to the most recent messages
        url = f"{base_url}direct_v2/threads/{group}/"
        response = requests.get(url, cookies=cookies, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            for thread in data.get('thread', {}).get('items', []):
                if 'user' in thread:
                    sender = thread['user']['username']
                    # Send the message to the group with the sender's username
                    message = message_template.format(sender=sender)
                    send_message_to_group(group, message, cookies, headers)
                    time.sleep(3)  # Adding a small delay to avoid rate-limiting
        else:
            print(f"Failed to fetch thread data for group {group}. Response: {response.text}")

# Run the bot
if __name__ == "__main__":
    main()
