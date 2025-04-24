from flask import Flask, request
import os
import requests

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Handle GET request for verification
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"GET request: mode={mode}, token={token}, challenge={challenge}")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Verification successful!")
            return challenge, 200
        else:
            print("Verification failed: Incorrect token.")
            return "Verification token mismatch", 403

    # Handle POST request for incoming messages
    elif request.method == "POST":
        data = request.get_json()
        print(f"Received data: {data}")
        
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                
                # Check if the message contains text
                if "message" in messaging_event:
                    message = messaging_event["message"].get("text", "")
                    print(f"Message from {sender_id}: {message}")
                    
                    # Craft a reply message
                    reply = f"@{sender_id} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
                    send_message(sender_id, reply)
                    
        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    
    # Log the response for debugging
    print(f"Response: {response.text}")

if __name__ == "__main__":
    # Get the port from environment variables (default to 5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
