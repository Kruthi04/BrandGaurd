# Phase 8: Agent Orchestration Pipeline

**Owner**: Nihal
**Effort**: 3-4 hours
**Priority**: P1 (Can simplify for demo, but needed for "autonomous" claim)
**Depends on**: Phase 2 (Senso), Phase 3 (Tavily), Phase 4 (Neo4j), Phase 5 (Yutori)
**Blocks**: Phase 9 (Kruthi's Deploy)

---

## Overview

Build the autonomous pipeline that connects all 6 sponsor tools into an end-to-end agent. When a Yutori scout detects a brand mention, the pipeline automatically: evaluates accuracy (Senso), traces sources (Tavily), maps the network (Neo4j), generates corrections (Senso), and creates alerts. This is what makes BrandGuard an "autonomous agent" rather than just a dashboard.

---

## Architecture

```
Yutori Scout Update (webhook)
  |
  v
[Monitoring Pipeline]
  1. Parse structured mention data
  2. Senso Evaluate → accuracy score
  3. Tavily Search → find cited sources
  4. Severity scoring (threshold check)
  5. Neo4j → store mention + relationships
  6. If severity >= HIGH → create alert
  7. If severity >= CRITICAL → auto-enqueue remediation
  |
  v
[Investigation Pipeline] (on-demand or auto)
  1. Tavily Extract → full content from flagged URLs
  2. Tavily Map → discover related pages
  3. Yutori Research → deep investigation
  4. Neo4j → add Source nodes, FEEDS relationships
  |
  v
[Remediation Pipeline] (on-demand or auto)
  1. Senso Evaluate → detailed accuracy report
  2. Senso Remediate → correction strategy
  3. Senso Generate → formatted content (blog, FAQ)
  4. Neo4j → create Correction node
  5. Senso Content Ingest → store as new ground truth
```

---

## Tasks

### 8.1 Pipeline Service

- [ ] Implement `backend/app/services/agent/orchestrator.py`:
  ```python
  class BrandGuardPipeline:
      def __init__(self, senso, tavily, neo4j, yutori):
          # Accept service clients from Nihal (Senso) and Sachin (Tavily, Neo4j, Yutori)

      async def process_mention(self, mention_data: dict) -> dict:
          """Full monitoring pipeline for a single mention"""
          # 1. Senso evaluate
          # 2. Tavily search for sources
          # 3. Score severity
          # 4. Store in Neo4j
          # 5. Create alert if needed
          # 6. Return pipeline result

      async def investigate(self, mention_id: str) -> dict:
          """Deep investigation of a flagged mention"""
          # 1. Tavily extract from source URLs
          # 2. Tavily map related pages
          # 3. Yutori research
          # 4. Update Neo4j graph

      async def remediate(self, mention_id: str) -> dict:
          """Auto-generate correction for a mention"""
          # 1. Senso evaluate (detailed)
          # 2. Senso remediate
          # 3. Senso generate content
          # 4. Store correction in Neo4j
  ```

### 8.2 Background Task Runner

- [ ] Use FastAPI `BackgroundTasks` for async pipeline execution:
  ```python
  @router.post("/api/pipeline/run")
  async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
      job_id = str(uuid4())
      background_tasks.add_task(pipeline.process_mention, request.mention_data, job_id)
      return {"job_id": job_id, "status": "queued"}
  ```

- [ ] Store job status in-memory dict (good enough for hackathon):
  ```python
  pipeline_jobs: dict[str, dict] = {}
  # {"job_id": {"status": "running", "steps": [...], "result": None}}
  ```

### 8.3 API Endpoints

- [ ] `POST /api/pipeline/run` — Trigger pipeline for a mention
  ```
  Request:  { "mention_id": str } or { "mention_data": dict }
  Response: { "job_id": str, "status": "queued" }
  ```

- [ ] `GET /api/pipeline/status/{job_id}` — Check pipeline progress
  ```
  Response: {
    "status": "running",
    "steps": [
      { "name": "senso_evaluate", "status": "completed", "result": {...} },
      { "name": "tavily_search", "status": "running" },
      { "name": "neo4j_store", "status": "pending" }
    ]
  }
  ```

- [ ] `POST /api/pipeline/investigate` — Trigger investigation
- [ ] `POST /api/pipeline/remediate` — Trigger remediation

### 8.4 Webhook Integration

- [ ] Update `POST /api/webhooks/yutori` (Sachin's endpoint) to call pipeline:
  - When Yutori webhook arrives, parse mentions, then call `pipeline.process_mention()` for each
  - Coordinate with Sachin on this — he owns the webhook, you own the pipeline

- [ ] Update `POST /api/webhooks/senso` to handle rule triggers:
  - When Senso rules fire, create alert and optionally auto-investigate

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/agent/orchestrator.py` | Implement full pipeline |
| `backend/app/api/agent.py` | Add pipeline endpoints |
| `backend/app/api/routes.py` | Register pipeline routes |

---

## What You Consume from Teammates

| Service | Owner | How You Use It |
|---------|-------|---------------|
| `SensoGEOClient` | Nihal (self) | Evaluate + Remediate in pipeline |
| `SensoSDKClient` | Nihal (self) | Generate + Ingest in remediation |
| `TavilyClient` | Sachin | Search + Extract + Map in investigation |
| `Neo4jClient` | Sachin | Store mentions, sources, corrections |
| `YutoriClient` | Sachin | Research for deep investigation |

**Important**: Import Sachin's service clients. Do NOT rewrite them. Use:
```python
from app.services.tavily.client import TavilyClient
from app.services.neo4j.client import Neo4jClient
from app.services.yutori.client import YutoriClient
```

---

## What You Expose to Teammates

Kruthi (Dashboard) calls:
- `POST /api/pipeline/run` — "Run Pipeline" button
- `GET /api/pipeline/status/{job_id}` — Show pipeline progress in UI
- `POST /api/pipeline/investigate` — "Investigate" button on alerts
- `POST /api/pipeline/remediate` — "Auto-Correct" button on alerts

---

## Demo Flow Integration

This pipeline is what makes the demo work end-to-end:
1. Show dashboard → mention detected (from Yutori scout)
2. Click "Investigate" → pipeline runs investigation
3. Graph updates in real-time with source mapping
4. Click "Auto-Correct" → pipeline generates correction
5. Correction appears in corrections page

For the demo, pre-seed some pipeline results so there's no waiting.

---

## Verification Checklist

- [ ] `POST /api/pipeline/run` triggers full monitoring pipeline
- [ ] Pipeline steps execute in order: evaluate → search → score → store → alert
- [ ] `GET /api/pipeline/status/{job_id}` shows real-time step progress
- [ ] Investigation enriches Neo4j graph with source data
- [ ] Remediation generates correction and stores in Neo4j
- [ ] Yutori webhook triggers pipeline automatically
- [ ] Pipeline handles errors gracefully (retry or skip step)
