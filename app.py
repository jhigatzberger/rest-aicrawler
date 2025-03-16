import os
import json
import asyncio
from flask import Flask, request, jsonify
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

app = Flask(__name__)

# Load API keys from environment variables
API_KEY = os.getenv("API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.route("/extract-llm", methods=["POST"])
def extract_data_llm():
    """
    POST /extract-llm
    Headers:
      x-api-key: <YOUR_API_KEY>
    JSON Body:
    {
      "url": "https://example.com/article",
      "instruction": "Extract title, author, publication date, and content.",
      "schema": {
        "name": "Article Schema",
        "fields": [
          { "name": "title", "type": "string" },
          { "name": "author", "type": "string" },
          { "name": "publication_date", "type": "string" },
          { "name": "content", "type": "string" }
        ]
      }
    }
    
    Returns:
      JSON object containing the extracted data.
    """

    # 1. Validate API Key
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Parse Input
    data = request.get_json()
    if not data or "url" not in data or "instruction" not in data or "schema" not in data:
        return jsonify({"error": "'url', 'instruction', and 'schema' fields are required."}), 400

    url = data["url"]
    instruction = data["instruction"]
    schema = data["schema"]

    # 3. Define LLM Extraction Strategy
    extraction_strategy = LLMExtractionStrategy(
        provider="deepseek/deepseek-chat",
        api_token=DEEPSEEK_API_KEY,
        extraction_type="schema",
        schema=schema,
        instruction=instruction,
        verbose=True
    )

    # 4. Crawler Configuration
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )

    # 5. Async Crawler Function
    async def crawl_site():
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url, config=config)
            if not result.success:
                raise RuntimeError(f"Failed to crawl: {result.error_message}")
            return json.loads(result.extracted_content)

    # 6. Execute Crawl & Return Response
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        extracted_data = loop.run_until_complete(crawl_site())
        return jsonify(extracted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not API_KEY or not DEEPSEEK_API_KEY:
        raise ValueError("API_KEY and DEEPSEEK_API_KEY environment variables must be set!")
    app.run(host="0.0.0.0", port=5000, debug=True)
