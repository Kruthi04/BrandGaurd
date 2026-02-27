# Neo4j, Modulate, Render, and Yutori — API Research for BrandGuard

Research compiled for the BrandGuard hackathon project. Each section covers capabilities, pricing, integration patterns, and BrandGuard-specific recommendations.

---

## Table of Contents

1. [Neo4j (Knowledge Graph)](#1-neo4j-knowledge-graph)
2. [Modulate AI (Voice Analysis)](#2-modulate-ai-voice-analysis)
3. [Render (Deployment Platform)](#3-render-deployment-platform)
4. [Yutori (Web Intelligence)](#4-yutori-web-intelligence)
5. [Integration Matrix for BrandGuard](#5-integration-matrix-for-brandguard)

---

## 1. Neo4j (Knowledge Graph)

### Overview

Neo4j is the leading graph database, ideal for BrandGuard's need to map brand mentions, AI platforms, source websites, and correction status as an interconnected knowledge graph. Relationships between entities (e.g., "AI Platform X cited misinformation from Source Y about Brand Z") are first-class citizens.

### Neo4j AuraDB (Cloud-Hosted)

**AuraDB Free Tier:**
- Up to **200,000 nodes** and **400,000 relationships**
- No credit card required
- Single database instance
- Includes: Aura Console, Neo4j Data Importer, Query API, GraphQL Library, Neo4j Bloom (basic visualization), Dashboards, MFA
- Available on AWS (regions vary)
- **Limitation**: No automated backups, no monitoring, no rolling updates
- **Limitation**: GDS (Graph Data Science) algorithms are NOT available on the free tier

**AuraDB Professional** (if needed): $65/GB/month, up to 128GB memory, daily backups, advanced metrics.

### Cypher Query Language

Cypher is Neo4j's declarative query language, optimized for graph pattern matching using ASCII-art syntax.

**Core Syntax:**
- Nodes: `(n:Label {prop: value})`
- Relationships: `-[:REL_TYPE {prop: value}]->`
- Pattern matching: `MATCH (a)-[:RELATES_TO]->(b) RETURN a, b`

**Key Clauses for BrandGuard:**

```cypher
-- Create a brand node
CREATE (b:Brand {name: "Acme Corp", industry: "tech"})

-- Create a misinformation mention linked to platform and source
MERGE (b:Brand {name: "Acme Corp"})
MERGE (p:Platform {name: "ChatGPT", type: "LLM"})
MERGE (s:Source {url: "https://example.com/article", domain: "example.com"})
MERGE (m:Mention {
  id: "mention-123",
  claim: "Acme Corp was founded in 1990",
  accuracy: "false",
  detected_at: datetime()
})
MERGE (m)-[:ABOUT]->(b)
MERGE (m)-[:FOUND_ON]->(p)
MERGE (m)-[:SOURCED_FROM]->(s)

-- Query: Find all inaccurate mentions about a brand
MATCH (b:Brand {name: "Acme Corp"})<-[:ABOUT]-(m:Mention {accuracy: "false"})
MATCH (m)-[:FOUND_ON]->(p:Platform)
MATCH (m)-[:SOURCED_FROM]->(s:Source)
RETURN m.claim, p.name, s.url, m.detected_at
ORDER BY m.detected_at DESC

-- Query: Find which sources feed the most misinformation to AI platforms
MATCH (s:Source)<-[:SOURCED_FROM]-(m:Mention {accuracy: "false"})-[:FOUND_ON]->(p:Platform)
RETURN s.domain, COUNT(m) AS misinfo_count, COLLECT(DISTINCT p.name) AS platforms
ORDER BY misinfo_count DESC LIMIT 10

-- Track correction status
MATCH (m:Mention {id: "mention-123"})
SET m.correction_status = "submitted",
    m.correction_date = datetime(),
    m.correction_method = "GEO"
```

**MERGE vs CREATE**: MERGE is idempotent -- it finds existing nodes/relationships or creates them if absent. Always use MERGE for entities that may already exist (brands, platforms, sources). Use CREATE only for guaranteed-unique entities (individual mentions with UUIDs).

### Graph Data Science (GDS) Algorithms

**Important**: GDS is NOT available on AuraDB Free. However, understanding the algorithms is valuable for architecture planning. If we need GDS, we would need AuraDB Professional ($65/GB/month) or run Neo4j self-hosted.

**Betweenness Centrality** (identifies influential nodes):
```cypher
-- Project the graph
MATCH (source)-[r:SOURCED_FROM|FOUND_ON|ABOUT]->(target)
RETURN gds.graph.project('brandGraph', source, target)

-- Stream betweenness scores
CALL gds.betweenness.stream('brandGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```
Use case: Find which sources or platforms are most central to misinformation spread.

**Louvain Community Detection** (finds clusters):
```cypher
CALL gds.louvain.stream('brandGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
ORDER BY communityId
```
Use case: Detect clusters of sources that tend to produce similar misinformation about brands.

**PageRank** (ranks node importance):
```cypher
CALL gds.pageRank.stream('brandGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```
Use case: Rank which AI platforms are most influential in propagating brand misinformation.

### JavaScript Driver (neo4j-driver)

**Installation:**
```bash
npm i neo4j-driver
```

**Connection Pattern:**
```typescript
import neo4j from 'neo4j-driver';

// AuraDB connection uses neo4j+s:// protocol (TLS encrypted)
const driver = neo4j.driver(
  'neo4j+s://xxxx.databases.neo4j.io',
  neo4j.auth.basic('neo4j', process.env.NEO4J_PASSWORD!)
);

// Verify connection
const serverInfo = await driver.getServerInfo();
console.log('Connected to Neo4j:', serverInfo);

// Run a query
const session = driver.session();
try {
  const result = await session.run(
    'MATCH (b:Brand {name: $name}) RETURN b',
    { name: 'Acme Corp' }
  );
  const records = result.records.map(r => r.get('b').properties);
} finally {
  await session.close();
}

// Always close driver on app shutdown
await driver.close();
```

**Key Driver Notes:**
- Driver objects are expensive to create; create ONE instance and reuse it
- Sessions are lightweight; create per-transaction
- Use parameterized queries (`$name`) to prevent Cypher injection
- AuraDB uses `neo4j+s://` protocol (encrypted); local uses `neo4j://` or `bolt://`
- Always close sessions in `finally` blocks
- For Next.js/serverless: store driver in a module-level singleton

**Python Driver:**
```bash
pip install neo4j
```
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j+s://xxxx.databases.neo4j.io",
    auth=("neo4j", os.environ["NEO4J_PASSWORD"])
)

with driver.session() as session:
    result = session.run(
        "MATCH (b:Brand {name: $name}) RETURN b",
        name="Acme Corp"
    )
    for record in result:
        print(record["b"])

driver.close()
```

### BrandGuard Knowledge Graph Schema

Recommended node types and relationships:

```
Node Labels:
  - Brand        {name, industry, aliases[], monitored_since}
  - Platform     {name, type: "LLM"|"search"|"social", url}
  - Source       {url, domain, credibility_score, type: "news"|"blog"|"wiki"|"social"}
  - Mention      {id, claim, accuracy, severity, detected_at, correction_status}
  - Correction   {id, method: "GEO"|"manual"|"api", submitted_at, status, response}

Relationships:
  - (Mention)-[:ABOUT]->(Brand)
  - (Mention)-[:FOUND_ON]->(Platform)
  - (Mention)-[:SOURCED_FROM]->(Source)
  - (Correction)-[:CORRECTS]->(Mention)
  - (Source)-[:FEEDS]->(Platform)         // discovered pattern
  - (Platform)-[:CITES]->(Source)         // discovered citation chain
```

### Environment Variables

```bash
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here
```

---

## 2. Modulate AI (Voice Analysis)

### Overview

Modulate AI builds ToxMod, a voice chat moderation product focused on gaming and social platforms. After researching their offerings, **Modulate is NOT a good fit for BrandGuard** for the following reasons:

### Why Modulate Is Not Suitable

1. **Enterprise-only product**: ToxMod is designed for gaming studios and social platforms, not general-purpose voice/audio analysis
2. **No public API**: Access requires enterprise sales contact and custom integration
3. **Focus mismatch**: ToxMod detects toxic behavior (harassment, hate speech, bullying) in live voice chat, not brand mention accuracy in podcasts/videos
4. **Pricing**: Starts at $0.15/hour of voice, enterprise custom pricing -- no free tier for hackathons
5. **SDK requires integration**: The SDK integrates with live voice chat infrastructure (Unity, Discord), not pre-recorded audio analysis
6. **No sentiment analysis for brand mentions**: ToxMod classifies toxicity types, not brand sentiment or factual accuracy

### Recommended Alternative: AssemblyAI

For analyzing brand mentions in podcasts and videos, **AssemblyAI** is significantly better suited:

**Free Tier**: $50 in free credits (~185 hours of transcription)

**Relevant Capabilities:**
| Feature | Cost | BrandGuard Use Case |
|---------|------|---------------------|
| Speech-to-Text (Universal) | $0.15/hr | Transcribe podcasts/videos mentioning brands |
| Sentiment Analysis | $0.02/hr | Detect sentiment around brand mentions |
| Entity Detection | $0.08/hr | Identify brand names, people, organizations |
| Topic Detection | $0.15/hr | Categorize content topics |
| Content Moderation | $0.15/hr | Flag problematic content |
| Summarization | $0.03/hr | Summarize long-form audio content |
| Speaker Diarization | $0.02/hr | Identify who is speaking about the brand |

**Integration Example:**
```typescript
import { AssemblyAI } from 'assemblyai';

const client = new AssemblyAI({ apiKey: process.env.ASSEMBLYAI_API_KEY });

const transcript = await client.transcripts.transcribe({
  audio_url: 'https://example.com/podcast-episode.mp3',
  sentiment_analysis: true,
  entity_detection: true,
  auto_chapters: true,
});

// Extract brand mentions with sentiment
const brandMentions = transcript.sentiment_analysis_results
  ?.filter(r => r.text.toLowerCase().includes('acme corp'))
  .map(r => ({
    text: r.text,
    sentiment: r.sentiment,    // POSITIVE, NEGATIVE, NEUTRAL
    confidence: r.confidence,
    start: r.start,
    end: r.end,
  }));
```

**Why AssemblyAI over Modulate for BrandGuard:**
- Free tier with $50 credits (enough for hackathon)
- Purpose-built for audio/video transcription + analysis
- Sentiment analysis directly applicable to brand monitoring
- Entity detection can find brand mentions automatically
- Works with pre-recorded audio (podcasts, videos, webinars)
- Simple REST API with official SDKs (JavaScript, Python)

### Other Alternatives Considered

| Tool | Pros | Cons |
|------|------|------|
| Deepgram | Audio intelligence, sentiment, topic detection | Less generous free tier |
| Google Speech-to-Text | Highly accurate, many languages | No built-in sentiment analysis |
| Whisper (OpenAI) | Free, open source, very accurate | No sentiment/entity analysis -- just transcription |

**Recommendation**: Use AssemblyAI as the voice/audio analysis component. It provides transcription + sentiment + entity detection in one API call, with generous free credits for hackathon use.

---

## 3. Render (Deployment Platform)

### Overview

Render is a cloud platform for deploying web applications, APIs, background workers, cron jobs, and databases. It provides a simpler alternative to AWS/GCP with Git-based deployments and infrastructure-as-code via `render.yaml`.

### Pricing Tiers

| Tier | Price | Best For |
|------|-------|----------|
| Hobby | Free ($0/month) | Personal projects, hackathons |
| Professional | $19/user/month | Production teams |
| Organization | $29/user/month | Compliance needs |
| Enterprise | Custom | Large-scale deployments |

### Service Types and Pricing

**Web Services:**

| Plan | RAM | CPU | Price |
|------|-----|-----|-------|
| Free | 512 MB | 0.1 | $0/month |
| Starter | 512 MB | 0.5 | $7/month |
| Standard | 2 GB | 1 | $25/month |
| Pro | 4 GB | 2 | $85/month |

**Free Tier Limitations:**
- App sleeps after 15 minutes of inactivity
- Slow cold starts on wake-up
- 512 MB RAM, 0.1 CPU
- Limited to web services, Key Value, and PostgreSQL

**Background Workers:**
- Same pricing tiers as web services
- Run continuously, no incoming traffic
- Process from task queues (BullMQ for Node.js, Celery for Python)
- Free tier available

**Cron Jobs:**
- **Minimum $1/month per cron job** (not free)
- Prorated by the second based on runtime
- Schedule via cron expressions (UTC)
- Max runtime: 12 hours per execution
- Cannot access persistent disks
- Guarantee: at most one active run at a time

**PostgreSQL:**
- Free tier available (30-day limit on free instances)
- Starter: $7/month
- Storage expansion: $0.30/GB
- Same region as web service required for private URL

**Key Value (Redis-compatible):**
- Free tier: 25 MB
- Starter: $10/month
- Used as job queue for background workers

### Infrastructure-as-Code (render.yaml)

Render supports declarative infrastructure via `render.yaml` in the repo root. This is the recommended approach for BrandGuard.

**BrandGuard Example render.yaml:**

```yaml
services:
  # Main API server
  - type: web
    name: brandguard-api
    runtime: node
    region: oregon
    plan: free
    buildCommand: npm install && npm run build
    startCommand: npm start
    healthCheckPath: /health
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
      - key: YUTORI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: SENSO_API_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: brandguard-db
          property: connectionString

  # Background worker for processing monitoring results
  - type: worker
    name: brandguard-worker
    runtime: node
    region: oregon
    plan: free
    buildCommand: npm install && npm run build
    startCommand: npm run worker
    envVars:
      - key: REDIS_URL
        fromService:
          name: brandguard-cache
          type: keyvalue
          property: connectionString
      - fromGroup: brandguard-secrets

  # Scheduled monitoring job (runs every 6 hours)
  - type: cron
    name: brandguard-monitor
    runtime: node
    region: oregon
    schedule: "0 */6 * * *"
    buildCommand: npm install && npm run build
    startCommand: npm run monitor
    envVars:
      - fromGroup: brandguard-secrets

  # Redis for job queue
  - type: keyvalue
    name: brandguard-cache
    plan: free
    region: oregon
    ipAllowList:
      - source: 0.0.0.0/0
        description: everywhere

databases:
  - name: brandguard-db
    plan: free
    region: oregon
    databaseName: brandguard
    user: brandguard_user

envVarGroups:
  - name: brandguard-secrets
    envVars:
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
      - key: YUTORI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: SENSO_API_KEY
        sync: false
```

### Deployment Workflow

1. Push code to GitHub
2. Render auto-deploys on push (configurable)
3. Build command runs (install dependencies, compile)
4. Start command launches the service
5. Health check verifies deployment success

**Service Types for BrandGuard:**

| Component | Render Service Type | Purpose |
|-----------|-------------------|---------|
| API Server | Web Service (free) | REST API + webhook receiver |
| Dashboard | Static Site (free) | Next.js frontend |
| Monitor Worker | Background Worker (free) | Process Yutori scout updates |
| Scheduled Scans | Cron Job ($1/month) | Periodic brand monitoring |
| Job Queue | Key Value (free 25MB) | Queue monitoring tasks |
| Relational Data | PostgreSQL (free) | User accounts, settings |

### Key Render Features

- **Auto-deploy from Git**: Push to branch triggers deployment
- **Preview Environments**: Automatic PR preview deployments
- **Environment Groups**: Share secrets across services
- **Private Networking**: Services communicate internally without public exposure
- **Blueprints**: Single `render.yaml` manages entire infrastructure
- **Zero-downtime deploys**: Health check path verification before traffic switch
- **Custom domains**: Free SSL/TLS certificates

### Keeping Free Services Alive

Free web services sleep after 15 minutes of inactivity. Workarounds:
1. Use the cron job ($1/month) to ping the web service every 10 minutes
2. Use Yutori webhook notifications as natural wake-up triggers
3. Accept cold starts for non-time-sensitive operations
4. Upgrade to Starter ($7/month) for always-on service

---

## 4. Yutori (Web Intelligence)

### Overview

Yutori provides always-on AI agents for web monitoring, browsing, and research. It is the primary intelligence-gathering tool for BrandGuard. Full documentation exists at `/Users/nihalnihalani/Desktop/Github/BrandGaurd/YUTORI_ARCHITECTURE_PATTERNS.md`.

### The Four APIs

| API | Purpose | Cost | BrandGuard Use Case |
|-----|---------|------|---------------------|
| **Scouting** | Persistent monitoring agents | $0.35/scout-run | Continuously monitor AI platforms for brand mentions |
| **Browsing** | On-demand browser automation | $0.015/step (n1) | Visit AI platforms and extract responses about brands |
| **Research** | Deep one-time investigation | $0.35/task | Deep-dive into specific misinformation claims |
| **n1 Model** | Vision-based browser control | $0.75/$3 per 1M tokens | Custom automation for complex platform interactions |

### BrandGuard-Specific Integration Patterns

**Pattern 1: Scout-per-Brand Monitoring**

Create one scout per brand being monitored. Each scout watches for brand mentions across AI platforms:

```typescript
const scout = await fetch('https://api.yutori.com/v1/scouting/tasks', {
  method: 'POST',
  headers: {
    'X-API-Key': process.env.YUTORI_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: `Monitor mentions of "Acme Corp" across AI chatbots (ChatGPT, Claude, Gemini, Perplexity) and fact-check any claims made about the company. Flag inaccurate information including wrong founding dates, incorrect products, false partnerships, or misleading financial data.`,
    display_name: "Acme Corp Brand Monitor",
    output_interval: 3600, // hourly
    skip_email: true,
    webhook_url: "https://brandguard-api.onrender.com/api/webhooks/yutori",
    output_schema: {
      type: "object",
      properties: {
        brand_mentions: {
          type: "array",
          items: {
            type: "object",
            properties: {
              platform: { type: "string", description: "AI platform name" },
              claim: { type: "string", description: "The claim made about the brand" },
              accuracy: { type: "string", enum: ["accurate", "inaccurate", "unverifiable", "partially_accurate"] },
              severity: { type: "string", enum: ["critical", "high", "medium", "low"] },
              source_url: { type: "string", description: "URL where this was found" },
              evidence: { type: "string", description: "Evidence supporting the accuracy assessment" },
              suggested_correction: { type: "string", description: "What the correct information should be" }
            },
            required: ["platform", "claim", "accuracy", "severity"]
          }
        },
        summary: { type: "string", description: "Overall brand health summary" },
        risk_level: { type: "string", enum: ["critical", "elevated", "normal", "positive"] }
      },
      required: ["brand_mentions", "summary", "risk_level"]
    }
  })
});
```

**Pattern 2: Browsing for Direct Platform Queries**

Use the Browsing API to directly query AI platforms and check their responses:

```typescript
const task = await fetch('https://api.yutori.com/v1/browsing/tasks', {
  method: 'POST',
  headers: {
    'X-API-Key': process.env.YUTORI_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task: `Go to ChatGPT and ask "Tell me about Acme Corp". Record the full response. Then ask "When was Acme Corp founded and who are their main competitors?". Record that response too.`,
    start_url: "https://chat.openai.com",
    max_steps: 50,
    output_schema: {
      type: "object",
      properties: {
        responses: {
          type: "array",
          items: {
            type: "object",
            properties: {
              query: { type: "string" },
              response: { type: "string" },
              claims_found: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    claim: { type: "string" },
                    category: { type: "string" }
                  }
                }
              }
            }
          }
        }
      }
    }
  })
});
```

**Pattern 3: Research for Deep Investigation**

When a misinformation claim is detected, use Research for deep investigation:

```typescript
const research = await fetch('https://api.yutori.com/v1/research/tasks', {
  method: 'POST',
  headers: {
    'X-API-Key': process.env.YUTORI_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: `Investigate the claim that "Acme Corp was founded in 1990". Find the actual founding date from authoritative sources. Trace where this misinformation originated. Identify which websites and AI platforms are propagating this incorrect date.`,
    output_schema: {
      type: "object",
      properties: {
        correct_information: { type: "string" },
        misinformation_sources: {
          type: "array",
          items: {
            type: "object",
            properties: {
              url: { type: "string" },
              platform: { type: "string" },
              date_found: { type: "string" }
            }
          }
        },
        propagation_chain: { type: "string", description: "How the misinformation spread" }
      }
    }
  })
});
```

### Webhook Integration

Yutori pushes scout updates to your endpoint. BrandGuard should receive these and process them into the Neo4j knowledge graph:

```typescript
// POST /api/webhooks/yutori
export async function POST(request: Request) {
  const event = request.headers.get('X-Scout-Event'); // "scout.update"
  const payload = await request.json();

  // Parse structured output
  const { brand_mentions, summary, risk_level } = payload.structured_result;

  // Store in Neo4j knowledge graph
  for (const mention of brand_mentions) {
    await neo4jSession.run(`
      MERGE (b:Brand {name: $brandName})
      MERGE (p:Platform {name: $platform})
      CREATE (m:Mention {
        claim: $claim,
        accuracy: $accuracy,
        severity: $severity,
        source_url: $sourceUrl,
        detected_at: datetime()
      })
      MERGE (m)-[:ABOUT]->(b)
      MERGE (m)-[:FOUND_ON]->(p)
    `, {
      brandName: 'Acme Corp',
      platform: mention.platform,
      claim: mention.claim,
      accuracy: mention.accuracy,
      severity: mention.severity,
      sourceUrl: mention.source_url || ''
    });
  }

  return Response.json({ received: true });
}
```

### Key Yutori Patterns from Reference Projects

1. **Sequential polling** to avoid rate limits (don't Promise.all scouts)
2. **AI-on-AI layering**: Use Yutori for data gathering, then a second LLM (Claude/GPT) for analysis
3. **Structured schemas** are critical -- complex schemas impress judges and enable programmatic processing
4. **Use all 3 APIs** (Scouting + Browsing + Research) for maximum impact
5. **Pre-seed demo data** -- scouts take time to accumulate updates
6. **Webhook + polling hybrid** for production reliability

### Pricing Summary

| API | Unit | Cost |
|-----|------|------|
| Scouting | Per scout-run | $0.35 |
| Browsing (n1) | Per step | $0.015 |
| Browsing (Claude CU) | Per step | $0.10 |
| Research | Per task | $0.35 |
| n1 Model (input) | Per 1M tokens | $0.75 |
| n1 Model (output) | Per 1M tokens | $3.00 |
| Free credits | On signup | $5.00 |

### Authentication

```bash
YUTORI_API_KEY=yut_...  # From platform.yutori.com/settings
```

All API calls use `X-API-Key` header. Base URL: `https://api.yutori.com`

---

## 5. Integration Matrix for BrandGuard

### Data Flow Architecture

```
Yutori Scouting (continuous)  ──┐
Yutori Browsing (on-demand)   ──┤
Yutori Research (deep-dive)   ──┤
Tavily Search/Crawl           ──┤── Raw Intelligence ──> Processing Layer
AssemblyAI (audio analysis)   ──┘                            │
                                                              ▼
                                                    AI Analysis Layer
                                                    (Claude / GPT)
                                                              │
                                                              ▼
                                                  Neo4j Knowledge Graph
                                                   (brand ← mention → platform → source)
                                                              │
                                                              ▼
                                                    Senso GEO/Evaluate
                                                    (correction generation)
                                                              │
                                                              ▼
                                                  Render (deployment)
                                                  - API Server (free)
                                                  - Dashboard (free)
                                                  - Cron Jobs ($1/mo)
                                                  - PostgreSQL (free)
```

### Environment Variables Summary

```bash
# Yutori
YUTORI_API_KEY=yut_...

# Neo4j
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...

# AssemblyAI (replacing Modulate)
ASSEMBLYAI_API_KEY=...

# Tavily
TAVILY_API_KEY=tvly-...

# Senso
SENSO_API_KEY=...

# Render (auto-configured)
DATABASE_URL=...         # PostgreSQL connection
REDIS_URL=...            # Key Value connection
RENDER_EXTERNAL_URL=...  # Public URL of the service
```

### Cost Estimate for Hackathon

| Service | Free Credits | Expected Usage | Cost |
|---------|-------------|----------------|------|
| Yutori | $5.00 | ~14 scout runs + browsing | $0 (within credits) |
| Neo4j AuraDB | Free tier | <200k nodes | $0 |
| AssemblyAI | $50.00 | ~10 hours audio | $0 (within credits) |
| Render Web Service | Free tier | 1 instance | $0 |
| Render Cron Job | -- | 1 job | $1/month |
| Render PostgreSQL | Free tier | 1 database | $0 |
| Render Key Value | Free tier (25MB) | Job queue | $0 |
| **Total** | | | **~$1/month** |

### Technology Stack Recommendation

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Frontend | Next.js (Static Site on Render) | SSR, React, TypeScript |
| API | Next.js API Routes or Express (Web Service on Render) | Same repo, simple deployment |
| Knowledge Graph | Neo4j AuraDB Free | Graph-native data model for brand networks |
| Relational DB | Render PostgreSQL Free | User accounts, settings, audit logs |
| Job Queue | Render Key Value (Redis) + BullMQ | Background job processing |
| Web Monitoring | Yutori Scouting + Browsing + Research | AI-powered web intelligence |
| Search/Crawl | Tavily | Web search and content extraction |
| Audio Analysis | AssemblyAI | Voice/podcast brand mention analysis |
| Content Evaluation | Senso GEO/Evaluate | AI content accuracy assessment |
| Deployment | Render | All-in-one platform with render.yaml |
| Scheduled Jobs | Render Cron ($1/mo) | Periodic brand monitoring triggers |
