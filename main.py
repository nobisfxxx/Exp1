from dotenv import load_dotenv
import os
from instagrapi import Client

# Load environment variables from .env file
load_dotenv()

# Get the Instagram username and password from the environment variables
USERNAME = os.getenv("bot_check_hu")
PASSWORD = os.getenv("nobilovestinglui")

# Check if username and password are loaded
if not USERNAME or not PASSWORD:
    raise ValueError("Instagram USERNAME or PASSWORD not provided in environment variables.")

# Create a new Instagram client
cl = Client()

# Log in to Instagram using the loaded credentials
cl.login(USERNAME, PASSWORD)

print("Logged in successfully!")
