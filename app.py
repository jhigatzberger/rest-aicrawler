import asyncio
from flask import Flask, Response
from crawl4ai import AsyncWebCrawler

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """
    When a GET request is made to '/', run the async Crawl4AI code
    and return the result's Markdown in the response.
    """
    
    async def crawl():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url="https://www.nbcnews.com/business",
            )
            return result.markdown

    # Synchronously execute our async crawler (blocking call).
    markdown_output = asyncio.run(crawl())

    # Return as plain text (or you could return JSON if you prefer).
    return Response(markdown_output, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
