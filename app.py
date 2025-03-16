import os
import json
import asyncio
from flask import Flask, request, jsonify
from extraction.jsoncss import extract_content  # ✅ Importing from the new folder

app = Flask(__name__)

# Load API key from environment variables
API_KEY = os.getenv("API_KEY")


@app.route("/extract", methods=["POST"])
def extract_data():
    """
    POST /extract
    Headers:
      x-api-key: <YOUR_API_KEY>
    JSON Body:
    {
      "url": "https://example.com",
      "schema": {
        "name": "Schema Name",
        "baseSelector": "div.article",
        "fields": [
          { "name": "title", "selector": "h1", "type": "text" },
          { "name": "author", "selector": ".author-name", "type": "text" }
        ]
      }
    }
    
    Returns:
      JSON array of extracted data (one object per match).
    """

    # 1. Validate API Key
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Validate JSON input
    data = request.get_json()
    if not data or "url" not in data or "schema" not in data:
        return jsonify({"error": "Both 'url' and 'schema' fields are required."}), 400

    url = data["url"]
    schema = data["schema"]

    # 3. Run the async function using an event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted_data = loop.run_until_complete(extract_content(url, schema))
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set!")
    app.run(host="0.0.0.0", port=5000, debug=True)
