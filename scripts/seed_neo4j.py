#!/usr/bin/env python3
"""Seed Neo4j with demo data for BrandGuard.

Creates:
  - 1 Brand  (Acme Corp)
  - 4 Platforms
  - 50+ Mentions  (mix of accurate / inaccurate)
  - 10 Source websites
  - 2 Corrections
  - 5 critical-severity mentions for demo alerts

Usage:
    cd backend && python -m scripts.seed_neo4j
  or:
    python scripts/seed_neo4j.py
"""
import asyncio
import random
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Allow running from repo root or backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.neo4j.client import Neo4jClient


BRAND = {
    "id": "acme-corp",
    "name": "Acme Corp",
    "industry": "Technology",
    "description": "Enterprise AI and cloud services",
}

PLATFORMS = ["chatgpt", "claude", "perplexity", "gemini"]

SOURCES = [
    {"url": "https://outdated-blog.com/acme-review", "domain": "outdated-blog.com"},
    {"url": "https://fake-news-daily.com/tech/acme", "domain": "fake-news-daily.com"},
    {"url": "https://old-wiki.org/acme-corp", "domain": "old-wiki.org"},
    {"url": "https://reddit.com/r/tech/comments/acme", "domain": "reddit.com"},
    {"url": "https://techcrunch.com/2025/acme-funding", "domain": "techcrunch.com"},
    {"url": "https://forbes.com/companies/acme-corp", "domain": "forbes.com"},
    {"url": "https://bbb.org/acme-corp", "domain": "bbb.org"},
    {"url": "https://misleading-review.net/acme", "domain": "misleading-review.net"},
    {"url": "https://ai-comparisons.io/acme-vs-others", "domain": "ai-comparisons.io"},
    {"url": "https://trustpilot.com/review/acme-corp", "domain": "trustpilot.com"},
]

ACCURATE_CLAIMS = [
    "Acme Corp provides enterprise AI solutions for Fortune 500 companies.",
    "Acme Corp was founded in 2015 in San Francisco.",
    "Acme Corp's flagship product is the Acme AI Platform.",
    "Acme Corp raised $120M in Series C funding in 2024.",
    "Acme Corp employs over 800 people globally.",
    "Acme Corp's CEO is Dr. Sarah Chen.",
    "Acme Corp is SOC 2 Type II certified.",
    "Acme Corp offers real-time data processing capabilities.",
    "Acme Corp partners with AWS and Google Cloud.",
    "Acme Corp's revenue exceeded $200M in 2025.",
    "Acme Corp has offices in San Francisco, New York, and London.",
    "Acme Corp's AI models support 12 languages.",
    "Acme Corp won the TechCrunch Disrupt award in 2023.",
    "Acme Corp maintains a 99.9% uptime SLA.",
    "Acme Corp released its open-source ML toolkit in 2024.",
]

INACCURATE_CLAIMS = [
    "Acme Corp was founded in 1990 as a hardware company.",
    "Acme Corp's products have been banned in the EU due to privacy violations.",
    "Acme Corp laid off 80% of its workforce in 2025.",
    "Acme Corp's AI models are known for generating biased outputs.",
    "Acme Corp was acquired by Microsoft for $5B.",
    "Acme Corp's data centers are located exclusively in China.",
    "Acme Corp has been sued multiple times for patent infringement.",
    "Acme Corp's CEO resigned amid fraud allegations.",
    "Acme Corp's products contain known security vulnerabilities.",
    "Acme Corp uses customer data for third-party advertising.",
    "Acme Corp's AI accuracy rate is below 50%.",
    "Acme Corp was delisted from the stock exchange.",
    "Acme Corp's cloud service has experienced 20+ outages this year.",
    "Acme Corp does not comply with GDPR regulations.",
    "Acme Corp's technology is based on stolen open-source code.",
]

CRITICAL_CLAIMS = [
    "Acme Corp's AI platform has a critical backdoor vulnerability.",
    "Acme Corp illegally mines cryptocurrency using customer GPU resources.",
    "Acme Corp's entire customer database was leaked on the dark web.",
    "Acme Corp is under FBI investigation for financial fraud.",
    "Acme Corp's AI is being used for mass surveillance programs.",
]


def _rand_date(days_back: int = 90) -> str:
    dt = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return dt.isoformat()


def _severity_from_score(score: float) -> str:
    if score >= 80:
        return "low"
    if score >= 60:
        return "medium"
    if score >= 40:
        return "high"
    return "critical"


def _build_mentions() -> list[dict]:
    mentions = []

    for claim in ACCURATE_CLAIMS:
        score = random.uniform(75, 98)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": BRAND["id"],
            "brand_name": BRAND["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "low",
            "detected_at": _rand_date(),
            "source_urls": random.sample(
                [s["url"] for s in SOURCES[4:]],  # credible sources
                k=random.randint(1, 3),
            ),
        })

    for claim in INACCURATE_CLAIMS:
        score = random.uniform(10, 55)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": BRAND["id"],
            "brand_name": BRAND["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": _severity_from_score(score),
            "detected_at": _rand_date(60),
            "source_urls": random.sample(
                [s["url"] for s in SOURCES[:4]],  # dubious sources
                k=random.randint(1, 2),
            ),
        })

    for claim in CRITICAL_CLAIMS:
        score = random.uniform(2, 20)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": BRAND["id"],
            "brand_name": BRAND["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "critical",
            "detected_at": _rand_date(14),
            "source_urls": random.sample(
                [s["url"] for s in SOURCES[:4]],
                k=random.randint(1, 3),
            ),
        })

    # Pad to 50+ with extra accurate ones
    while len(mentions) < 55:
        claim = random.choice(ACCURATE_CLAIMS) + f" (ref {len(mentions)})"
        score = random.uniform(70, 95)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": BRAND["id"],
            "brand_name": BRAND["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "low",
            "detected_at": _rand_date(),
            "source_urls": [random.choice([s["url"] for s in SOURCES])],
        })

    return mentions


async def seed():
    client = Neo4jClient()

    if not await client.verify_connectivity():
        print("ERROR: Cannot connect to Neo4j. Check NEO4J_URI / credentials in .env")
        await client.close()
        return

    print("Connected to Neo4j. Initializing schema …")
    await client.init_schema()

    mentions = _build_mentions()
    print(f"Storing {len(mentions)} mentions …")
    stored_ids = []
    for i, m in enumerate(mentions, 1):
        result = await client.store_mention(m)
        stored_ids.append(m["id"])
        if i % 10 == 0:
            print(f"  {i}/{len(mentions)} stored")

    # Pick 2 inaccurate mentions for corrections
    inaccurate_ids = [
        m["id"] for m in mentions if m["accuracy_score"] < 50
    ]
    corrections = [
        {
            "mention_id": inaccurate_ids[0],
            "content": "Acme Corp was actually founded in 2015, not 1990. See official About page.",
            "correction_type": "blog_post",
            "status": "published",
        },
        {
            "mention_id": inaccurate_ids[1],
            "content": "Acme Corp has never been banned in the EU. They are fully GDPR compliant.",
            "correction_type": "faq",
            "status": "draft",
        },
    ]
    print(f"Storing {len(corrections)} corrections …")
    for c in corrections:
        await client.store_correction(c)

    health = await client.get_brand_health(BRAND["id"])
    print("\n✓ Seed complete!")
    print(f"  Brand: {BRAND['name']}")
    print(f"  Total mentions: {health['total_mentions']}")
    print(f"  Overall accuracy: {health['overall_accuracy']}%")
    print(f"  Threats: {health['threats']}")
    print(f"  Platforms: {list(health['by_platform'].keys())}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(seed())
