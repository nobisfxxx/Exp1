import requests
import time

# Your session cookie details (use the provided cookie values)
cookies = {
    'sessionid': '4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw',
    'ds_user_id': '4815764655',
    'csrftoken': 'CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf',
    'ig_did': '01ECD94D-82CA-4A2B-B39C-21F48E6309E0',
    'mid': 'Z_-yPwABAAGrQkPVuZUxYwTPbtND',
    'rur': '"PRN\\0544815764655\\0541776346914:01f70c1c6b15d54b0fa9377fa5465397bb70f7045f7415af439dbb8586e431fced2c06fb"',
}

# Instagram API base URL
base_url = 'https://i.instagram.com/api/v1/'

# Correct User-Agent to match session device
headers = {
    'User-Agent': 'Instagram 272.0.0.18.84 Android (14/34; 480dpi; 1080x2400; Infinix; GT10Pro; GT10Pro; mt6893; en_US)',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Message to send
reply_message = "@sender Oii massage maat kar warga nobi aa jaega"

# Fetch the list of group chats
def get_active_groups(cookies, headers):
    url = f"{base_url}direct_v2/inbox/"
    response = requests.get(url, cookies=cookies, headers=headers)
    
    print(f"Fetching active groups... Status code: {response.status_code}")  # Debugging output
    
    if response.status_code == 200:
        data = response.json()
        active_groups = []
        for thread in data.get('inbox', {}).get('threads', []):
            if 'thread_id' in thread and thread['is_group'] and thread['users']:
                # Check if the bot is a participant in the group (check for the bot's user ID)
                bot_is_member = any(user['pk'] == cookies['ds_user_id'] for user in thread['users'])
                if bot_is_member:
                    active_groups.append(thread['thread_id'])
        return active_groups
    else:
        print(f"Failed to fetch active groups. Response: {response.text}")  # Debugging output
        return []

# Send message to the group
def send_reply_to_group(thread_id, message, cookies, headers):
    url = f"{base_url}direct_v2/threads/{thread_id}/broadcast/"
    data = {
        'message': message
    }
    response = requests.post(url, cookies=cookies, headers=headers, data=data)
    
    if response.status_code == 200:
        print(f"Replied to group {thread_id} successfully.")
    elif response.status_code == 404:
        print(f"Failed to send message to group {thread_id}: Group not found or bot is not in the group.")
    else:
        print(f"Failed to send message to group {thread_id}, Status code: {response.status_code}, Response: {response.text}")

# Main execution
def main():
    active_groups = get_active_groups(cookies, headers)
    
    if not active_groups:
        print("No active groups to reply to.")
        return
    
    # Loop through active groups and send a message
    for group_id in active_groups:
        send_reply_to_group(group_id, reply_message, cookies, headers)
        time.sleep(3)  # Add a delay to stay under radar (rate-limiting)

if __name__ == "__main__":
    main()
