"""Investigation endpoints — Yutori browsing and research for brand claims."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from app.services.yutori.client import YutoriClient, PLATFORM_URLS, NO_AUTH_PLATFORMS

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request Models ──────────────────────────────────────────────

class BrowsePlatformRequest(BaseModel):
    platform: str  # chatgpt, claude, perplexity, gemini
    query: str
    brand_name: str
    max_steps: int = 30


class DeepResearchRequest(BaseModel):
    claim: str
    brand_id: str
    brand_name: Optional[str] = None


class BrowseTaskStatusRequest(BaseModel):
    task_id: str


class ResearchTaskStatusRequest(BaseModel):
    task_id: str


# ── Helpers ─────────────────────────────────────────────────────

def _yutori() -> YutoriClient:
    try:
        return YutoriClient()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


_BROWSE_CLAIMS_SCHEMA = {
    "type": "object",
    "properties": {
        "responses": {
            "type": "array",
            "description": "List of queries asked to the AI platform and their responses",
            "items": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question asked to the AI platform"},
                    "response": {"type": "string", "description": "The full response from the AI platform"},
                    "claims_found": {
                        "type": "array",
                        "description": "Factual claims about the brand extracted from the response",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim": {"type": "string", "description": "A specific factual claim made about the brand"},
                                "category": {
                                    "type": "string",
                                    "description": "Category of the claim",
                                    "enum": ["founding", "product", "financial", "partnership", "legal", "personnel", "other"],
                                },
                                "accuracy": {
                                    "type": "string",
                                    "enum": ["accurate", "inaccurate", "unverifiable", "partially_accurate"],
                                },
                            },
                            "required": ["claim"],
                        },
                    },
                },
                "required": ["query", "response"],
            },
        },
    },
    "required": ["responses"],
}

_RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "correct_information": {"type": "string", "description": "The verified correct facts about the claim"},
        "misinformation_sources": {
            "type": "array",
            "description": "Websites and platforms propagating the misinformation",
            "items": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the misinformation source"},
                    "platform": {"type": "string", "description": "Platform name (e.g. blog, news, AI chatbot)"},
                    "date_found": {"type": "string", "description": "When the misinformation was published (ISO 8601)"},
                    "credibility": {
                        "type": "string",
                        "enum": ["verified", "credible", "unverified", "disputed"],
                    },
                },
                "required": ["url"],
            },
        },
        "propagation_chain": {"type": "string", "description": "How the misinformation spread from origin to AI platforms"},
        "severity": {
            "type": "string",
            "description": "How severe is this misinformation for the brand",
            "enum": ["critical", "high", "medium", "low"],
        },
    },
    "required": ["correct_information", "misinformation_sources", "propagation_chain"],
}


# ── Endpoints ───────────────────────────────────────────────────

@router.post("/browse")
async def browse_platform(request: BrowsePlatformRequest):
    """Query an AI platform directly using Yutori Browsing API.

    Launches a browser agent that navigates to the AI platform and asks
    about the brand, returning the claims found.
    """
    client = _yutori()
    platform_lower = request.platform.lower()
    start_url = PLATFORM_URLS.get(platform_lower)
    if not start_url:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown platform '{request.platform}'. "
                   f"Supported: {list(PLATFORM_URLS.keys())}",
        )

    task_instruction = (
        f'Go to {request.platform} and ask: "{request.query} about {request.brand_name}". '
        f'Record the full response. Identify any factual claims made about {request.brand_name}.'
    )
    try:
        result = await client.browse(
            task=task_instruction,
            start_url=start_url,
            max_steps=request.max_steps,
            output_schema=_BROWSE_CLAIMS_SCHEMA,
        )
        resp = {
            "task_id": result.get("task_id") or result.get("id"),
            "status": result.get("status", "queued"),
            "view_url": result.get("view_url"),
        }
        if platform_lower not in NO_AUTH_PLATFORMS:
            resp["warning"] = f"{request.platform} requires login; results may be limited. Use 'perplexity' for best results."
        return resp
    except httpx.HTTPStatusError as exc:
        logger.error("Yutori browse error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.post("/browse/result")
async def get_browse_result(request: BrowseTaskStatusRequest):
    """Get the result of a browsing task (poll until complete or check status)."""
    client = _yutori()
    try:
        result = await client.get_browse_result(request.task_id)
        status = result.get("status", "unknown")
        response: dict = {
            "task_id": request.task_id,
            "status": status,
        }
        if status == "succeeded":
            structured = result.get("structured_result")
            if structured and isinstance(structured, dict):
                responses = structured.get("responses", [])
                claims = []
                for resp in responses:
                    for c in resp.get("claims_found", []):
                        claims.append({"claim": c.get("claim", ""), "context": resp.get("response", "")[:200]})
                response["claims"] = claims
                response["raw_response"] = result.get("result", "")
            else:
                response["raw_response"] = result.get("result", "")
                response["claims"] = []
        elif status == "failed":
            response["error"] = result.get("error", "Task failed")
        return response
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.post("/browse/trajectory")
async def get_browse_trajectory(request: BrowseTaskStatusRequest):
    """Get step-by-step screenshots and actions from a completed browsing task."""
    client = _yutori()
    try:
        result = await client.get_browse_trajectory(request.task_id)
        return result
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.post("/research")
async def deep_research(request: DeepResearchRequest):
    """Launch a deep investigation of a claim using Yutori Research API."""
    client = _yutori()
    brand = request.brand_name or request.brand_id
    query = (
        f'Investigate the claim: "{request.claim}" about {brand}. '
        f'Find the correct information from authoritative sources. '
        f'Trace where this claim originated. '
        f'Identify which websites and AI platforms are propagating it.'
    )
    try:
        result = await client.research(
            query=query,
            output_schema=_RESEARCH_SCHEMA,
        )
        return {
            "task_id": result.get("task_id") or result.get("id"),
            "status": result.get("status", "queued"),
            "view_url": result.get("view_url"),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("Yutori research error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")


@router.post("/research/result")
async def get_research_result(request: ResearchTaskStatusRequest):
    """Get the result of a research task."""
    client = _yutori()
    try:
        result = await client.get_research_result(request.task_id)
        status = result.get("status", "unknown")
        response: dict = {
            "task_id": request.task_id,
            "status": status,
        }
        if status == "succeeded":
            structured = result.get("structured_result")
            if structured and isinstance(structured, dict):
                response["report"] = structured.get("correct_information", "")
                response["sources"] = structured.get("misinformation_sources", [])
                response["propagation_chain"] = structured.get("propagation_chain", "")
            else:
                response["report"] = result.get("result", "")
                response["sources"] = []
                response["propagation_chain"] = ""
        elif status == "failed":
            response["error"] = result.get("error", "Task failed")
        return response
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to reach Yutori API")
