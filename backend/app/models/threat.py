"""Threat data models for reputation risks."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCreate(BaseModel):
    """Data for a new threat."""
    brand_id: str
    title: str
    description: str
    source_url: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.MEDIUM


class Threat(ThreatCreate):
    """A reputation threat tracked in the system."""
    id: str
    detected_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    related_mentions: list[str] = []
