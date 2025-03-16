import os
import json
import asyncio
from flask import Flask, request, jsonify
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

app = Flask(__name__)

print(f"Crawl4AI Version: {crawl4ai.__version__}")

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

    # 1. Check API key
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Validate JSON input
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    url = data.get("url")
    schema = data.get("schema")

    if not url or not schema:
        return jsonify({"error": "Both 'url' and 'schema' fields are required."}), 400

    # 3. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # 4. Configure the crawler
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Avoid caching for fresh data
        extraction_strategy=extraction_strategy,
        wait_for=None,  # Adjust if you need to wait for elements to load
        js_code=None,  # Insert JS execution if required
    )

    # 5. Define async crawling function
    async def crawl_site():
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url, config=config)
            if not result.success:
                raise RuntimeError(f"Failed to crawl: {result.error_message}")
            return json.loads(result.extracted_content)

    # 6. Run the async function using an event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted_data = loop.run_until_complete(crawl_site())
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure API_KEY is set before running the app
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set!")
    app.run(host="0.0.0.0", port=5000, debug=True)