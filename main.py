import requests
import time
import json
from datetime import datetime, timezone

# === CONFIG ===
REPLY_DELAY = 3
REPLY_MESSAGE = "@{username} Oii massage maat kar warga nobi aa jaega"

# === COOKIES FROM EXPORT ===
COOKIES = {
    "ds_user_id": "4815764655",
    "sessionid": "4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw",
    "csrftoken": "CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf",
    "mid": "Z_-yPwABAAGrQkPVuZUxYwTPbtND",
    "ig_did": "01ECD94D-82CA-4A2B-B39C-21F48E6309E0",
    "rur": "PRN",
}

HEADERS = {
    "User-Agent": "Instagram 267.0.0.19.107 Android",
    "X-CSRFToken": COOKIES["csrftoken"],
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.cookies.update(COOKIES)

def get_group_threads():
    url = "https://i.instagram.com/api/v1/direct_v2/inbox/"
    try:
        res = SESSION.get(url)
        if res.status_code != 200:
            print(f"Failed to fetch inbox: {res.status_code}")
            return []

        data = res.json()
        return data.get("inbox", {}).get("threads", [])
    except Exception as e:
        print(f"[!] Inbox fetch error: {e}")
        return []

def is_recent_message(message_timestamp):
    try:
        message_time = datetime.fromtimestamp(message_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - message_time).total_seconds() <= 60
    except Exception as e:
        print(f"[!] Timestamp error: {e}")
        return False

def send_reply(thread_id, item_id, username):
    try:
        message = REPLY_MESSAGE.format(username=username)
        payload = {
            "action": "send_item",
            "client_context": str(int(time.time() * 1000)),
            "item_type": "text",
            "text": message,
        }

        url = f"https://i.instagram.com/api/v1/direct_v2/threads/{thread_id}/items/"
        res = SESSION.post(url, data=payload)
        if res.status_code == 200:
            print(f"Replied to @{username} in {thread_id}")
        else:
            print(f"[!] Failed to reply to {thread_id}: {res.status_code}")
    except Exception as e:
        print(f"[!] Reply error: {e}")

def main():
    while True:
        threads = get_group_threads()

        for thread in threads:
            thread_id = thread.get("thread_id")
            users = thread.get("users", [])
            last_permanent_item = thread.get("last_permanent_item", {})
            last_message_type = last_permanent_item.get("item_type")

            # Skip non-text messages
            if last_message_type != "text":
                continue

            timestamp = int(last_permanent_item.get("timestamp", "0")) // 1000000
            if not is_recent_message(timestamp):
                continue

            # Check if still in the group
            if not thread.get("is_group") or not thread.get("viewer_is_active"):
                print(f"Skipped {thread_id} (you’re not in this group)")
                continue

            # Get sender username
            sender = last_permanent_item.get("user_id")
            sender_username = next((u["username"] for u in users if u["pk"] == sender), "user")

            item_id = last_permanent_item.get("item_id")
            if thread_id and item_id and sender_username:
                send_reply(thread_id, item_id, sender_username)
                time.sleep(REPLY_DELAY)

        time.sleep(3)

if __name__ == "__main__":
    main()
