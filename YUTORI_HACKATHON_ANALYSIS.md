# Yutori API Hackathon — Winning Projects Analysis

## About Yutori

**Yutori** is an AI company (raised $15M seed round, March 2025) that builds always-on AI agents ("Scouts") that monitor the web for users. Their platform provides three core API products:

- **Scouting API** (`/v1/scouting/tasks`) — Create persistent AI agents that continuously monitor the web for specific topics, returning structured intelligence reports with citations
- **Browsing API** (`/v1/browsing/tasks`) — On-demand browser automation agents that navigate websites, fill forms, and extract data
- **Research API** (`/v1/research/tasks`) — Deep research tasks that conduct wide-ranging investigation across the web using 100+ MCP tools and web navigation agents

The hackathon challenged developers to build innovative applications on top of these APIs. Below are the three winning projects.

---

## Project 1: LawSync

**AI-powered legal research and document analysis platform**

### Problem Solved

Legal professionals spend enormous amounts of time on repetitive research tasks — monitoring case law updates, filling court forms, querying legal databases, and tracking regulatory changes. LawSync automates all of this through a suite of specialized AI agents, branded as "LawSync.io - AI Legal Intelligence."

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite 5 (SWC) + Tailwind CSS 3 + shadcn/ui (40+ Radix primitives) + Framer Motion 12 |
| Routing | React Router DOM 6 |
| State | TanStack React Query 5 |
| Backend | Python + FastAPI (4 microservices on ports 8000, 8001, 8003, 8004) |
| AI Framework | Strands Agents SDK (AWS) with @tool decorator pattern |
| LLMs | Google Gemini 2.0 Flash (Scout), Gemini 2.5 Flash (Browsing Chat), OpenAI GPT-4o (Form Analyzer) |
| Yutori Integration | Scouting API (8 endpoints, full CRUD) + Browsing API (2 endpoints) + Web Platform |
| Other | CUA Computer SDK (cloud VM browser automation), Axios, Recharts, Lucide icons |

### Architecture

```
User → React Frontend (Vite, port 5173)
         |
         +-→ Scout Agent API (port 8000)     → Strands + Gemini 2.0 Flash → Yutori Scouting API
         |
         +-→ Browsing Agent API (port 8003)  → Strands + Gemini 2.5 Flash / GPT-4o → Yutori Browsing API
         |
         +-→ Deep Research Proxy (port 8004) → External Cloudflare research API
         |
         +-→ CUA Sandbox API (port 8001)     → CUA Computer SDK → Cloud Windows VM (VNC)
         |
         +-→ SQL Intelligence                → SQLite (California Housing Dataset)
```

The system runs **four independent backend microservices**, each on its own port with separate requirements and configuration.

### Key Features

- **Scout Agent** — Uses Gemini 2.0 Flash to transform simple queries ("Monitor Tesla lawsuits") into 3-4 optimized monitoring prompts covering different angles (broad, specific, technical, competitive). Creates Yutori Scouts for continuous legal news monitoring with full lifecycle management.
- **Browsing Agent** — Conversational AI interface for web form automation. 3-step workflow: analyze form structure via Yutori's `navigator-n1-preview` agent with structured JSON output schema, collect user data, then auto-fill and submit via Yutori browser automation.
- **Deep Research Agent** — Advanced legal research through a proxied deep research API (Cloudflare tunneled), with markdown rendering.
- **SQL Intelligence** — Natural language to SQL translation with chart visualization.
- **Chat Agent** — Conversational AI assistant for general legal Q&A.
- **CUA Sandbox** — Embeds a live Windows VM via VNC iframe that programmatically opens Edge browser, navigates to Yutori scout pages, and goes fullscreen using keyboard automation.

### Yutori API Usage

LawSync has the **most comprehensive Yutori integration** of all three projects, using **10 distinct endpoints across 2 API products** plus the web platform:

**Scouting API (8 endpoints):**

| Method | Endpoint | Tool Function | Purpose |
|--------|----------|--------------|---------|
| `POST` | `/v1/scouting/tasks` | `create_scout()` | Create monitoring tasks with query, interval, timezone, skip_email |
| `GET` | `/v1/scouting/tasks` | `list_scouts()` | List all active scouts |
| `GET` | `/v1/scouting/tasks/{id}` | `get_scout_detail()` | Fetch individual scout details |
| `GET` | `/v1/scouting/tasks/{id}/updates` | `get_scout_updates()` | Paginated retrieval of scout reports |
| `POST` | `/v1/scouting/tasks/{id}/done` | `mark_scout_done()` | Stop a scout from running |
| `PATCH` | `/v1/scouting/tasks/{id}` | `update_scout()` | Modify output_interval or timezone |
| `DELETE` | `/v1/scouting/tasks/{id}` | `delete_scout()` | Permanently delete a scout |
| `PUT` | `/v1/scouting/tasks/{id}/email-settings` | `update_email_settings()` | Manage email notifications and subscribers |

**Browsing API (2 endpoints):**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/v1/browsing/tasks` | Create browsing task with structured output schema (form analysis + form filling) |
| `GET` | `/v1/browsing/tasks/{id}` | Poll task status every 3s until succeeded/failed (300s timeout) |

**Web Platform Integration:**
- Direct links to `https://scouts.yutori.com/{scout_id}` for native scout viewing
- HTML proxy endpoint that fetches Yutori web pages with injected `<base>` tag for iframe embedding
- CUA sandbox browser automation navigating to Yutori's web UI

All 8 scouting tools are registered with the Strands Agent framework, allowing the AI to autonomously decide when and how to call each endpoint based on natural language input.

### What Made It Stand Out

- **Multi-agent architecture** — 5+ distinct AI agents (Scout, Browsing Chat, Form Analyzer, Deep Research, CUA Browser), each with specialized capabilities and different AI models
- **Production-grade UI** — Law firm aesthetic with serif typography, warm earth tones (#8b6f47), Framer Motion animations, full landing page with hero/stats/CTA sections
- **Agentic tool use** — Strands framework lets AI autonomously orchestrate Yutori API calls rather than hard-coding sequences
- **4 ways of interacting with Yutori** — API calls, web platform links, HTML proxy, and CUA browser automation
- **Deepest API coverage** — Likely covers every operation the Yutori Scouting API supports

---

## Project 2: Access AI (accessibility-agent)

**Automated web accessibility auditing and remediation platform**

### Problem Solved

Web accessibility compliance (WCAG, ADA, Section 508) is critical but auditing is manual, expensive, and time-consuming. Access AI automates the entire pipeline: scan websites for accessibility violations, generate structured reports with AI vision analysis (screenshots), and create actionable tickets directly in Linear.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.1.2 (App Router) + React 19.2.3 + TypeScript 5 |
| Styling | Tailwind CSS v4 + @tailwindcss/typography |
| Fonts | Instrument Sans, Instrument Serif, Geist Sans, Geist Mono |
| Yutori Integration | Scouting API + Browsing API + Research API (3 products) |
| Secondary Automation | Mino AI (tinyfish) for browser automation |
| Ticket Management | Linear GraphQL API |
| AI Analysis | OpenAI GPT-5.2 with vision (screenshots as image_url inputs) |
| Deployment | Vercel (`accessibility-agent.vercel.app`) |

### Architecture

```
User → Next.js App (9 API Routes) → Yutori Browsing API  (core audit engine)
                                   → Yutori Scouting API  (discover inaccessible sites)
                                   → Yutori Research API   (find site owners/contacts)
                                   → Mino AI               (alternative automation)
                                   → OpenAI GPT-5.2        (report generation with vision)
                                   → Linear GraphQL API    (ticket creation)
```

### Key Features

- **Multi-Framework Auditing** — Supports 9 accessibility standards: WCAG, APG, Section 508, EN 301 549 (EU), ADA, ATAG, UAAG, ISO 40500, BBC GEL/GOV.UK
- **Dual Agent System** — Users choose between Yutori's browsing agent or Mino AI (tinyfish) for automation, with seamless switching
- **Sitemap Builder** — Automatically discovers all subpages before auditing for comprehensive coverage
- **AI Vision Analysis** — GPT-5.2 analyzes both raw audit logs AND screenshots to detect visual issues like color contrast problems
- **Structured Output Schema** — Uses Yutori's `output_schema` for typed JSON responses
- **Report Generation** — Converts raw automation logs into structured analysis with POUR-categorized summaries and prioritized tickets
- **Linear Integration** — One-click ticket creation with auto-detected team, workflow state, and priority mapping (urgent=1 through low=4)
- **Site Owner Discovery** — Parallel execution using Yutori Research API to find contacts responsible for accessibility
- **Scout Creation** — Creates Yutori Scouts to continuously monitor for inaccessible URLs over time
- **Session Persistence** — Full state restoration from localStorage, including auto-resuming in-progress Yutori tasks after page refresh via tracked task IDs

### Yutori API Usage

Access AI is the **only project to use all three Yutori API products**:

1. **Browsing API** (`/v1/browsing/tasks`) — The core audit engine. For each URL, creates a browsing task with a detailed accessibility audit prompt (specifying POUR principles, semantic HTML, ARIA, contrast, focus management, etc.) as the `task` goal. Polls every 3 seconds for up to 6 minutes (120 attempts). Supports multiple URLs in parallel.

2. **Scouting API** (`/v1/scouting/tasks`) — Creates persistent scouts with a structured `output_schema` returning JSON with `inaccessible_urls` array (url + reason). Triggered via the "Not sure what site to audit? Let us find one for you" feature.

3. **Research API** (`/v1/research/tasks`) — Finds the contact person/email responsible for accessibility at given websites. Returns structured contacts with url, name, email, and role. Runs in parallel with the main audit.

### What Made It Stand Out

- **Practical real-world impact** — Web accessibility is a legal requirement; this tool directly saves companies from lawsuits and makes the web more inclusive
- **End-to-end pipeline** — From website discovery to audit findings to engineering tickets in Linear
- **Only project using all 3 Yutori APIs** — Browsing, Scouting, and Research integrated into one workflow
- **Resilient architecture** — Session persistence with task ID tracking survives page refreshes; auto-resume capability
- **Vision-enabled AI** — Sends screenshots alongside text logs to GPT-5.2 for visual accessibility analysis
- **Beautiful, accessible UI** — Interactive eye animations following mouse cursor (trigonometric calculations), typewriter effects, WebGL gradient backgrounds, clean minimal design

---

## Project 3: Signal Trade Bot (signal-trade-bot)

**AI-powered prediction market intelligence and auto-trading platform (KalshiBot Terminal)**

### Problem Solved

Prediction markets (like Kalshi) require constant monitoring of news, social media, and world events to spot trading opportunities. Signal Trade Bot automates intelligence gathering via Yutori Scouts and uses Claude as a hedge fund analyst to generate trading signals — then can automatically execute real trades on Kalshi.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16.1.3 (App Router) + React 19.2.3 + TypeScript 5 |
| Styling | Tailwind CSS 4, Google Material Symbols, Inter + JetBrains Mono fonts |
| Yutori Integration | Scouting API with 150+ line structured intelligence report schemas |
| AI Analysis | Anthropic Claude 3.5 Sonnet (trade signal generation) |
| Trading | Kalshi API v2 with RSA-PSS cryptographic signing |
| Market Data | Browser-Use API (live Kalshi market discovery) |
| API Routes | 5 routes: `/api/kalshi`, `/api/scouts/create`, `/api/scouts/poll`, `/api/scouts/poll-all`, `/api/agent/analyze` |

### Architecture

```
[Kalshi Markets via Browser-Use API] → Market Discovery Page → User selects market
                                                                      ↓
                                              Strategy Modal → Configure data sources → Deploy
                                                                      ↓
                                              Yutori Scouts created (1 per data source)
                                                                      ↓
                                              Poll every 30s → Yutori API: Get Updates
                                                                      ↓
                                              New intelligence → Claude 3.5 Sonnet analysis
                                                                      ↓
                                              AI Signal (buy_yes/buy_no/hold + confidence)
                                                                      ↓
                                              if confidence >= 75% → Kalshi API: Execute Trade
                                                                      ↓
                                              Live Feed displays all events
```

### Key Features

- **Live Market Discovery** — Real-time Kalshi market data via Browser-Use API with search, category filtering (Politics, Economics, Tech, Crypto, etc.), volume/liquidity visualization, 60-second auto-refresh
- **Multi-Source Intelligence** — Configure scouts across 7 platforms: Twitter/X, Reddit, Google News, Telegram, Discord, GitHub, RSS feeds
- **Strategy Builder** — Create named strategies targeting specific Kalshi market tickers, each with configured data sources
- **Structured Intelligence Reports** — Yutori scouts return JSON-structured reports (150+ line schema) with:
  - `headline` and `status` classification (no_change / escalation / de_escalation / critical_event / breaking)
  - `confidence_level` (0-100)
  - `key_findings` with source URLs, authors, timestamps, and credibility ratings (verified / credible / unverified / disputed)
  - `not_reported` — things NOT being reported (useful for ruling out scenarios)
  - `misinformation_alerts` with claims, sources, and debunk status
  - `trending_topics` with activity levels (very_high / high / moderate / low)
  - `community_sentiment` analysis (strongly_positive through strongly_negative)
  - `baseline_status` — clear current state assessment
  - `trading_signal` with direction (bullish/bearish/neutral/uncertain), confidence, rationale, and key triggers
- **AI Trading Agent** — Claude 3.5 Sonnet acts as a hedge fund analyst, receiving the full intelligence timeline and outputting `buy_yes`, `buy_no`, or `hold` with confidence, reasoning, and optional limit price
- **Auto-Execution** — When confidence >= 75%, auto-places orders on Kalshi via RSA-PSS signed requests (1 contract default for safety)
- **Live Feed** — Real-time split-panel view with strategy list (left) and color-coded event feed (right) showing 6 event types: signal, analysis, trade, error, system, scout
- **Terminal UI** — Dark-themed trading terminal aesthetic with grid/dot backgrounds, glass panels, terminal glow effects, and custom scrollbars

### Yutori API Usage

Signal Trade Bot pushes the Scouting API furthest with its **structured output schema**:

- Creates scouts via `/v1/scouting/tasks` with the most complex `json_schema` of any project (150+ lines defining the intelligence report structure)
- Each data source (Twitter handle, subreddit, news topic) gets its own dedicated scout with platform-contextualized queries (e.g., "Get the latest updates from X/Twitter: @US_FDA")
- Polls `/v1/scouting/tasks/{id}/updates` every 30 seconds for all active scouts (sequential to avoid rate limits)
- Updates deduplicated by ID client-side
- Parses structured JSON into typed `IntelligenceReport` objects with full TypeScript type safety
- New scout updates automatically trigger Claude analysis pipeline

### What Made It Stand Out

- **Complete autonomous trading pipeline** — From web monitoring to executed real-money trades, fully automated
- **Most sophisticated structured outputs** — 150+ line JSON schema turns raw web intelligence into market-actionable data with credibility ratings, misinformation detection, and trading signals
- **Real money on the line** — Actually executes financial transactions via Kalshi with RSA-PSS cryptographic auth
- **Multi-source correlation** — Cross-references Twitter, Reddit, and news to build holistic intelligence before trading
- **Risk management** — 75% confidence threshold, 1-contract default size, limit pricing, ticker validation, execution status tracking
- **Professional terminal aesthetic** — Looks like a real trading terminal, not a hackathon prototype

---

## Comparative Analysis

| Dimension | LawSync | Access AI | Signal Trade Bot |
|-----------|---------|-----------|-----------------|
| **Yutori APIs Used** | Scouting (8 endpoints) + Browsing (2 endpoints) | Scouting + Browsing + Research (3 products) | Scouting (structured output) |
| **Yutori Endpoints** | 10 total | 5+ total | 3 total |
| **AI Orchestration** | Strands Agent Framework (Gemini + GPT-4o) | Direct API calls + GPT-5.2 vision | Claude 3.5 Sonnet |
| **Frontend** | React 18 + Vite 5 | Next.js 16 | Next.js 16 |
| **Backend** | Python/FastAPI (4 microservices) | Next.js API Routes (9 routes) | Next.js API Routes (5 routes) |
| **External APIs** | Gemini, OpenAI, CUA SDK | Mino AI, Linear, OpenAI | Kalshi, Anthropic, Browser-Use |
| **Domain** | Legal Tech | Web Accessibility | FinTech / Trading |
| **Complexity** | Highest (4 microservices + CUA VM) | High (dual-agent, 3 Yutori APIs, persistence) | High (auto-trading, RSA crypto) |
| **Yutori Depth** | Deepest CRUD + agentic tool use | Broadest API product coverage | Most advanced output schemas |
| **UI Theme** | Law firm warm earth tones | Clean minimal white | Dark trading terminal |

---

## Why These Projects Won

### 1. Genuine Problem-Market Fit
Each project tackled a real, painful problem in a specific high-value industry — legal research, web accessibility compliance, and prediction market intelligence. None were toy demos.

### 2. Deep Yutori API Integration
All three projects went well beyond basic API calls:
- **LawSync** used 10 Yutori endpoints across 2 API products, wrapped as agentic tools letting AI autonomously orchestrate calls
- **Access AI** is the only project using all 3 Yutori API products (Scouting + Browsing + Research) in a unified pipeline
- **Signal Trade Bot** used the most advanced structured output schemas (150+ lines) to extract market-actionable intelligence

### 3. End-to-End Automation
None of these projects just "fetch and display." They each built complete pipelines:
- LawSync: Query → Gemini prompt enhancement → Scout creation → Updates → Legal insights + Form analysis → Auto-fill
- Access AI: URL → Sitemap discovery → Accessibility audit → GPT-5.2 vision analysis → Report → Linear tickets
- Signal Trade Bot: Strategy → Scout deployment → Intelligence gathering → Claude analysis → Kalshi trade execution

### 4. Production-Quality UX
All three feature polished, responsive interfaces with loading states, error handling, animations, and thoughtful design. LawSync has a full marketing-grade landing page; Access AI has interactive eye animations and WebGL backgrounds; Signal Trade Bot has a professional trading terminal aesthetic.

### 5. Intelligent AI Layering
Each project layers additional AI on top of Yutori's AI agents:
- LawSync uses Gemini to enhance prompts before feeding them to Yutori, and GPT-4o to analyze form structures
- Access AI uses GPT-5.2 with vision to analyze raw audit logs + screenshots into structured reports
- Signal Trade Bot uses Claude 3.5 Sonnet to analyze Yutori's intelligence reports and generate trading decisions

This "AI on AI" pattern maximizes the value extracted from Yutori's monitoring capabilities.

### 6. Resilience and Production Readiness
- LawSync: Microservices architecture with independent scaling, config validation preventing startup without credentials
- Access AI: Session persistence with localStorage, auto-resume of in-progress Yutori tasks across page reloads
- Signal Trade Bot: Rate-limit awareness with sequential polling, trade safety with confidence thresholds and position limits

---

## Complete Yutori API Endpoint Map

### Scouting API

```
POST   /v1/scouting/tasks                       — Create a scout
                                                   Used by: All 3 projects
GET    /v1/scouting/tasks                        — List all scouts
                                                   Used by: LawSync
GET    /v1/scouting/tasks/{id}                   — Get scout details
                                                   Used by: LawSync
GET    /v1/scouting/tasks/{id}/updates           — Poll for updates (paginated)
                                                   Used by: All 3 projects
PATCH  /v1/scouting/tasks/{id}                   — Update scout config
                                                   Used by: LawSync
POST   /v1/scouting/tasks/{id}/done              — Mark scout as done
                                                   Used by: LawSync
DELETE /v1/scouting/tasks/{id}                   — Delete scout
                                                   Used by: LawSync
PUT    /v1/scouting/tasks/{id}/email-settings    — Manage email notifications
                                                   Used by: LawSync
```

### Browsing API

```
POST   /v1/browsing/tasks                        — Create browsing automation task
                                                   Used by: LawSync, Access AI
GET    /v1/browsing/tasks/{id}                   — Poll task status
                                                   Used by: LawSync, Access AI
```

### Research API

```
POST   /v1/research/tasks                        — Create deep research task
                                                   Used by: Access AI
```

### Authentication

All projects use the same header-based auth:
```
X-API-Key: <YUTORI_API_KEY>
```

### Structured Output Schema (`task_spec.output_schema`)

All three projects use Yutori's structured output feature, with increasing complexity:
- **Access AI** — Simple schema: `{inaccessible_urls: [{url, reason}]}`
- **LawSync** — Form analysis schema: `{form_type, form_name, fields: [{name, type, label, required, options}], submit_button_text}`
- **Signal Trade Bot** — Complex intelligence report schema (150+ lines): headlines, status classification, key findings with credibility, misinformation alerts, trending topics, sentiment analysis, trading signals

---

*Analysis generated from comprehensive source code review of all three hackathon-winning projects by a team of specialized analysis agents.*
