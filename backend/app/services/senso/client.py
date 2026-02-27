"""Senso API clients for GEO Platform and Context OS SDK.

Senso provides two core systems:
- GEO Platform (apiv2.senso.ai): Evaluate brand accuracy and generate remediation strategies.
- Context OS SDK (sdk.senso.ai): Manage brand knowledge, content generation, and rules engine.
"""
import httpx
from typing import Any, Optional, List, Dict

from app.config import settings

class SensoGEOClient:
    """GEO Platform API (apiv2.senso.ai)"""
    
    def __init__(self):
        self.api_key = settings.SENSO_GEO_API_KEY
        self.base_url = "https://apiv2.senso.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def evaluate(self, query: str, brand: str, network: str) -> dict:
        """Evaluate content against brand guidelines using Senso GEO."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/evaluate",
                headers=self.headers,
                json={
                    "query": query,
                    "brand": brand,
                    "network": network
                }
            )
            response.raise_for_status()
            return response.json()

    async def remediate(self, context: str, optimize_for: str, targets: list) -> dict:
        """Generate correction strategy using Senso GEO."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/remediate",
                headers=self.headers,
                json={
                    "context": context,
                    "optimize_for": optimize_for,
                    "targets": targets
                }
            )
            response.raise_for_status()
            return response.json()


class SensoSDKClient:
    """Context OS SDK API (sdk.senso.ai)"""
    
    def __init__(self):
        self.api_key = settings.SENSO_SDK_API_KEY
        self.base_url = "https://sdk.senso.ai/api/v1"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def ingest_content(self, content: str, title: str) -> dict:
        """Ingest brand ground truth into Senso SDK."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/knowledge",
                headers=self.headers,
                json={
                    "content": content,
                    "title": title
                }
            )
            response.raise_for_status()
            return response.json()

    async def search(self, query: str) -> dict:
        """Search brand knowledge base."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={
                    "query": query
                }
            )
            response.raise_for_status()
            return response.json()

    async def generate(self, prompt: str, template_id: Optional[str] = None) -> dict:
        """Generate brand-compliant content using Context OS SDK."""
        payload: Dict[str, Any] = {"prompt": prompt}
        if template_id:
            payload["template_id"] = template_id
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def create_rule(self, name: str, conditions: dict) -> dict:
        """Set up automated misrepresentation detection rule."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rules",
                headers=self.headers,
                json={
                    "name": name,
                    "conditions": conditions
                }
            )
            response.raise_for_status()
            return response.json()

    async def create_trigger(self, rule_id: str, webhook_url: str) -> dict:
        """Create a trigger linking rule to webhook."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/triggers",
                headers=self.headers,
                json={
                    "rule_id": rule_id,
                    "webhook_url": webhook_url
                }
            )
            response.raise_for_status()
            return response.json()
