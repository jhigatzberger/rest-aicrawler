import json
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_content(url: str, schema: dict):
    """
    Asynchronous function to extract content from a given URL using Crawl4AI.
    
    Args:
        url (str): The target URL to crawl.
        schema (dict): The JSON CSS extraction schema.

    Returns:
        dict: Extracted content in JSON format.
    """

    # 1. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # 2. Configure the crawler
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Avoid caching for fresh data
        extraction_strategy=extraction_strategy
    )

    # 3. Run the crawler
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            raise RuntimeError(f"Failed to crawl: {result.error_message}")
        return json.loads(result.extracted_content)
