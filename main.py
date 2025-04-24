from flask import Flask, request

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
