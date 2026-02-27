# Phase 9: Render Deployment & Cron Jobs

**Owner**: Kruthi
**Effort**: 1-2 hours
**Priority**: P0 (Must be live for demo)
**Depends on**: Phase 8 (Nihal's Orchestration)
**Blocks**: Phase 10 (Demo Preparation)

---

## Overview

Deploy BrandGuard to Render so it's live for the hackathon demo. This includes the FastAPI backend, React frontend (static site), and a cron job for periodic monitoring.

---

## Reference

Read the research doc: `docs/research/neo4j-modulate-render-yutori-research.md` (Render section)

### Render Free Tier
- Web Services: 750 hours/month free
- Static Sites: free
- Cron Jobs: $1/month minimum
- PostgreSQL: free tier available
- Key Value (Redis): free tier available

---

## Tasks

### 9.1 Update `render.yaml`

- [ ] Finalize the Render blueprint (already scaffolded):
  ```yaml
  services:
    # Backend API
    - type: web
      name: brandguard-api
      runtime: python
      repo: https://github.com/{your-repo}
      rootDir: backend
      buildCommand: pip install -r requirements.txt
      startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
      envVars:
        - key: SENSO_GEO_API_KEY
          sync: false
        - key: SENSO_SDK_API_KEY
          sync: false
        - key: TAVILY_API_KEY
          sync: false
        - key: NEO4J_URI
          sync: false
        - key: NEO4J_USERNAME
          sync: false
        - key: NEO4J_PASSWORD
          sync: false
        - key: YUTORI_API_KEY
          sync: false
        - key: WEBHOOK_BASE_URL
          sync: false
      healthCheckPath: /health

    # Frontend Static Site
    - type: web
      name: brandguard-dashboard
      runtime: static
      rootDir: frontend
      buildCommand: npm install && npm run build
      staticPublishPath: dist
      headers:
        - path: /*
          name: Cache-Control
          value: public, max-age=0, must-revalidate
      routes:
        - type: rewrite
          source: /*
          destination: /index.html

    # Cron Job (periodic monitoring)
    - type: cron
      name: brandguard-monitor
      runtime: python
      rootDir: backend
      buildCommand: pip install -r requirements.txt
      schedule: "0 */6 * * *"  # Every 6 hours
      startCommand: python scripts/cron_monitor.py
  ```

### 9.2 Create Cron Monitor Script

- [ ] Create `backend/scripts/cron_monitor.py`:
  ```python
  """
  Runs every 6 hours via Render cron job.
  1. Gets all active scouts
  2. Polls for new updates
  3. Processes any new mentions through the pipeline
  """
  import asyncio
  from app.services.yutori.client import YutoriClient
  from app.services.agent.orchestrator import BrandGuardPipeline
  from app.config.settings import settings

  async def main():
      # Initialize clients
      # Poll all active scouts
      # Process new mentions
      pass

  if __name__ == "__main__":
      asyncio.run(main())
  ```

### 9.3 Environment Variables on Render

- [ ] Go to Render Dashboard → Environment Variable Groups
- [ ] Create group "brandguard-env" with all keys from `.env.example`
- [ ] Link group to all 3 services

### 9.4 Frontend Environment

- [ ] Set `VITE_API_BASE_URL` to the deployed backend URL:
  ```
  VITE_API_BASE_URL=https://brandguard-api.onrender.com
  ```
- [ ] Set `VITE_USE_MOCKS=false` for production

### 9.5 Deploy

- [ ] Push code to GitHub
- [ ] Connect repo to Render (or use `render.yaml` Blueprint)
- [ ] Verify builds succeed for all 3 services
- [ ] Test health check: `curl https://brandguard-api.onrender.com/health`
- [ ] Test frontend loads: `https://brandguard-dashboard.onrender.com`
- [ ] Verify CORS allows the frontend domain
- [ ] Test webhook URLs are publicly accessible

### 9.6 Webhook URLs

- [ ] Update webhook URLs in Senso and Yutori configs:
  ```
  Yutori webhook: https://brandguard-api.onrender.com/api/webhooks/yutori
  Senso webhook:  https://brandguard-api.onrender.com/api/webhooks/senso
  ```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `render.yaml` | Finalize with all services |
| `backend/scripts/cron_monitor.py` | Create cron job script |
| `frontend/.env.production` | Set production API URL |

---

## Verification Checklist

- [ ] Backend deploys and `/health` returns 200
- [ ] Frontend deploys and loads the dashboard
- [ ] CORS works between frontend and backend
- [ ] All API endpoints accessible from deployed frontend
- [ ] Cron job appears in Render dashboard
- [ ] Webhook URLs are publicly reachable
- [ ] Neo4j AuraDB accessible from Render
