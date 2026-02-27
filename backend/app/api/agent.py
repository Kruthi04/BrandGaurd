"""Agent endpoints - autonomous orchestration and chat interface."""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.agent.orchestrator import (
    AgentOrchestrator,
    get_task,
    store_task,
    list_tasks,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class AgentChatRequest(BaseModel):
    """Request to interact with the BrandGuard agent."""
    message: str
    brand_id: Optional[str] = None
    session_id: Optional[str] = None


class AgentTaskRequest(BaseModel):
    """Request to start an autonomous agent task."""
    task_type: str  # full_scan, threat_assessment, compliance_check
    brand_id: str
    parameters: Optional[dict] = None


def _orchestrator() -> AgentOrchestrator:
    try:
        return AgentOrchestrator()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}")


@router.post("/chat")
async def agent_chat(request: AgentChatRequest):
    """Chat with the BrandGuard AI agent."""
    orchestrator = _orchestrator()
    try:
        result = await orchestrator.chat(
            message=request.message,
            brand_id=request.brand_id,
            session_id=request.session_id,
        )
        return result
    except Exception as exc:
        logger.error("Agent chat failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/tasks")
async def start_agent_task(request: AgentTaskRequest):
    """Start an autonomous agent task (scan, assessment, etc.)."""
    orchestrator = _orchestrator()
    params = request.parameters or {}

    try:
        if request.task_type == "full_scan":
            result = await orchestrator.run_full_scan(request.brand_id)
        elif request.task_type == "threat_assessment":
            result = await orchestrator.run_threat_assessment(request.brand_id)
        elif request.task_type == "compliance_check":
            content = params.get("content", "")
            if not content:
                raise HTTPException(
                    status_code=422,
                    detail="compliance_check requires 'content' in parameters",
                )
            result = await orchestrator.run_compliance_check(request.brand_id, content)
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown task_type '{request.task_type}'. "
                       f"Supported: full_scan, threat_assessment, compliance_check",
            )

        store_task(result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Agent task failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a completed agent task."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.get("/tasks")
async def list_agent_tasks(status: Optional[str] = None):
    """List all agent tasks."""
    return {"tasks": list_tasks(status=status)}
