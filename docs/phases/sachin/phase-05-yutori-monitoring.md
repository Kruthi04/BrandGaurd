# Phase 5: Yutori Integration (Scouts + Browsing + Research)

**Owner**: Sachin
**Effort**: 3-4 hours
**Priority**: P0 (Continuous monitoring backbone)
**Depends on**: Phase 1 (Nihal's Setup), Phase 4 (Sachin's Neo4j — for storing results)
**Blocks**: Phase 7 (Kruthi's Dashboard), Phase 8 (Nihal's Orchestration)

---

## Overview

Integrate all 3 Yutori APIs to power BrandGuard's monitoring system. Scouts continuously watch the web for brand mentions. Browsing API directly queries AI platforms about a brand. Research API does deep investigation. This is the "always-on monitoring" capability.

---

## Reference

- Yutori patterns doc: `YUTORI_ARCHITECTURE_PATTERNS.md` (in repo root)
- Hackathon analysis: `YUTORI_HACKATHON_ANALYSIS.md` (in repo root)
- Research doc: `docs/research/neo4j-modulate-render-yutori-research.md` (Yutori section)
- Reference projects: `reference projects/LawSync/`, `reference projects/signal-trade-bot/`

### API Summary

| API | Endpoint | Purpose | Pricing |
|-----|----------|---------|---------|
| Scouting | `POST /v1/scouting/tasks` | Create persistent monitoring agent | $0.35/run |
| Browsing | `POST /v1/browsing/tasks` | On-demand browser automation | $0.015/step |
| Research | `POST /v1/research/tasks` | Deep one-time investigation | $0.35/task |

**Base URL**: `https://api.yutori.com`
**Auth**: `X-API-Key: {YUTORI_API_KEY}`

---

## Tasks

### 5.1 Yutori Service Client

- [ ] Implement `backend/app/services/yutori/client.py`:
  ```python
  class YutoriClient:
      def __init__(self, api_key: str):
          self.api_key = api_key
          self.base_url = "https://api.yutori.com"
          self.timeout = 30  # seconds

      # Scouting API
      async def create_scout(self, query: str, output_schema: dict = None,
                              interval: str = "6h") -> dict
      async def list_scouts(self) -> list
      async def get_scout(self, scout_id: str) -> dict
      async def get_scout_updates(self, scout_id: str) -> list
      async def stop_scout(self, scout_id: str) -> dict
      async def delete_scout(self, scout_id: str) -> dict

      # Browsing API
      async def browse(self, instructions: str, url: str = None,
                        output_schema: dict = None) -> dict
      async def get_browse_result(self, task_id: str) -> dict
      async def poll_browse_result(self, task_id: str, timeout: int = 300) -> dict

      # Research API
      async def research(self, query: str) -> dict
      async def get_research_result(self, task_id: str) -> dict
  ```

### 5.2 Structured Output Schema

- [ ] Create BrandGuard-specific output schema for scouts:
  ```python
  BRAND_MENTION_SCHEMA = {
      "type": "json",
      "json_schema": {
          "type": "object",
          "properties": {
              "brand_mentions": {
                  "type": "array",
                  "items": {
                      "type": "object",
                      "properties": {
                          "platform": {"type": "string", "enum": ["chatgpt", "claude", "perplexity", "gemini", "other"]},
                          "claim": {"type": "string", "description": "What the AI said about the brand"},
                          "source_url": {"type": "string"},
                          "context": {"type": "string"},
                          "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                          "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                      },
                      "required": ["platform", "claim"]
                  }
              },
              "summary": {"type": "string"},
              "total_mentions": {"type": "integer"}
          }
      }
  }
  ```

### 5.3 API Endpoints

- [ ] `POST /api/monitoring/start` — Create a Yutori scout for a brand
  ```
  Request:  { "brand_id": str, "brand_name": str }
  Response: { "scout_id": str, "status": "active" }
  ```
  Implementation:
  ```python
  scout = await yutori.create_scout(
      query=f"Monitor what AI chatbots (ChatGPT, Claude, Perplexity, Gemini) say about {brand_name}",
      output_schema=BRAND_MENTION_SCHEMA,
      interval="6h"
  )
  ```

- [ ] `POST /api/monitoring/stop` — Stop a scout
  ```
  Request:  { "scout_id": str }
  Response: { "status": "stopped" }
  ```

- [ ] `GET /api/monitoring/status` — Get all active scouts with latest updates
  ```
  Response: { "scouts": [{ "id": str, "brand_id": str, "status": str, "last_update": str, "mentions_found": int }] }
  ```

- [ ] `POST /api/webhooks/yutori` — Webhook receiver for scout updates
  ```
  Body: Yutori webhook payload with structured brand_mentions
  Action:
    1. Parse brand_mentions from structured output
    2. For each mention:
       a. Store in Neo4j (use your Phase 4 client)
       b. Trigger Nihal's pipeline (if Phase 8 is ready)
       c. Create alert if mention seems inaccurate
  ```

- [ ] `POST /api/investigate/browse` — Query an AI platform directly
  ```
  Request:  { "platform": "chatgpt"|"claude"|"perplexity"|"gemini", "query": str, "brand_name": str }
  Response: { "claims": [{ "claim": str, "context": str }], "raw_response": str }
  ```
  Implementation: Use Yutori Browsing API to navigate to the AI platform and ask about the brand

- [ ] `POST /api/investigate/research` — Deep investigation of a claim
  ```
  Request:  { "claim": str, "brand_id": str }
  Response: { "report": str, "sources": [...], "propagation_chain": [...] }
  ```

### 5.4 Polling Fallback

- [ ] Implement polling for when webhooks aren't available (local dev):
  ```python
  async def poll_scout_updates(scout_id: str):
      """Poll every 60s for new updates, process like webhook"""
  ```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/yutori/client.py` | Implement full Yutori client |
| `backend/app/api/monitoring.py` | Add monitoring + investigate endpoints |
| `backend/app/api/routes.py` | Register monitoring routes |

---

## What You Expose to Teammates

Nihal (Phase 8 Orchestration) imports your client:
```python
from app.services.yutori.client import YutoriClient
# Uses: research() in investigation pipeline
```

Kruthi (Phase 7 Dashboard) calls your endpoints:
- `POST /api/monitoring/start` — "Start Monitoring" button
- `POST /api/monitoring/stop` — "Stop" button
- `GET /api/monitoring/status` — Scout list with status indicators
- `POST /api/investigate/browse` — "Query Platform" button
- `POST /api/investigate/research` — "Deep Investigate" button

---

## What You Consume from Teammates

| Service | Owner | How You Use It |
|---------|-------|---------------|
| Neo4j Client | Sachin (self - Phase 4) | Store parsed mentions from scout updates |

**Important**: Phase 4 (Neo4j) must be done before the webhook handler can store data. You can develop the Yutori client and endpoints first, then add Neo4j storage once Phase 4 is ready.

---

## Pre-Demo Preparation

**CRITICAL**: Scouts need to run 24-48 hours before the demo to accumulate data.
- Create scouts for "Acme Corp" 2 days before demo day
- Let them run on a 6-hour interval to gather real mentions
- The seed script (Phase 4) provides fallback data if scouts don't return enough

---

## Verification Checklist

- [ ] Scout created successfully with structured output schema
- [ ] Scout returns brand_mentions in the expected JSON format
- [ ] `GET /api/monitoring/status` shows active scouts
- [ ] Webhook receives scout updates and parses mentions correctly
- [ ] Parsed mentions are stored in Neo4j with correct relationships
- [ ] Browsing API queries an AI platform and returns claims
- [ ] Research API produces an investigation report
- [ ] Polling fallback works for local development
- [ ] Yutori client importable: `from app.services.yutori.client import YutoriClient`
