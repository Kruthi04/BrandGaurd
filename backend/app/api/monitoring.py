"""Monitoring endpoints - Yutori scouts and Tavily web searches."""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
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

@router.post("/webhooks/yutori")
async def yutori_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook receiver for Yutori scout updates.
    
    When Yutori finds mentions, parse them and trigger the pipeline.
    """
    import logging
    from uuid import uuid4
    from app.services.agent.orchestrator import BrandGuardPipeline
    
    logger = logging.getLogger(__name__)
    try:
        payload = await request.json()
        logger.info(f"Received Yutori Webhook: {payload}")
        
        mentions = payload.get("mentions", [])
        if not mentions:
            # Fallback for hackathon testing if payload shape differs
            mentions = [{"id": str(uuid4()), "content": str(payload), "brand_id": "test_brand"}]
            
        pipeline = BrandGuardPipeline()
        job_ids = []
        
        for mention in mentions:
            job_id = str(uuid4())
            background_tasks.add_task(pipeline.process_mention, mention, job_id)
            job_ids.append(job_id)
            
        return {"status": "received", "jobs_started": len(job_ids), "job_ids": job_ids}
        
    except Exception as e:
        logger.error(f"Error processing Yutori webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
