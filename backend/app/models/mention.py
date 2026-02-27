"""Mention data models for tracked brand references."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SentimentScore(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CRITICAL = "critical"


class MentionCreate(BaseModel):
    """Data for a new brand mention."""
    brand_id: str
    source_url: str
    content: str
    platform: str
    author: Optional[str] = None


class Mention(MentionCreate):
    """A tracked brand mention."""
    id: str
    detected_at: datetime
    sentiment: SentimentScore = SentimentScore.NEUTRAL
    compliance_score: Optional[float] = None
    threat_level: Optional[str] = None
    scout_id: Optional[str] = None
