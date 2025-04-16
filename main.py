import time
import random
from instagrapi import Client
from datetime import datetime, timezone, timedelta

# === SESSION COOKIE LOGIN ===
SESSION_ID = "4815764655%3ABpgYGEkoM6HMII%3A2%3AAYcFyc4OBkVLhiqNHXmQqP2N8IxvKbZmQZDTyA5jVA"

# === DEVICE SPOOFING ===
DEVICE = {
    "app_version": "272.0.0.18.84",
    "android_version": 34,
    "android_release": "14",
    "dpi": "480dpi",
    "resolution": "1080x2400",
    "manufacturer": "infinix",
    "device": "Infinix-X6739",
    "model": "Infinix X6739",
    "cpu": "mt6893"
}

# === BOT SETTINGS ===
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work well?.. If not, make changes to the script.. till then boii boii boss"
ROASTS = [
    "kya chomu message bhej diya re tu", "teri typing dekh ke keyboard bhi sharma gaya",
    "abe chup reh, tere jese toh recharge bhi expire ho jate hain", "tumse na ho payega bhai"
]
REPLY_DELAY = 3  # seconds between replies

# === Initialize Instagram Client ===
cl = Client()
cl.set_device(DEVICE)
cl.login_by_sessionid(SESSION_ID)
print("[+] Logged in via session ID.")

last_reply_time = datetime.now(timezone.utc) - timedelta(seconds=REPLY_DELAY)

# Main loop
while True:
    try:
        print("[+] Fetching threads...")
        threads = cl.direct_threads()
        print(f"[+] Retrieved {len(threads)} threads.")

        now = datetime.now(timezone.utc)

        for thread in threads:
            thread_id = thread.id

            if not thread.messages:
                print(f"[+] No messages in {thread_id}")
                continue

            for msg in thread.messages:
                if msg.timestamp is None:
                    continue

                # Adjust timestamp if it's naive
                if msg.timestamp.tzinfo is None:
                    msg.timestamp = msg.timestamp.replace(tzinfo=timezone.utc)

                time_diff = now - msg.timestamp
                if time_diff.total_seconds() > 60:
                    print(f"[+] Skipping message in {thread_id} as it is older than 60 seconds")
                    continue

                if now - last_reply_time < timedelta(seconds=REPLY_DELAY):
                    print("[+] Waiting due to reply delay.")
                    continue

                text = msg.text or ""
                sender_username = cl.user_info(msg.user_id).username

                if TRIGGER_PHRASE.lower() in text.lower():
                    print(f"[+] Trigger phrase found in message: {text}")
                    cl.direct_send(TRIGGER_RESPONSE, [thread_id])
                    print(f"[trigger] Replied in {thread_id}")
                    last_reply_time = now
                    continue

                roast = random.choice(ROASTS)
                reply_text = f"@{sender_username} {roast}"
                try:
                    cl.direct_answer(thread_id, msg.id, reply_text)
                    print(f"[reply] {reply_text} -> {thread_id}")
                    last_reply_time = now
                    time.sleep(REPLY_DELAY)
                except Exception as e:
                    print(f"[!] Failed to reply in {thread_id}: {e}")
                    if "403" in str(e):
                        print("Sleeping 90 seconds after 403...")
                        time.sleep(90)

        time.sleep(8)  # Delay to prevent overloading

    except Exception as e:
        print("[error]", e)
        time.sleep(20)  # Retry after failure
