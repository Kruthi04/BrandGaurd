"""Tavily API client for web search, content extraction, site mapping, and crawling.

Tavily provides four core endpoints used by BrandGuard:
- Search: Find source websites that AI models are citing about a brand
- Extract: Pull full content from flagged URLs for claim analysis
- Map: Discover all pages on a site mentioning a brand
- Crawl: Combined map + extract for comprehensive site analysis
"""
import httpx
import logging
from typing import Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 60.0
_CRAWL_TIMEOUT = 180.0


class TavilyClient:
    """Client for the Tavily Search, Extract, Map, and Crawl APIs."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com"
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Set TAVILY_API_KEY in .env"
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _post(
        self, endpoint: str, payload: dict[str, Any], timeout: float = _DEFAULT_TIMEOUT
    ) -> dict[str, Any]:
        """Send a POST request to Tavily and return the JSON response."""
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    # ── Search API ──────────────────────────────────────────────

    async def search(
        self,
        query: str,
        *,
        topic: str = "general",
        search_depth: str = "basic",
        time_range: Optional[str] = None,
        max_results: int = 10,
        include_answer: bool | str = True,
        include_raw_content: bool | str = False,
        include_domains: Optional[list[str]] = None,
        exclude_domains: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Search the web for brand-related claims.

        Args:
            query: Search query string.
            topic: "general", "news", or "finance".
            search_depth: "basic" (1 credit) or "advanced" (2 credits).
            time_range: "day", "week", "month", or "year".
            max_results: Number of results (0-20).
            include_answer: Return an AI-synthesized answer.
            include_raw_content: Return full page content.
            include_domains: Only search these domains.
            exclude_domains: Exclude these domains.

        Returns:
            Dict with "results", optional "answer", and metadata.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        payload: dict[str, Any] = {
            "query": query,
            "topic": topic,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
        }
        if time_range:
            payload["time_range"] = time_range
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        logger.info("Tavily search: query=%r topic=%s depth=%s", query, topic, search_depth)
        return await self._post("search", payload)

    # ── Extract API ─────────────────────────────────────────────

    async def extract(
        self,
        urls: list[str],
        *,
        query: Optional[str] = None,
        extract_depth: str = "basic",
        format: str = "markdown",
    ) -> dict[str, Any]:
        """Extract full content from specific URLs.

        Args:
            urls: List of URLs to extract (max 20).
            query: Optional query for chunk reranking.
            extract_depth: "basic" or "advanced".
            format: "markdown" or "text".

        Returns:
            Dict with "results" and "failed_results".
        """
        if not urls:
            raise ValueError("At least one URL is required for extraction")
        if len(urls) > 20:
            raise ValueError("Tavily extract supports at most 20 URLs per request")

        payload: dict[str, Any] = {
            "urls": urls,
            "extract_depth": extract_depth,
            "format": format,
        }
        if query:
            payload["query"] = query

        logger.info("Tavily extract: %d URLs, depth=%s", len(urls), extract_depth)
        return await self._post("extract", payload)

    # ── Map API ─────────────────────────────────────────────────

    async def map(
        self,
        url: str,
        *,
        instructions: Optional[str] = None,
        max_depth: int = 1,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Discover the structure of a website.

        Args:
            url: Root URL to begin mapping.
            instructions: Natural-language crawl guidance.
            max_depth: Traversal depth (1-5).
            limit: Maximum total links to process.

        Returns:
            Dict with "results" (list of discovered URLs).
        """
        payload: dict[str, Any] = {
            "url": url,
            "max_depth": max_depth,
            "limit": limit,
        }
        if instructions:
            payload["instructions"] = instructions

        logger.info("Tavily map: url=%r depth=%d limit=%d", url, max_depth, limit)
        return await self._post("map", payload, timeout=_CRAWL_TIMEOUT)

    # ── Crawl API ───────────────────────────────────────────────

    async def crawl(
        self,
        url: str,
        *,
        instructions: Optional[str] = None,
        max_depth: int = 1,
        limit: int = 50,
        extract_depth: str = "basic",
        format: str = "markdown",
    ) -> dict[str, Any]:
        """Combined map + extract for comprehensive site analysis.

        Args:
            url: Root URL to crawl.
            instructions: Natural-language crawl guidance.
            max_depth: Crawl depth (1-5).
            limit: Maximum total links to process.
            extract_depth: "basic" or "advanced".
            format: "markdown" or "text".

        Returns:
            Dict with "results" containing extracted content per page.
        """
        payload: dict[str, Any] = {
            "url": url,
            "max_depth": max_depth,
            "limit": limit,
            "extract_depth": extract_depth,
            "format": format,
        }
        if instructions:
            payload["instructions"] = instructions

        logger.info("Tavily crawl: url=%r depth=%d limit=%d", url, max_depth, limit)
        return await self._post("crawl", payload, timeout=_CRAWL_TIMEOUT)


# ── Helper: Source Analyzer ─────────────────────────────────────

async def analyze_claim_sources(claim: str, brand: str) -> dict[str, Any]:
    """Investigate a claim by searching the web and extracting source content.

    Workflow:
      1. Search the web for the claim + brand name
      2. Extract full content from the top results
      3. Return sources with their content and relevance scores
    """
    client = TavilyClient()

    search_results = await client.search(
        query=f"{brand} {claim}",
        topic="news",
        search_depth="advanced",
        max_results=10,
        include_answer=True,
    )

    source_urls = [r["url"] for r in search_results.get("results", [])]

    extracted = {"results": [], "failed_results": []}
    if source_urls:
        extracted = await client.extract(
            urls=source_urls[:20],
            query=f"What claims does this source make about {brand}?",
            extract_depth="basic",
        )

    search_hits = search_results.get("results", [])
    extracted_map = {r["url"]: r.get("raw_content", "") for r in extracted.get("results", [])}

    sources = []
    for hit in search_hits:
        sources.append({
            "url": hit["url"],
            "title": hit.get("title", ""),
            "snippet": hit.get("content", ""),
            "score": hit.get("score", 0),
            "raw_content": extracted_map.get(hit["url"], ""),
        })

    return {
        "claim": claim,
        "brand": brand,
        "answer": search_results.get("answer", ""),
        "sources": sources,
        "failed_extractions": [
            r["url"] for r in extracted.get("failed_results", [])
        ],
    }
