import os
import asyncio
from flask import Flask, request, Response, jsonify
from crawl4ai import AsyncWebCrawler

app = Flask(__name__)

# Retrieve the valid API key from environment variables
API_KEY = os.getenv("API_KEY")

@app.route("/", methods=["GET"])
def index():
    """
    When a GET request is made to '/', run the async Crawl4AI code
    only if the supplied API key is correct.
    """
    # Get the API key from the request header (e.g., x-api-key)
    client_key = request.headers.get("x-api-key")

    if client_key != API_KEY:
        # If there's no match, return a 401 Unauthorized
        return jsonify({"error": "Unauthorized"}), 401

    async def crawl():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url="https://www.nbcnews.com/business",
            )
            return result.markdown

    # Synchronously run our async function
    markdown_output = asyncio.run(crawl())

    # Return as plain text
    return Response(markdown_output, mimetype="text/plain")

if __name__ == "__main__":
    # Optional: raise an error if API_KEY is not set
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set!")

    app.run(host="0.0.0.0", port=5000, debug=True)
