from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Webhook verification endpoint
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Replace this with your own verification token
    verify_token = os.getenv('VERIFY_TOKEN', 'your-verify-token')  
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
 flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Webhook is live!"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = 'IGAAYMtqnh68pBZAFAxSlNkbHlCVnNxMTR2eWxNbVBMd2RUVC1jaWNPMmVlTW95WER1MkUtRDRudUxuMUxwcFJXRnVIblVxYjVYMzRfWVhFNk44N3hpdVp5cHVlMkpYdmc2aEJBLXg1SVo5dy1HWlRZAa0ZALSHZAFZAUMta3RuNUdyYwZDZD'
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        else:
            return 'Verification failed', 403
    return 'Webhook received!', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
