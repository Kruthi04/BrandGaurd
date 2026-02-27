"""Agent endpoints - autonomous orchestration and chat interface."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from uuid import uuid4

from app.services.agent.orchestrator import BrandGuardPipeline, pipeline_jobs

router = APIRouter()
logger = logging.getLogger(__name__)

pipeline = BrandGuardPipeline()

class PipelineRunRequest(BaseModel):
    """Request to trigger the full monitoring pipeline."""
    mention_id: Optional[str] = None
    mention_data: Optional[Dict[str, Any]] = None

class PipelineInvestigateRequest(BaseModel):
    """Request to trigger an investigation."""
    mention_id: str

class PipelineRemediateRequest(BaseModel):
    """Request to trigger a remediation generation."""
    mention_id: str
    brand_id: str


@router.post("/pipeline/run")
async def run_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    """Trigger the monitoring pipeline for a mention."""
    job_id = str(uuid4())
    
    # If we only got an ID, try to fetch the data (mocked for now)
    mention_data = request.mention_data or {"id": request.mention_id, "content": "mock mention text", "brand_id": "mock_brand"}
    
    background_tasks.add_task(pipeline.process_mention, mention_data, job_id)
    return {"job_id": job_id, "status": "queued"}

@router.get("/pipeline/status/{job_id}")
async def get_pipeline_status(job_id: str):
    """Check pipeline progress and get results."""
    if job_id not in pipeline_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return pipeline_jobs[job_id]

@router.post("/pipeline/investigate")
async def investigate_mention(request: PipelineInvestigateRequest, background_tasks: BackgroundTasks):
    """Trigger a deep investigation for a flagged mention."""
    job_id = str(uuid4())
    background_tasks.add_task(pipeline.investigate, request.mention_id, job_id)
    return {"job_id": job_id, "status": "queued"}

@router.post("/pipeline/remediate")
async def remediate_mention(request: PipelineRemediateRequest, background_tasks: BackgroundTasks):
    """Trigger a remediation content generation for a flagged mention."""
    job_id = str(uuid4())
    background_tasks.add_task(pipeline.remediate, request.mention_id, request.brand_id, job_id)
    return {"job_id": job_id, "status": "queued"}

# Original chat endpoints 
class AgentChatRequest(BaseModel):
    message: str
    brand_id: Optional[str] = None
    session_id: Optional[str] = None

@router.post("/agent/chat")
async def agent_chat(request: AgentChatRequest):
    """Chat with the BrandGuard AI agent."""
    raise HTTPException(status_code=501, detail="Not yet implemented")
