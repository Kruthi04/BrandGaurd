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


@router.get("/brand/{brand_id}/threats")
async def get_brand_threats(brand_id: str, limit: int = 50):
    """Return inaccurate mentions as threat alerts for the dashboard."""
    client = _client()
    try:
        query = """
        MATCH (m:Mention)-[:ABOUT]->(b:Brand {id: $brand_id})
        MATCH (m)-[:FOUND_ON]->(p:Platform)
        OPTIONAL MATCH (m)-[:SOURCED_FROM]->(s:Source)
        WHERE m.accuracy_score < 70
        RETURN m.id AS id, m.claim AS claim, m.accuracy_score AS accuracy_score,
               m.severity AS severity, m.detected_at AS detected_at,
               p.name AS platform, collect(DISTINCT s.url) AS source_urls
        ORDER BY m.accuracy_score ASC
        LIMIT $limit
        """
        records = await client.run_query(query, {"brand_id": brand_id, "limit": limit})
        threats = []
        for r in records:
            sev = r.get("severity", "medium")
            threats.append({
                "id": r["id"],
                "severity": sev,
                "platform": (r.get("platform") or "unknown").title(),
                "claim": r.get("claim", ""),
                "context": f"AI platform {(r.get('platform') or 'unknown').title()} made this claim about your brand with {r.get('accuracy_score', 0):.0f}% accuracy.",
                "accuracy_score": round(r.get("accuracy_score", 0), 1),
                "status": "open",
                "detected_at": r.get("detected_at", ""),
                "source_url": (r.get("source_urls") or [""])[0] if r.get("source_urls") else "",
                "suggested_correction": f"This claim has a low accuracy score ({r.get('accuracy_score', 0):.0f}%). Investigate and publish a correction.",
            })
        return {"threats": threats, "total": len(threats)}
    except Exception as exc:
        logger.error("get_brand_threats failed: %s", exc)
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
