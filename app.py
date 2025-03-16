import os
import json
import asyncio
from flask import Flask, request, jsonify
from extraction.jsoncss import extract_content  # ✅ Import extraction logic
from extraction.deepseek import extract_content_using_deepseek  # ✅ Import extraction logic
from middlewares import validate_api_key, validate_json_request, API_KEY  # ✅ Import middleware

app = Flask(__name__)

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

    # ✅ Apply API key validation
    api_error = validate_api_key()
    if api_error:
        return api_error  # Middleware returns JSON error if invalid

    # ✅ Apply JSON request validation
    json_error = validate_json_request(["url", "schema"])
    if json_error:
        return json_error  # Middleware returns JSON error if invalid

    # Extract validated data
    data = request.get_json()
    url = data["url"]
    schema = data["schema"]

    # Run the async function using an event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted_data = loop.run_until_complete(extract_content(url, schema))
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/extract-llm", methods=["POST"])
def extract_data_using_llm():
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

    # ✅ Apply API key validation
    api_error = validate_api_key()
    if api_error:
        return api_error  # Middleware returns JSON error if invalid

    # ✅ Apply JSON request validation
    json_error = validate_json_request(["url", "schema", "instruction"])
    if json_error:
        return json_error  # Middleware returns JSON error if invalid

    # Extract validated data
    data = request.get_json()
    url = data["url"]
    schema = data["schema"]
    instruction = data["instruction"]

    # Run the async function using an event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted_data = loop.run_until_complete(extract_content_using_deepseek(url, schema, instruction))
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set!")
    app.run(host="0.0.0.0", port=5000, debug=True)
