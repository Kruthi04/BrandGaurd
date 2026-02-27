"""Monitoring endpoints - Yutori scouts and Tavily web searches."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class CreateScoutRequest(BaseModel):
    """Request to create a new Yutori monitoring scout."""
    query: str
    brand_name: str
    output_interval: Optional[int] = 86400
    user_timezone: Optional[str] = "America/Los_Angeles"


class WebSearchRequest(BaseModel):
    """Request to trigger a Tavily web search."""
    query: str
    search_depth: Optional[str] = "advanced"
    max_results: Optional[int] = 10


@router.post("/scouts")
async def create_scout(request: CreateScoutRequest):
    """Create a Yutori scout to monitor brand mentions."""
    # TODO: Implement with YutoriService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/scouts")
async def list_scouts():
    """List all active monitoring scouts."""
    # TODO: Implement with YutoriService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/scouts/{scout_id}/updates")
async def get_scout_updates(scout_id: str, page_size: int = 20):
    """Get updates from a specific scout."""
    # TODO: Implement with YutoriService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.delete("/scouts/{scout_id}")
async def delete_scout(scout_id: str):
    """Delete a monitoring scout."""
    # TODO: Implement with YutoriService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/search")
async def web_search(request: WebSearchRequest):
    """Run a Tavily web search for brand mentions."""
    # TODO: Implement with TavilyService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/crawl")
async def crawl_url(url: str):
    """Crawl a specific URL with Tavily for brand content."""
    # TODO: Implement with TavilyService
    raise HTTPException(status_code=501, detail="Not yet implemented")
