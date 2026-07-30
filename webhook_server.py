from flask import Flask, request, jsonify
import subprocess
import os
import hmac
import hashlib

app = Flask(__name__)

# 🛡️ अपनी Secret Key यहाँ डालें (GitHub Secret से match karna hoga)
SECRET = "MySuperSecret749"
VERIFY_SIGNATURE = False

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    print("=" * 50)
    print("🔔 GitHub Webhook Request Received!")
    
    event = request.headers.get('X-GitHub-Event')
    print(f"🚀 Event Type: {event}")
    
    if event == 'ping':
        return jsonify({"message": "Webhook received successfully! Pong!"}), 200
        
    if event != 'push':
        print("⏭️ Ignoring non-push event.")
        return jsonify({"message": "Ignored"}), 200

    if VERIFY_SIGNATURE:
        print("🔒 Verifying Signature...")
        signature_header = request.headers.get('X-Hub-Signature-256')
        if not signature_header:
            print("❌ Signature missing!")
            return 'Signature missing', 401
        payload = request.get_data()
        expected_signature = 'sha256=' + hmac.new(
            SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_signature, signature_header):
            print("❌ Invalid Signature!")
            return 'Invalid signature', 401
        print("✅ Signature Verified Successfully!")

    script_path = "/home/ubuntu/auto_deploy.sh"
    if not os.path.exists(script_path):
        print(f"❌ ERROR: Script not found at {script_path}")
        return jsonify({"error": "Script not found"}), 500
    else:
        print(f"✅ Script found at {script_path}")

    print("🚀 Executing script in background...")
    # Background में script चलाएं, ताकि Flask तुरंत Response भेज दे
    subprocess.Popen(["/bin/bash", script_path], start_new_session=True)

    return jsonify({"status": "Deploy triggered in background"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return "✅ Webhook Server is Running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
