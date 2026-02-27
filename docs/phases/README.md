# BrandGuard — Phase Assignments

## Team Split

| Person | Phases | Focus Area | Estimated Effort |
|--------|--------|------------|-----------------|
| **Nihal** | 1, 2, 8 | Backend Core + Senso (Prize Target) + Orchestration | 8-11 hours |
| **Sachin** | 3, 4, 5 | Data Pipeline: Tavily + Neo4j + Yutori | 8-11 hours |
| **Kruthi** | 6, 7, 9, 10 | Frontend + Deploy + Demo | 8-13 hours |

## Critical Path

```
Phase 1 (Nihal - Setup)          ← EVERYONE BLOCKS ON THIS
  |
  +── Phase 2 (Nihal - Senso) ──────────┐
  |                                      |
  +── Phase 3 (Sachin - Tavily) ────────┤
  |                                      ├── Phase 7 (Kruthi - Dashboard)
  +── Phase 4 (Sachin - Neo4j) ─────────┤        |
  |                                      ├── Phase 8 (Nihal - Orchestration)
  +── Phase 5 (Sachin - Yutori) ────────┘        |
  |                                          Phase 9 (Kruthi - Deploy)
  +── Phase 6 (Kruthi - Audio) OPTIONAL          |
                                             Phase 10 (Kruthi - Demo)
```

## Parallel Work Strategy

### Day 1: Foundation (All 3 work in parallel after Phase 1)
1. **Nihal** completes Phase 1 (setup) first — everyone clones and starts from there
2. Then all 3 work simultaneously:
   - Nihal → Phase 2 (Senso)
   - Sachin → Phase 3 (Tavily) + Phase 4 (Neo4j)
   - Kruthi → Phase 7 (Dashboard skeleton with mock data)

### Day 2: Integration + Polish
3. Continue parallel work:
   - Nihal → Phase 8 (Orchestration — connects everyone's services)
   - Sachin → Phase 5 (Yutori)
   - Kruthi → Connect dashboard to real APIs, Phase 6 (Audio if time)
4. Final push:
   - Kruthi → Phase 9 (Deploy) + Phase 10 (Demo prep)
   - Everyone → Bug fixes, polish

## Integration Points

See `integration/integration-contracts.md` for the shared API contracts, data models, and interface boundaries.

### Who Exposes What

| Person | Backend Endpoints | Files |
|--------|------------------|-------|
| **Nihal** | `/api/evaluate`, `/api/remediate`, `/api/content/*`, `/api/rules/*`, `/api/webhooks/senso`, `/api/pipeline/*` | `backend/app/services/senso/`, `backend/app/services/agent/`, `backend/app/api/analysis.py` |
| **Sachin** | `/api/search/*`, `/api/graph/*`, `/api/monitoring/*`, `/api/investigate/*`, `/api/webhooks/yutori` | `backend/app/services/tavily/`, `backend/app/services/neo4j/`, `backend/app/services/yutori/`, `backend/app/api/monitoring.py`, `backend/app/api/graph.py` |
| **Kruthi** | Frontend pages, `render.yaml`, deploy config | `frontend/src/**`, `render.yaml`, seed scripts |

### Who Consumes What

| Person | Depends On |
|--------|-----------|
| **Nihal (Phase 8)** | Sachin's Neo4j service (to store pipeline results), Sachin's Tavily service (for investigation), Sachin's Yutori webhooks |
| **Sachin (Phase 5)** | Sachin's own Neo4j service (Phase 4 must be done first) |
| **Kruthi (Phase 7)** | ALL backend endpoints from Nihal + Sachin |

## Git Workflow

1. Everyone works on feature branches: `nihal/phase-X`, `sachin/phase-X`, `kruthi/phase-X`
2. Merge to `main` after each phase is verified
3. Avoid editing the same files — the folder structure is designed to minimize conflicts
4. Shared files (models, config) — coordinate before editing
