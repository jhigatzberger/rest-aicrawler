import os
import asyncio
from typing import Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig 
from crawl4ai.async_configs import LlmConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

async def extract_content_using_deepseek(url: str, schema: dict, instruction: str):

    # Extra LLM config
    extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 2000}

    crawler_config = CrawlerRunConfig(
        cache_mode="bypass",  # Always fetch fresh content
        word_count_threshold=1,  
        page_timeout=80000,  # Handle slow websites
        extraction_strategy=LLMExtractionStrategy(
            llmConfig=LlmConfig(provider="deepseek/deepseek-chat", api_token=DEEPSEEK_API_KEY),
            schema=schema,
            extraction_type="schema",
            instruction=instruction,
            extra_args=extra_args,
        ),
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url, config=crawler_config)

    return results.extracted_content if results else {"error": "No content extracted."}
