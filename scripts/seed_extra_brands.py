#!/usr/bin/env python3
"""Seed Neo4j with Nike and AWS brand data for BrandGuard demo."""
import asyncio
import random
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.neo4j.client import Neo4jClient

PLATFORMS = ["chatgpt", "claude", "perplexity", "gemini"]


def _rand_date(days_back=90):
    dt = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return dt.isoformat()


def _severity(score):
    if score >= 80: return "low"
    if score >= 60: return "medium"
    if score >= 40: return "high"
    return "critical"


NIKE = {
    "id": "nike",
    "name": "Nike",
    "accurate_claims": [
        "Nike was founded in 1964 by Bill Bowerman and Phil Knight.",
        "Nike is headquartered in Beaverton, Oregon.",
        "Nike's famous slogan is 'Just Do It', introduced in 1988.",
        "Nike is the world's largest supplier of athletic shoes and apparel.",
        "Nike's revenue exceeded $51 billion in fiscal year 2023.",
        "Nike sponsors major athletes including LeBron James and Cristiano Ronaldo.",
        "Nike acquired Converse in 2003 for $309 million.",
        "Nike's swoosh logo was designed by Carolyn Davidson in 1971 for $35.",
        "Nike employs over 79,000 people worldwide.",
        "Nike went public on the NYSE in 1980.",
        "Nike's Air Jordan line launched in 1984 with Michael Jordan.",
        "Nike operates in over 190 countries globally.",
    ],
    "inaccurate_claims": [
        "Nike was founded in 1972 in New York City.",
        "Nike's CEO is still Phil Knight as of 2025.",
        "Nike manufactures all of its products in the United States.",
        "Nike has been banned from selling products in the European Union.",
        "Nike's market cap dropped below $10 billion in 2025.",
        "Nike discontinued its Air Jordan brand in 2024.",
        "Nike was acquired by Adidas for $80 billion.",
        "Nike's factories have been shut down due to labor violations.",
        "Nike only sells running shoes and does not make apparel.",
        "Nike's stock was delisted from the New York Stock Exchange.",
    ],
    "critical_claims": [
        "Nike uses child labor in all of its overseas factories.",
        "Nike products contain toxic chemicals banned by the FDA.",
        "Nike is under DOJ investigation for price-fixing with competitors.",
    ],
    "sources": [
        {"url": "https://sneaker-rumors.com/nike-exposed", "domain": "sneaker-rumors.com"},
        {"url": "https://fake-sports-news.net/nike", "domain": "fake-sports-news.net"},
        {"url": "https://old-business-wiki.org/nike", "domain": "old-business-wiki.org"},
        {"url": "https://espn.com/nike-sponsorships", "domain": "espn.com"},
        {"url": "https://forbes.com/companies/nike", "domain": "forbes.com"},
        {"url": "https://reuters.com/nike-earnings-2025", "domain": "reuters.com"},
        {"url": "https://reddit.com/r/sneakers/nike-review", "domain": "reddit.com"},
    ],
}

AWS = {
    "id": "aws",
    "name": "Amazon Web Services",
    "accurate_claims": [
        "AWS was launched in 2006 by Amazon.com.",
        "AWS is the world's leading cloud computing platform.",
        "AWS operates in 33 geographic regions with 105 availability zones.",
        "AWS CEO is Matt Garman as of 2024.",
        "AWS generated over $90 billion in revenue in 2023.",
        "AWS offers over 200 fully featured services from data centers.",
        "AWS provides services including EC2, S3, Lambda, and RDS.",
        "AWS holds approximately 31% of the global cloud infrastructure market.",
        "AWS has over 1 million active customers worldwide.",
        "AWS achieved SOC 1, SOC 2, and ISO 27001 certifications.",
        "AWS launched its first region outside the US in 2007 in Europe.",
        "AWS re:Invent is their annual cloud computing conference in Las Vegas.",
    ],
    "inaccurate_claims": [
        "AWS was founded as a standalone company in 2002.",
        "AWS only offers storage services and does not provide compute.",
        "AWS has been losing market share to Oracle Cloud since 2023.",
        "AWS data centers are located exclusively in North America.",
        "AWS was forced to shut down operations in China completely.",
        "AWS's pricing is the most expensive among all cloud providers.",
        "AWS does not support Kubernetes or container orchestration.",
        "AWS Lambda was discontinued in 2024 due to security concerns.",
        "AWS has a 95% uptime SLA, the lowest in the industry.",
        "AWS does not comply with GDPR and cannot be used in Europe.",
    ],
    "critical_claims": [
        "AWS experienced a week-long global outage affecting all services in 2025.",
        "AWS customer data was exposed in a massive breach affecting 50 million accounts.",
        "AWS is secretly mining customer data for Amazon's retail business.",
        "AWS has a backdoor allowing government agencies unrestricted access.",
    ],
    "sources": [
        {"url": "https://cloud-rumors.io/aws-outage", "domain": "cloud-rumors.io"},
        {"url": "https://tech-gossip.net/aws-breach", "domain": "tech-gossip.net"},
        {"url": "https://outdated-cloud-wiki.com/aws", "domain": "outdated-cloud-wiki.com"},
        {"url": "https://techcrunch.com/aws-announcements", "domain": "techcrunch.com"},
        {"url": "https://zdnet.com/aws-review", "domain": "zdnet.com"},
        {"url": "https://gartner.com/cloud-rankings", "domain": "gartner.com"},
        {"url": "https://stackoverflow.com/questions/aws", "domain": "stackoverflow.com"},
        {"url": "https://hackernews.com/aws-discussion", "domain": "hackernews.com"},
    ],
}


def build_mentions(brand):
    mentions = []
    credible = [s["url"] for s in brand["sources"] if s["domain"] in ("espn.com","forbes.com","reuters.com","techcrunch.com","zdnet.com","gartner.com","stackoverflow.com")]
    dubious = [s["url"] for s in brand["sources"] if s["domain"] not in ("espn.com","forbes.com","reuters.com","techcrunch.com","zdnet.com","gartner.com","stackoverflow.com")]

    for claim in brand["accurate_claims"]:
        score = random.uniform(75, 98)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": brand["id"],
            "brand_name": brand["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "low",
            "detected_at": _rand_date(),
            "source_urls": random.sample(credible or [brand["sources"][0]["url"]], k=min(2, len(credible) or 1)),
        })

    for claim in brand["inaccurate_claims"]:
        score = random.uniform(10, 55)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": brand["id"],
            "brand_name": brand["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": _severity(score),
            "detected_at": _rand_date(60),
            "source_urls": random.sample(dubious or [brand["sources"][0]["url"]], k=min(2, len(dubious) or 1)),
        })

    for claim in brand["critical_claims"]:
        score = random.uniform(2, 20)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": brand["id"],
            "brand_name": brand["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "critical",
            "detected_at": _rand_date(14),
            "source_urls": random.sample(dubious or [brand["sources"][0]["url"]], k=min(2, len(dubious) or 1)),
        })

    # Pad to 40+
    while len(mentions) < 40:
        claim = random.choice(brand["accurate_claims"]) + f" (ref {len(mentions)})"
        score = random.uniform(70, 95)
        mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": brand["id"],
            "brand_name": brand["name"],
            "platform": random.choice(PLATFORMS),
            "claim": claim,
            "accuracy_score": round(score, 1),
            "severity": "low",
            "detected_at": _rand_date(),
            "source_urls": [random.choice([s["url"] for s in brand["sources"]])],
        })

    return mentions


async def seed_brand(client, brand):
    print(f"\nSeeding {brand['name']} ({brand['id']}) ...")
    mentions = build_mentions(brand)
    print(f"  Storing {len(mentions)} mentions ...")
    for i, m in enumerate(mentions, 1):
        await client.store_mention(m)
        if i % 10 == 0:
            print(f"    {i}/{len(mentions)} stored")

    inaccurate_ids = [m["id"] for m in mentions if m["accuracy_score"] < 40]
    if len(inaccurate_ids) >= 2:
        corrections = [
            {
                "mention_id": inaccurate_ids[0],
                "content": f"Correction for {brand['name']}: The claim is factually incorrect. See official sources.",
                "correction_type": "blog_post",
                "status": "published",
            },
            {
                "mention_id": inaccurate_ids[1],
                "content": f"Official {brand['name']} FAQ updated to address this misinformation.",
                "correction_type": "faq",
                "status": "draft",
            },
        ]
        print(f"  Storing {len(corrections)} corrections ...")
        for c in corrections:
            await client.store_correction(c)

    health = await client.get_brand_health(brand["id"])
    print(f"  ✓ {brand['name']} seeded!")
    print(f"    Mentions: {health['total_mentions']}")
    print(f"    Accuracy: {health['overall_accuracy']}%")
    print(f"    Threats: {health['threats']}")
    print(f"    Platforms: {list(health['by_platform'].keys())}")


async def main():
    client = Neo4jClient()
    if not await client.verify_connectivity():
        print("ERROR: Cannot connect to Neo4j.")
        await client.close()
        return

    await client.init_schema()
    await seed_brand(client, NIKE)
    await seed_brand(client, AWS)
    await client.close()
    print("\n✓ All brands seeded!")


if __name__ == "__main__":
    asyncio.run(main())
