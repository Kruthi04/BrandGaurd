# Phase 1: Project Setup & Environment Config

**Owner**: Nihal
**Effort**: 2-3 hours
**Priority**: P0 (Blocks everyone)
**Depends on**: Nothing
**Blocks**: ALL other phases — Sachin and Kruthi cannot start until this is merged to `main`

---

## Overview

Set up the complete project foundation: backend (FastAPI), frontend (React + Vite), environment config, and initial Render deployment. This phase produces the skeleton that Sachin and Kruthi will build on.

---

## Tasks

- [ ] **Verify existing scaffold** — The scaffolder agent already created the folder structure. Verify it works:
  ```bash
  cd backend && pip install -r requirements.txt && uvicorn main:app --reload
  cd frontend && npm install && npm run dev
  ```
- [ ] **Fix any scaffold issues** — Ensure both backend and frontend boot without errors
- [ ] **Set up `.env` file** — Copy `.env.example` to `.env`, fill in all API keys:
  - `SENSO_GEO_API_KEY` and `SENSO_SDK_API_KEY` (get from andy@senso.ai / hackathon portal)
  - `TAVILY_API_KEY` (get from tavily.com)
  - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` (create AuraDB Free instance)
  - `YUTORI_API_KEY` (get from platform.yutori.com)
- [ ] **Set up Neo4j AuraDB Free**:
  - Go to https://neo4j.com/cloud/aura-free/
  - Create free instance (200k nodes, 400k rels)
  - Save connection URI and credentials to `.env`
- [ ] **Configure CORS** in `backend/main.py`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173"],  # Vite dev server
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- [ ] **Add health check endpoint**:
  ```python
  @app.get("/health")
  async def health():
      return {"status": "ok", "service": "brandguard-api"}
  ```
- [ ] **Verify all API keys work** — Create a simple test script:
  ```python
  # scripts/verify_keys.py
  # Hit each API with a simple test request and report status
  ```
- [ ] **Initial Render deployment** (optional, can defer to Phase 9):
  - Push to GitHub
  - Connect repo to Render
  - Verify build succeeds
- [ ] **Push to `main`** and notify Sachin + Kruthi to pull

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `backend/.env` | Create from `.env.example` |
| `backend/main.py` | Verify CORS, health endpoint |
| `backend/app/config/settings.py` | Verify env var loading |
| `scripts/verify_keys.py` | Create — test all API connections |
| `frontend/.env` | Create with `VITE_API_BASE_URL=http://localhost:8000` |

---

## What You Expose to Teammates

After this phase, teammates get:
- A running backend at `http://localhost:8000` with `/health` and `/docs`
- A running frontend at `http://localhost:5173`
- All API keys configured and verified
- Neo4j AuraDB instance ready for Sachin
- The `main` branch as their starting point

---

## Verification Checklist

- [ ] `cd backend && uvicorn main:app --reload` starts without errors
- [ ] `curl http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `http://localhost:8000/docs` shows FastAPI auto-docs
- [ ] `cd frontend && npm run dev` starts without errors
- [ ] `http://localhost:5173` shows the app skeleton
- [ ] `scripts/verify_keys.py` reports all API keys valid
- [ ] Neo4j AuraDB connection verified
- [ ] Pushed to `main`, Sachin and Kruthi can pull and run
