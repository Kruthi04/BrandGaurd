"""Scout data models for Yutori monitoring tasks."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Scout(BaseModel):
    """A Yutori scouting task."""
    id: str
    brand_id: str
    query: str
    display_name: str
    status: str = "active"
    output_interval: int = 86400
    created_at: datetime
    next_run: Optional[datetime] = None


class ScoutUpdate(BaseModel):
    """An update received from a Yutori scout."""
    id: str
    scout_id: str
    content: str
    citations: list[dict] = []
    created_at: datetime
