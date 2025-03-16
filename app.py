import os
import json
import asyncio
from flask import Flask, request, jsonify
from crawl4ai import AsyncWebCrawler
from crawl4ai.config import CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

app = Flask(__name__)

# Load your API key from environment variables
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
        "name": "Some extraction name",
        "baseSelector": "div.article",
        "fields": [
          {
            "name": "title",
            "selector": "h1",
            "type": "text"
          },
          {
            "name": "author",
            "selector": ".author-name",
            "type": "text"
          }
        ]
      }
    }
    
    Returns:
      JSON array of extracted data (one object per match).
    """

    # 1. Check the API key in the headers
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Parse JSON from the request body
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    url = data.get("url")
    schema = data.get("schema")

    if not url or not schema:
        return jsonify({"error": "Both 'url' and 'schema' fields are required."}), 400

    # 3. Create the JsonCssExtractionStrategy from the user-provided schema
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # 4. Create a CrawlerRunConfig if needed (optional adjustments)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        # Additional config if your target site requires dynamic loading:
        # wait_for="css:.some-late-loaded-element"
        # or js_code="window.scrollTo(0,document.body.scrollHeight)"
        # etc.
    )

    # 5. Perform the async crawl
    async def crawl_site():
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url, config=config)
            if not result.success:
                raise RuntimeError(f"Failed to crawl: {result.error_message}")
            # The extracted content is a JSON string with your scraped data
            return json.loads(result.extracted_content)

    # 6. Run it and handle errors
    try:
        extracted_data = asyncio.run(crawl_site())
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Optional check: if no API key is set, raise an error
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set!")
    app.run(host="0.0.0.0", port=5000, debug=True)
