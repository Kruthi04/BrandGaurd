# BrandGuard -- System Architecture Design Document

**Date**: 2026-02-27
**Project**: BrandGuard -- Autonomous AI Reputation Monitoring Agent
**Hackathon**: MCP - AWS - Enterprise Agents Challenge (July 25, 2025)
**Target Prizes**: Senso ($2k credits), Tavily ($1k + credits), Best AWS AI Use ($10k)
**Requirement**: Use at least 3 sponsor tools

---

## 1. Product Vision

BrandGuard is an autonomous AI agent that monitors how AI systems (ChatGPT, Claude, Perplexity, Gemini) describe a brand, detects misrepresentations, traces misinformation sources, maps propagation networks in a knowledge graph, and auto-generates GEO-optimized correction content -- all from a single dashboard.

### Why This Wins

1. **Real enterprise pain** -- brands have no visibility into what AI chatbots say about them
2. **6 sponsor tool integrations** (Yutori x3 APIs, Senso x2 API systems, Tavily x3 endpoints, Neo4j, Render, + bonus Yutori n1)
3. **End-to-end autonomous pipeline** -- from detection to correction, no human in the loop
4. **AI-on-AI layering** -- Yutori gathers, Senso evaluates, Claude analyzes, Senso generates corrections
5. **Knowledge graph visualization** -- interactive misinformation network map
6. **150+ line structured output schemas** -- signals deep platform understanding

---

## 2. Demo Flow (3-Minute Hackathon Pitch)

**Pre-seeded state**: "Acme Corp" monitored for 48 hours, 20+ mentions, 8 flagged inaccurate.

| Minute | Action | Tools Shown |
|--------|--------|-------------|
| 0:00-0:40 | Open dashboard. Show brand health score (73/100), per-platform accuracy breakdown, 3 active alerts. | Neo4j graph query, React dashboard |
| 0:40-1:20 | Click Perplexity alert: "Acme Corp was founded in 1990". Show Senso Evaluate results -- accuracy 34%, missing citations. Show the full AI response. | Senso GEO /evaluate |
| 1:20-2:00 | Click "Investigate". Tavily Search finds source: outdated blog post. Tavily Extract pulls full content. Switch to knowledge graph -- see propagation path: `outdated-blog.com -> Perplexity -> Gemini`. | Tavily Search + Extract, Neo4j viz |
| 2:00-2:40 | Click "Auto-Correct". Senso Remediate generates GEO-optimized correction. Senso Generate creates a corrected FAQ. Show before/after. | Senso GEO /remediate, Senso SDK /generate |
| 2:40-3:00 | Trigger live scan. Yutori Browsing task checks Claude. Show webhook arriving in real-time. Close on the knowledge graph with full misinformation network. | Yutori Browsing, webhook live |

---

## 3. Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | React 18 + TypeScript + Vite 5 (SWC) + Tailwind CSS 4 + shadcn/ui | Fast HMR, rich components, matches LawSync (hackathon winner) |
| **State** | TanStack React Query 5 | Server state caching, polling intervals, optimistic updates |
| **Graph Viz** | react-force-graph-2d | Interactive Neo4j graph rendering, WebGL-accelerated |
| **Charts** | Recharts | Accuracy trends, share-of-voice bar charts |
| **Routing** | React Router DOM 6 | Client-side routing, lazy loading |
| **Backend** | Python 3.11 + FastAPI | Async-native, auto-docs, Senso/Tavily Python SDKs |
| **Graph DB** | Neo4j AuraDB Free | 200k nodes/400k rels, graph-native misinformation mapping |
| **Task Queue** | FastAPI BackgroundTasks + asyncio | Lightweight, no Redis needed for hackathon |
| **Deployment** | Render (render.yaml IaC) | Free tier, auto-deploy from Git |

### Why React + Vite + FastAPI (not Next.js)?

1. **Senso Python SDK** (`senso_developers`) -- official SDK is Python-only
2. **Tavily Python SDK** (`tavily-python`) -- mature, async-ready
3. **Neo4j Python driver** -- well-supported, matches FastAPI async
4. **LawSync pattern** -- hackathon winner used React + Vite frontend with Python FastAPI backend
5. **Separation of concerns** -- frontend (Render static site) and backend (Render web service) deploy independently
6. **FastAPI auto-docs** -- /docs endpoint for judges to explore the API

---

## 4. Service Architecture

```
                        +---------------------+
                        |   React Dashboard   |
                        |  Vite + shadcn/ui   |
                        |  (Render Static)    |
                        +---------+-----------+
                                  |
                                  | REST API (CORS)
                                  v
                        +---------------------+
                        |   FastAPI Backend   |
                        |   (Render Web Svc)  |
                        +---------+-----------+
                                  |
               +------------------+------------------+
               |                  |                  |
               v                  v                  v
        +----------+       +----------+       +----------+
        |  Yutori  |       |  Senso   |       |  Tavily  |
        | Scout    |       | GEO API  |       | Search   |
        | Browse   |       | (apiv2)  |       | Extract  |
        | Research |       |          |       | Map/Crawl|
        +----------+       | SDK API  |       +----------+
               |            | (sdk)   |              |
               |            +----------+             |
               |                  |                  |
               +------------------+------------------+
                                  |
                                  v
                        +---------------------+
                        |  Neo4j AuraDB Free  |
                        |  Knowledge Graph    |
                        +---------------------+
```

### Backend Module Organization

```
backend/
  app/
    __init__.py
    main.py                      # FastAPI app, CORS, lifespan (driver init/close)
    config.py                    # Env validation singleton (like LawSync)
    api/
      __init__.py
      brands.py                  # POST/GET/PUT/DELETE /api/brands
      monitoring.py              # POST /api/brands/{id}/scan, GET .../status
      mentions.py                # GET /api/brands/{id}/mentions, POST .../investigate
      graph.py                   # GET /api/brands/{id}/graph (nodes/edges for viz)
      corrections.py             # POST /api/mentions/{id}/correct, GET history
      webhooks.py                # POST /api/webhooks/yutori, .../senso
      health.py                  # GET /health
    services/
      __init__.py
      yutori_service.py          # Scouting + Browsing + Research client
      senso_service.py           # GEO Evaluate/Remediate + SDK Generate/Search/Rules
      tavily_service.py          # Search + Extract + Map + Crawl
      neo4j_service.py           # Graph CRUD + visualization queries
      pipeline.py                # Autonomous orchestration engine
    models/
      __init__.py
      schemas.py                 # Pydantic request/response models
      yutori_schemas.py          # 150+ line structured output schemas
  requirements.txt
  .env.example
```

---

## 5. Data Flow Architecture

### 5.1 Brand Onboarding

```
User enters brand name + ground truth data
  |
  v
POST /api/brands
  |
  +-> Neo4j: CREATE (b:Brand {name, industry, monitored_since})
  +-> Senso SDK: POST /content/raw  (ingest ground truth)
  +-> Senso SDK: POST /categories + /topics  (organize knowledge)
  +-> Senso SDK: POST /rules + /rules/{id}/values  (misrepresentation patterns)
  +-> Senso SDK: POST /webhooks + /triggers  (automated alerting)
  +-> Yutori: POST /v1/scouting/tasks  (create scout with structured schema)
  |
  v
Brand is now actively monitored
```

### 5.2 Continuous Monitoring Pipeline (Autonomous)

```
Yutori Scout Update (webhook or polling)
  |
  v
POST /api/webhooks/yutori
  |
  v
Parse structured_result -> brand_mentions[]
  |
  v
For each mention:
  |
  +-> Senso GEO: POST /evaluate
  |     query=mention.query_used, brand=brand_name, network=mention.platform
  |     Returns: accuracy_score, citation_quality, share_of_voice
  |
  +-> Neo4j: MERGE (p:Platform), CREATE (m:Mention)-[:ABOUT]->(Brand)
  |          CREATE (m)-[:FOUND_ON]->(p)
  |
  +-> If mention.accuracy in (inaccurate, partially_accurate):
  |     |
  |     +-> Tavily: POST /search  (find source URLs)
  |     +-> Tavily: POST /extract  (get full content from top sources)
  |     |
  |     v
  |   Neo4j: CREATE (s:Source)-[:SOURCED_FROM]-(m)
  |          MERGE (s)-[:FEEDS]->(p)
  |     |
  |     +-> If severity in (critical, high):
  |           |
  |           +-> Senso GEO: POST /remediate  (GEO-optimized correction)
  |           +-> Senso SDK: POST /generate  (formatted correction content)
  |           |
  |           v
  |         Neo4j: CREATE (c:Correction)-[:CORRECTS]->(m)
  |
  v
Dashboard: Polling picks up new data via TanStack Query
```

### 5.3 On-Demand Investigation Pipeline

```
User clicks "Investigate" on a flagged mention
  |
  v
POST /api/mentions/{id}/investigate
  |
  +-> Tavily: POST /search  (find web sources for the claim)
  +-> Tavily: POST /extract  (extract content from flagged URLs)
  +-> Tavily: POST /map      (discover all brand pages on source site)
  +-> Yutori: POST /v1/research/tasks  (deep investigation)
  |
  v
Poll Yutori research task until complete
  |
  v
Parse propagation chain from research results
  |
  v
Neo4j: Build full propagation subgraph
  Source A --FEEDS--> Perplexity --mentions--> Claim X
  Source A --FEEDS--> Gemini --mentions--> Claim X
  Source B --LINKS_TO--> Source A
  |
  v
Dashboard: Graph Explorer shows updated network
```

### 5.4 Remediation Pipeline

```
Auto-triggered (severity >= HIGH) or user clicks "Auto-Correct"
  |
  v
POST /api/mentions/{id}/correct
  |
  +-> Senso GEO: POST /evaluate  (get full accuracy diagnostics)
  +-> Senso GEO: POST /remediate
  |     context=brand_ground_truth
  |     optimize_for="mentions"
  |     target_networks=[platform]
  |     Returns: GEO-optimized correction content
  |
  +-> Senso SDK: POST /generate
  |     content_type="correction_faq" or "correction_blog"
  |     instructions="Write a correction for: {claim}. Correct info: {ground_truth}"
  |     Returns: formatted correction with sources
  |
  +-> Senso SDK: POST /content/raw  (store correction as new ground truth)
  |
  +-> Neo4j: CREATE (c:Correction {method, content, status})-[:CORRECTS]->(m)
  |
  v
Dashboard: Show correction in review panel, before/after comparison
```

---

## 6. Sponsor Tool Integration Details

### 6.1 Yutori -- 3 API Products, 8+ Endpoints

**Scouting API** (continuous monitoring):
- One scout per brand, structured output schema with 150+ lines
- Webhook delivery to `/api/webhooks/yutori`
- Output interval: 3600s (hourly)
- Sequential polling fallback for reliability

**Browsing API** (on-demand spot-checks):
- Direct queries to AI platforms (ChatGPT, Claude, Gemini, Perplexity)
- Agent: `navigator-n1-latest` ($0.015/step)
- Structured output schema for parsed responses
- Used during live demo for real-time check

**Research API** (deep investigation):
- Triggered when investigating specific misinformation claims
- Traces propagation chains across web sources
- Structured output schema for investigation results

**Structured Output Schema (Scouting):**

```python
BRAND_MONITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "brand_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["chatgpt", "claude", "perplexity", "gemini",
                                 "copilot", "meta_ai"],
                        "description": "AI platform where mention was found"
                    },
                    "query_used": {
                        "type": "string",
                        "description": "The prompt that triggered this AI response"
                    },
                    "claim": {
                        "type": "string",
                        "description": "Specific factual claim about the brand"
                    },
                    "full_response_excerpt": {
                        "type": "string",
                        "description": "Relevant excerpt from AI response"
                    },
                    "accuracy": {
                        "type": "string",
                        "enum": ["accurate", "inaccurate", "partially_accurate",
                                 "unverifiable", "outdated"],
                        "description": "Assessment of claim accuracy"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["founding_date", "products", "pricing",
                                 "partnerships", "leadership", "financials",
                                 "competitors", "location", "mission", "other"],
                        "description": "Category of the brand claim"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"],
                        "description": "Impact severity if inaccurate"
                    },
                    "source_urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "URLs cited by AI platform for this claim"
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Evidence supporting accuracy assessment"
                    },
                    "suggested_correction": {
                        "type": "string",
                        "description": "What the correct information should be"
                    }
                },
                "required": ["platform", "claim", "accuracy", "category", "severity"]
            }
        },
        "platforms_checked": {
            "type": "array",
            "items": {"type": "string"},
            "description": "AI platforms checked in this update"
        },
        "overall_brand_health": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "description": "Brand health score 0-100"
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["critical", "elevated", "normal", "positive"]
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary of current brand representation"
                },
                "trend": {
                    "type": "string",
                    "enum": ["improving", "stable", "declining"]
                }
            },
            "required": ["score", "risk_level", "summary"]
        },
        "misinformation_alerts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "origin_url": {"type": "string"},
                    "platforms_affected": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "spread_assessment": {
                        "type": "string",
                        "enum": ["contained", "spreading", "widespread"]
                    }
                },
                "required": ["claim", "spread_assessment"]
            }
        },
        "competitive_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "competitor": {"type": "string"},
                    "context": {"type": "string"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["favorable_to_brand", "favorable_to_competitor",
                                 "neutral"]
                    }
                }
            }
        }
    },
    "required": ["brand_mentions", "platforms_checked", "overall_brand_health"]
}
```

### 6.2 Senso -- 2 API Systems, 10+ Endpoints

**GEO Platform API (apiv2.senso.ai):**

| Endpoint | BrandGuard Usage |
|----------|-----------------|
| `POST /evaluate` | Evaluate brand accuracy on each AI platform per mention |
| `POST /remediate` | Generate GEO-optimized correction content |

**Context OS SDK API (sdk.senso.ai):**

| Endpoint | BrandGuard Usage |
|----------|-----------------|
| `POST /content/raw` | Ingest brand ground truth + store corrections |
| `POST /search` | Search ground truth for fact-checking |
| `POST /generate` | Generate correction blog posts, FAQs |
| `POST /generate/prompt` | Templated correction generation |
| `POST /prompts` | Create brand-specific correction prompts |
| `POST /templates` | JSON/text templates for corrections |
| `POST /rules` + `/rules/{id}/values` | Define misrepresentation detection rules |
| `POST /webhooks` | Register BrandGuard webhook endpoint |
| `POST /triggers` | Link rules to webhooks for auto-alerting |

**Rules Engine Setup per Brand:**

```python
async def setup_brand_monitoring(brand_name: str, known_false_claims: list[str]):
    # 1. Create rule
    rule = await senso_sdk_request("POST", "/rules", {
        "name": f"{brand_name} Misrepresentation",
        "type": "keyword",
        "target": "response"
    })
    rule_id = rule["rule_id"]

    # 2. Add known misinformation patterns
    rule_value_ids = []
    for claim in known_false_claims:
        rv = await senso_sdk_request("POST", f"/rules/{rule_id}/values", {
            "value": claim
        })
        rule_value_ids.append(rv["rule_value_id"])

    # 3. Register webhook
    webhook = await senso_sdk_request("POST", "/webhooks", {
        "name": f"{brand_name} Alert",
        "url": f"{APP_URL}/api/webhooks/senso",
        "auth": {"type": "bearer", "token": WEBHOOK_SECRET}
    })
    webhook_id = webhook["webhook_id"]

    # 4. Create triggers
    for rv_id in rule_value_ids:
        await senso_sdk_request("POST", "/triggers", {
            "name": f"{brand_name} Alert",
            "rule_id": rule_id,
            "rule_value_id": rv_id,
            "webhook_id": webhook_id
        })
```

### 6.3 Tavily -- 4 Endpoints

| Endpoint | BrandGuard Usage | Credits |
|----------|-----------------|---------|
| `POST /search` | Find sources spreading brand misinformation | 1-2/req |
| `POST /extract` | Get full content from flagged URLs | 1/5 URLs |
| `POST /map` | Discover all brand pages on a source site | 1/10 pages |
| `POST /crawl` | Combined map+extract for deep site analysis | ~3/10 pages |

**Key Integration Patterns:**

```python
from tavily import AsyncTavilyClient

tavily = AsyncTavilyClient(api_key=config.TAVILY_API_KEY)

async def trace_misinformation_source(brand_name: str, claim: str):
    # Step 1: Search for the claim
    search_results = await tavily.search(
        query=f'"{brand_name}" {claim}',
        search_depth="advanced",
        max_results=10,
        topic="news",
        time_range="month",
        include_answer=True,
        include_raw_content="markdown"
    )

    # Step 2: Extract full content from top results
    urls = [r["url"] for r in search_results["results"][:5]]
    extracted = await tavily.extract(
        urls=urls,
        query=f"What claims does this page make about {brand_name}?",
        chunks_per_source=5,
        extract_depth="advanced"
    )

    # Step 3: Map the top source site
    if urls:
        site_map = await tavily.map(
            url=urls[0],
            instructions=f"Find all pages mentioning {brand_name}",
            max_depth=2,
            limit=50
        )

    return search_results, extracted, site_map
```

### 6.4 Neo4j -- Knowledge Graph

**Schema:**

```cypher
// Node Labels
(:Brand {name, industry, aliases, monitored_since, ground_truth_senso_id})
(:Platform {name, type, url})
(:Source {url, domain, credibility_score, type})
(:Mention {id, claim, accuracy, severity, category, detected_at, correction_status, senso_quality_score})
(:Correction {id, method, content_type, status, generated_at, senso_content_id})

// Relationships
(Mention)-[:ABOUT]->(Brand)
(Mention)-[:FOUND_ON]->(Platform)
(Mention)-[:SOURCED_FROM]->(Source)
(Source)-[:FEEDS]->(Platform)
(Correction)-[:CORRECTS]->(Mention)
(Correction)-[:TARGETS]->(Platform)
(Platform)-[:CITES]->(Source)
(Source)-[:LINKS_TO]->(Source)
```

**Key Queries:**

```cypher
-- Dashboard: Brand health per platform
MATCH (b:Brand {name: $brand})<-[:ABOUT]-(m:Mention)-[:FOUND_ON]->(p:Platform)
RETURN p.name,
       COUNT(m) AS total,
       SUM(CASE WHEN m.accuracy = 'accurate' THEN 1 ELSE 0 END) AS accurate,
       toFloat(SUM(CASE WHEN m.accuracy = 'accurate' THEN 1 ELSE 0 END))
         / COUNT(m) * 100 AS accuracy_pct
ORDER BY total DESC

-- Graph viz: Full misinformation network
MATCH (b:Brand {name: $brand})<-[:ABOUT]-(m:Mention)
OPTIONAL MATCH (m)-[:FOUND_ON]->(p:Platform)
OPTIONAL MATCH (m)-[:SOURCED_FROM]->(s:Source)
OPTIONAL MATCH (c:Correction)-[:CORRECTS]->(m)
RETURN b, m, p, s, c

-- Top misinformation sources
MATCH (s:Source)<-[:SOURCED_FROM]-(m:Mention {accuracy: "inaccurate"})
  -[:ABOUT]->(b:Brand {name: $brand})
RETURN s.domain, COUNT(m) AS false_claims,
       COLLECT(DISTINCT m.category) AS categories
ORDER BY false_claims DESC LIMIT 10

-- Propagation chain for a claim
MATCH (m:Mention {id: $mentionId})-[:SOURCED_FROM]->(s:Source)
OPTIONAL MATCH (s)-[:LINKS_TO*1..3]->(upstream:Source)
OPTIONAL MATCH (s)-[:FEEDS]->(p:Platform)
RETURN s, upstream, p
```

### 6.5 Render -- Deployment

```yaml
# render.yaml
services:
  # FastAPI Backend
  - type: web
    name: brandguard-api
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - fromGroup: brandguard-secrets

  # React Frontend (Static)
  - type: web
    name: brandguard-dashboard
    runtime: static
    region: oregon
    plan: free
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    headers:
      - path: /*
        name: Cache-Control
        value: public, max-age=0, must-revalidate
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_URL
        value: https://brandguard-api.onrender.com

  # Scheduled monitoring (every 6 hours)
  - type: cron
    name: brandguard-monitor
    runtime: python
    region: oregon
    schedule: "0 */6 * * *"
    buildCommand: pip install -r requirements.txt
    startCommand: python -m app.workers.monitor_worker
    envVars:
      - fromGroup: brandguard-secrets

envVarGroups:
  - name: brandguard-secrets
    envVars:
      - key: YUTORI_API_KEY
        sync: false
      - key: SENSO_GEO_API_KEY
        sync: false
      - key: SENSO_SDK_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_USERNAME
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
```

---

## 7. API Design (Backend Endpoints)

### Brand Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/brands` | Create brand with name, industry, ground truth |
| `GET` | `/api/brands` | List all monitored brands |
| `GET` | `/api/brands/{id}` | Get brand details + health score |
| `PUT` | `/api/brands/{id}` | Update brand config/ground truth |
| `DELETE` | `/api/brands/{id}` | Stop monitoring + cleanup scouts |

### Monitoring Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/brands/{id}/scan` | Trigger immediate scan (Yutori Browsing) |
| `GET` | `/api/brands/{id}/status` | Current monitoring status + active scouts |
| `POST` | `/api/brands/{id}/scouts` | Create/recreate Yutori scouts |
| `GET` | `/api/brands/{id}/scouts` | List active scouts + last update times |

### Mentions & Detections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/brands/{id}/mentions` | List mentions (filter: accuracy, platform, severity) |
| `GET` | `/api/mentions/{id}` | Single mention details + source trace |
| `POST` | `/api/mentions/{id}/investigate` | Trigger deep investigation (Tavily + Yutori Research) |
| `GET` | `/api/brands/{id}/alerts` | Active misinformation alerts |

### Knowledge Graph

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/brands/{id}/graph` | Full graph data for visualization (nodes + edges) |
| `GET` | `/api/brands/{id}/graph/sources` | Top misinformation sources |
| `GET` | `/api/brands/{id}/graph/propagation/{mention_id}` | Propagation chain for a claim |
| `GET` | `/api/brands/{id}/graph/stats` | Node/edge counts, clustering |

### Corrections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/mentions/{id}/correct` | Generate correction (Senso Remediate + Generate) |
| `GET` | `/api/brands/{id}/corrections` | List all corrections |
| `GET` | `/api/corrections/{id}` | Correction details + content |
| `POST` | `/api/corrections/{id}/deploy` | Mark as deployed |

### Webhooks (Incoming)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/webhooks/yutori` | Receive Yutori scout updates |
| `POST` | `/api/webhooks/senso` | Receive Senso rule trigger alerts |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/api/stats` | Dashboard aggregate statistics |

---

## 8. Dashboard Components

### 8.1 Main Dashboard (Brand Health Overview)

```
+------------------------------------------------------------------+
|  BrandGuard                                    [+ Add Brand]     |
+------------------------------------------------------------------+
| Sidebar      | Brand Health Overview                              |
| ----------   |                                                    |
| Dashboard    | +----------+ +----------+ +----------+ +--------+ |
| Brands       | | Accuracy | | Mentions | | Alerts   | | SoV    | |
| Alerts       | |   73%    | |   127    | |    3     | |  34%   | |
| Graph        | +----------+ +----------+ +----------+ +--------+ |
| Corrections  |                                                    |
| Settings     | Accuracy Trend (7 days)                            |
|              | [========= Line Chart ==================]          |
|              |                                                    |
|              | Platform Breakdown                                 |
|              | ChatGPT    [=========] 92%                         |
|              | Claude     [=========] 91%                         |
|              | Gemini     [=======]   85%                         |
|              | Perplexity [======]    79%                         |
|              |                                                    |
|              | Active Alerts                                      |
|              | [!] Perplexity: "Founded in 1990"  CRITICAL       |
|              | [!] Gemini: Missing product list   HIGH            |
|              | [~] ChatGPT: Outdated pricing      MEDIUM         |
+------------------------------------------------------------------+
```

### 8.2 Knowledge Graph Explorer

- Interactive force-directed graph (react-force-graph-2d)
- **Node types**: Brand (blue, large), Platform (green, medium), Source (red/yellow, small), Mention (orange, small)
- **Edge types**: Color-coded by relationship type
- Click any node for detail panel
- Filter controls: accuracy, severity, platform, time range
- Highlight propagation paths on click
- Layout: 3D-capable, zoom/pan, node drag

### 8.3 Mention Timeline

- Chronological list with infinite scroll
- Each card: platform icon, claim text, accuracy badge, severity indicator
- Expandable detail: full AI response, source URLs, Senso evaluation results
- Action buttons: [Investigate] [Auto-Correct] [Dismiss]
- Filter bar: platform, accuracy, severity, date range

### 8.4 Correction Review Panel

- Side-by-side: original claim vs. corrected content
- Senso GEO metrics: before/after accuracy improvement projection
- Content preview (blog post / FAQ format)
- Status badges: Draft, Deployed, Verified
- Deploy button with target platform selection

### 8.5 Source Analysis Panel

- Domain credibility score
- Number of inaccurate claims traced to this source
- Which AI platforms cite this source (FEEDS relationships)
- Tavily extract results: full content from the source
- Site map: related pages on this domain

---

## 9. Agent Orchestration

### The AI-on-AI Layering Stack

```
Layer 4: Senso Generate     -- produces correction content
Layer 3: Senso Evaluate     -- measures accuracy, citation quality
Layer 2: Yutori (3 APIs)    -- gathers raw intelligence from AI platforms + web
Layer 1: Tavily             -- finds and extracts source content
Layer 0: Neo4j              -- stores and connects everything
```

### Pipeline State Machine

```
IDLE --> MONITORING --> DETECTING --> EVALUATING --> [accurate] --> MONITORING
                                        |
                                        +--> [inaccurate] --> TRACING --> CORRECTING --> MONITORING
                                                                |
                                                                +--> [deep dive requested] --> INVESTIGATING
```

### Pipeline Implementation

```python
class BrandGuardPipeline:
    """Autonomous pipeline orchestrating the full monitoring cycle."""

    def __init__(self, yutori, senso, tavily, neo4j):
        self.yutori = yutori
        self.senso = senso
        self.tavily = tavily
        self.neo4j = neo4j

    async def process_scout_update(self, brand_id: str, update: dict):
        """Process a Yutori scout update through the full pipeline."""
        brand = await self.neo4j.get_brand(brand_id)
        mentions = update.get("brand_mentions", [])

        for mention in mentions:
            # Step 1: Store mention in Neo4j
            mention_id = await self.neo4j.create_mention(brand_id, mention)

            # Step 2: Evaluate with Senso GEO
            evaluation = await self.senso.evaluate(
                query=mention.get("query_used", mention["claim"]),
                brand=brand["name"],
                network=mention["platform"]
            )

            # Step 3: Update mention with Senso metrics
            await self.neo4j.update_mention(mention_id, {
                "senso_quality_score": evaluation.get("quality_score")
            })

            # Step 4: If inaccurate, trace and correct
            if mention["accuracy"] in ("inaccurate", "partially_accurate"):
                await self._trace_and_correct(brand, mention_id, mention)

    async def _trace_and_correct(self, brand, mention_id, mention):
        """Trace source and auto-generate correction for inaccurate mentions."""
        # Tavily source tracing
        search_results = await self.tavily.search(
            query=f'"{brand["name"]}" {mention["claim"]}',
            search_depth="advanced",
            max_results=10,
            include_raw_content="markdown"
        )

        # Store sources in Neo4j
        for result in search_results.get("results", []):
            await self.neo4j.link_source(mention_id, result)

        # Extract content from top sources
        urls = [r["url"] for r in search_results.get("results", [])[:5]]
        if urls:
            await self.tavily.extract(urls, brand["name"])

        # Auto-correct if severity is high enough
        if mention["severity"] in ("critical", "high"):
            correction = await self.senso.remediate(
                context=brand["ground_truth"],
                optimize_for="mentions",
                target_networks=[mention["platform"]]
            )
            generated = await self.senso.generate(
                content_type="correction_faq",
                instructions=f"Correct this claim: {mention['claim']}. "
                             f"The correct information: {mention.get('suggested_correction', '')}"
            )
            await self.neo4j.create_correction(mention_id, {
                "method": "senso_geo",
                "content": generated.get("generated_text", ""),
                "status": "draft"
            })
```

---

## 10. Environment Variables

```bash
# Yutori (Web Intelligence)
YUTORI_API_KEY=yut_...

# Senso GEO Platform (apiv2.senso.ai)
SENSO_GEO_API_KEY=...           # Bearer token

# Senso Context OS SDK (sdk.senso.ai)
SENSO_SDK_API_KEY=tgr_live_...  # X-API-Key

# Tavily (Web Search + Extract)
TAVILY_API_KEY=tvly-...

# Neo4j AuraDB
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...

# App Config
VITE_API_URL=http://localhost:8000
APP_URL=https://brandguard-api.onrender.com
WEBHOOK_SECRET=...              # For Senso webhook auth
```

---

## 11. File Structure (Full Project)

```
BrandGaurd/
  backend/
    app/
      __init__.py
      main.py                      # FastAPI app entry, CORS, lifespan
      config.py                    # Config singleton with validation
      api/
        __init__.py
        brands.py                  # Brand CRUD
        monitoring.py              # Scan triggers + status
        mentions.py                # Mention queries + investigation
        graph.py                   # Neo4j graph data for visualization
        corrections.py             # Correction generation + history
        webhooks.py                # Yutori + Senso webhook handlers
        health.py                  # Health check
      services/
        __init__.py
        yutori_service.py          # Scouting + Browsing + Research
        senso_service.py           # GEO Evaluate/Remediate + SDK
        tavily_service.py          # Search + Extract + Map + Crawl
        neo4j_service.py           # Graph CRUD + visualization queries
        pipeline.py                # Autonomous orchestration engine
      models/
        __init__.py
        schemas.py                 # Pydantic request/response models
        yutori_schemas.py          # Structured output schemas
      workers/
        __init__.py
        monitor_worker.py          # Cron job: poll scouts, process updates
    requirements.txt
    .env.example

  frontend/
    src/
      App.tsx                      # Router + layout
      main.tsx                     # Entry point
      config/
        api.ts                     # API base URL config
      pages/
        Dashboard.tsx              # Main brand health overview
        BrandDetail.tsx            # Single brand deep view
        GraphExplorer.tsx          # Knowledge graph visualization
        MentionDetail.tsx          # Individual mention + investigation
        CorrectionHistory.tsx      # All generated corrections
        Settings.tsx               # Brand configuration
      components/
        layout/
          Header.tsx
          Sidebar.tsx
        dashboard/
          BrandHealthCard.tsx       # Per-brand health score
          PlatformGrid.tsx          # Platform accuracy indicators
          AlertsList.tsx            # Active misinformation alerts
          StatsCards.tsx            # Aggregate statistics
          AccuracyTrend.tsx         # Recharts line chart
        graph/
          MisinfoGraph.tsx          # react-force-graph-2d
          GraphControls.tsx         # Filter + highlight controls
          NodeDetailPanel.tsx       # Node click detail
        mentions/
          MentionTimeline.tsx       # Chronological mention list
          MentionCard.tsx           # Individual mention card
          InvestigationPanel.tsx    # Source trace results
        corrections/
          CorrectionCard.tsx        # Before/after comparison
          CorrectionEditor.tsx      # Review + deploy
        ui/                         # shadcn/ui components
          button.tsx
          card.tsx
          badge.tsx
          dialog.tsx
          input.tsx
          select.tsx
          table.tsx
          tabs.tsx
          tooltip.tsx
          ...
      services/
        brandApi.ts                # Brand CRUD API calls
        monitoringApi.ts           # Monitoring + scan triggers
        mentionApi.ts              # Mention queries
        graphApi.ts                # Neo4j graph data
        correctionApi.ts           # Correction operations
      hooks/
        useBrandHealth.ts          # TanStack Query polling
        useGraphData.ts            # Graph data hook
        useMentions.ts             # Mention list with filters
      lib/
        utils.ts                   # Utility functions
    index.html
    package.json
    vite.config.ts
    tailwind.config.ts
    tsconfig.json

  render.yaml                      # Render IaC deployment config
  .env.example
  README.md
  docs/
    plans/
      2026-02-27-brandguard-design.md  # This document
    research/
      senso-api-research.md
      tavily-api-research.md
      neo4j-modulate-render-yutori-research.md
```

---

## 12. Cost Estimate (Hackathon)

| Service | Free Credits | Expected Usage | Cost |
|---------|-------------|----------------|------|
| Yutori | $5.00 | ~10 scout runs + 5 browsing + 2 research | $0 |
| Senso | $2k prize credits | ~50 evaluations + 10 remediations + SDK | $0 |
| Tavily | 1,000 credits/mo | ~100 searches + 50 extracts | $0 |
| Neo4j AuraDB Free | 200k nodes | ~500 nodes / 1000 rels | $0 |
| Render Web | Free tier | 1 API + 1 static | $0 |
| Render Cron | -- | 1 cron job | $1/mo |
| **Total** | | | **~$1/month** |

---

## 13. Pre-Seeding Strategy

Scouts take time to accumulate. For the 3-minute demo:

1. **Pre-create Yutori Scouts** 48 hours before demo
2. **Pre-ingest ground truth** into Senso SDK (`POST /content/raw`)
3. **Pre-populate Neo4j** with 50+ mentions across 4 platforms (5 inaccurate, various severities)
4. **Pre-run Senso Evaluate** on known-bad queries to cache results
5. **Pre-generate corrections** via Senso Remediate + Generate
6. **Seed script**: `python -m app.seed_demo` rebuilds entire demo state

```
python -m app.seed_demo
  -> Create "Acme Corp" brand in Neo4j
  -> Ingest ground truth into Senso SDK
  -> Create Senso rules + triggers for Acme Corp
  -> Populate 50+ mentions across ChatGPT/Claude/Gemini/Perplexity
  -> Include 8 inaccurate mentions with traced sources
  -> Create 3 corrections (1 deployed, 2 draft)
  -> Create Yutori scout for live monitoring
```

---

## 14. Sponsor Tool Usage Matrix

| Sponsor Tool | APIs Used | Endpoints | Schema Lines | Demo Visibility |
|-------------|----------|-----------|-------------|-----------------|
| **Yutori** | Scouting, Browsing, Research | 8+ | 150+ | High: live scout + browsing demo |
| **Senso** | GEO Evaluate, GEO Remediate, SDK Generate, SDK Search, SDK Content, SDK Rules, SDK Webhooks, SDK Triggers | 12+ | N/A | High: core eval + correction engine |
| **Tavily** | Search, Extract, Map, Crawl | 4 | N/A | Medium: source tracing demo |
| **Neo4j** | AuraDB, Cypher queries | 5 node types, 8 rel types | N/A | High: interactive graph |
| **Render** | Web Service, Static Site, Cron Job, render.yaml | 3 services | N/A | Medium: deployment platform |

**Total: 5+ sponsor tools, 25+ distinct API endpoints, 150+ line structured output schema.**

---

## 15. Key Architectural Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Frontend framework | React + Vite (not Next.js) | LawSync winner pattern, separate deployment, faster HMR |
| Backend framework | FastAPI (not Node.js) | Python SDKs for Senso + Tavily + Neo4j, auto-docs |
| Graph DB | Neo4j (not MongoDB/Postgres) | Misinformation propagation IS a graph problem |
| Task queue | FastAPI BackgroundTasks | No Redis dependency, sufficient for hackathon |
| Polling vs webhooks | Both (hybrid) | Webhooks primary, polling fallback for demo reliability |
| Auth for hackathon | None (skip) | Time-boxed; add auth post-hackathon if needed |
| Monolith vs micro | Single FastAPI service | Hackathon: fewer services = fewer things to break |

---

## References

- Senso API Research: `docs/research/senso-api-research.md`
- Tavily API Research: `docs/research/tavily-api-research.md`
- Neo4j/Modulate/Render/Yutori Research: `docs/research/neo4j-modulate-render-yutori-research.md`
- Yutori Hackathon Analysis: `YUTORI_HACKATHON_ANALYSIS.md`
- Yutori Architecture Patterns: `YUTORI_ARCHITECTURE_PATTERNS.md`
- LawSync Reference: `reference projects/LawSync/`
- Signal Trade Bot Reference: `reference projects/signal-trade-bot/`
- Access AI Reference: `reference projects/accessibility-agent/`
