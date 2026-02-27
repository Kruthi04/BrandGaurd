"""Neo4j knowledge graph client for BrandGuard.

Manages the misinformation network graph:
  Nodes  — Brand, Platform, Mention, Source, Correction
  Edges  — ABOUT, FOUND_ON, SOURCED_FROM, FEEDS, CORRECTS, FOR_BRAND
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from neo4j import AsyncGraphDatabase

from app.config import settings

logger = logging.getLogger(__name__)

# ── Node colors for visualization ───────────────────────────────
NODE_COLORS = {
    "Brand": "#3B82F6",
    "Platform": "#10B981",
    "Mention_accurate": "#6B7280",
    "Mention_inaccurate": "#EF4444",
    "Source": "#F59E0B",
    "Correction": "#8B5CF6",
}


class Neo4jClient:
    """Async client for the Neo4j knowledge graph."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.uri = uri or settings.NEO4J_URI
        self.username = username or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self.driver = AsyncGraphDatabase.driver(
            self.uri, auth=(self.username, self.password)
        )

    async def close(self):
        await self.driver.close()

    async def verify_connectivity(self) -> bool:
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception as exc:
            logger.warning("Neo4j connectivity check failed: %s", exc)
            return False

    # ── Low-level query helper ──────────────────────────────────

    async def run_query(
        self, query: str, params: dict | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return result records as dicts."""
        async with self.driver.session() as session:
            result = await session.run(query, params or {})
            return [record.data() async for record in result]

    # ── Schema initialization ───────────────────────────────────

    async def init_schema(self):
        """Create constraints, indexes, and seed platform nodes."""
        statements = [
            "CREATE CONSTRAINT brand_id IF NOT EXISTS FOR (b:Brand) REQUIRE b.id IS UNIQUE",
            "CREATE CONSTRAINT platform_name IF NOT EXISTS FOR (p:Platform) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT mention_id IF NOT EXISTS FOR (m:Mention) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE",
            "CREATE CONSTRAINT correction_id IF NOT EXISTS FOR (c:Correction) REQUIRE c.id IS UNIQUE",
            "CREATE INDEX mention_accuracy IF NOT EXISTS FOR (m:Mention) ON (m.accuracy_score)",
            "CREATE INDEX mention_date IF NOT EXISTS FOR (m:Mention) ON (m.detected_at)",
        ]
        async with self.driver.session() as session:
            for stmt in statements:
                try:
                    await session.run(stmt)
                except Exception as exc:
                    logger.warning("Schema statement skipped: %s — %s", stmt[:60], exc)

        platforms = ["chatgpt", "claude", "perplexity", "gemini"]
        for name in platforms:
            await self.run_query("MERGE (:Platform {name: $name})", {"name": name})

        logger.info("Neo4j schema initialized with %d platform nodes", len(platforms))

    # ── Store a mention ─────────────────────────────────────────

    async def store_mention(self, mention: dict[str, Any]) -> dict[str, Any]:
        """Store a mention and create Brand, Platform, Source relationships.

        Expected mention keys:
            id, brand_id, brand_name, platform, claim, accuracy_score,
            severity, detected_at, source_urls (list[str])
        """
        mention_id = mention.get("id") or str(uuid.uuid4())
        detected_at = mention.get("detected_at") or datetime.now(timezone.utc).isoformat()
        is_accurate = mention.get("accuracy_score", 0) >= 70

        query = """
        MERGE (b:Brand {id: $brand_id})
        ON CREATE SET b.name = $brand_name
        MERGE (p:Platform {name: $platform})
        CREATE (m:Mention {
            id: $mention_id,
            claim: $claim,
            accuracy_score: $accuracy_score,
            is_accurate: $is_accurate,
            severity: $severity,
            detected_at: $detected_at
        })
        CREATE (m)-[:ABOUT]->(b)
        CREATE (m)-[:FOUND_ON]->(p)
        RETURN m.id AS mention_id, elementId(m) AS neo4j_id
        """
        params = {
            "brand_id": mention["brand_id"],
            "brand_name": mention.get("brand_name", mention["brand_id"]),
            "platform": mention["platform"],
            "mention_id": mention_id,
            "claim": mention["claim"],
            "accuracy_score": float(mention.get("accuracy_score", 0)),
            "is_accurate": is_accurate,
            "severity": mention.get("severity", "medium"),
            "detected_at": str(detected_at),
        }
        records = await self.run_query(query, params)
        neo4j_id = records[0]["neo4j_id"] if records else None

        rels_created = 2  # ABOUT + FOUND_ON
        source_urls = mention.get("source_urls", [])
        for url in source_urls:
            domain = _extract_domain(url)
            src_query = """
            MATCH (m:Mention {id: $mention_id})
            MATCH (p:Platform {name: $platform})
            MERGE (s:Source {url: $url})
            ON CREATE SET s.domain = $domain
            CREATE (m)-[:SOURCED_FROM]->(s)
            MERGE (s)-[:FEEDS]->(p)
            """
            await self.run_query(
                src_query,
                {
                    "mention_id": mention_id,
                    "platform": mention["platform"],
                    "url": url,
                    "domain": domain,
                },
            )
            rels_created += 2  # SOURCED_FROM + FEEDS

        return {
            "neo4j_id": neo4j_id,
            "mention_id": mention_id,
            "relationships_created": rels_created,
        }

    # ── Store a correction ──────────────────────────────────────

    async def store_correction(self, correction: dict[str, Any]) -> dict[str, Any]:
        """Store a correction linked to a mention and brand."""
        correction_id = correction.get("id") or str(uuid.uuid4())
        created_at = correction.get("created_at") or datetime.now(timezone.utc).isoformat()

        query = """
        MATCH (m:Mention {id: $mention_id})
        MATCH (m)-[:ABOUT]->(b:Brand)
        CREATE (c:Correction {
            id: $correction_id,
            content: $content,
            type: $type,
            status: $status,
            created_at: $created_at
        })
        CREATE (c)-[:CORRECTS]->(m)
        CREATE (c)-[:FOR_BRAND]->(b)
        RETURN c.id AS correction_id, elementId(c) AS neo4j_id
        """
        params = {
            "mention_id": correction["mention_id"],
            "correction_id": correction_id,
            "content": correction.get("content", ""),
            "type": correction.get("correction_type", "blog_post"),
            "status": correction.get("status", "draft"),
            "created_at": str(created_at),
        }
        records = await self.run_query(query, params)
        neo4j_id = records[0]["neo4j_id"] if records else None
        return {"neo4j_id": neo4j_id, "correction_id": correction_id}

    # ── Brand health ────────────────────────────────────────────

    async def get_brand_health(self, brand_id: str) -> dict[str, Any]:
        """Accuracy breakdown by platform for a brand."""
        query = """
        MATCH (m:Mention)-[:ABOUT]->(b:Brand {id: $brand_id})
        MATCH (m)-[:FOUND_ON]->(p:Platform)
        RETURN p.name AS platform,
               count(m) AS mentions,
               avg(m.accuracy_score) AS avg_accuracy,
               sum(CASE WHEN m.is_accurate THEN 1 ELSE 0 END) AS accurate_count,
               sum(CASE WHEN m.severity IN ['high', 'critical'] THEN 1 ELSE 0 END) AS threats
        """
        records = await self.run_query(query, {"brand_id": brand_id})

        by_platform = {}
        total_mentions = 0
        total_accurate = 0
        total_threats = 0
        weighted_sum = 0.0

        for r in records:
            plat = r["platform"]
            count = r["mentions"]
            acc = round(r["avg_accuracy"], 1) if r["avg_accuracy"] is not None else 0
            by_platform[plat] = {"accuracy": acc, "mentions": count}
            total_mentions += count
            total_accurate += r["accurate_count"]
            total_threats += r["threats"]
            weighted_sum += (r["avg_accuracy"] or 0) * count

        overall = round(weighted_sum / total_mentions, 1) if total_mentions else 0

        return {
            "overall_accuracy": overall,
            "total_mentions": total_mentions,
            "accurate_mentions": total_accurate,
            "threats": total_threats,
            "by_platform": by_platform,
        }

    # ── Top misinformation sources ──────────────────────────────

    async def get_brand_sources(self, brand_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Rank sources by how many inaccurate mentions they feed."""
        query = """
        MATCH (s:Source)<-[:SOURCED_FROM]-(m:Mention)-[:ABOUT]->(b:Brand {id: $brand_id})
        WHERE m.accuracy_score < 70
        OPTIONAL MATCH (s)-[:FEEDS]->(p:Platform)
        RETURN s.url AS url,
               s.domain AS domain,
               count(DISTINCT m) AS mentions_fed,
               collect(DISTINCT p.name) AS platforms_affected
        ORDER BY mentions_fed DESC
        LIMIT $limit
        """
        records = await self.run_query(query, {"brand_id": brand_id, "limit": limit})
        return [
            {
                "url": r["url"],
                "domain": r["domain"],
                "mentions_fed": r["mentions_fed"],
                "platforms_affected": r["platforms_affected"],
            }
            for r in records
        ]

    # ── Full graph for visualization ────────────────────────────

    async def get_brand_network(self, brand_id: str) -> dict[str, Any]:
        """Return nodes + edges for the brand's knowledge graph."""
        query = """
        MATCH (b:Brand {id: $brand_id})
        OPTIONAL MATCH (m:Mention)-[:ABOUT]->(b)
        OPTIONAL MATCH (m)-[:FOUND_ON]->(p:Platform)
        OPTIONAL MATCH (m)-[:SOURCED_FROM]->(s:Source)
        OPTIONAL MATCH (c:Correction)-[:CORRECTS]->(m)
        RETURN b, collect(DISTINCT m) AS mentions,
               collect(DISTINCT p) AS platforms,
               collect(DISTINCT s) AS sources,
               collect(DISTINCT c) AS corrections
        """
        records = await self.run_query(query, {"brand_id": brand_id})
        if not records:
            return {"nodes": [], "edges": []}

        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        for record in records:
            brand = record["b"]
            if brand:
                bid = f"brand-{brand['id']}"
                nodes[bid] = {
                    "id": bid,
                    "type": "Brand",
                    "label": brand.get("name", brand["id"]),
                    "color": NODE_COLORS["Brand"],
                }

            for m in record.get("mentions") or []:
                if m is None:
                    continue
                mid = f"mention-{m['id']}"
                is_acc = m.get("is_accurate", m.get("accuracy_score", 0) >= 70)
                color_key = "Mention_accurate" if is_acc else "Mention_inaccurate"
                nodes[mid] = {
                    "id": mid,
                    "type": "Mention",
                    "label": (m.get("claim") or "")[:50],
                    "color": NODE_COLORS[color_key],
                    "accuracy": m.get("accuracy_score"),
                }
                edges.append({"source": mid, "target": f"brand-{brand_id}", "type": "ABOUT"})

            for p in record.get("platforms") or []:
                if p is None:
                    continue
                pid = f"platform-{p['name']}"
                nodes[pid] = {
                    "id": pid,
                    "type": "Platform",
                    "label": p["name"].title(),
                    "color": NODE_COLORS["Platform"],
                }

            for s in record.get("sources") or []:
                if s is None:
                    continue
                sid = f"source-{s['url']}"
                nodes[sid] = {
                    "id": sid,
                    "type": "Source",
                    "label": s.get("domain", s["url"]),
                    "color": NODE_COLORS["Source"],
                }

            for c in record.get("corrections") or []:
                if c is None:
                    continue
                cid = f"correction-{c['id']}"
                nodes[cid] = {
                    "id": cid,
                    "type": "Correction",
                    "label": (c.get("content") or "")[:40],
                    "color": NODE_COLORS["Correction"],
                }

        rel_query = """
        MATCH (b:Brand {id: $brand_id})
        OPTIONAL MATCH (m:Mention)-[r1:ABOUT]->(b)
        OPTIONAL MATCH (m)-[r2:FOUND_ON]->(p:Platform)
        OPTIONAL MATCH (m)-[r3:SOURCED_FROM]->(s:Source)
        OPTIONAL MATCH (s)-[r4:FEEDS]->(p2:Platform)
        OPTIONAL MATCH (c:Correction)-[r5:CORRECTS]->(m)
        RETURN m.id AS mid, p.name AS pname, s.url AS surl,
               p2.name AS p2name, c.id AS cid
        """
        rels = await self.run_query(rel_query, {"brand_id": brand_id})
        seen_edges: set[tuple] = set()

        for r in rels:
            mid = r.get("mid")
            if mid:
                key_found = (f"mention-{mid}", r.get("pname"))
                if r.get("pname") and key_found not in seen_edges:
                    edges.append({
                        "source": f"mention-{mid}",
                        "target": f"platform-{r['pname']}",
                        "type": "FOUND_ON",
                    })
                    seen_edges.add(key_found)

                key_src = (f"mention-{mid}", r.get("surl"))
                if r.get("surl") and key_src not in seen_edges:
                    edges.append({
                        "source": f"mention-{mid}",
                        "target": f"source-{r['surl']}",
                        "type": "SOURCED_FROM",
                    })
                    seen_edges.add(key_src)

            if r.get("surl") and r.get("p2name"):
                key_feeds = (r["surl"], r["p2name"])
                if key_feeds not in seen_edges:
                    edges.append({
                        "source": f"source-{r['surl']}",
                        "target": f"platform-{r['p2name']}",
                        "type": "FEEDS",
                    })
                    seen_edges.add(key_feeds)

            if r.get("cid") and mid:
                key_corr = (r["cid"], mid)
                if key_corr not in seen_edges:
                    edges.append({
                        "source": f"correction-{r['cid']}",
                        "target": f"mention-{mid}",
                        "type": "CORRECTS",
                    })
                    seen_edges.add(key_corr)

        return {"nodes": list(nodes.values()), "edges": edges}


# ── Singleton accessor ──────────────────────────────────────────

_client: Optional[Neo4jClient] = None


def get_neo4j_client() -> Neo4jClient:
    """Return a module-level Neo4jClient singleton."""
    global _client
    if _client is None:
        _client = Neo4jClient()
    return _client


# ── Utility ─────────────────────────────────────────────────────

def _extract_domain(url: str) -> str:
    """Pull the domain from a URL."""
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc or url
    except Exception:
        return url
