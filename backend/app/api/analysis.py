"""Analysis endpoints — Senso content evaluation and Modulate audio analysis."""
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.modulate.client import ModulateService

router = APIRouter()


class EvaluateContentRequest(BaseModel):
    """Request to evaluate content against brand guidelines using Senso."""
    content: str
    brand_id: str
    content_type: Optional[str] = "text"


@router.post("/evaluate")
async def evaluate_content(request: EvaluateContentRequest):
    """Evaluate content against brand guidelines using Senso GEO/Evaluate."""
    # TODO: Implement with SensoService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/rules/check")
async def check_rules(request: EvaluateContentRequest):
    """Check content against brand rules engine via Senso."""
    # TODO: Implement with SensoService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/generate")
async def generate_response(brand_id: str, context: str):
    """Generate brand-compliant response using Senso Generate."""
    # TODO: Implement with SensoService
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/audio")
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file (MP3, WAV, MP4, FLAC, OGG, etc.)"),
    brand_name: str = Form(..., description="Brand name to search for in the transcript"),
    speaker_diarization: bool = Form(True, description="Enable per-speaker labelling"),
    emotion_signal: bool = Form(True, description="Enable emotion detection per utterance"),
    fast_english: bool = Form(False, description="Use the English-optimised fast model"),
) -> dict[str, Any]:
    """Transcribe an audio file using Modulate Velma-2 and extract brand mentions.

    Returns the full transcript, duration, all utterances, and the subset of
    utterances that contain the brand name — each annotated with speaker ID,
    emotion, accent, and timestamps.
    """
    audio_bytes = await file.read()
    filename = file.filename or "audio.mp3"

    service = ModulateService()
    try:
        result = await service.analyze_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            brand_name=brand_name,
            speaker_diarization=speaker_diarization,
            emotion_signal=emotion_signal,
            fast_english=fast_english,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return result
