"""
BrandGuard Cron Monitor

Runs every 6 hours via Render cron job.
1. Gets all active scouts from Yutori
2. Polls each scout for new updates
3. Processes any new mentions through the evaluation pipeline
"""
import asyncio
import sys
import os

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.services.yutori.client import YutoriService
from app.services.senso.client import SensoService
from app.services.neo4j.client import Neo4jService

import structlog

log = structlog.get_logger()


async def poll_scouts(yutori: YutoriService) -> list[dict]:
    """Fetch all active scouts and collect their latest updates."""
    try:
        scouts_response = await yutori.list_scouts()
        scouts = scouts_response.get("tasks", [])
        log.info("fetched_scouts", count=len(scouts))
    except NotImplementedError:
        log.warning("yutori_not_implemented", msg="Yutori list_scouts not yet implemented, skipping")
        return []
    except Exception as e:
        log.error("fetch_scouts_failed", error=str(e))
        return []

    all_updates = []
    for scout in scouts:
        scout_id = scout.get("id")
        if not scout_id:
            continue
        try:
            updates = await yutori.get_scout_updates(scout_id)
            entries = updates.get("updates", [])
            log.info("scout_updates", scout_id=scout_id, count=len(entries))
            all_updates.extend(entries)
        except NotImplementedError:
            log.warning("get_updates_not_implemented", scout_id=scout_id)
        except Exception as e:
            log.error("scout_poll_failed", scout_id=scout_id, error=str(e))

    return all_updates


async def evaluate_mentions(senso: SensoService, mentions: list[dict]) -> list[dict]:
    """Run each mention through Senso content evaluation."""
    results = []
    for mention in mentions:
        content = mention.get("content", "")
        if not content:
            continue
        try:
            evaluation = await senso.evaluate_content(content)
            results.append({**mention, "evaluation": evaluation})
            log.info("evaluated_mention", mention_id=mention.get("id"))
        except NotImplementedError:
            log.warning("senso_not_implemented", msg="Senso evaluate_content not yet implemented, skipping")
            break
        except Exception as e:
            log.error("evaluation_failed", mention_id=mention.get("id"), error=str(e))

    return results


async def store_results(neo4j: Neo4jService, evaluated: list[dict]) -> int:
    """Persist evaluated mentions to the knowledge graph."""
    stored = 0
    for item in evaluated:
        try:
            await neo4j.store_mention(item)
            stored += 1
        except NotImplementedError:
            log.warning("neo4j_not_implemented", msg="Neo4j store_mention not yet implemented, skipping")
            break
        except Exception as e:
            log.error("store_failed", error=str(e))

    return stored


async def main():
    """Main cron job entry point."""
    log.info("cron_started", msg="BrandGuard periodic monitoring started")

    # Validate minimum config
    missing = settings.validate()
    if missing:
        log.warning("missing_config", keys=missing)

    # Initialize service clients
    yutori = YutoriService()
    senso = SensoService()
    neo4j = Neo4jService()

    # Step 1: Poll all active scouts for new mentions
    mentions = await poll_scouts(yutori)
    log.info("poll_complete", total_mentions=len(mentions))

    if not mentions:
        log.info("cron_complete", msg="No new mentions found")
        return

    # Step 2: Evaluate mentions through Senso pipeline
    evaluated = await evaluate_mentions(senso, mentions)
    log.info("evaluation_complete", evaluated_count=len(evaluated))

    # Step 3: Store results in knowledge graph
    stored = await store_results(neo4j, evaluated)
    log.info("cron_complete", mentions_found=len(mentions), evaluated=len(evaluated), stored=stored)


if __name__ == "__main__":
    asyncio.run(main())
