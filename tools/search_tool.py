"""
Web Search Tool — DuckDuckGo search wrapper for competitor research.
Free to use, no API key required.
"""
from __future__ import annotations
from typing import List, Dict, Optional
import time


def search_web(query: str, max_results: int = 8) -> List[Dict[str, str]]:
    """
    Search the web using DuckDuckGo and return structured results.
    
    Returns a list of dicts with: title, url, body (snippet).
    Falls back to empty list on error.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", ""),
                })
        return results
    except Exception as e:
        print(f"[Search] Warning: DuckDuckGo search failed: {e}")
        return []


def search_competitor(product_name: str, competitor_name: str) -> List[Dict[str, str]]:
    """Search for specific competitor information."""
    queries = [
        f"{competitor_name} product features pricing 2024",
        f"{competitor_name} vs {product_name} comparison",
        f"{competitor_name} new features launch 2024",
    ]
    all_results = []
    for query in queries:
        results = search_web(query, max_results=4)
        all_results.extend(results)
        time.sleep(0.5)  # Polite delay between requests
    return all_results[:12]


def search_market_trends(product_domain: str) -> List[Dict[str, str]]:
    """Search for market trends in a product domain."""
    queries = [
        f"{product_domain} market trends 2024",
        f"best {product_domain} software features 2024",
        f"{product_domain} product gaps opportunities",
    ]
    all_results = []
    for query in queries:
        results = search_web(query, max_results=4)
        all_results.extend(results)
        time.sleep(0.5)
    return all_results[:12]


def format_search_results(results: List[Dict[str, str]]) -> str:
    """Format search results as readable text for LLM consumption."""
    if not results:
        return "No search results found."
    
    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "N/A")
        url = r.get("url", "N/A")
        body = r.get("body", "No description")[:300]
        formatted.append(f"{i}. **{title}**\n   URL: {url}\n   {body}")
    
    return "\n\n".join(formatted)
