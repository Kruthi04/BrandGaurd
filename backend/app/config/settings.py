"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for all BrandGuard services."""

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Senso API - content evaluation, rules engine, generation
    SENSO_GEO_API_KEY: str = os.getenv("SENSO_GEO_API_KEY", "")
    SENSO_SDK_API_KEY: str = os.getenv("SENSO_SDK_API_KEY", "")
    SENSO_API_BASE_URL: str = os.getenv("SENSO_API_BASE_URL", "https://api.senso.ai")

    # Tavily API - web search, crawl, research
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Neo4j - graph database for entity relationships
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")

    # Yutori - scouting and browsing agent
    YUTORI_API_KEY: str = os.getenv("YUTORI_API_KEY", "")
    YUTORI_API_BASE_URL: str = os.getenv("YUTORI_API_BASE_URL", "https://api.yutori.com")

    # Modulate - voice/audio transcription and analysis (Velma-2)
    MODULATE_API_KEY: str = os.getenv("MODULATE_API_KEY", "")
    MODULATE_API_BASE_URL: str = os.getenv("MODULATE_API_BASE_URL", "https://modulate-developer-apis.com")

    # OpenAI - for agent orchestration LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Render - deployment (configured via render.yaml, not runtime)

    def validate(self) -> list[str]:
        """Return a list of missing required configuration keys."""
        missing = []
        if not self.SENSO_GEO_API_KEY:
            missing.append("SENSO_GEO_API_KEY")
        if not self.SENSO_SDK_API_KEY:
            missing.append("SENSO_SDK_API_KEY")
        if not self.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if not self.NEO4J_PASSWORD:
            missing.append("NEO4J_PASSWORD")
        if not self.YUTORI_API_KEY:
            missing.append("YUTORI_API_KEY")
        if not self.MODULATE_API_KEY:
            missing.append("MODULATE_API_KEY")
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing


settings = Settings()
