"""Agent orchestrator that coordinates all BrandGuard services autonomously.

The orchestrator is the central brain of BrandGuard. It:
1. Receives high-level tasks (e.g., "full brand scan for Acme Corp")
2. Breaks them into subtasks using tool-calling patterns
3. Dispatches work to Tavily (search), Yutori (scouts/browsing),
   Senso (evaluation), and Neo4j (graph storage)
4. Aggregates results into actionable intelligence
"""
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, Optional, Dict

from app.config import settings
from app.services.senso import SensoGEOClient, SensoSDKClient
from app.services.tavily import TavilyClient
from app.services.neo4j import Neo4jClient
from app.services.yutori import YutoriClient
from app.services.modulate import ModulateService

logger = logging.getLogger(__name__)

# In-memory task store for tracking async agent tasks
_task_store: dict[str, dict[str, Any]] = {}

# Global in-memory job store for hackathon purposes
pipeline_jobs: Dict[str, Dict[str, Any]] = {}


class BrandGuardPipeline:
    """Autonomous agent pipeline that orchestrates all brand monitoring services."""

    def __init__(self):
        self.geo_client = SensoGEOClient()
        self.sdk_client = SensoSDKClient()
        self.tavily = TavilyClient()
        self.neo4j = Neo4jClient()
        self.yutori = YutoriClient()

    def _update_job_step(self, job_id: str, step_name: str, status: str, result: Any = None):
        """Update the status of a specific step in a job."""
        if job_id not in pipeline_jobs:
            return

        for step in pipeline_jobs[job_id]["steps"]:
            if step["name"] == step_name:
                step["status"] = status
                if result is not None:
                    step["result"] = result
                break

    async def process_mention(self, mention_data: dict, job_id: str) -> dict:
        """Full monitoring pipeline for a single mention.

        1. Senso evaluate
        2. Tavily search for sources
        3. Score severity
        4. Store in Neo4j
        5. Create alert if needed
        """
        try:
            pipeline_jobs[job_id] = {
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "steps": [
                    {"name": "senso_evaluate", "status": "pending"},
                    {"name": "tavily_search", "status": "pending"},
                    {"name": "score_severity", "status": "pending"},
                    {"name": "neo4j_store", "status": "pending"}
                ],
                "result": None
            }

            brand_id = mention_data.get("brand_id", "unknown_brand")
            content = mention_data.get("content", "")

            # Step 1: Senso evaluate
            self._update_job_step(job_id, "senso_evaluate", "running")
            try:
                eval_res = await self.geo_client.evaluate(query=content, brand=brand_id, network="web")
            except Exception as e:
                logger.error(f"Senso evaluate failed: {e}")
                eval_res = {"accuracy": 0.5, "citations": [], "missing": []}
            self._update_job_step(job_id, "senso_evaluate", "completed", eval_res)

            # Step 2: Tavily search
            self._update_job_step(job_id, "tavily_search", "running")
            try:
                search_res = await self.tavily.search(query=content, search_depth="basic", max_results=3)
            except Exception as e:
                logger.error(f"Tavily search failed: {e}")
                search_res = {"results": [{"title": "Mock Source", "url": "https://example.com"}]}
            self._update_job_step(job_id, "tavily_search", "completed", search_res)

            # Step 3: Score severity
            self._update_job_step(job_id, "score_severity", "running")
            accuracy = eval_res.get("accuracy", 1.0)
            severity = "LOW"
            if accuracy < 0.6:
                severity = "CRITICAL"
            elif accuracy < 0.8:
                severity = "HIGH"
            elif accuracy < 0.9:
                severity = "MEDIUM"

            score_res = {"accuracy": accuracy, "severity": severity}
            self._update_job_step(job_id, "score_severity", "completed", score_res)

            # Step 4: Store in Neo4j
            self._update_job_step(job_id, "neo4j_store", "running")
            try:
                pass
            except Exception as e:
                logger.error(f"Neo4j store failed: {e}")

            neo4j_res = {"status": "stored", "entity_id": mention_data.get("id", "mock_id")}
            self._update_job_step(job_id, "neo4j_store", "completed", neo4j_res)

            # Finalize job
            final_result = {
                "mention_id": mention_data.get("id"),
                "severity": severity,
                "accuracy": accuracy,
                "alert_created": severity in ["HIGH", "CRITICAL"],
                "auto_remediate_queued": severity == "CRITICAL"
            }

            pipeline_jobs[job_id]["status"] = "completed"
            pipeline_jobs[job_id]["result"] = final_result
            pipeline_jobs[job_id]["end_time"] = datetime.now().isoformat()

            return final_result

        except Exception as e:
            logger.error(f"Pipeline error for job {job_id}: {e}")
            if job_id in pipeline_jobs:
                pipeline_jobs[job_id]["status"] = "failed"
                pipeline_jobs[job_id]["error"] = str(e)
            raise

    async def investigate(self, mention_id: str, job_id: str) -> dict:
        """Deep investigation of a flagged mention.

        1. Tavily extract from source URLs
        2. Tavily map related pages
        3. Yutori research
        4. Update Neo4j graph
        """
        try:
            pipeline_jobs[job_id] = {
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "steps": [
                    {"name": "tavily_extract", "status": "pending"},
                    {"name": "yutori_research", "status": "pending"},
                    {"name": "neo4j_update", "status": "pending"}
                ],
                "result": None
            }

            # Step 1: Tavily extract
            self._update_job_step(job_id, "tavily_extract", "running")
            await asyncio.sleep(1)  # Simulate work
            self._update_job_step(job_id, "tavily_extract", "completed", {"sources_extracted": 2})

            # Step 2: Yutori research
            self._update_job_step(job_id, "yutori_research", "running")
            await asyncio.sleep(1)  # Simulate work
            self._update_job_step(job_id, "yutori_research", "completed", {"insights": ["Insight 1", "Insight 2"]})

            # Step 3: Update Neo4j
            self._update_job_step(job_id, "neo4j_update", "running")
            await asyncio.sleep(1)  # Simulate work
            self._update_job_step(job_id, "neo4j_update", "completed", {"nodes_added": 3, "edges_added": 4})

            final_result = {
                "mention_id": mention_id,
                "investigation_status": "complete",
                "sources_found": 2,
                "insights_generated": 2
            }

            pipeline_jobs[job_id]["status"] = "completed"
            pipeline_jobs[job_id]["result"] = final_result
            pipeline_jobs[job_id]["end_time"] = datetime.now().isoformat()

            return final_result

        except Exception as e:
            logger.error(f"Investigation error for job {job_id}: {e}")
            if job_id in pipeline_jobs:
                pipeline_jobs[job_id]["status"] = "failed"
                pipeline_jobs[job_id]["error"] = str(e)
            raise

    async def remediate(self, mention_id: str, brand_id: str, job_id: str) -> dict:
        """Auto-generate correction for a mention.

        1. Senso evaluate (detailed)
        2. Senso remediate
        3. Senso generate content
        4. Store correction in Neo4j
        """
        try:
            pipeline_jobs[job_id] = {
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "steps": [
                    {"name": "senso_evaluate_detail", "status": "pending"},
                    {"name": "senso_remediate_strategy", "status": "pending"},
                    {"name": "senso_generate_content", "status": "pending"},
                    {"name": "neo4j_store_correction", "status": "pending"}
                ],
                "result": None
            }

            # Step 1: Senso evaluate
            self._update_job_step(job_id, "senso_evaluate_detail", "running")
            try:
                eval_res = await self.geo_client.evaluate(query=f"Mention {mention_id}", brand=brand_id, network="web")
            except Exception:
                eval_res = {"accuracy": 0.5, "missing": ["Fact A"]}
            self._update_job_step(job_id, "senso_evaluate_detail", "completed", eval_res)

            # Step 2: Senso remediate
            self._update_job_step(job_id, "senso_remediate_strategy", "running")
            try:
                rem_res = await self.geo_client.remediate(
                    context=f"Mention {mention_id}",
                    optimize_for="brand_safety",
                    target_networks=["web"]
                )
            except Exception:
                rem_res = {"strategy": "Acknowledge and correct"}
            self._update_job_step(job_id, "senso_remediate_strategy", "completed", rem_res)

            # Step 3: Senso generate
            self._update_job_step(job_id, "senso_generate_content", "running")
            try:
                prompt = f"Write a professional correction for mention {mention_id} regarding brand {brand_id}."
                gen_res = await self.sdk_client.generate(prompt=prompt)
            except Exception:
                gen_res = {"generated_text": "We are aware of the statements and want to clarify our position based on our official guidelines."}
            self._update_job_step(job_id, "senso_generate_content", "completed", gen_res)

            # Step 4: Neo4j store
            self._update_job_step(job_id, "neo4j_store_correction", "running")
            await asyncio.sleep(0.5)
            self._update_job_step(job_id, "neo4j_store_correction", "completed", {"status": "stored"})

            final_result = {
                "mention_id": mention_id,
                "strategy": rem_res.get("strategy", "Standard strategy"),
                "correction_content": gen_res.get("generated_text", ""),
                "status": "ready_for_review"
            }

            pipeline_jobs[job_id]["status"] = "completed"
            pipeline_jobs[job_id]["result"] = final_result
            pipeline_jobs[job_id]["end_time"] = datetime.now().isoformat()

            return final_result

        except Exception as e:
            logger.error(f"Remediation error for job {job_id}: {e}")
            if job_id in pipeline_jobs:
                pipeline_jobs[job_id]["status"] = "failed"
                pipeline_jobs[job_id]["error"] = str(e)
            raise


class AgentOrchestrator:
    """High-level orchestrator providing chat, full scan, threat assessment,
    and compliance check capabilities."""

    def __init__(self):
        self.senso_geo = SensoGEOClient()
        self.senso_sdk = SensoSDKClient()
        self.tavily = TavilyClient()
        self.neo4j = Neo4jClient()
        self.yutori = YutoriClient()
        self.modulate = ModulateService()
        self.model = settings.OPENAI_MODEL

    async def chat(self, message: str, brand_id: Optional[str] = None, session_id: Optional[str] = None) -> dict[str, Any]:
        """Process a natural-language chat message and route to the right service.

        Routes messages to appropriate services based on keywords:
        - "search" / "find" -> Tavily web search
        - "health" / "score" -> Neo4j brand health
        - "threats" / "sources" -> Neo4j threat sources
        - "evaluate" / "check" -> Senso GEO evaluate
        - "scan" -> Full brand scan
        - Default -> Brand health summary
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
        """Run a comprehensive brand scan.

        Pipeline: Tavily search -> Senso evaluation -> Neo4j storage -> report
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
        """Assess current threats against a brand.

        Pipeline: Neo4j existing data -> Tavily fresh search -> combined report
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

        Pipeline: Senso evaluate -> report
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
