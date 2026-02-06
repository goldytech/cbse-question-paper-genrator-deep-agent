"""Curriculum search tool using Tavily."""

import os
from typing import Dict, List, Literal
from tavily import TavilyClient
from langchain_core.tools import tool

# Initialize Tavily client
_tavily_client = None


def _get_tavily_client() -> TavilyClient:
    """Get or create Tavily client."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not set in environment")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


@tool
def search_cbse_curriculum_tool(
    query: str,
    subject: Literal["mathematics", "science", "english"] = "mathematics",
    class_level: int = 10,
    max_results: int = 5,
) -> Dict:
    """
    Searches CBSE curriculum topics using Tavily.

    Args:
        query: Search query (e.g., 'LCM HCF topics', 'Real Numbers chapter content')
        subject: Subject area (mathematics, science, or english)
        class_level: Class level (default: 10)
        max_results: Number of results to return (default: 5)

    Returns:
        {
          topics: list[str],
          sources: list[str],
          results_count: int,
          error: str (if error occurred)
        }
    """
    try:
        # Build search query
        search_query = f"CBSE Class {class_level} {subject} {query}"

        # Get Tavily client
        client = _get_tavily_client()

        # Perform search
        results = client.search(
            query=search_query, max_results=max_results, include_raw_content=True, topic="general"
        )

        # Extract topics and sources
        topics = []
        sources = []

        for result in results.get("results", [])[:max_results]:
            content = result.get("content", "")
            url = result.get("url", "")

            # Shorten content to reasonable length for context
            if content:
                topics.append(content[:800])
            sources.append(url)

        return {"topics": topics, "sources": sources, "results_count": len(topics)}

    except ValueError as e:
        return {"error": str(e), "topics": [], "sources": [], "results_count": 0}
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "topics": [],
            "sources": [],
            "results_count": 0,
        }
