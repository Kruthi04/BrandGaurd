"""Graph endpoints — Neo4j knowledge graph for brand reputation."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.neo4j.client import get_neo4j_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response Models ───────────────────────────────────

class StoreMentionRequest(BaseModel):
    id: Optional[str] = None
    brand_id: str
    brand_name: Optional[str] = None
    platform: str
    claim: str
    accuracy_score: float = Field(ge=0, le=100)
    severity: str = "medium"
    detected_at: Optional[str] = None
    source_urls: list[str] = []


class StoreCorrectionRequest(BaseModel):
    mention_id: str
    id: Optional[str] = None
    content: str = ""
    correction_type: str = "blog_post"
    status: str = "draft"
    created_at: Optional[str] = None


class InitSchemaRequest(BaseModel):
    confirm: bool = True


# ── Helpers ─────────────────────────────────────────────────────

def _client():
    try:
        return get_neo4j_client()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Neo4j unavailable: {exc}")


# ── Endpoints ───────────────────────────────────────────────────

@router.post("/init")
async def init_schema(request: InitSchemaRequest):
    """Create constraints, indexes, and seed platform nodes."""
    client = _client()
    try:
        await client.init_schema()
        return {"status": "ok", "message": "Schema initialized"}
    except Exception as exc:
        logger.error("Schema init failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/mentions")
async def store_mention(request: StoreMentionRequest):
    """Store a new mention with Brand, Platform, Source relationships."""
    client = _client()
    try:
        result = await client.store_mention(request.model_dump())
        return result
    except Exception as exc:
        logger.error("store_mention failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/corrections")
async def store_correction(request: StoreCorrectionRequest):
    """Store a correction linked to a mention."""
    client = _client()
    try:
        result = await client.store_correction(request.model_dump())
        return result
    except Exception as exc:
        logger.error("store_correction failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/health")
async def get_brand_health(brand_id: str):
    """Brand accuracy overview broken down by platform."""
    client = _client()
    try:
        return await client.get_brand_health(brand_id)
    except Exception as exc:
        logger.error("get_brand_health failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/sources")
async def get_brand_sources(brand_id: str, limit: int = 20):
    """Top misinformation sources ranked by influence."""
    client = _client()
    try:
        sources = await client.get_brand_sources(brand_id, limit=limit)
        return {"sources": sources}
    except Exception as exc:
        logger.error("get_brand_sources failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/mentions")
async def get_brand_mentions(brand_id: str):
    """List all mentions for a brand with derived status."""
    client = _client()
    try:
        mentions = await client.get_brand_mentions(brand_id)
        return {"mentions": mentions}
    except Exception as exc:
        logger.error("get_brand_mentions failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/corrections")
async def get_brand_corrections(brand_id: str):
    """List all corrections for a brand."""
    client = _client()
    try:
        corrections = await client.get_brand_corrections(brand_id)
        return {"corrections": corrections}
    except Exception as exc:
        logger.error("get_brand_corrections failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/trend")
async def get_accuracy_trend(brand_id: str):
    """Daily accuracy trend per platform."""
    client = _client()
    try:
        return await client.get_accuracy_trend(brand_id)
    except Exception as exc:
        logger.error("get_accuracy_trend failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/brand/{brand_id}/network")
async def get_brand_network(brand_id: str):
    """Full graph data (nodes + edges) for visualization."""
    client = _client()
    try:
        return await client.get_brand_network(brand_id)
    except Exception as exc:
        logger.error("get_brand_network failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
