"""Agent endpoints - autonomous orchestration and chat interface."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

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


@router.post("/chat")
async def agent_chat(request: AgentChatRequest):
    """Chat with the BrandGuard AI agent."""
    # TODO: Implement with AgentOrchestrator
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/tasks")
async def start_agent_task(request: AgentTaskRequest):
    """Start an autonomous agent task (scan, assessment, etc.)."""
    # TODO: Implement with AgentOrchestrator
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a running agent task."""
    # TODO: Implement with AgentOrchestrator
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/tasks")
async def list_tasks(status: Optional[str] = None):
    """List all agent tasks."""
    # TODO: Implement with AgentOrchestrator
    raise HTTPException(status_code=501, detail="Not yet implemented")
