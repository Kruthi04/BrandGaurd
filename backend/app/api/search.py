"""Search endpoints — Tavily web search, extract, map, and crawl."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from app.services.tavily.client import TavilyClient, analyze_claim_sources

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response Models ───────────────────────────────────

class WebSearchRequest(BaseModel):
    query: str
    topic: str = "general"
    time_range: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=20)
    search_depth: str = "basic"
    include_domains: Optional[list[str]] = None
    exclude_domains: Optional[list[str]] = None


class ExtractRequest(BaseModel):
    urls: list[str] = Field(..., max_length=20)
    query: Optional[str] = None
    extract_depth: str = "basic"


class MapRequest(BaseModel):
    url: str
    instructions: Optional[str] = None
    max_depth: int = Field(default=1, ge=1, le=5)
    limit: int = Field(default=50, ge=1)


class CrawlRequest(BaseModel):
    url: str
    instructions: Optional[str] = None
    max_depth: int = Field(default=1, ge=1, le=5)
    limit: int = Field(default=50, ge=1)
    extract_depth: str = "basic"


class AnalyzeClaimRequest(BaseModel):
    claim: str
    brand: str


# ── Endpoints ───────────────────────────────────────────────────

def _tavily_client() -> TavilyClient:
    try:
        return TavilyClient()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/web")
async def web_search(request: WebSearchRequest):
    """Search the web for brand mentions and citations."""
    client = _tavily_client()
    try:
        result = await client.search(
            query=request.query,
            topic=request.topic,
            search_depth=request.search_depth,
            time_range=request.time_range,
            max_results=request.max_results,
            include_answer=True,
            include_domains=request.include_domains,
            exclude_domains=request.exclude_domains,
        )
        return {
            "results": result.get("results", []),
            "answer": result.get("answer"),
            "response_time": result.get("response_time"),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("Tavily search error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except httpx.RequestError as exc:
        logger.error("Tavily search network error: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach Tavily API")


@router.post("/extract")
async def extract_content(request: ExtractRequest):
    """Extract full content from flagged URLs."""
    client = _tavily_client()
    try:
        result = await client.extract(
            urls=request.urls,
            query=request.query,
            extract_depth=request.extract_depth,
        )
        return {
            "results": result.get("results", []),
            "failed": [r.get("url", r) for r in result.get("failed_results", [])],
            "response_time": result.get("response_time"),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("Tavily extract error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except httpx.RequestError as exc:
        logger.error("Tavily extract network error: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach Tavily API")


@router.post("/map")
async def map_site(request: MapRequest):
    """Discover pages on a misinformation source."""
    client = _tavily_client()
    try:
        result = await client.map(
            url=request.url,
            instructions=request.instructions,
            max_depth=request.max_depth,
            limit=request.limit,
        )
        return {
            "pages": [{"url": u} for u in result.get("results", [])],
            "base_url": result.get("base_url"),
            "response_time": result.get("response_time"),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("Tavily map error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("Tavily map network error: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach Tavily API")


@router.post("/crawl")
async def crawl_site(request: CrawlRequest):
    """Full site analysis of a misinformation source (map + extract)."""
    client = _tavily_client()
    try:
        result = await client.crawl(
            url=request.url,
            instructions=request.instructions,
            max_depth=request.max_depth,
            limit=request.limit,
            extract_depth=request.extract_depth,
        )
        return {
            "results": [
                {"url": r.get("url"), "content": r.get("raw_content", "")}
                for r in result.get("results", [])
            ],
            "base_url": result.get("base_url"),
            "response_time": result.get("response_time"),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("Tavily crawl error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("Tavily crawl network error: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach Tavily API")


@router.post("/analyze")
async def analyze_claim(request: AnalyzeClaimRequest):
    """Search + extract pipeline: investigate a claim about a brand."""
    try:
        result = await analyze_claim_sources(
            claim=request.claim,
            brand=request.brand,
        )
        return result
    except httpx.HTTPStatusError as exc:
        logger.error("Tavily analyze error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("Tavily analyze network error: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to reach Tavily API")
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
