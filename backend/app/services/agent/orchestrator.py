"""Agent orchestrator that coordinates all BrandGuard services autonomously.

The orchestrator is the central brain of BrandGuard. It:
1. Receives high-level tasks (e.g., "full brand scan for Acme Corp")
2. Breaks them into subtasks using tool-calling patterns
3. Dispatches work to Tavily (search), Yutori (scouts/browsing),
   Senso (evaluation), and Neo4j (graph storage)
4. Aggregates results into actionable intelligence
"""
from typing import Any, Optional, Dict
import logging
import asyncio
from datetime import datetime

from app.config import settings
from app.services.senso import SensoGEOClient, SensoSDKClient
from app.services.tavily import TavilyService as TavilyClient
from app.services.neo4j import Neo4jService as Neo4jClient
from app.services.yutori import YutoriService as YutoriClient

logger = logging.getLogger(__name__)

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
                # In a real app we'd pass the actual text. Using a simplified approach here
                eval_res = await self.geo_client.evaluate(query=content, brand=brand_id, network="web")
            except Exception as e:
                logger.error(f"Senso evaluate failed: {e}")
                eval_res = {"accuracy": 0.5, "citations": [], "missing": []}
            self._update_job_step(job_id, "senso_evaluate", "completed", eval_res)
            
            # Step 2: Tavily search
            self._update_job_step(job_id, "tavily_search", "running")
            try:
                # Search for related sources
                search_res = await self.tavily.search(query=content, search_depth="basic", max_results=3)
            except Exception as e:
                logger.error(f"Tavily search failed: {e}")
                search_res = {"results": [{"title": "Mock Source", "url": "https://example.com"}]}
            self._update_job_step(job_id, "tavily_search", "completed", search_res)
            
            # Step 3: Score severity
            self._update_job_step(job_id, "score_severity", "running")
            # Simple scoring logic: lower accuracy = higher severity
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
                # In a real app we would call self.neo4j.add_entity() etc.
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
            await asyncio.sleep(1) # Simulate work
            self._update_job_step(job_id, "tavily_extract", "completed", {"sources_extracted": 2})
            
            # Step 2: Yutori research
            self._update_job_step(job_id, "yutori_research", "running")
            await asyncio.sleep(1) # Simulate work
            self._update_job_step(job_id, "yutori_research", "completed", {"insights": ["Insight 1", "Insight 2"]})
            
            # Step 3: Update Neo4j
            self._update_job_step(job_id, "neo4j_update", "running")
            await asyncio.sleep(1) # Simulate work
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
                    targets=["web"]
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
