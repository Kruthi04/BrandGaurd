"""Agent orchestrator that coordinates all BrandGuard services autonomously.

The orchestrator is the central brain of BrandGuard. It:
1. Receives high-level tasks (e.g., "full brand scan for Acme Corp")
2. Breaks them into subtasks using tool-calling patterns
3. Dispatches work to Tavily (search), Yutori (scouts/browsing),
   Senso (evaluation), Modulate (voice), and Neo4j (graph storage)
4. Aggregates results into actionable intelligence
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.config import settings
from app.services.senso import SensoGEOClient, SensoSDKClient
from app.services.tavily import TavilyClient
from app.services.neo4j import Neo4jClient
from app.services.yutori import YutoriClient
from app.services.modulate import ModulateService

logger = logging.getLogger(__name__)

# In-memory task store for tracking async agent tasks
_task_store: dict[str, dict[str, Any]] = {}


class AgentOrchestrator:
    """Autonomous agent that orchestrates all brand monitoring services."""

    def __init__(self):
        self.senso_geo = SensoGEOClient()
        self.senso_sdk = SensoSDKClient()
        self.tavily = TavilyClient()
        self.neo4j = Neo4jClient()
        self.yutori = YutoriClient()
        self.modulate = ModulateService()
        self.model = settings.OPENAI_MODEL

    async def chat(self, message: str, brand_id: Optional[str] = None, session_id: Optional[str] = None) -> dict[str, Any]:
        """Process a chat message and respond with relevant brand intelligence.

        Routes messages to appropriate services based on keywords:
        - "search" / "find" → Tavily web search
        - "health" / "score" → Neo4j brand health
        - "threats" / "sources" → Neo4j threat sources
        - "evaluate" / "check" → Senso GEO evaluate
        - "scan" → Full brand scan
        - Default → Brand health summary
        """
        brand = brand_id or "default"
        msg_lower = message.lower()
        actions_taken = []

        try:
            if any(kw in msg_lower for kw in ["search", "find", "web"]):
                result = await self.tavily.search(
                    query=f"{brand} {message}",
                    max_results=5,
                    include_answer=True,
                )
                actions_taken.append("tavily_search")
                return {
                    "response": result.get("answer", "No answer synthesized."),
                    "sources": [
                        {"url": r.get("url"), "title": r.get("title")}
                        for r in result.get("results", [])[:5]
                    ],
                    "actions": actions_taken,
                }

            if any(kw in msg_lower for kw in ["health", "score", "accuracy", "overview"]):
                health = await self.neo4j.get_brand_health(brand)
                actions_taken.append("neo4j_brand_health")
                return {
                    "response": (
                        f"Brand health for '{brand}': "
                        f"Overall accuracy {health['overall_accuracy']}%, "
                        f"{health['total_mentions']} total mentions, "
                        f"{health['threats']} threats detected."
                    ),
                    "data": health,
                    "actions": actions_taken,
                }

            if any(kw in msg_lower for kw in ["threat", "source", "misinfo"]):
                sources = await self.neo4j.get_brand_sources(brand, limit=10)
                actions_taken.append("neo4j_brand_sources")
                return {
                    "response": f"Found {len(sources)} misinformation sources for '{brand}'.",
                    "sources": sources,
                    "actions": actions_taken,
                }

            if any(kw in msg_lower for kw in ["evaluate", "check", "verify"]):
                try:
                    eval_result = await self.senso_geo.evaluate(
                        query=message, brand=brand, network="all"
                    )
                    actions_taken.append("senso_evaluate")
                    return {
                        "response": "Content evaluated with Senso GEO.",
                        "evaluation": eval_result,
                        "actions": actions_taken,
                    }
                except Exception as exc:
                    logger.warning("Senso evaluate failed: %s", exc)
                    return {
                        "response": f"Evaluation attempted but Senso returned an error: {exc}",
                        "actions": ["senso_evaluate_failed"],
                    }

            if "scan" in msg_lower:
                return await self.run_full_scan(brand)

            # Default: return brand health summary
            health = await self.neo4j.get_brand_health(brand)
            actions_taken.append("neo4j_brand_health")
            return {
                "response": (
                    f"Brand '{brand}' has an accuracy score of {health['overall_accuracy']}% "
                    f"across {health['total_mentions']} mentions. "
                    f"Ask me to search the web, check threats, evaluate content, or run a full scan."
                ),
                "data": health,
                "actions": actions_taken,
            }
        except Exception as exc:
            logger.error("Agent chat error: %s", exc)
            return {
                "response": f"I encountered an error processing your request: {exc}",
                "actions": ["error"],
                "error": str(exc),
            }

    async def run_full_scan(self, brand_id: str) -> dict[str, Any]:
        """Run a comprehensive brand reputation scan.

        Pipeline: Tavily search → Senso evaluation → Neo4j storage → report
        """
        task_id = str(uuid.uuid4())
        steps_completed = []
        mentions_stored = 0
        errors = []

        # Step 1: Search the web for brand mentions
        try:
            search_result = await self.tavily.search(
                query=f"{brand_id} brand reputation claims",
                topic="news",
                search_depth="advanced",
                max_results=10,
                include_answer=True,
            )
            steps_completed.append("web_search")
            web_results = search_result.get("results", [])
        except Exception as exc:
            logger.warning("Full scan: Tavily search failed: %s", exc)
            errors.append(f"web_search: {exc}")
            web_results = []

        # Step 2: Evaluate each result with Senso GEO
        evaluated = []
        for result in web_results[:10]:
            claim = result.get("content", result.get("title", ""))[:300]
            try:
                eval_result = await self.senso_geo.evaluate(
                    query=claim, brand=brand_id, network="all"
                )
                accuracy = eval_result.get("accuracy_score", eval_result.get("score", 50))
                evaluated.append({
                    "claim": claim,
                    "url": result.get("url", ""),
                    "accuracy_score": float(accuracy),
                    "evaluation": eval_result,
                })
            except Exception:
                # Assign a default score if Senso is unavailable
                evaluated.append({
                    "claim": claim,
                    "url": result.get("url", ""),
                    "accuracy_score": 50.0,
                    "evaluation": {"fallback": True},
                })
        if evaluated:
            steps_completed.append("senso_evaluation")

        # Step 3: Store mentions in Neo4j
        for item in evaluated:
            severity = "low"
            score = item["accuracy_score"]
            if score < 40:
                severity = "critical"
            elif score < 60:
                severity = "high"
            elif score < 80:
                severity = "medium"

            mention = {
                "brand_id": brand_id,
                "brand_name": brand_id,
                "platform": "web",
                "claim": item["claim"],
                "accuracy_score": score,
                "severity": severity,
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "source_urls": [item["url"]] if item.get("url") else [],
            }
            try:
                await self.neo4j.store_mention(mention)
                mentions_stored += 1
            except Exception as exc:
                errors.append(f"neo4j_store: {exc}")
        if mentions_stored > 0:
            steps_completed.append("neo4j_storage")

        # Step 4: Get updated brand health
        try:
            health = await self.neo4j.get_brand_health(brand_id)
            steps_completed.append("health_report")
        except Exception:
            health = {}

        return {
            "task_id": task_id,
            "task_type": "full_scan",
            "brand_id": brand_id,
            "status": "completed",
            "steps_completed": steps_completed,
            "results": {
                "web_results_found": len(web_results),
                "mentions_evaluated": len(evaluated),
                "mentions_stored": mentions_stored,
                "health": health,
            },
            "errors": errors,
        }

    async def run_threat_assessment(self, brand_id: str) -> dict[str, Any]:
        """Assess current threats to the brand.

        Pipeline: Neo4j existing data → Tavily fresh search → combined report
        """
        task_id = str(uuid.uuid4())
        steps_completed = []
        errors = []

        # Step 1: Get existing threats from Neo4j
        try:
            health = await self.neo4j.get_brand_health(brand_id)
            sources = await self.neo4j.get_brand_sources(brand_id, limit=10)
            steps_completed.append("neo4j_query")
        except Exception as exc:
            health = {}
            sources = []
            errors.append(f"neo4j: {exc}")

        # Step 2: Search for recent threats
        try:
            search = await self.tavily.search(
                query=f"{brand_id} misinformation controversy negative claims",
                topic="news",
                time_range="week",
                max_results=10,
                include_answer=True,
            )
            steps_completed.append("tavily_search")
            new_threats = [
                {
                    "url": r.get("url"),
                    "title": r.get("title"),
                    "snippet": r.get("content", "")[:200],
                    "score": r.get("score", 0),
                }
                for r in search.get("results", [])
            ]
        except Exception as exc:
            new_threats = []
            errors.append(f"tavily: {exc}")

        return {
            "task_id": task_id,
            "task_type": "threat_assessment",
            "brand_id": brand_id,
            "status": "completed",
            "steps_completed": steps_completed,
            "results": {
                "overall_accuracy": health.get("overall_accuracy", 0),
                "total_threats": health.get("threats", 0),
                "known_sources": sources,
                "new_threats": new_threats,
                "summary": search.get("answer", "") if "tavily_search" in steps_completed else "Could not search for new threats.",
            },
            "errors": errors,
        }

    async def run_compliance_check(self, brand_id: str, content: str) -> dict[str, Any]:
        """Check content for brand compliance using Senso GEO.

        Pipeline: Senso evaluate → report
        """
        task_id = str(uuid.uuid4())
        steps_completed = []
        errors = []

        # Evaluate with Senso GEO
        try:
            eval_result = await self.senso_geo.evaluate(
                query=content, brand=brand_id, network="all"
            )
            steps_completed.append("senso_evaluate")
            accuracy = eval_result.get("accuracy_score", eval_result.get("score", None))
            is_compliant = accuracy is not None and float(accuracy) >= 70
        except Exception as exc:
            logger.warning("Compliance check: Senso failed: %s", exc)
            errors.append(f"senso: {exc}")
            eval_result = {"error": str(exc), "fallback": True}
            accuracy = None
            is_compliant = None

        # Try to search brand knowledge for context
        try:
            knowledge = await self.senso_sdk.search(query=content)
            steps_completed.append("senso_sdk_search")
        except Exception as exc:
            knowledge = {}
            errors.append(f"senso_sdk: {exc}")

        return {
            "task_id": task_id,
            "task_type": "compliance_check",
            "brand_id": brand_id,
            "status": "completed",
            "steps_completed": steps_completed,
            "results": {
                "is_compliant": is_compliant,
                "accuracy_score": accuracy,
                "evaluation": eval_result,
                "knowledge_context": knowledge,
                "content_checked": content[:200],
            },
            "errors": errors,
        }


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a task from the in-memory store."""
    return _task_store.get(task_id)


def store_task(task: dict[str, Any]) -> None:
    """Save a task result to the in-memory store."""
    _task_store[task.get("task_id", str(uuid.uuid4()))] = task


def list_tasks(status: Optional[str] = None) -> list[dict[str, Any]]:
    """List all stored tasks, optionally filtered by status."""
    tasks = list(_task_store.values())
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    return tasks
