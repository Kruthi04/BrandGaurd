# BrandGuard -- Phased Implementation Plan

**Project**: BrandGuard -- AI Brand Reputation Monitoring Agent
**Hackathon**: MCP-AWS Enterprise Agents Challenge (July 25, 2025)
**Target Prizes**: Senso ($2k), Tavily MCP ($1k), Best AWS AI ($10k)
**Architecture Reference**: `docs/plans/2026-02-27-brandguard-design.md`

---

## Current Scaffolding State

The project has been scaffolded with a **two-service architecture** (not the Next.js monolith from the design doc):

- **Backend**: Python 3 + FastAPI (`backend/`) on port 8000
  - `backend/app/config/settings.py` -- env-based configuration
  - `backend/app/services/senso/client.py` -- stub
  - `backend/app/services/tavily/client.py` -- stub
  - `backend/app/services/yutori/client.py` -- stub
  - `backend/app/services/neo4j/client.py` -- stub
  - `backend/app/services/modulate/client.py` -- stub (to be replaced with AssemblyAI)
  - `backend/app/services/agent/orchestrator.py` -- stub
  - `backend/app/models/` -- Pydantic models (brand, mention, threat, scout, agent, graph)
  - `backend/app/api/` -- route stubs (routes, monitoring, analysis, graph, agent)
  - Dependencies: FastAPI, uvicorn, httpx, neo4j, openai, apscheduler, structlog

- **Frontend**: React 18 + Vite 5 + TypeScript (`frontend/`)
  - React Router DOM 6, TanStack React Query 5, Recharts, Framer Motion, sonner
  - shadcn/ui (Radix primitives), Tailwind CSS 3, Lucide icons
  - Pages: Dashboard, Monitoring, GraphExplorer, Threats, AgentChat, Settings
  - Services: analysisApi, agentApi, graphApi, monitoringApi
  - Types: brand, mention, threat, agent, scout, graph

- **Infrastructure**: `render.yaml` with Python backend web service + static frontend

---

## Phase 1: Project Setup & Configuration

**Goal**: Get a running development environment with all API keys configured and health checks passing.

**Depends on**: Nothing (first phase)

### Tasks

1. **Create `.env.example`** at `backend/.env.example` with all required variables:
   ```
   # Senso (two API systems)
   SENSO_GEO_API_KEY=           # Bearer token for apiv2.senso.ai
   SENSO_SDK_API_KEY=tgr_live_  # X-API-Key for sdk.senso.ai

   # Tavily
   TAVILY_API_KEY=tvly-

   # Yutori
   YUTORI_API_KEY=yut_

   # Neo4j AuraDB
   NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=

   # AssemblyAI (replaces Modulate)
   ASSEMBLYAI_API_KEY=

   # OpenAI (for LLM analysis layer)
   OPENAI_API_KEY=
   OPENAI_MODEL=gpt-4o
   ```

2. **Update `backend/app/config/settings.py`**:
   - Split `SENSO_API_KEY` into `SENSO_GEO_API_KEY` and `SENSO_SDK_API_KEY`
   - Replace `MODULATE_API_KEY` / `MODULATE_API_BASE_URL` with `ASSEMBLYAI_API_KEY`
   - Fix `SENSO_API_BASE_URL` to distinguish GEO (`apiv2.senso.ai`) from SDK (`sdk.senso.ai/api/v1`)
   - Make validation soft (warn on missing keys, don't hard fail during dev)

3. **Install and verify backend**:
   - `cd backend && pip install -r requirements.txt`
   - `python main.py` starts and `/health` returns 200

4. **Install and verify frontend**:
   - `cd frontend && npm install`
   - `npm run dev` starts Vite dev server

5. **Set up Neo4j AuraDB Free instance**:
   - Create account at neo4j.io/aura
   - Create free database (200k nodes, 400k relationships)
   - Record connection URI + password
   - Test connection: `backend/app/services/neo4j/client.py` connects successfully

6. **Acquire all API keys**:
   - Senso: Contact andy@senso.ai for hackathon keys (both GEO and SDK systems)
   - Tavily: https://app.tavily.com (free tier, 1,000 credits/month)
   - Yutori: https://platform.yutori.com/settings ($5 free credits)
   - AssemblyAI: https://www.assemblyai.com ($50 free credits)

7. **Create `frontend/.env.example`**:
   ```
   VITE_API_URL=http://localhost:8000
   ```

### Deliverables
- `.env.example` files for backend and frontend
- Backend starts and responds to `/health`
- Frontend starts and renders shell layout with navigation
- All API keys acquired and stored in `.env`
- Neo4j AuraDB instance created and connected

### Files to Create/Modify
- `backend/.env.example` (create)
- `backend/app/config/settings.py` (modify)
- `frontend/.env.example` (create)

### Effort Estimate: 2-3 hours

---

## Phase 2: Senso Core Integration (HIGHEST PRIORITY)

**Goal**: Implement the full Senso integration across both API systems. This is the most critical phase -- the Senso prize ($2k) depends on deep, creative use of their platform.

**Depends on**: Phase 1 (API keys configured)

### Tasks

#### 2.1 GEO Platform API (`apiv2.senso.ai`)

1. **Implement Evaluate endpoint** in `backend/app/services/senso/client.py`:
   - `POST https://apiv2.senso.ai/evaluate`
   - Auth: `Authorization: Bearer {SENSO_GEO_API_KEY}`
   - Params: `{query, brand, network}` where network is "chatgpt", "perplexity", "gemini", "claude"
   - Returns: accuracy metrics, citation quality, share of voice, competitive visibility
   - Create Pydantic response model: `EvaluateResponse` in `backend/app/models/`

2. **Implement Remediate endpoint**:
   - `POST https://apiv2.senso.ai/remediate`
   - Params: `{context, optimize_for, target_networks}`
   - `optimize_for`: "mentions", "share_of_voice", "conversions"
   - Returns: optimized correction content for target AI platforms

3. **Create API routes** in `backend/app/api/routes.py`:
   - `POST /api/evaluate` -- proxy to Senso Evaluate
   - `POST /api/remediate` -- proxy to Senso Remediate

#### 2.2 Context OS SDK API (`sdk.senso.ai/api/v1`)

4. **Implement SDK base request function**:
   - Base URL: `https://sdk.senso.ai/api/v1`
   - Auth: `X-API-Key: {SENSO_SDK_API_KEY}`
   - Pagination: `?limit=10&offset=0`

5. **Content management**:
   - `POST /content/raw` -- ingest brand ground-truth as markdown (returns 202 + content_id)
   - `GET /content/{id}` -- check processing_status (completed/failed/processing)
   - `POST /content/file` -- upload PDF/DOCX brand documents

6. **Search**:
   - `POST /search` -- natural language search against ingested knowledge
   - Returns: AI-generated answer with citations, processing_time_ms

7. **Generate**:
   - `POST /generate` -- generate correction content from knowledge base
   - Params: `{content_type, instructions, save, max_results}`
   - Returns: generated_text with source citations
   - `POST /generate/prompt` -- generate with prompt + template

8. **Prompts and Templates**:
   - `POST /prompts` -- create reusable prompt with `{{variable}}` substitution
   - `POST /templates` -- create output templates (JSON/text format)
   - CRUD for both (GET, PUT, PATCH, DELETE)

9. **Categories and Topics**:
   - `POST /categories` -- organize brand knowledge
   - `POST /categories/{id}/topics` -- create topics within categories
   - `POST /categories/batch-create` -- bulk create with topics

#### 2.3 Rules Engine + Triggers + Webhooks

10. **Rules**:
    - `POST /rules` -- create keyword rules targeting "response"
    - `POST /rules/{id}/values` -- add rule values (specific misrepresentation patterns)

11. **Webhooks**:
    - `POST /webhooks` -- register BrandGuard's receiver URL with bearer auth

12. **Triggers**:
    - `POST /triggers` -- link rule + rule_value + webhook
    - Flow: Rule value matched -> Trigger fires -> Webhook POST to BrandGuard

13. **Webhook receiver** in `backend/app/api/webhooks.py`:
    - `POST /api/webhooks/senso` -- receive Senso trigger notifications
    - Parse payload, enqueue for pipeline processing

#### 2.4 Brand Onboarding API

14. **Create `POST /api/brands`** for brand onboarding:
    - Accept: brand name, industry, ground truth text/markdown, aliases
    - Step 1: Ingest ground truth into Senso SDK (`/content/raw`)
    - Step 2: Create category + topic in Senso for the brand
    - Step 3: Create Senso rules for misrepresentation patterns
    - Step 4: Register webhook + create triggers
    - Step 5: Store brand record locally
    - Return: brand_id, senso_content_id, rule_ids

15. **Seed "Acme Corp" ground truth**:
    - Create a seed script that ingests sample brand data into Senso
    - Include: founding date, products, leadership, partnerships, financials

### Deliverables
- Dual Senso client (GEO API + SDK API) with all endpoints implemented
- API routes: evaluate, remediate, content ingest, search, generate
- Rules engine setup (rules, values, webhook, triggers)
- Brand onboarding flow that auto-configures Senso
- Webhook receiver for trigger notifications
- "Acme Corp" ground truth seeded into Senso

### Files to Create/Modify
- `backend/app/services/senso/client.py` (rewrite: dual-system client)
- `backend/app/services/senso/schemas.py` (create: output schemas)
- `backend/app/models/brand.py` (modify: add senso_content_id, ground_truth fields)
- `backend/app/models/senso.py` (create: EvaluateResponse, RemediateResponse models)
- `backend/app/api/routes.py` (modify: add evaluate, remediate, brand endpoints)
- `backend/app/api/webhooks.py` (create: Senso webhook receiver)
- `backend/scripts/seed_senso.py` (create: seed Acme Corp ground truth)

### Verification
- `/api/evaluate` returns accuracy metrics for "Acme Corp" on "chatgpt"
- `/api/remediate` generates correction content
- `/api/brands` creates brand with Senso rules and ground truth
- Webhook endpoint receives and logs trigger events

### Effort Estimate: 4-5 hours

---

## Phase 3: Tavily Source Tracing

**Goal**: Implement web search and content extraction to trace where misinformation originates and map its scope.

**Depends on**: Phase 1 (Tavily API key)

### Tasks

#### 3.1 Core Client

1. **Implement full Tavily client** in `backend/app/services/tavily/client.py`:
   - Auth: `Authorization: Bearer {TAVILY_API_KEY}`
   - Base URL: `https://api.tavily.com`

2. **Search** (`POST /search`):
   - Params: query, search_depth (basic=1 credit / advanced=2), max_results (0-20), topic (general/news/finance), time_range (day/week/month/year), include_answer, include_raw_content, include/exclude_domains
   - Response: results with title, url, content, score; optional answer and images

3. **Extract** (`POST /extract`):
   - Params: urls (up to 20), query (for chunk reranking), extract_depth, format (markdown/text)
   - Response: results with url and raw_content; failed_results with errors
   - Cost: 1 credit per 5 URLs (basic)

4. **Map** (`POST /map`):
   - Params: url, instructions (natural language crawl guidance), max_depth (1-5), max_breadth (1-500), limit, path/domain filters
   - Response: array of discovered URLs
   - Use case: discover all pages on a site mentioning a brand

5. **Crawl** (`POST /crawl`):
   - Combined map + extract in one call
   - Params: same as map + extract options
   - Use case: comprehensive site analysis of misinformation sources

#### 3.2 API Routes

6. **Create routes** in `backend/app/api/analysis.py`:
   - `POST /api/search` -- web search for brand claims
   - `POST /api/extract` -- extract content from flagged URLs
   - `POST /api/map` -- map site structure of a source
   - `POST /api/investigate` -- combined investigation pipeline:
     1. Tavily Search for the claim across the web
     2. Tavily Extract from top result URLs
     3. Tavily Map the source domain
     4. Return comprehensive report with sources and content

#### 3.3 Integration with Pipeline

7. **Create investigation pipeline function**:
   - When Senso Evaluate detects inaccuracy, trigger investigation:
     1. Search for the inaccurate claim
     2. Extract content from cited sources
     3. Map the source sites
     4. Feed results to Neo4j (Phase 4) and agent orchestrator (Phase 8)

### Deliverables
- Full Tavily client (search, extract, map, crawl)
- API routes for search, extract, map, and combined investigation
- Investigation pipeline function for automated source tracing

### Files to Create/Modify
- `backend/app/services/tavily/client.py` (rewrite: full Tavily client)
- `backend/app/services/tavily/schemas.py` (create: response models)
- `backend/app/api/analysis.py` (rewrite: search, extract, investigate endpoints)

### Verification
- `/api/search` returns web results for "Acme Corp AI reputation"
- `/api/extract` pulls content from a test URL
- `/api/investigate` runs the full search -> extract -> map pipeline

### Effort Estimate: 2-3 hours

---

## Phase 4: Neo4j Knowledge Graph

**Goal**: Build the graph database that maps brand misinformation networks: brands, AI platforms, source websites, mentions, corrections, and their interconnections.

**Depends on**: Phase 1 (Neo4j AuraDB instance)

### Tasks

#### 4.1 Client and Schema

1. **Implement Neo4j client singleton** in `backend/app/services/neo4j/client.py`:
   - Driver singleton (create once, reuse -- drivers are expensive)
   - `run_query(cypher, params)` helper with session management
   - Connection verification on startup
   - Parameterized queries to prevent Cypher injection
   - Protocol: `neo4j+s://` for AuraDB (TLS encrypted)

2. **Create schema initialization** in `backend/app/services/neo4j/schema.py`:
   - Node labels and constraints:
     ```cypher
     CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE;
     CREATE CONSTRAINT platform_name IF NOT EXISTS FOR (p:Platform) REQUIRE p.name IS UNIQUE;
     CREATE CONSTRAINT mention_id IF NOT EXISTS FOR (m:Mention) REQUIRE m.id IS UNIQUE;
     CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE;
     CREATE CONSTRAINT correction_id IF NOT EXISTS FOR (c:Correction) REQUIRE c.id IS UNIQUE;
     ```
   - Indexes for common queries:
     ```cypher
     CREATE INDEX mention_accuracy IF NOT EXISTS FOR (m:Mention) ON (m.accuracy);
     CREATE INDEX mention_detected IF NOT EXISTS FOR (m:Mention) ON (m.detected_at);
     CREATE INDEX source_domain IF NOT EXISTS FOR (s:Source) ON (s.domain);
     ```
   - Seed initial Platform nodes: ChatGPT, Gemini, Perplexity, Claude

3. **Define graph schema** (from design doc Section 5):
   ```
   Nodes: Brand, Platform, Source, Mention, Correction
   Relationships:
     (Mention)-[:ABOUT]->(Brand)
     (Mention)-[:FOUND_ON]->(Platform)
     (Mention)-[:SOURCED_FROM]->(Source)
     (Correction)-[:CORRECTS]->(Mention)
     (Source)-[:FEEDS]->(Platform)
     (Platform)-[:CITES]->(Source)
     (Source)-[:RELATED_TO]->(Source)
   ```

#### 4.2 CRUD Operations

4. **`store_mention()`**: Create Mention node with ABOUT, FOUND_ON, SOURCED_FROM relationships
   - MERGE for brands/platforms/sources (idempotent)
   - CREATE for mentions (unique by UUID)

5. **`store_source()`**: Create/update Source nodes, link to platforms via FEEDS/CITES

6. **`store_correction()`**: Create Correction node linked to Mention, update correction_status

#### 4.3 Dashboard Queries

7. **Brand health query**: accuracy breakdown by platform (total, accurate, accuracy %)
8. **Top misinformation sources**: ranked by false claim count, with affected platforms
9. **Propagation network**: for a given mention, trace full path through sources and platforms
10. **Graph statistics**: node/edge counts by type, most connected nodes

#### 4.4 API Routes

11. **Create routes** in `backend/app/api/graph.py`:
    - `GET /api/graph/data?brand=&platform=&accuracy=&days=` -- force-graph-compatible nodes + edges
    - `GET /api/graph/stats` -- summary statistics
    - `GET /api/graph/propagation/{mention_id}` -- propagation network for a mention
    - `GET /api/graph/health/{brand}` -- accuracy by platform

12. **Node format for react-force-graph-2d**:
    ```json
    {
      "nodes": [{"id": "...", "label": "Brand", "name": "Acme Corp", "color": "#3B82F6"}],
      "links": [{"source": "...", "target": "...", "label": "ABOUT"}]
    }
    ```
    Colors: Brand=#3B82F6, Platform=#22C55E, Source=#EF4444, Mention=#F97316, Correction=#A855F7

#### 4.5 Demo Seed Data

13. **Create seed script** `backend/scripts/seed_neo4j.py`:
    - 1 Brand (Acme Corp)
    - 4 Platforms (ChatGPT, Gemini, Perplexity, Claude)
    - 10+ Sources (mix of real and fictional domains)
    - 50+ Mentions across all platforms (40 accurate, 5 inaccurate of varying severity, 5 partially_accurate)
    - 2 Corrections for high-severity inaccurate mentions
    - Propagation chains: Source -> multiple platforms

### Deliverables
- Neo4j client with connection pooling and parameterized queries
- Graph schema with constraints and indexes
- CRUD operations for all node/relationship types
- Dashboard, investigation, and visualization queries
- Force-graph-compatible API endpoints
- Demo seed script with 50+ mentions

### Files to Create/Modify
- `backend/app/services/neo4j/client.py` (rewrite: full client with singleton driver)
- `backend/app/services/neo4j/schema.py` (create: constraints, indexes, seed platforms)
- `backend/app/services/neo4j/queries.py` (create: reusable Cypher query functions)
- `backend/app/api/graph.py` (rewrite: data, stats, propagation, health endpoints)
- `backend/app/models/graph.py` (modify: force-graph node/link response models)
- `backend/scripts/seed_neo4j.py` (create: demo data seeder)

### Verification
- Schema initialization runs without errors
- Seed script populates 50+ nodes
- `/api/graph/data` returns nodes/links for react-force-graph
- `/api/graph/health/Acme Corp` returns per-platform accuracy

### Effort Estimate: 3-4 hours

### Note on GDS (Graph Data Science)
GDS algorithms (betweenness centrality, Louvain, PageRank) are NOT available on AuraDB Free. For the hackathon, implement equivalent logic in application code or demonstrate the concept with pre-computed values. If needed later, AuraDB Professional ($65/GB/month) includes GDS.

---

## Phase 5: Yutori Monitoring

**Goal**: Implement continuous brand monitoring using Yutori Scouting and on-demand investigation using Browsing and Research APIs.

**Depends on**: Phase 1 (Yutori API key), Phase 4 (Neo4j for storing results)

### Tasks

#### 5.1 Scouting API (Continuous Monitoring)

1. **Implement Yutori client** in `backend/app/services/yutori/client.py`:
   - Auth: `X-API-Key: {YUTORI_API_KEY}`
   - Base URL: `https://api.yutori.com`
   - Timeout: 30 seconds with AbortController pattern (httpx timeout)
   - Error handling with structured error responses

2. **Scout creation** (`POST /v1/scouting/tasks`):
   - Use the BrandGuard structured output schema (from design doc Section 9)
   - Fields: brand_mentions[].{platform, claim, accuracy, severity, category, source_url, evidence, suggested_correction}, summary, risk_level, platforms_checked, total_mentions, accurate_count, inaccurate_count
   - Config: output_interval=3600 (hourly), skip_email=true, webhook_url

3. **Scout lifecycle**:
   - List: `GET /v1/scouting/tasks`
   - Detail: `GET /v1/scouting/tasks/{id}`
   - Updates: `GET /v1/scouting/tasks/{id}/updates?page_size=10&cursor=`
   - Stop: `POST /v1/scouting/tasks/{id}/done`
   - Delete: `DELETE /v1/scouting/tasks/{id}`

4. **Webhook receiver** `POST /api/webhooks/yutori`:
   - Verify `X-Scout-Event: scout.update` header
   - Parse structured_result (brand_mentions array)
   - For each mention: evaluate, store in Neo4j, create alert if high severity
   - Respond within 10 seconds (Yutori timeout)

5. **Polling fallback** for webhook reliability:
   - Sequential polling of all active scouts (avoid rate limits)
   - Deduplication by update ID
   - Triggered by cron or when no webhook received for 2x interval

#### 5.2 Browsing API (On-Demand Platform Queries)

6. **Browsing task creation** (`POST /v1/browsing/tasks`):
   - Task: "Go to [platform], ask about [brand], record the response"
   - start_url: platform URL
   - max_steps: 50
   - Structured output schema for responses and claims
   - Agent: navigator-n1-latest (cheapest, $0.015/step)

7. **Browsing task polling** (`GET /v1/browsing/tasks/{id}`):
   - Poll every 3 seconds, timeout 300 seconds
   - States: queued -> running -> succeeded | failed

8. **API route** `POST /api/monitoring/browse`:
   - Accept brand name and target platform
   - Create browsing task
   - Return task_id + view_url

#### 5.3 Research API (Deep Investigation)

9. **Research task creation** (`POST /v1/research/tasks`):
   - Structured output: correct_information, misinformation_sources, propagation_chain
   - Use for deep investigation of specific claims

10. **API route** `POST /api/monitoring/research`:
    - Accept a claim to investigate
    - Return task_id

#### 5.4 Monitoring Management

11. **`POST /api/monitoring/start`**: Create scout for a brand, store scout_id
12. **`POST /api/monitoring/stop`**: Stop scout by brand_id
13. **`GET /api/monitoring/status`**: Active scouts, last updates, health

### Deliverables
- Full Yutori client (Scouting CRUD + Browsing + Research)
- BrandGuard-specific structured output schema
- Webhook receiver with Neo4j integration
- Polling fallback with deduplication
- Monitoring management API

### Files to Create/Modify
- `backend/app/services/yutori/client.py` (rewrite: full client)
- `backend/app/services/yutori/schemas.py` (create: output schemas)
- `backend/app/api/monitoring.py` (rewrite: start, stop, status, browse, research)
- `backend/app/api/webhooks.py` (modify: add Yutori webhook handler)

### Verification
- Scout created with structured schema, returns scout_id
- Webhook receives updates and stores mentions in Neo4j
- Browsing task queries ChatGPT and returns structured claims
- `/api/monitoring/status` shows active scouts

### Effort Estimate: 3-4 hours

---

## Phase 6: Voice/Audio Analysis (Optional -- AssemblyAI)

**Goal**: Analyze brand mentions in podcasts and videos. Modulate is NOT suitable (enterprise gaming product). AssemblyAI replaces it.

**Depends on**: Phase 1 (AssemblyAI API key)

### Tasks

1. **Replace Modulate with AssemblyAI**:
   - Update `backend/requirements.txt`: add `assemblyai`
   - Rewrite `backend/app/services/modulate/client.py` as AssemblyAI client

2. **Implement transcription + analysis**:
   - Accept audio/video URL
   - Transcribe with `sentiment_analysis=True, entity_detection=True`
   - Filter for brand mentions by entity name matching
   - Extract: text, sentiment (POSITIVE/NEGATIVE/NEUTRAL), confidence, timestamps

3. **API route** `POST /api/analyze/audio`:
   - Accept: audio_url, brand_name
   - Return: brand mentions with sentiment, timestamps, surrounding context

4. **Integrate with pipeline**:
   - When Tavily or Yutori discover podcast/video URLs
   - Send to AssemblyAI for analysis
   - Store as audio-sourced Mentions in Neo4j

### Deliverables
- AssemblyAI client replacing Modulate
- Audio analysis API route
- Brand mention extraction with sentiment

### Files to Create/Modify
- `backend/app/services/modulate/client.py` (rewrite as AssemblyAI client)
- `backend/requirements.txt` (add `assemblyai`)
- `backend/app/api/analysis.py` (modify: add audio endpoint)
- `backend/app/config/settings.py` (modify: replace Modulate vars)

### Effort Estimate: 1-2 hours (skip if time-constrained)

---

## Phase 7: Frontend Dashboard

**Goal**: Build a polished React dashboard with brand monitoring panels, graph visualization, alert management, correction history, and real-time status updates.

**Depends on**: Phase 1 (frontend runs), Phases 2-5 (APIs to consume). Can start with mock data.

### Tasks

#### 7.1 Layout and Navigation

1. **Implement sidebar layout** in `frontend/src/components/layout/`:
   - Fixed sidebar: Dashboard, Brands, Alerts, Graph, Corrections, Monitoring, Settings
   - Responsive: collapsible on mobile (use-mobile hook exists)
   - Brand name/logo in header bar

2. **Configure React Router** in `frontend/src/App.tsx`:
   - Routes: `/`, `/brands/:id`, `/alerts`, `/graph`, `/corrections`, `/monitoring`, `/settings`

3. **Configure React Query** (`frontend/src/lib/api.ts`):
   - QueryClient with stale times and auto-refetch intervals
   - API base URL from `VITE_API_URL`

#### 7.2 Main Dashboard (`/` -- `frontend/src/pages/Dashboard.tsx`)

4. **Overview cards** (accuracy %, total mentions, active alerts, share of voice)
   - Animate on load with Framer Motion
   - Color-coded by health: green (>90%), yellow (70-90%), red (<70%)

5. **Accuracy trend chart** (Recharts line chart, 7/30-day toggle)
6. **Platform breakdown** (horizontal bars: ChatGPT, Gemini, Perplexity, Claude with %)
7. **Recent alerts list** (severity icon + platform + claim, auto-refresh 30s)

#### 7.3 Alert Management (`/alerts` -- `frontend/src/pages/Threats.tsx`)

8. **Alerts list** with filters (severity, status, platform, date range)
9. **Alert detail** (modal or page):
   - Claim text, platform, source URL, detected timestamp
   - Senso Evaluate results (accuracy %, citation quality)
   - "Investigate" button -> triggers Tavily search + shows results
   - "Auto-Remediate" button -> triggers Senso remediate/generate + shows preview
   - Correction editor with approve/publish actions

#### 7.4 Graph Visualization (`/graph` -- `frontend/src/pages/GraphExplorer.tsx`)

10. **Install react-force-graph-2d**: `npm install react-force-graph-2d`
11. **Interactive force-directed graph**:
    - Fetch from `GET /api/graph/data`
    - Color-coded nodes: Brand (blue), Platform (green), Source (red/yellow), Mention (orange), Correction (purple)
    - Node size by connection count
    - Click node -> detail panel
    - Hover -> tooltip
12. **Filter panel**: by brand, platform, accuracy, time range, node type
13. **Statistics sidebar**: total nodes/edges, top sources, most affected platforms

#### 7.5 Corrections (`/corrections`)

14. **Corrections list**: status (draft/approved/published), method (GEO/manual), platform
15. **Correction detail**: full generated content, edit capability, publish action

#### 7.6 Monitoring Status (`/monitoring` -- `frontend/src/pages/Monitoring.tsx`)

16. **Active scouts panel**: list per brand, status, last update, next run
17. **Start/stop controls**: create/stop scouts for brands
18. **Real-time status**: connection health, last webhook timestamp

#### 7.7 Brand Management

19. **Brand onboarding form**: name, industry, ground truth text, aliases
20. **Brand detail page** (`/brands/:id`): mention history, per-platform accuracy, scout status, ground truth management

#### 7.8 UI Polish

21. **Loading states**: skeleton loaders for all data-fetching components
22. **Error boundaries**: with retry buttons
23. **Toast notifications** (sonner): for actions (brand added, correction published, alert dismissed)
24. **Animations** (Framer Motion): page transitions, card reveals
25. **Empty states**: with call-to-action when no data

### Deliverables
- Complete multi-page React dashboard
- Interactive Neo4j graph visualization with filters
- Alert management with investigate/remediate actions
- Correction generation, review, and publish flow
- Monitoring controls and status display
- Polished UI with loading states, animations, error handling

### Files to Create/Modify
- `frontend/src/App.tsx` (modify: routing, layout)
- `frontend/src/pages/*.tsx` (modify: all pages with real content)
- `frontend/src/components/dashboard/` (create: overview cards, trend chart, platform bars, alert list)
- `frontend/src/components/graph/` (create: force-graph, filters, stats sidebar)
- `frontend/src/components/alerts/` (create: alert list, alert detail, investigation panel, remediation panel)
- `frontend/src/components/corrections/` (create: list, detail, editor)
- `frontend/src/components/monitoring/` (create: scout list, controls, status)
- `frontend/src/services/*.ts` (modify: connect to real API endpoints)
- `frontend/src/hooks/` (create: useAlerts, useBrands, useGraph, useMonitoring query hooks)
- `frontend/package.json` (modify: add react-force-graph-2d)

### Effort Estimate: 5-7 hours

---

## Phase 8: Agent Orchestration Pipeline

**Goal**: Connect all tools into an autonomous end-to-end detection-to-remediation pipeline.

**Depends on**: Phase 2 (Senso), Phase 3 (Tavily), Phase 4 (Neo4j), Phase 5 (Yutori)

### Tasks

#### 8.1 Background Processing

1. **Set up APScheduler** (already in requirements):
   - Interval job: poll Yutori scouts every 5 minutes (fallback)
   - Cron job: comprehensive brand scan every 6 hours
   - Process incoming webhook events asynchronously

2. **Define job types**:
   - `process_scout_update`: parse Yutori update, evaluate each claim
   - `investigate_claim`: run Tavily search + extract for a flagged claim
   - `remediate_mention`: run Senso remediate + generate
   - `update_graph`: store all results in Neo4j

#### 8.2 Core Orchestration Flow

3. **Implement `backend/app/services/agent/orchestrator.py`**:

   ```
   on_webhook_event(source, payload):
     claims = parse_claims(payload)
     for claim in claims:
       |
       +-> evaluation = senso.evaluate(claim.text, claim.brand, claim.platform)
       |
       +-> if evaluation.accuracy < threshold:
       |     |
       |     +-> sources = tavily.search(claim.text)
       |     +-> content = tavily.extract(sources.top_urls)
       |     +-> site_map = tavily.map(sources.top_domain)
       |     |
       |     +-> neo4j.store_mention(claim, accuracy="inaccurate", severity)
       |     +-> neo4j.store_sources(sources)
       |     |
       |     +-> alert = create_alert(claim, severity, sources)
       |     |
       |     +-> if auto_remediate:
       |           +-> correction = senso.remediate(ground_truth, networks)
       |           +-> content = senso.generate(correction_type, instructions)
       |           +-> neo4j.store_correction(correction)
       |
       +-> else:
             +-> neo4j.store_mention(claim, accuracy="accurate")
   ```

4. **Severity scoring** with LLM:
   - Use OpenAI GPT-4o to compare claim vs ground truth
   - Score: critical (fundamental error, high-reach platform), high (wrong key fact), medium (outdated info), low (minor)
   - Weight by platform reach (ChatGPT weighted higher)

5. **Alert management**:
   - Create alerts with: mention_id, severity, platform, recommended_action
   - `GET /api/alerts` -- list alerts with filtering
   - `PUT /api/alerts/{id}` -- update status (new/investigating/corrected/dismissed)

#### 8.3 Cron Job

6. **Create `backend/scripts/cron_monitor.py`**:
   - Poll all active Yutori scouts for new updates
   - Run Senso evaluate on predefined queries per brand
   - Process findings through the orchestration pipeline
   - Designed to run as Render cron job (`0 */6 * * *`)

#### 8.4 Demo Seed Script

7. **Create `backend/scripts/seed_demo.py`** (master seed):
   - Calls `seed_senso.py` (ground truth, rules, prompts, templates)
   - Calls `seed_neo4j.py` (50+ mentions, sources, corrections)
   - Creates Yutori scout for Acme Corp
   - Pre-runs evaluations to populate alerts
   - Designed to rebuild full demo state from scratch

#### 8.5 Error Handling

8. **Retry logic**: exponential backoff for API failures (httpx retry)
9. **Structured logging**: structlog with correlation IDs per pipeline run
10. **Graceful degradation**: if one API is down, continue with others and log

### Deliverables
- End-to-end orchestration pipeline (detection -> investigation -> remediation)
- Background job processing with APScheduler
- Severity scoring with LLM
- Alert management API
- Cron job script for periodic monitoring
- Master demo seed script
- Structured logging

### Files to Create/Modify
- `backend/app/services/agent/orchestrator.py` (rewrite: full pipeline)
- `backend/app/services/agent/scoring.py` (create: severity scoring with LLM)
- `backend/app/api/webhooks.py` (modify: connect webhooks to orchestrator)
- `backend/app/api/agent.py` (modify: alert management, pipeline status)
- `backend/scripts/cron_monitor.py` (create)
- `backend/scripts/seed_demo.py` (create: master seeder)

### Effort Estimate: 3-4 hours

---

## Phase 9: Render Deployment

**Goal**: Deploy the full BrandGuard stack to Render with working infrastructure.

**Depends on**: Phases 1-8

### Tasks

1. **Update `render.yaml`**:
   - Backend web service: Python, starter plan, buildCommand, startCommand, healthCheckPath
   - Frontend static site: Vite build output, SPA rewrite rules
   - Cron job: `0 */6 * * *`, runs `backend/scripts/cron_monitor.py` ($1/month)
   - Environment variable group: all API keys shared across services

2. **Verify Dockerfiles**:
   - `backend/Dockerfile` builds and runs correctly
   - `frontend/Dockerfile` builds static assets correctly

3. **Configure production settings**:
   - `DEBUG=false`
   - CORS configured for frontend domain
   - Proper logging for Render log stream
   - Health check: `GET /api/health` returns 200

4. **Deploy**:
   - Connect GitHub repository to Render
   - Create environment variable group with all API keys
   - Deploy backend, frontend, and cron job
   - Verify all services show "Live"

5. **Configure webhooks with production URLs**:
   - Yutori scouts: webhook_url = `https://brandguard-api.onrender.com/api/webhooks/yutori`
   - Senso triggers: webhook url = `https://brandguard-api.onrender.com/api/webhooks/senso`
   - Test webhook delivery

6. **Handle free tier sleep**:
   - Option A: Cron job pings backend every 10 minutes (add keepalive route)
   - Option B: Accept cold starts (webhooks will wake the service)
   - Option C: Upgrade to Starter ($7/month) for always-on

### Deliverables
- Full stack deployed to Render
- Auto-deploy on git push
- Webhooks configured with production URLs
- Cron job running every 6 hours
- Health checks passing

### Files to Create/Modify
- `render.yaml` (modify: finalize all services, env var group, cron)
- `backend/Dockerfile` (verify)
- `frontend/Dockerfile` (verify)

### Effort Estimate: 1-2 hours

---

## Phase 10: Demo Preparation

**Goal**: Prepare a polished, scripted 3-minute demo showcasing BrandGuard's full capabilities.

**Depends on**: Phase 9 (deployed)

### Tasks

#### 10.1 Pre-Seed Demo Data (24-48 hours before)

1. **Run master seed script**: `python backend/scripts/seed_demo.py`
   - Acme Corp brand with ground truth in Senso
   - 50+ mentions in Neo4j across 4 platforms
   - 5 inaccurate mentions (critical, high, medium severity)
   - 2 pre-generated corrections
   - Active Yutori scout accumulating real data

2. **Verify demo data**:
   - Dashboard shows metrics (not zeros)
   - Graph has enough nodes for visual impact
   - Alerts exist with actionable data
   - At least one correction is pre-generated

#### 10.2 Demo Script (3 minutes)

3. **Write and rehearse the demo flow**:

   **0:00-0:30 -- Problem** (1 slide):
   "AI chatbots are saying wrong things about brands. ChatGPT tells users Acme Corp was founded in 1990 -- it was actually 2005. This happens 1000s of times daily across AI platforms."

   **0:30-1:00 -- Dashboard**:
   Show BrandGuard dashboard: Acme Corp health 87%, 3 active alerts, accuracy breakdown by platform.

   **1:00-1:30 -- Detection + Investigation**:
   Click alert "ChatGPT: Founded in 1990". Show Senso Evaluate results (34% accuracy). Click "Investigate" -- Tavily traces source to fake-review-site.com.

   **1:30-2:15 -- Graph + Remediation**:
   Switch to Graph view -- show Neo4j propagation network (source feeds 3 platforms). Click "Auto-Remediate" -- Senso generates corrected FAQ and blog post.

   **2:15-2:45 -- Continuous Monitoring**:
   Show Yutori scout running. Accuracy trending up after corrections (94%). "BrandGuard never sleeps."

   **2:45-3:00 -- Architecture + Close**:
   Quick visual: 6 sponsor tools. "Built with Senso, Tavily, Neo4j, Yutori, AssemblyAI, and Render."

#### 10.3 Polish

4. **Final UI pass**: fix visual glitches, test on 1920x1080 resolution
5. **Add sponsor logos**: footer or about section
6. **Record backup demo video** (screen recording with voiceover)
7. **Prepare offline fallback**: screenshots of each key screen

#### 10.4 Submission

8. **Devpost submission**:
   - Title, description, screenshots
   - Tech stack and sponsor tool usage documentation
   - Link to live deployment
   - Demo video link

### Deliverables
- Pre-seeded demo database
- Scripted 3-minute demo flow
- Polished UI at demo resolution
- Backup demo video
- Devpost submission materials

### Effort Estimate: 2-3 hours

---

## Implementation Schedule

```
                                           Start     End
Phase 1:  Setup & Config                   Day 1     Day 1
Phase 2:  Senso Integration (CRITICAL)     Day 1     Day 2
Phase 4:  Neo4j Knowledge Graph            Day 1     Day 2   (parallel with Phase 2)
Phase 3:  Tavily Source Tracing            Day 2     Day 2
Phase 5:  Yutori Monitoring                Day 2     Day 3
Phase 7:  Frontend Dashboard               Day 2     Day 4   (start with mock data)
Phase 8:  Agent Orchestration              Day 3     Day 4
Phase 6:  Audio Analysis (optional)        Day 3     Day 3
Phase 9:  Render Deployment                Day 4     Day 4
Phase 10: Demo Preparation                 Day 4     Day 5   (seed 24-48h before)
```

### Critical Path

```
Phase 1 --> Phase 2 (Senso) --> Phase 8 (Orchestration) --> Phase 9 (Deploy) --> Phase 10 (Demo)
```

Senso integration is the longest pole. Start it first, continue with Neo4j and Tavily in parallel. Frontend can be built incrementally with mock data.

### If Time-Constrained (MVP in 12 hours)

1. Phase 1: Setup (2h)
2. Phase 2: Senso Evaluate + Remediate only (2h)
3. Phase 5: Yutori Scout + webhook only (2h)
4. Phase 4: Neo4j basic schema + seed data (2h)
5. Phase 7: Dashboard with pre-seeded data (3h)
6. Phase 10: Demo prep (1h)

Skip: Phase 3 (use hardcoded sources), Phase 6 (audio), Phase 8 (manual orchestration), Phase 9 (run locally or deploy to Vercel).

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Senso API unavailable or undocumented | HIGH | Contact andy@senso.ai early; SDK docs at sensoai.mintlify.app are detailed; mock responses as fallback |
| Yutori scout takes too long to accumulate data | MEDIUM | Pre-seed scouts 48h before demo; use Browsing API for on-demand queries as backup |
| Neo4j AuraDB Free tier limitations | LOW | 200k nodes is plenty; GDS not available but application-level analytics suffice |
| Render free tier sleeps | MEDIUM | Cron keepalive ping; webhooks naturally wake service; $7 upgrade if needed |
| Modulate API not suitable | RESOLVED | Replaced with AssemblyAI; optional phase |
| API rate limits | MEDIUM | Sequential polling (Yutori), basic search depth (Tavily), response caching |
| Demo day API outage | HIGH | Pre-record backup video; screenshot fallback; local seed data |
| Two Senso API systems with different auth | MEDIUM | Separate client methods for GEO (Bearer) vs SDK (X-API-Key) |

---

## Effort Summary

| Phase | Effort | Priority | Notes |
|-------|--------|----------|-------|
| 1. Setup & Config | 2-3 hours | P0 | Blocks everything |
| 2. Senso Integration | 4-5 hours | P0 | Prize target, most APIs to implement |
| 3. Tavily Source Tracing | 2-3 hours | P0 | Source investigation capability |
| 4. Neo4j Knowledge Graph | 3-4 hours | P0 | Graph is the "wow factor" |
| 5. Yutori Monitoring | 3-4 hours | P0 | Continuous monitoring backbone |
| 6. Audio Analysis | 1-2 hours | P2 | Optional, skip if time-constrained |
| 7. Frontend Dashboard | 5-7 hours | P0 | Judges evaluate the UI |
| 8. Agent Orchestration | 3-4 hours | P1 | Can simplify for demo |
| 9. Render Deployment | 1-2 hours | P0 | Must be live for demo |
| 10. Demo Preparation | 2-3 hours | P0 | Win or lose in the demo |
| **Total** | **27-37 hours** | | |

---

## Cost Summary

| Service | Free Credits | Estimated Cost |
|---------|-------------|----------------|
| Senso | $2k prize credits | $0 |
| Tavily | 1,000 credits/month | $0 |
| Yutori | $5 free credits | $0 |
| AssemblyAI | $50 free credits | $0 |
| Neo4j AuraDB | Free tier (200k nodes) | $0 |
| Render Web + Static | Free tier | $0 |
| Render Cron Job | -- | $1/month |
| OpenAI GPT-4o | -- | ~$2-5 for dev |
| **Total** | | **~$3-6** |
