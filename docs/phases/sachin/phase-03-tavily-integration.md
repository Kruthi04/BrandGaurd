# Phase 3: Tavily Integration (Search & Crawl)

**Owner**: Sachin
**Effort**: 2-3 hours
**Priority**: P0 (Source investigation is key to the demo)
**Depends on**: Phase 1 (Nihal's Setup)
**Blocks**: Phase 7 (Kruthi's Dashboard), Phase 8 (Nihal's Orchestration)

---

## Overview

Integrate Tavily's 4 APIs to power the source investigation pipeline. When BrandGuard detects a misrepresentation, Tavily finds WHERE the misinformation originated — which websites are AI models citing, what content those sites have, and how they're connected. This is the "trace the source" capability.

---

## Reference

Read the full Tavily research doc: `docs/research/tavily-api-research.md`

### API Endpoints

| Endpoint | Purpose | Credits |
|----------|---------|---------|
| `POST https://api.tavily.com/search` | Web search | 1-2/request |
| `POST https://api.tavily.com/extract` | Content extraction from URLs | 1/5 URLs |
| `POST https://api.tavily.com/map` | Site structure discovery | 1/10 pages |
| `POST https://api.tavily.com/crawl` | Combined Map + Extract | Variable |

**Auth**: `Authorization: Bearer {TAVILY_API_KEY}` OR `api_key` field in request body
**Free tier**: 1,000 credits/month
**Rate limits**: 100 RPM (dev), 1,000 RPM (prod)

---

## Tasks

### 3.1 Tavily Service Client

- [ ] Implement `backend/app/services/tavily/client.py`:
  ```python
  class TavilyClient:
      def __init__(self, api_key: str):
          self.api_key = api_key
          self.base_url = "https://api.tavily.com"

      async def search(self, query: str, topic: str = "general",
                       time_range: str = None, max_results: int = 10,
                       include_answer: bool = True) -> dict:
          """Search the web for brand-related claims"""

      async def extract(self, urls: list[str], query: str = None) -> dict:
          """Extract full content from specific URLs"""

      async def map(self, url: str, instruction: str = None,
                    max_pages: int = 10) -> dict:
          """Map the structure of a website"""

      async def crawl(self, url: str, query: str = None,
                      max_pages: int = 10) -> dict:
          """Combined map + extract for comprehensive site analysis"""
  ```

### 3.2 API Endpoints

- [ ] `POST /api/search/web` — Find brand mentions and citations on the web
  ```
  Request:  { "query": str, "topic": "general"|"news", "time_range": "day"|"week"|"month", "max_results": int }
  Response: { "results": [{ "url": str, "title": str, "content": str, "score": float }], "answer": str }
  ```

- [ ] `POST /api/search/extract` — Extract full content from flagged URLs
  ```
  Request:  { "urls": [str], "query": str }
  Response: { "results": [{ "url": str, "raw_content": str }], "failed": [str] }
  ```

- [ ] `POST /api/search/map` — Discover pages on a misinformation source
  ```
  Request:  { "url": str, "instruction": "Find pages mentioning {brand}" }
  Response: { "pages": [{ "url": str }] }
  ```

- [ ] `POST /api/search/crawl` — Full site analysis of a misinformation source
  ```
  Request:  { "url": str, "query": str, "max_pages": int }
  Response: { "results": [{ "url": str, "content": str }] }
  ```

### 3.3 Helper: Source Analyzer

- [ ] Create utility function that combines search + extract for investigation:
  ```python
  async def analyze_claim_sources(claim: str, brand: str) -> dict:
      """
      1. Search web for the claim
      2. Extract content from top results
      3. Return analyzed sources with relevance scores
      """
  ```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/tavily/client.py` | Implement full Tavily client |
| `backend/app/api/monitoring.py` | Add search endpoints (or create new `search.py`) |
| `backend/app/api/routes.py` | Register search routes |

---

## What You Expose to Teammates

Nihal (Phase 8 Orchestration) imports your client directly:
```python
from app.services.tavily.client import TavilyClient
# Uses: search(), extract(), map() in the investigation pipeline
```

Kruthi (Phase 7 Dashboard) calls your endpoints:
- `POST /api/search/web` — "Investigate" button shows search results
- `POST /api/search/extract` — Show extracted content from source URLs
- `POST /api/search/map` — Show site structure of misinformation source

---

## What You Consume from Teammates

Nothing — Tavily is fully independent. You only need Phase 1 (env setup + API key).

---

## Verification Checklist

- [ ] `POST /api/search/web` with `"Acme Corp AI accuracy"` returns relevant results
- [ ] `POST /api/search/extract` extracts content from a test URL
- [ ] `POST /api/search/map` discovers pages on a test domain
- [ ] `POST /api/search/crawl` returns combined map + extract results
- [ ] All endpoints handle errors gracefully (invalid URLs, rate limits)
- [ ] All endpoints visible in FastAPI `/docs`
- [ ] Tavily client importable by Nihal: `from app.services.tavily.client import TavilyClient`
