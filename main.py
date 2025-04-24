from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Webhook verification endpoint
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Access VERIFY_TOKEN from environment variable
    verify_token = os.getenv('VERIFY_TOKEN', 'your-verify-token')  # Replace with the actual token or use environment variable
    challenge = request.args.get('hub.challenge')
    token = request.args.get('hub.verify_token')
    
    if token == verify_token:
        return challenge
    else:
        return 'Verification failed', 403

# Webhook event handling
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json  # The incoming data from Instagram
    print("Received webhook data:", data)  # For debugging

    # Process the event data here (you can print or store it as needed)

    # Respond back to Instagram that the event was processed successfully
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
