"""Yutori API client for scouting, browsing, and research.

Three APIs power BrandGuard's monitoring system:
- Scouting: Persistent agents that continuously watch for brand mentions
- Browsing: On-demand browser automation to query AI platforms directly
- Research: Deep one-time investigation of misinformation claims
"""
import asyncio
import logging
import time
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30.0
_POLL_TIMEOUT = 300
_POLL_INTERVAL = 5

BRAND_MENTION_SCHEMA = {
    "type": "object",
    "properties": {
        "brand_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "AI platform name",
                    },
                    "claim": {
                        "type": "string",
                        "description": "The claim made about the brand",
                    },
                    "accuracy": {
                        "type": "string",
                        "enum": ["accurate", "inaccurate", "unverifiable", "partially_accurate"],
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"],
                    },
                    "source_url": {"type": "string", "description": "URL where this was found"},
                    "evidence": {"type": "string", "description": "Evidence supporting the accuracy assessment"},
                    "suggested_correction": {"type": "string", "description": "What the correct information should be"},
                },
                "required": ["platform", "claim", "accuracy", "severity"],
            },
        },
        "summary": {"type": "string", "description": "Overall brand health summary"},
        "risk_level": {"type": "string", "enum": ["critical", "elevated", "normal", "positive"]},
    },
    "required": ["brand_mentions", "summary", "risk_level"],
}

PLATFORM_URLS = {
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
    "perplexity": "https://www.perplexity.ai",
    "gemini": "https://gemini.google.com",
}


class YutoriClient:
    """Async client for Yutori Scouting, Browsing, and Research APIs."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.YUTORI_API_KEY
        self.base_url = "https://api.yutori.com"
        if not self.api_key:
            raise ValueError("Yutori API key is required. Set YUTORI_API_KEY in .env")

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method, url, json=payload, headers=self._headers()
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {"status": "ok"}
            return response.json()

    # ═══════════════════════════════════════════════════════════
    #  Scouting API
    # ═══════════════════════════════════════════════════════════

    async def create_scout(
        self,
        query: str,
        *,
        display_name: str | None = None,
        output_schema: dict | None = None,
        output_interval: int = 21600,  # 6 hours
        webhook_url: str | None = None,
        skip_email: bool = True,
        user_timezone: str = "America/Los_Angeles",
    ) -> dict[str, Any]:
        """Create a persistent monitoring scout.

        Args:
            query: Natural language description of what to monitor.
            display_name: Human-readable name for the scout.
            output_schema: JSON Schema for structured responses.
            output_interval: Update interval in seconds (min 1800).
            webhook_url: HTTPS URL for push notifications.
            skip_email: Disable email notifications.
            user_timezone: IANA timezone string.
        """
        payload: dict[str, Any] = {
            "query": query,
            "output_interval": output_interval,
            "skip_email": skip_email,
            "user_timezone": user_timezone,
        }
        if display_name:
            payload["display_name"] = display_name
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if output_schema:
            payload["task_spec"] = {
                "output_schema": {"type": "json", "json_schema": output_schema}
            }

        logger.info("Creating Yutori scout: %s", query[:80])
        return await self._request("POST", "/v1/scouting/tasks", payload)

    async def list_scouts(self) -> list[dict[str, Any]]:
        """List all scouts."""
        data = await self._request("GET", "/v1/scouting/tasks")
        if isinstance(data, list):
            return data
        return data.get("tasks", data.get("scouts", [data] if "id" in data else []))

    async def get_scout(self, scout_id: str) -> dict[str, Any]:
        """Get details of a specific scout."""
        return await self._request("GET", f"/v1/scouting/tasks/{scout_id}")

    async def get_scout_updates(
        self, scout_id: str, page_size: int = 20, cursor: str | None = None
    ) -> dict[str, Any]:
        """Get updates from a scout (paginated)."""
        params = f"?page_size={page_size}"
        if cursor:
            params += f"&cursor={cursor}"
        return await self._request("GET", f"/v1/scouting/tasks/{scout_id}/updates{params}")

    async def stop_scout(self, scout_id: str) -> dict[str, Any]:
        """Mark a scout as done (stops future runs)."""
        return await self._request("PUT", f"/v1/scouting/tasks/{scout_id}", {"status": "done"})

    async def delete_scout(self, scout_id: str) -> dict[str, Any]:
        """Delete a scout permanently."""
        return await self._request("DELETE", f"/v1/scouting/tasks/{scout_id}")

    # ═══════════════════════════════════════════════════════════
    #  Browsing API
    # ═══════════════════════════════════════════════════════════

    async def browse(
        self,
        task: str,
        *,
        start_url: str | None = None,
        max_steps: int = 25,
        output_schema: dict | None = None,
        agent: str = "navigator-n1-latest",
    ) -> dict[str, Any]:
        """Create a browser automation task.

        Args:
            task: Natural language description of what to do.
            start_url: Where to begin browsing.
            max_steps: Maximum browser steps (2-100).
            output_schema: JSON Schema for structured result.
            agent: Agent model to use.
        """
        payload: dict[str, Any] = {
            "task": task,
            "max_steps": max_steps,
            "agent": agent,
        }
        if start_url:
            payload["start_url"] = start_url
        if output_schema:
            payload["task_spec"] = {
                "output_schema": {"type": "json", "json_schema": output_schema}
            }

        logger.info("Creating Yutori browse task: %s", task[:80])
        return await self._request("POST", "/v1/browsing/tasks", payload)

    async def get_browse_result(self, task_id: str) -> dict[str, Any]:
        """Get the current status and result of a browsing task."""
        return await self._request("GET", f"/v1/browsing/tasks/{task_id}")

    async def poll_browse_result(
        self, task_id: str, timeout: int = _POLL_TIMEOUT, interval: int = _POLL_INTERVAL
    ) -> dict[str, Any]:
        """Poll until a browsing task completes or times out."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            result = await self.get_browse_result(task_id)
            status = result.get("status", "")
            if status in ("succeeded", "failed"):
                return result
            await asyncio.sleep(interval)
        raise TimeoutError(f"Browsing task {task_id} did not complete within {timeout}s")

    # ═══════════════════════════════════════════════════════════
    #  Research API
    # ═══════════════════════════════════════════════════════════

    async def research(
        self,
        query: str,
        *,
        output_schema: dict | None = None,
        user_timezone: str = "America/Los_Angeles",
    ) -> dict[str, Any]:
        """Start a deep research task.

        Args:
            query: What to research.
            output_schema: JSON Schema for structured output.
            user_timezone: Timezone for context.
        """
        payload: dict[str, Any] = {
            "query": query,
            "user_timezone": user_timezone,
        }
        if output_schema:
            payload["task_spec"] = {
                "output_schema": {"type": "json", "json_schema": output_schema}
            }

        logger.info("Creating Yutori research task: %s", query[:80])
        return await self._request("POST", "/v1/research/tasks", payload)

    async def get_research_result(self, task_id: str) -> dict[str, Any]:
        """Get the status and result of a research task."""
        return await self._request("GET", f"/v1/research/tasks/{task_id}")

    async def poll_research_result(
        self, task_id: str, timeout: int = _POLL_TIMEOUT, interval: int = _POLL_INTERVAL
    ) -> dict[str, Any]:
        """Poll until a research task completes or times out."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            result = await self.get_research_result(task_id)
            status = result.get("status", "")
            if status in ("succeeded", "failed"):
                return result
            await asyncio.sleep(interval)
        raise TimeoutError(f"Research task {task_id} did not complete within {timeout}s")
