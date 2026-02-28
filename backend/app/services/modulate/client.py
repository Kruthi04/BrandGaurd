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


    async def analyze_youtube(
        self,
        youtube_url: str,
        brand_name: str,
    ) -> dict[str, Any]:
        """Download audio from a YouTube video and analyze it for brand mentions.

        Args:
            youtube_url: YouTube video URL.
            brand_name: Brand name to filter mentions by.

        Returns:
            Transcript, brand mentions, video metadata, and sentiment data.
        """
        import tempfile
        import os
        import subprocess
        import json as _json

        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "audio.%(ext)s")

            js_runtime = ["--js-runtimes", "node", "--remote-components", "ejs:github"]

            # Extract video metadata
            meta_cmd = [
                "yt-dlp", *js_runtime, "--dump-json", "--no-download", youtube_url,
            ]
            meta_result = subprocess.run(
                meta_cmd, capture_output=True, text=True, timeout=30,
            )
            video_meta = {}
            if meta_result.returncode == 0:
                try:
                    info = _json.loads(meta_result.stdout)
                    video_meta = {
                        "title": info.get("title", ""),
                        "channel": info.get("channel", info.get("uploader", "")),
                        "duration_seconds": info.get("duration", 0),
                        "view_count": info.get("view_count", 0),
                        "upload_date": info.get("upload_date", ""),
                        "description": (info.get("description") or "")[:500],
                    }
                except _json.JSONDecodeError:
                    pass

            # Download audio (extract only, keep original format to avoid ffmpeg dependency)
            dl_cmd = [
                "yt-dlp",
                *js_runtime,
                "-x",
                "-o", output_template,
                "--no-playlist",
                "--max-filesize", "50M",
                youtube_url,
            ]
            dl_result = subprocess.run(
                dl_cmd, capture_output=True, text=True, timeout=180,
            )
            if dl_result.returncode != 0:
                raise RuntimeError(f"Failed to download audio: {dl_result.stderr[:300]}")

            # Find the downloaded file (extension varies)
            actual_path = None
            for f in os.listdir(tmpdir):
                if f.startswith("audio.") and not f.endswith(".part"):
                    actual_path = os.path.join(tmpdir, f)
                    break

            if not actual_path or not os.path.exists(actual_path):
                raise RuntimeError("Audio file not found after download")

            with open(actual_path, "rb") as f:
                audio_bytes = f.read()

            filename = os.path.basename(actual_path)

        if self.api_key:
            result = await self.analyze_audio(
                audio_bytes=audio_bytes,
                filename=filename,
                brand_name=brand_name,
            )
        else:
            brand_lower = brand_name.lower()
            desc_lower = video_meta.get("description", "").lower()
            title_lower = video_meta.get("title", "").lower()
            mentions = []
            if brand_lower in title_lower:
                mentions.append({
                    "text": video_meta.get("title", ""),
                    "location": "title",
                    "sentiment": "neutral",
                })
            if brand_lower in desc_lower:
                for line in video_meta.get("description", "").split("\n"):
                    if brand_lower in line.lower():
                        mentions.append({
                            "text": line.strip()[:200],
                            "location": "description",
                            "sentiment": "neutral",
                        })

            result = {
                "text": f"[Audio downloaded: {len(audio_bytes)} bytes — Modulate API key required for full transcription]",
                "duration_ms": video_meta.get("duration_seconds", 0) * 1000,
                "brand_mentions": mentions,
                "total_mentions": len(mentions),
                "all_utterances": [],
                "note": "Set MODULATE_API_KEY for full speech-to-text transcription and sentiment analysis",
            }

        result["video_metadata"] = video_meta
        result["youtube_url"] = youtube_url
        result["audio_size_bytes"] = len(audio_bytes)
        return result


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
