# Phase 2: Senso Integration (Core)

**Owner**: Nihal
**Effort**: 3-4 hours
**Priority**: P0 (Prize target — this is the #1 differentiator)
**Depends on**: Phase 1 (Setup)
**Blocks**: Phase 7 (Kruthi's Dashboard), Phase 8 (Nihal's Orchestration)

---

## Overview

Integrate both Senso API systems: the GEO Platform API (`apiv2.senso.ai`) for brand evaluation/remediation, and the Context OS SDK API (`sdk.senso.ai`) for knowledge management, content generation, and rules engine. This is the CORE of BrandGuard and the key to winning the Senso prize ($2k credits).

---

## Reference

Read the full Senso research doc: `docs/research/senso-api-research.md`

### Two API Systems

| System | Base URL | Auth | Purpose |
|--------|----------|------|---------|
| GEO Platform | `https://apiv2.senso.ai` | Bearer token | Evaluate brand accuracy, generate remediation |
| Context OS SDK | `https://sdk.senso.ai/api/v1` | X-API-Key header | Knowledge base, content gen, rules, triggers |

---

## Tasks

### 2.1 Senso Service Client

- [ ] Implement `backend/app/services/senso/client.py` with both API clients:
  ```python
  class SensoGEOClient:
      """GEO Platform API (apiv2.senso.ai)"""
      async def evaluate(self, query: str, brand: str, network: str) -> dict
      async def remediate(self, context: str, optimize_for: str, targets: list) -> dict

  class SensoSDKClient:
      """Context OS SDK API (sdk.senso.ai)"""
      async def ingest_content(self, content: str, title: str) -> dict
      async def search(self, query: str) -> dict
      async def generate(self, prompt: str, template_id: str = None) -> dict
      async def create_rule(self, name: str, conditions: dict) -> dict
      async def create_trigger(self, rule_id: str, webhook_url: str) -> dict
  ```

### 2.2 API Endpoints

- [ ] `POST /api/evaluate` — Core evaluation endpoint
  ```
  Request:  { "brand_id": str, "query": str, "platform": str }
  Response: { "accuracy_score": float, "citations": [...], "missing_info": [...] }
  ```

- [ ] `POST /api/remediate` — Generate correction strategy
  ```
  Request:  { "mention_id": str, "brand_id": str }
  Response: { "correction_strategy": str, "optimized_content": str }
  ```

- [ ] `POST /api/content/ingest` — Ingest brand ground truth into Senso
  ```
  Request:  { "brand_id": str, "content": str, "title": str }
  Response: { "content_id": str, "status": "ingested" }
  ```

- [ ] `POST /api/content/generate` — Generate correction content
  ```
  Request:  { "brand_id": str, "mention_id": str, "format": "blog_post"|"faq"|"social_media" }
  Response: { "content": str, "format": str }
  ```

- [ ] `POST /api/content/search` — Search brand knowledge base
  ```
  Request:  { "brand_id": str, "query": str }
  Response: { "results": [{ "content": str, "relevance": float }] }
  ```

### 2.3 Rules Engine

- [ ] `POST /api/rules/setup` — Set up automated misrepresentation detection:
  1. Create rule (POST `/rules`)
  2. Add rule values (POST `/rules/{id}/values`)
  3. Register webhook (POST `/webhooks`)
  4. Create trigger (POST `/triggers`) linking rule to webhook

- [ ] `POST /api/webhooks/senso` — Webhook receiver for Senso triggers:
  - Parse incoming webhook payload
  - Create a Threat/Alert record
  - Enqueue investigation job (for Phase 8)

### 2.4 Seed Data

- [ ] Create seed script for "Acme Corp" demo:
  ```python
  # scripts/seed_senso.py
  # 1. Ingest Acme Corp ground truth facts into Senso SDK
  # 2. Create categories and topics
  # 3. Set up rules for common misrepresentations
  # 4. Create prompts/templates for correction generation
  ```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/senso/client.py` | Implement GEO + SDK clients |
| `backend/app/api/analysis.py` | Add evaluate, remediate, content endpoints |
| `backend/app/api/routes.py` | Register new routes |
| `scripts/seed_senso.py` | Create — seed Acme Corp data |

---

## What You Expose to Teammates

Kruthi (Dashboard) calls these endpoints from the frontend:
- `POST /api/evaluate` — Show accuracy results on alert detail page
- `POST /api/remediate` — "Auto-Correct" button on alerts page
- `POST /api/content/generate` — Generate correction content
- `POST /api/content/search` — Search ground truth

Nihal (Phase 8 Orchestration) uses the service client directly:
- `SensoGEOClient.evaluate()` in the monitoring pipeline
- `SensoGEOClient.remediate()` in the remediation pipeline
- `SensoSDKClient.generate()` for auto-correction

---

## What You Consume from Teammates

- Sachin's Neo4j service (Phase 4) — to look up brand data, but not required for Phase 2
- Can work independently using brand data from the seed script

---

## Verification Checklist

- [ ] `POST /api/evaluate` with "Acme Corp" returns accuracy metrics
- [ ] `POST /api/remediate` generates correction content
- [ ] `POST /api/content/ingest` stores content in Senso SDK
- [ ] `POST /api/content/generate` creates formatted corrections
- [ ] `POST /api/content/search` returns ground truth results
- [ ] Senso Rules Engine webhook fires when triggered
- [ ] Seed script runs successfully and populates Senso with demo data
- [ ] All endpoints visible in FastAPI `/docs`
