"""Brand data models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandCreate(BaseModel):
    """Request model for creating a brand profile."""
    name: str
    description: Optional[str] = None
    keywords: list[str] = []
    domains: list[str] = []


class Brand(BrandCreate):
    """Brand profile stored in the system."""
    id: str
    created_at: datetime
    updated_at: datetime
    reputation_score: Optional[float] = None
    active_scouts: int = 0
    total_mentions: int = 0
