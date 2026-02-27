# BrandGuard — Integration Contracts

Shared interfaces, data models, and API contracts that all team members must follow. **Do not change these without coordinating with the team.**

---

## 1. Shared Pydantic Models (backend/app/models/)

Everyone imports from the same models. These are the source of truth.

### Brand

```python
# backend/app/models/brand.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Brand(BaseModel):
    id: str
    name: str
    industry: str
    description: str
    ground_truth: list[str]  # Key facts about the brand
    monitored_since: datetime
    senso_category_id: Optional[str] = None
    yutori_scout_id: Optional[str] = None
    neo4j_node_id: Optional[str] = None
```

### Mention

```python
# backend/app/models/mention.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class Mention(BaseModel):
    id: str
    brand_id: str
    platform: Literal["chatgpt", "claude", "perplexity", "gemini"]
    claim: str                    # What the AI said about the brand
    accuracy_score: float         # 0-100 from Senso Evaluate
    is_accurate: bool             # True if accuracy_score >= 70
    severity: Literal["low", "medium", "high", "critical"]
    source_urls: list[str]        # URLs the AI cited (from Tavily)
    senso_evaluation: Optional[dict] = None  # Raw Senso response
    detected_at: datetime
    investigated: bool = False
    corrected: bool = False
```

### Threat (Alert)

```python
# backend/app/models/threat.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class Threat(BaseModel):
    id: str
    brand_id: str
    mention_id: str
    severity: Literal["low", "medium", "high", "critical"]
    title: str                    # Human-readable summary
    description: str
    platform: str
    status: Literal["open", "investigating", "corrected", "dismissed"]
    created_at: datetime
    resolved_at: Optional[datetime] = None
```

### Correction

```python
class Correction(BaseModel):
    id: str
    mention_id: str
    brand_id: str
    correction_type: Literal["blog_post", "faq", "social_media", "press_release"]
    content: str                  # Generated correction content
    senso_remediation: Optional[dict] = None  # Raw Senso remediate response
    status: Literal["draft", "published", "deployed"]
    created_at: datetime
```

---

## 2. API Endpoint Contracts

### Nihal's Endpoints (Senso + Pipeline)

```
POST /api/evaluate
  Request:  { "brand_id": str, "query": str, "platform": str }
  Response: { "accuracy_score": float, "citations": [...], "missing_info": [...], "raw": {...} }

POST /api/remediate
  Request:  { "mention_id": str, "brand_id": str }
  Response: { "correction_strategy": str, "optimized_content": str, "target_networks": [...] }

POST /api/content/ingest
  Request:  { "brand_id": str, "content": str, "title": str }
  Response: { "content_id": str, "status": "ingested" }

POST /api/content/generate
  Request:  { "brand_id": str, "mention_id": str, "format": "blog_post"|"faq"|"social_media" }
  Response: { "content": str, "format": str }

POST /api/content/search
  Request:  { "brand_id": str, "query": str }
  Response: { "results": [{ "content": str, "relevance": float }] }

POST /api/rules/setup
  Request:  { "brand_id": str, "patterns": [str] }
  Response: { "rule_id": str, "trigger_id": str, "webhook_id": str }

POST /api/webhooks/senso
  (Webhook receiver — called by Senso when rule triggers)
  Body: Senso webhook payload
  Action: Creates alert, enqueues pipeline job

POST /api/pipeline/run
  Request:  { "mention_id": str }
  Response: { "job_id": str, "status": "queued" }

GET  /api/pipeline/status/{job_id}
  Response: { "status": "queued"|"running"|"completed"|"failed", "steps": [...] }
```

### Sachin's Endpoints (Tavily + Neo4j + Yutori)

```
POST /api/search/web
  Request:  { "query": str, "topic": "general"|"news", "time_range": str }
  Response: { "results": [{ "url": str, "title": str, "content": str, "score": float }] }

POST /api/search/extract
  Request:  { "urls": [str], "query": str }
  Response: { "results": [{ "url": str, "raw_content": str, "relevant_chunks": [...] }] }

POST /api/search/map
  Request:  { "url": str, "instruction": str }
  Response: { "pages": [{ "url": str, "title": str }] }

POST /api/search/crawl
  Request:  { "url": str, "query": str, "max_pages": int }
  Response: { "results": [{ "url": str, "content": str }] }

POST /api/graph/mentions
  Request:  Mention model (see above)
  Response: { "neo4j_id": str, "relationships_created": int }

GET  /api/graph/brand/{brand_id}/health
  Response: { "overall_accuracy": float, "by_platform": { "chatgpt": float, ... }, "total_mentions": int, "threats": int }

GET  /api/graph/brand/{brand_id}/sources
  Response: { "sources": [{ "url": str, "influence_score": float, "mentions_fed": int }] }

GET  /api/graph/brand/{brand_id}/network
  Response: { "nodes": [{ "id": str, "type": str, "label": str, ... }], "edges": [{ "source": str, "target": str, "type": str }] }

POST /api/graph/corrections
  Request:  { "mention_id": str, "correction": Correction }
  Response: { "neo4j_id": str }

POST /api/monitoring/start
  Request:  { "brand_id": str }
  Response: { "scout_id": str, "status": "active" }

POST /api/monitoring/stop
  Request:  { "scout_id": str }
  Response: { "status": "stopped" }

GET  /api/monitoring/status
  Response: { "scouts": [{ "id": str, "brand_id": str, "status": str, "last_update": str }] }

POST /api/webhooks/yutori
  (Webhook receiver — called by Yutori when scout finds mentions)
  Body: Yutori structured output
  Action: Parses mentions, stores in Neo4j, creates alerts

POST /api/investigate/browse
  Request:  { "platform": str, "query": str }
  Response: { "claims": [{ "claim": str, "context": str }] }

POST /api/investigate/research
  Request:  { "claim": str, "brand_id": str }
  Response: { "report": str, "sources": [...], "propagation_chain": [...] }
```

### Kruthi's Frontend Routes

```
/                    → Dashboard (brand health overview)
/brands/:id          → Brand detail page
/alerts              → Alert list with actions
/corrections         → Correction history
/graph               → Neo4j knowledge graph visualization
/monitoring          → Scout management
/settings            → API keys, brand config
```

---

## 3. Neo4j Schema (Sachin owns, everyone reads)

### Nodes
```cypher
(:Brand {id, name, industry, description})
(:Platform {name})          -- chatgpt, claude, perplexity, gemini
(:Mention {id, claim, accuracy_score, severity, detected_at})
(:Source {url, domain, title, credibility_score})
(:Correction {id, content, type, status, created_at})
```

### Relationships
```cypher
(mention)-[:ABOUT]->(brand)
(mention)-[:FOUND_ON]->(platform)
(mention)-[:SOURCED_FROM]->(source)
(source)-[:FEEDS]->(platform)        -- source website feeds AI platform
(correction)-[:CORRECTS]->(mention)
(correction)-[:FOR_BRAND]->(brand)
(platform)-[:MENTIONS]->(brand)
(source)-[:LINKS_TO]->(source)       -- source-to-source propagation
```

---

## 4. Environment Variables (.env)

```bash
# Nihal manages these
SENSO_GEO_API_KEY=           # For apiv2.senso.ai
SENSO_GEO_BASE_URL=https://apiv2.senso.ai
SENSO_SDK_API_KEY=           # For sdk.senso.ai
SENSO_SDK_BASE_URL=https://sdk.senso.ai/api/v1
SENSO_BOT_ID=                # Senso bot identifier

# Sachin manages these
TAVILY_API_KEY=              # For api.tavily.com
NEO4J_URI=                   # Neo4j AuraDB connection URI
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=              # Neo4j password
YUTORI_API_KEY=              # For api.yutori.com

# Kruthi manages these
ASSEMBLYAI_API_KEY=          # Optional: for audio analysis
RENDER_API_KEY=              # For Render deployments
VITE_API_BASE_URL=           # Backend URL for frontend

# Shared
WEBHOOK_BASE_URL=            # Public URL for webhooks (ngrok for dev)
```

---

## 5. How to Work Separately

1. **Nihal finishes Phase 1 first** — pushes to `main`, everyone pulls
2. Each person creates their branch: `git checkout -b {name}/phase-{N}`
3. Work in your assigned directories (see file ownership below)
4. To test against teammates' APIs before they're ready, use the mock data in `tests/mocks/`
5. Merge to `main` when a phase is complete and verified

### File Ownership (Avoid Merge Conflicts)

| File/Directory | Owner | Others Can Read |
|---------------|-------|----------------|
| `backend/app/services/senso/` | Nihal | Yes |
| `backend/app/services/agent/` | Nihal | Yes |
| `backend/app/api/analysis.py` | Nihal | Yes |
| `backend/app/services/tavily/` | Sachin | Yes |
| `backend/app/services/neo4j/` | Sachin | Yes |
| `backend/app/services/yutori/` | Sachin | Yes |
| `backend/app/api/monitoring.py` | Sachin | Yes |
| `backend/app/api/graph.py` | Sachin | Yes |
| `frontend/src/**` | Kruthi | Yes |
| `render.yaml` | Kruthi | Yes |
| `backend/app/models/` | **Shared** | Coordinate changes |
| `backend/app/config/` | **Shared** | Coordinate changes |
| `backend/main.py` | **Shared** | Coordinate changes |
| `.env.example` | **Shared** | Coordinate changes |
