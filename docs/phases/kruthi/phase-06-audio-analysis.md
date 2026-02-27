# Phase 6: Audio/Voice Analysis (Optional)

**Owner**: Kruthi
**Effort**: 1-2 hours
**Priority**: P2 (Skip if time-constrained)
**Depends on**: Phase 1 (Nihal's Setup)
**Blocks**: Nothing

---

## Overview

Add voice/audio analysis for brand mentions in podcasts and videos. Uses AssemblyAI (NOT Modulate — Modulate is enterprise-only, no public API). This is a nice-to-have that adds an extra data source to the monitoring pipeline.

**Decision**: Only implement this if Phases 7 and 9 are on track. Dashboard and deployment are higher priority.

---

## Important: Modulate is NOT viable

From research: Modulate's ToxMod is enterprise-only, focused on live gaming voice chat. No public API, no free tier, no hackathon access. **Use AssemblyAI instead**:
- $50 free credits on signup
- Speech-to-text + sentiment analysis + entity detection in one API call
- Python SDK: `pip install assemblyai`

---

## Tasks

### 6.1 AssemblyAI Client

- [ ] Install: `pip install assemblyai` (add to `requirements.txt`)
- [ ] Implement `backend/app/services/modulate/client.py` (keep the filename for the sponsor tool slot):
  ```python
  import assemblyai as aai

  class AudioAnalysisClient:
      def __init__(self, api_key: str):
          aai.settings.api_key = api_key

      async def analyze_audio(self, audio_url: str, brand_name: str) -> dict:
          """
          1. Transcribe audio
          2. Detect entities (look for brand mentions)
          3. Analyze sentiment around brand mentions
          4. Return structured results
          """
          transcriber = aai.Transcriber()
          config = aai.TranscriptionConfig(
              entity_detection=True,
              sentiment_analysis=True,
          )
          transcript = transcriber.transcribe(audio_url, config=config)

          # Filter for brand mentions
          brand_mentions = []
          for entity in transcript.entities:
              if brand_name.lower() in entity.text.lower():
                  brand_mentions.append({
                      "text": entity.text,
                      "entity_type": entity.entity_type,
                      "start": entity.start,
                      "end": entity.end,
                  })

          # Get sentiment around mentions
          for sentence in transcript.sentiment_analysis:
              if brand_name.lower() in sentence.text.lower():
                  brand_mentions.append({
                      "text": sentence.text,
                      "sentiment": sentence.sentiment.value,
                      "confidence": sentence.confidence,
                  })

          return {
              "transcript_id": transcript.id,
              "brand_mentions": brand_mentions,
              "total_mentions": len(brand_mentions),
          }
  ```

### 6.2 API Endpoint

- [ ] `POST /api/analyze/audio` — Transcribe and analyze audio for brand mentions
  ```
  Request:  { "audio_url": str, "brand_name": str }
  Response: { "transcript_id": str, "brand_mentions": [...], "total_mentions": int }
  ```

### 6.3 Dashboard Integration

- [ ] Add "Audio Sources" tab to the monitoring page (if time permits)
- [ ] Show audio-sourced mentions with podcast/video icons

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/modulate/client.py` | Replace with AssemblyAI implementation |
| `backend/app/api/analysis.py` | Add audio analysis endpoint |
| `backend/requirements.txt` | Add `assemblyai` |

---

## Verification Checklist

- [ ] Audio transcription works with a test podcast URL
- [ ] Brand mentions detected and extracted
- [ ] Sentiment analysis returns positive/negative/neutral
- [ ] Endpoint returns structured response

