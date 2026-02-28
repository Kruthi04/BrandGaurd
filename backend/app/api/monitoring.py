"""Monitoring endpoints — Yutori scouts, Tavily web searches, and webhook receiver."""
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.yutori.client import YutoriClient, BRAND_MENTION_SCHEMA
from app.services.neo4j.client import get_neo4j_client
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory scout↔brand mapping (sufficient for hackathon demo)
_scout_to_brand: dict[str, dict] = {}  # scout_id -> {"brand_id": ..., "brand_name": ...}


# ── Request Models ──────────────────────────────────────────────

class StartMonitoringRequest(BaseModel):
    brand_id: str
    brand_name: str
    interval: int = 21600  # 6h default
    webhook_url: Optional[str] = None


class StopMonitoringRequest(BaseModel):
    scout_id: str


# ── Helpers ─────────────────────────────────────────────────────

def _yutori() -> YutoriClient:
    try:
        return YutoriClient()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


def _severity_score(severity: str) -> float:
    return {"critical": 10, "high": 30, "medium": 55, "low": 80}.get(severity, 50)


# ── Endpoints ───────────────────────────────────────────────────

@router.post("/start")
async def start_monitoring(request: StartMonitoringRequest):
    """Create a Yutori scout to continuously monitor a brand."""
    client = _yutori()
    query = (
        f'Monitor what AI chatbots (ChatGPT, Claude, Perplexity, Gemini) '
        f'say about "{request.brand_name}". Find brand mentions, check accuracy, '
        f'and flag inaccurate information including wrong facts, misleading claims, '
        f'or outdated data.'
    )
    try:
        result = await client.create_scout(
            query=query,
            display_name=f"BrandGuard — {request.brand_name}",
            output_schema=BRAND_MENTION_SCHEMA,
            output_interval=request.interval,
            skip_email=True,
            webhook_url=request.webhook_url,
        )
        scout_id = result.get("id", "")
        _scout_to_brand[scout_id] = {
            "brand_id": request.brand_id,
            "brand_name": request.brand_name,
        }
        return {"scout_id": scout_id, "status": "active"}
    except httpx.HTTPStatusError as exc:
        logger.error("Yutori create_scout error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.post("/stop")
async def stop_monitoring(request: StopMonitoringRequest):
    """Stop a Yutori scout."""
    client = _yutori()
    try:
        await client.stop_scout(request.scout_id)
        _scout_to_brand.pop(request.scout_id, None)
        return {"status": "stopped"}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.get("/status")
async def monitoring_status(brand_name: str | None = None):
    """List scouts, optionally filtered by brand name."""
    client = _yutori()
    try:
        scouts = await client.list_scouts()
        result = []
        for s in scouts:
            # Filter by brand if requested — match against display_name or query
            if brand_name:
                haystack = (s.get("display_name", "") + " " + s.get("query", "")).lower()
                if brand_name.lower() not in haystack:
                    continue
            result.append({
                "id": s.get("id"),
                "display_name": s.get("display_name", ""),
                "status": s.get("status", "unknown"),
                "query": s.get("query", ""),
                "created_at": s.get("created_at"),
                "next_run": s.get("next_run_timestamp"),
            })
        return {"scouts": result}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.get("/scouts/{scout_id}/updates")
async def get_scout_updates(scout_id: str, page_size: int = 20):
    """Get updates from a specific scout."""
    client = _yutori()
    try:
        data = await client.get_scout_updates(scout_id, page_size=page_size)
        return data
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.delete("/scouts/{scout_id}")
async def delete_scout(scout_id: str):
    """Delete a scout permanently."""
    client = _yutori()
    try:
        await client.delete_scout(scout_id)
        return {"status": "deleted"}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


# ── Webhook Receiver ────────────────────────────────────────────

@router.post("/crawl")
async def crawl_url(url: str):
    """Crawl a specific URL with Tavily for brand content."""
    # TODO: Implement with TavilyService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/webhooks/yutori")
async def yutori_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive scout update webhooks from Yutori, parse mentions, store in Neo4j, and trigger pipeline."""
    from uuid import uuid4
    from app.services.agent.orchestrator import BrandGuardPipeline

    body = await request.json()
    logger.info("Yutori webhook received: %s", str(body)[:200])

    scout_id = body.get("scout_id") or body.get("task_id", "")
    brand_info = _scout_to_brand.get(scout_id, {
        "brand_id": body.get("brand_id", "acme-corp"),
        "brand_name": body.get("brand_name", "Acme Corp"),
    })

    structured = body.get("structured_result") or body.get("result", {})
    mentions = []
    if isinstance(structured, dict):
        mentions = structured.get("brand_mentions", [])
    elif isinstance(structured, str):
        return {"received": True, "parsed_mentions": 0, "note": "Unstructured result"}

    # Store mentions in Neo4j
    stored = 0
    try:
        neo4j = get_neo4j_client()
        for m in mentions:
            score = _severity_score(m.get("severity", "medium"))
            if m.get("accuracy") == "accurate":
                score = max(score, 80)
            elif m.get("accuracy") == "inaccurate":
                score = min(score, 40)

            await neo4j.store_mention({
                "brand_id": brand_info["brand_id"],
                "brand_name": brand_info["brand_name"],
                "platform": m.get("platform", "unknown"),
                "claim": m.get("claim", ""),
                "accuracy_score": score,
                "severity": m.get("severity", "medium"),
                "source_urls": [m["source_url"]] if m.get("source_url") else [],
            })
            stored += 1
    except Exception as exc:
        logger.error("Failed to store webhook mentions in Neo4j: %s", exc)

    # Trigger pipeline for each mention
    pipeline = BrandGuardPipeline()
    job_ids = []
    for mention in mentions:
        job_id = str(uuid4())
        background_tasks.add_task(pipeline.process_mention, mention, job_id)
        job_ids.append(job_id)

    return {
        "received": True,
        "parsed_mentions": len(mentions),
        "stored_in_neo4j": stored,
        "jobs_started": len(job_ids),
        "job_ids": job_ids,
    }
