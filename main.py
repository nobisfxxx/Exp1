import os
from dotenv import load_dotenv
from instagrapi import Client

# Load environment variables from .env file
load_dotenv()

# Get Instagram username and password from environment variables
USERNAME = os.getenv('bot_check_hu')
PASSWORD = os.getenv('nobilovestinglui')

# Check if username and password are provided
if not USERNAME or not PASSWORD:
    raise ValueError("Instagram USERNAME or PASSWORD not provided in environment variables.")

# Initialize the Instagram client
cl = Client()

# Log in to Instagram
cl.login(USERNAME, PASSWORD)

# Your bot logic here (add more features as needed)

print("Successfully logged in to Instagram.")
