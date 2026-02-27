# Phase 4: Neo4j Knowledge Graph

**Owner**: Sachin
**Effort**: 3-4 hours
**Priority**: P0 (The knowledge graph is the "wow factor" for judges)
**Depends on**: Phase 1 (Nihal's Setup)
**Blocks**: Phase 5 (Sachin's Yutori — stores results here), Phase 7 (Kruthi's Dashboard), Phase 8 (Nihal's Orchestration)

---

## Overview

Build the knowledge graph that maps the misinformation network: which brands are mentioned on which AI platforms, what source websites feed those platforms, how misinformation propagates, and which corrections have been applied. Neo4j is the visual centerpiece of the demo — judges will see the interactive graph.

---

## Reference

Read the research doc: `docs/research/neo4j-modulate-render-yutori-research.md` (Neo4j section)

### Neo4j AuraDB Free Tier
- 200,000 nodes, 400,000 relationships
- No GDS algorithms (betweenness centrality) — use basic Cypher queries instead
- Connection via `neo4j+s://` URI with `neo4j` Python driver

---

## Tasks

### 4.1 Neo4j Service Client

- [ ] Implement `backend/app/services/neo4j/client.py`:
  ```python
  from neo4j import AsyncGraphDatabase

  class Neo4jClient:
      def __init__(self, uri: str, username: str, password: str):
          self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

      async def close(self):
          await self.driver.close()

      async def run_query(self, query: str, params: dict = None) -> list:
          """Execute a Cypher query and return results"""

      async def init_schema(self):
          """Create constraints and indexes"""

      async def store_mention(self, mention: dict) -> str:
          """Store a mention with Brand, Platform, Source relationships"""

      async def store_correction(self, correction: dict) -> str:
          """Store a correction linked to a mention"""

      async def get_brand_health(self, brand_id: str) -> dict:
          """Accuracy breakdown by platform"""

      async def get_brand_sources(self, brand_id: str) -> list:
          """Top misinformation sources ranked by influence"""

      async def get_brand_network(self, brand_id: str) -> dict:
          """Full graph data (nodes + edges) for visualization"""
  ```

### 4.2 Schema Initialization

- [ ] Create schema script (run once):
  ```cypher
  // Constraints
  CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (b:Brand) REQUIRE b.id IS UNIQUE;
  CREATE CONSTRAINT platform_name IF NOT EXISTS FOR (p:Platform) REQUIRE p.name IS UNIQUE;
  CREATE CONSTRAINT mention_id IF NOT EXISTS FOR (m:Mention) REQUIRE m.id IS UNIQUE;
  CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE;
  CREATE CONSTRAINT correction_id IF NOT EXISTS FOR (c:Correction) REQUIRE c.id IS UNIQUE;

  // Indexes
  CREATE INDEX mention_accuracy IF NOT EXISTS FOR (m:Mention) ON (m.accuracy_score);
  CREATE INDEX mention_date IF NOT EXISTS FOR (m:Mention) ON (m.detected_at);

  // Seed platforms
  MERGE (:Platform {name: "chatgpt"})
  MERGE (:Platform {name: "claude"})
  MERGE (:Platform {name: "perplexity"})
  MERGE (:Platform {name: "gemini"})
  ```

### 4.3 API Endpoints

- [ ] `POST /api/graph/mentions` — Store a new mention
  ```
  Request:  Mention model (see integration-contracts.md)
  Response: { "neo4j_id": str, "relationships_created": int }
  ```
  Cypher:
  ```cypher
  MERGE (b:Brand {id: $brand_id})
  MERGE (p:Platform {name: $platform})
  CREATE (m:Mention {id: $id, claim: $claim, accuracy_score: $accuracy_score, severity: $severity, detected_at: $detected_at})
  CREATE (m)-[:ABOUT]->(b)
  CREATE (m)-[:FOUND_ON]->(p)
  // For each source URL:
  MERGE (s:Source {url: $source_url})
  CREATE (m)-[:SOURCED_FROM]->(s)
  CREATE (s)-[:FEEDS]->(p)
  ```

- [ ] `GET /api/graph/brand/{brand_id}/health` — Brand accuracy overview
  ```
  Response: {
    "overall_accuracy": 73.2,
    "total_mentions": 47,
    "accurate_mentions": 35,
    "threats": 8,
    "by_platform": {
      "chatgpt": { "accuracy": 68.5, "mentions": 15 },
      "claude": { "accuracy": 82.1, "mentions": 12 },
      "perplexity": { "accuracy": 71.0, "mentions": 10 },
      "gemini": { "accuracy": 65.0, "mentions": 10 }
    }
  }
  ```

- [ ] `GET /api/graph/brand/{brand_id}/sources` — Top misinformation sources
  ```
  Response: {
    "sources": [
      { "url": "outdated-blog.com", "domain": "outdated-blog.com", "mentions_fed": 5, "platforms_affected": ["perplexity", "gemini"] },
      ...
    ]
  }
  ```
  Cypher (influence = how many inaccurate mentions this source feeds):
  ```cypher
  MATCH (s:Source)-[:FEEDS]->(p:Platform)<-[:FOUND_ON]-(m:Mention)-[:ABOUT]->(b:Brand {id: $brand_id})
  WHERE m.accuracy_score < 70
  RETURN s.url, s.domain, count(DISTINCT m) as mentions_fed, collect(DISTINCT p.name) as platforms
  ORDER BY mentions_fed DESC
  LIMIT 20
  ```

- [ ] `GET /api/graph/brand/{brand_id}/network` — Full graph for visualization
  ```
  Response: {
    "nodes": [
      { "id": "brand-1", "type": "Brand", "label": "Acme Corp", "color": "#3B82F6" },
      { "id": "platform-chatgpt", "type": "Platform", "label": "ChatGPT", "color": "#10B981" },
      { "id": "mention-1", "type": "Mention", "label": "Founded 1990", "color": "#EF4444", "accuracy": 34 },
      { "id": "source-1", "type": "Source", "label": "outdated-blog.com", "color": "#F59E0B" },
      ...
    ],
    "edges": [
      { "source": "mention-1", "target": "brand-1", "type": "ABOUT" },
      { "source": "mention-1", "target": "platform-chatgpt", "type": "FOUND_ON" },
      { "source": "mention-1", "target": "source-1", "type": "SOURCED_FROM" },
      { "source": "source-1", "target": "platform-chatgpt", "type": "FEEDS" },
      ...
    ]
  }
  ```

- [ ] `POST /api/graph/corrections` — Store a correction
  ```
  Request:  { "mention_id": str, "correction": Correction }
  Response: { "neo4j_id": str }
  ```

### 4.4 Seed Script

- [ ] Create `scripts/seed_neo4j.py`:
  ```python
  # Populate Neo4j with demo data for "Acme Corp":
  # - 1 Brand node (Acme Corp)
  # - 4 Platform nodes
  # - 50+ Mention nodes (mix of accurate and inaccurate)
  # - 10 Source nodes (websites)
  # - Propagation chains: source -> platform -> mention
  # - 2 pre-existing Correction nodes
  # - 5 "critical" inaccurate mentions for demo alerts
  ```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/app/services/neo4j/client.py` | Implement full Neo4j client |
| `backend/app/api/graph.py` | Add graph endpoints |
| `backend/app/api/routes.py` | Register graph routes |
| `scripts/seed_neo4j.py` | Create — seed demo data |

---

## What You Expose to Teammates

Nihal (Phase 8 Orchestration) imports your client:
```python
from app.services.neo4j.client import Neo4jClient
# Uses: store_mention(), store_correction(), get_brand_health()
```

Kruthi (Phase 7 Dashboard) calls your endpoints:
- `GET /api/graph/brand/{id}/health` — Dashboard health cards
- `GET /api/graph/brand/{id}/sources` — Top misinformation sources list
- `GET /api/graph/brand/{id}/network` — Graph visualization page (react-force-graph-2d)
- `POST /api/graph/corrections` — Store corrections from remediation

---

## What You Consume from Teammates

Nothing directly — Neo4j is self-contained. Other services WRITE to Neo4j through your client.

---

## Node Color Scheme (for Kruthi's graph visualization)

| Node Type | Color | Hex |
|-----------|-------|-----|
| Brand | Blue | `#3B82F6` |
| Platform | Green | `#10B981` |
| Mention (accurate) | Gray | `#6B7280` |
| Mention (inaccurate) | Red | `#EF4444` |
| Source | Amber | `#F59E0B` |
| Correction | Purple | `#8B5CF6` |

---

## Verification Checklist

- [ ] Neo4j AuraDB connection works
- [ ] Schema constraints and indexes created
- [ ] `POST /api/graph/mentions` stores mention with all relationships
- [ ] `GET /api/graph/brand/{id}/health` returns correct accuracy breakdown
- [ ] `GET /api/graph/brand/{id}/sources` returns ranked misinformation sources
- [ ] `GET /api/graph/brand/{id}/network` returns nodes + edges in visualization format
- [ ] Seed script populates 50+ mentions with realistic demo data
- [ ] Neo4j client importable: `from app.services.neo4j.client import Neo4jClient`
