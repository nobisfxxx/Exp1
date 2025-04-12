from instagrapi import Client
import os
import time

# Read environment variables
USERNAME = os.getenv("bot_check_hu")
PASSWORD = os.getenv("nobilovestinglui")

# Debug logs to verify values
print("DEBUG USERNAME:", repr(USERNAME))
print("DEBUG PASSWORD:", repr(PASSWORD))

if not USERNAME or not PASSWORD:
    raise ValueError("Instagram USERNAME or PASSWORD not provided in environment variables.")

# Initialize and login
cl = Client()
cl.login(USERNAME, PASSWORD)

# Example action: Print your own profile info
profile = cl.account_info()
print("Logged in as:", profile.username)
print("Full Name:", profile.full_name)
print("Followers:", profile.follower_count)

# Keep the script running
while True:
    print("Bot is running...")
    time.sleep(60)
