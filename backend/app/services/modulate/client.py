"""Modulate Velma-2 API client for voice/audio transcription and brand mention analysis.

Velma-2 capabilities used:
- Speech-to-text (70+ languages)
- Speaker diarization
- Emotion detection per utterance
- Accent identification

Docs: https://modulate-developer-apis.com/web/docs.html
"""
from typing import Any

import httpx

from app.config import settings

BATCH_ENDPOINT = "/api/velma-2-stt-batch"
BATCH_FAST_ENDPOINT = "/api/velma-2-stt-batch-english-vfast"


class ModulateService:
    """Client for the Modulate Velma-2 speech-to-text API."""

    def __init__(self):
        self.api_key = settings.MODULATE_API_KEY
        self.base_url = settings.MODULATE_API_BASE_URL.rstrip("/")

    async def analyze_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        brand_name: str,
        speaker_diarization: bool = True,
        emotion_signal: bool = True,
        fast_english: bool = False,
    ) -> dict[str, Any]:
        """Transcribe audio and extract utterances that mention the brand.

        Args:
            audio_bytes: Raw audio file content.
            filename: Original filename (used to infer content-type).
            brand_name: Brand name to filter utterances by.
            speaker_diarization: Enable per-speaker labelling.
            emotion_signal: Enable emotion detection per utterance.
            fast_english: Use the English-optimised fast model instead of multilingual.

        Returns:
            {
                "text": str,                  # full transcript
                "duration_ms": int,
                "brand_mentions": [           # utterances containing the brand name
                    {
                        "text": str,
                        "start_ms": int,
                        "duration_ms": int,
                        "speaker": int,
                        "language": str,
                        "emotion": str,
                        "accent": str,
                        "utterance_uuid": str,
                    },
                    ...
                ],
                "total_mentions": int,
                "all_utterances": [...],      # full utterance list for reference
            }
        """
        endpoint = BATCH_FAST_ENDPOINT if fast_english else BATCH_ENDPOINT
        url = f"{self.base_url}{endpoint}"

        content_type = _content_type_for(filename)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={"X-API-Key": self.api_key},
                files={"upload_file": (filename, audio_bytes, content_type)},
                data={
                    "speaker_diarization": str(speaker_diarization).lower(),
                    "emotion_signal": str(emotion_signal).lower(),
                },
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Modulate API error {response.status_code}: {response.text}"
            )

        payload: dict[str, Any] = response.json()

        brand_lower = brand_name.lower()
        brand_mentions = [
            u for u in payload.get("utterances", [])
            if brand_lower in u.get("text", "").lower()
        ]

        return {
            "text": payload.get("text", ""),
            "duration_ms": payload.get("duration_ms", 0),
            "brand_mentions": brand_mentions,
            "total_mentions": len(brand_mentions),
            "all_utterances": payload.get("utterances", []),
        }

    async def check_voice_safety(self, audio_bytes: bytes, filename: str) -> dict[str, Any]:
        """Transcribe audio and return full utterance list with emotion/accent data."""
        return await self.analyze_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            brand_name="",          # no brand filter — return everything
            speaker_diarization=True,
            emotion_signal=True,
        )


def _content_type_for(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    mapping = {
        "mp3": "audio/mpeg",
        "mp4": "video/mp4",
        "mov": "video/quicktime",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
        "opus": "audio/opus",
        "webm": "audio/webm",
        "aac": "audio/aac",
        "aiff": "audio/aiff",
    }
    return mapping.get(ext, "application/octet-stream")
