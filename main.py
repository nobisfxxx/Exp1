import os
import time
from instagrapi import Client

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
message = os.getenv("SPAM_MESSAGE", "hello")
delay = int(os.getenv("SPAM_DELAY", 3))

cl = Client()

try:
    cl.login(username, password)
    print("[+] Logged in.")
except Exception as e:
    print(f"[!] Login failed: {e}")
    exit()

def get_group_threads():
    threads = cl.direct_threads()
    group_threads = []
    for thread in threads:
        if len(thread.users) > 1:
            group_threads.append(thread.id)
    return group_threads

# Get all group thread IDs
group_ids = get_group_threads()
print(f"[+] Found {len(group_ids)} group chats.")

while True:
    for thread_id in group_ids:
        try:
            cl.direct_send(message, [], thread_ids=[thread_id])
            print(f"[+] Sent to {thread_id}")
        except Exception as e:
            print(f"[!] Failed to send to {thread_id}: {e}")
    time.sleep(delay)
