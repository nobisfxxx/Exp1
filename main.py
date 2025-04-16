import time
import requests
import json
from datetime import datetime, timezone

# ---- CONFIG ----
DELAY = 3
REPLY_TEXT = "@{username} Oii massage maat kar warga nobi aa jaega"

# ---- LOAD COOKIES ----
cookies = {
    "ds_user_id": "4815764655",
    "csrftoken": "CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf",
    "sessionid": "4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw"
}

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 14; Infinix X6739) AppleWebKit/537.36 Chrome/122.0.0.0 Mobile Safari/537.36 Instagram 272.0.0.18.84 Android",
    "x-ig-app-id": "936619743392459",
    "x-csrftoken": cookies["csrftoken"]
}

session = requests.Session()
session.cookies.update(cookies)
session.headers.update(headers)


def get_group_threads():
    url = "https://i.instagram.com/api/v1/direct_v2/inbox/?persistentBadging=true&limit=20"
    res = session.get(url)
    threads = res.json().get("inbox", {}).get("threads", [])
    return threads


def is_recent(timestamp_str):
    try:
        ts = datetime.fromtimestamp(timestamp_str, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - ts).total_seconds() <= 60
    except:
        return False


def reply_to_message(thread_id, item_id, username):
    text = REPLY_TEXT.format(username=username)
    url = f"https://i.instagram.com/api/v1/direct_v2/threads/{thread_id}/items/{item_id}/reply/"
    data = {
        "action": "send_item",
        "text": text
    }
    res = session.post(url, data=data)
    print(f"Replied to @{username} in {thread_id} | Status: {res.status_code}")


def start_bot():
    print("Bot started...")

    while True:
        try:
            threads = get_group_threads()
            for thread in threads:
                if not thread.get("is_group"):
                    continue

                if not thread.get("viewer_joined"):
                    print(f"Skipped {thread.get('thread_id')} (you’re not in this group)")
                    continue

                last_msg = thread.get("items", [])[0] if thread.get("items") else None
                if not last_msg or not is_recent(last_msg.get("timestamp")[:10]):
                    continue

                user = last_msg.get("user_id") or thread.get("users", [{}])[0].get("pk")
                username = last_msg.get("user", {}).get("username", "user")

                reply_to_message(thread["thread_id"], last_msg["item_id"], username)
                time.sleep(DELAY)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    start_bot()
