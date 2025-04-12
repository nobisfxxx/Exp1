import os
from instagrapi import Client
from dotenv import load_dotenv

# Load environment variables from the system
load_dotenv()

# Retrieve the Instagram username and password from environment variables
USERNAME = os.getenv("bot_check_hu")  # Replace 'bot_check_hu' with the environment variable name
PASSWORD = os.getenv("nobilovestinglui")  # Replace 'nobilovestinglui' with the environment variable name

# Debugging output to check if the values are being fetched correctly
print(f"DEBUG USERNAME: {USERNAME}")
print(f"DEBUG PASSWORD: {PASSWORD}")

# Check if username and password are provided, else raise an error
if not USERNAME or not PASSWORD:
    raise ValueError("Instagram USERNAME or PASSWORD not provided in environment variables.")

# Initialize the Instagram client
cl = Client()

# Login to Instagram using the provided credentials
cl.login(USERNAME, PASSWORD)

print("Logged in successfully!")

# Add your other functionality (like interacting with Instagram, sending messages, etc.) here.
