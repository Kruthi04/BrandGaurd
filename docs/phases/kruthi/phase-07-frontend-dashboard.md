# Phase 7: Frontend Dashboard

**Owner**: Kruthi
**Effort**: 4-6 hours
**Priority**: P0 (Judges see the UI — this is what wins or loses)
**Depends on**: Phase 2 (Nihal's Senso), Phase 3 (Sachin's Tavily), Phase 4 (Sachin's Neo4j), Phase 5 (Sachin's Yutori)
**Blocks**: Phase 10 (Demo Preparation)

---

## Overview

Build the complete monitoring dashboard that ties all backend services together in a polished UI. This is what judges see during the 3-minute demo. The scaffold already has page skeletons — your job is to implement them with real data, interactions, and polish.

**Strategy**: Start with mock data on Day 1 while Nihal and Sachin build the APIs, then swap to real API calls on Day 2.

---

## Tech Stack (already scaffolded)

| Tool | Purpose |
|------|---------|
| React 18 + TypeScript | UI framework |
| Vite 5 (SWC) | Build tool |
| Tailwind CSS | Styling |
| shadcn/ui | Component library (Button, Card, Badge, Dialog, Table, Tabs) |
| TanStack React Query 5 | Server state, polling, caching |
| react-force-graph-2d | Neo4j graph visualization |
| Recharts | Charts (accuracy trends, platform breakdown) |
| React Router DOM 6 | Client-side routing |
| Framer Motion | Animations (optional but judges love it) |

---

## Tasks

### 7.1 Dashboard Home Page (`/`)

- [ ] **Brand Health Score Card**: Large circular score (0-100) with color coding
  - Green (80-100), Yellow (60-79), Red (0-59)
  - Calls: `GET /api/graph/brand/{id}/health` (Sachin)

- [ ] **Platform Breakdown**: 4 horizontal bars showing accuracy per AI platform
  - ChatGPT, Claude, Perplexity, Gemini
  - Color-coded by accuracy
  - Calls: Same health endpoint

- [ ] **Accuracy Trend Chart**: Recharts line chart showing 7-day accuracy trend
  - One line per platform
  - Uses mock data initially, then real data from mentions over time

- [ ] **Recent Alerts List**: Last 5 alerts with severity badges
  - Click to navigate to alert detail
  - Severity badges: Critical (red), High (orange), Medium (yellow), Low (gray)

- [ ] **Active Scouts Counter**: Number of active Yutori scouts
  - Calls: `GET /api/monitoring/status` (Sachin)

### 7.2 Alerts Page (`/alerts`)

- [ ] **Alert Cards**: List of all threats/alerts
  - Severity badge, platform icon, claim text, detected time
  - Status: Open, Investigating, Corrected, Dismissed

- [ ] **Alert Detail Expand**: Click to see full details
  - Full claim text + context
  - Senso evaluation results (accuracy score, citations, missing info)
  - Calls: `POST /api/evaluate` (Nihal) if not cached

- [ ] **"Investigate" Button**: Triggers source tracing
  - Calls: `POST /api/pipeline/investigate` (Nihal's Phase 8)
  - Shows Tavily search results (source URLs, content snippets)
  - Shows loading state with step progress

- [ ] **"Auto-Correct" Button**: Triggers remediation
  - Calls: `POST /api/pipeline/remediate` (Nihal's Phase 8)
  - Shows before/after comparison
  - Shows generated correction content
  - "Publish" button to deploy correction

### 7.3 Graph Explorer Page (`/graph`)

- [ ] **react-force-graph-2d**: Interactive knowledge graph
  - Color-coded nodes (see Phase 4 color scheme)
  - Brand (blue), Platform (green), Mention (red/gray), Source (amber), Correction (purple)
  - Calls: `GET /api/graph/brand/{id}/network` (Sachin)

- [ ] **Click-to-Inspect**: Click a node to see details in a side panel
  - Mention: show claim, accuracy, platform
  - Source: show URL, influence score, platforms affected
  - Correction: show content, status

- [ ] **Filters**: Filter by platform, accuracy threshold, time range
  - Re-fetches graph data with filters

### 7.4 Monitoring Page (`/monitoring`)

- [ ] **Scout List**: Active scouts with status indicators
  - Calls: `GET /api/monitoring/status` (Sachin)
  - Green dot = active, Yellow = pending, Red = error

- [ ] **"Start Monitoring" Button**: Create new scout
  - Calls: `POST /api/monitoring/start` (Sachin)
  - Input: brand name

- [ ] **"Query Platform" Button**: One-off AI platform query
  - Calls: `POST /api/investigate/browse` (Sachin)
  - Select platform dropdown + query input

### 7.5 Corrections Page (`/corrections`)

- [ ] **Correction History Table**: List of generated corrections
  - Type (blog, FAQ, social), status (draft, published), date
  - Calls: `GET /api/graph/brand/{id}/corrections` or custom endpoint

- [ ] **Preview Panel**: Click to see full correction content
  - Before/after comparison
  - "Publish" action button

### 7.6 Brand Onboarding Flow

- [ ] **Add Brand Form** (Settings or modal):
  1. Input: brand name, industry, description
  2. Input: ground truth facts (list of key facts)
  3. On submit:
     - `POST /api/content/ingest` (Nihal) — push ground truth to Senso
     - `POST /api/graph/mentions` (Sachin) — create brand node
     - `POST /api/rules/setup` (Nihal) — set up Senso rules
     - `POST /api/monitoring/start` (Sachin) — start Yutori scout

### 7.7 Polish & UX

- [ ] Loading skeletons for all async data
- [ ] Error boundaries with retry buttons
- [ ] Empty states with helpful CTAs
- [ ] Toast notifications (sonner) for actions
- [ ] Responsive layout (test on projector resolution ~1920x1080)
- [ ] Dark mode support (optional, but add if quick with Tailwind)
- [ ] Framer Motion: fade-in for cards, slide for panels (optional)

---

## API Endpoints You Call

### From Nihal (Senso + Pipeline)
```
POST /api/evaluate          → Alert detail: accuracy results
POST /api/remediate         → "Auto-Correct" button
POST /api/content/ingest    → Brand onboarding
POST /api/content/generate  → View generated corrections
POST /api/rules/setup       → Brand onboarding
POST /api/pipeline/run      → "Run Pipeline" button
POST /api/pipeline/investigate → "Investigate" button
POST /api/pipeline/remediate   → "Auto-Correct" button
GET  /api/pipeline/status/{id} → Show pipeline progress
```

### From Sachin (Tavily + Neo4j + Yutori)
```
POST /api/search/web            → Investigation results
GET  /api/graph/brand/{id}/health   → Dashboard health cards
GET  /api/graph/brand/{id}/sources  → Top misinformation sources
GET  /api/graph/brand/{id}/network  → Graph visualization data
POST /api/monitoring/start      → Start monitoring button
POST /api/monitoring/stop       → Stop monitoring button
GET  /api/monitoring/status     → Scout status list
POST /api/investigate/browse    → Query platform button
POST /api/investigate/research  → Deep investigate button
```

---

## Frontend Service Files to Implement

| File | Endpoints |
|------|-----------|
| `frontend/src/services/analysisApi.ts` | Nihal's Senso + pipeline endpoints |
| `frontend/src/services/monitoringApi.ts` | Sachin's Yutori monitoring endpoints |
| `frontend/src/services/graphApi.ts` | Sachin's Neo4j graph endpoints |
| `frontend/src/services/agentApi.ts` | Nihal's pipeline endpoints |

---

## Mock Data Strategy (Start on Day 1)

While waiting for Nihal and Sachin's APIs, use mock data:

```typescript
// frontend/src/lib/mockData.ts
export const mockBrandHealth = {
  overall_accuracy: 73.2,
  total_mentions: 47,
  by_platform: {
    chatgpt: { accuracy: 68.5, mentions: 15 },
    claude: { accuracy: 82.1, mentions: 12 },
    perplexity: { accuracy: 71.0, mentions: 10 },
    gemini: { accuracy: 65.0, mentions: 10 }
  }
};

export const mockAlerts = [
  { id: "1", severity: "critical", platform: "perplexity", claim: "Acme Corp was founded in 1990", accuracy_score: 34 },
  // ... more mock alerts
];

export const mockGraphData = {
  nodes: [...],
  edges: [...]
};
```

Use an env flag to toggle: `VITE_USE_MOCKS=true`

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `frontend/src/pages/Dashboard.tsx` | Implement with health cards, charts, alerts |
| `frontend/src/pages/Threats.tsx` | Implement alerts page with investigate/correct |
| `frontend/src/pages/GraphExplorer.tsx` | Implement graph visualization |
| `frontend/src/pages/Monitoring.tsx` | Implement scout management |
| `frontend/src/pages/Settings.tsx` | Implement brand onboarding |
| `frontend/src/components/dashboard/*` | Implement dashboard widgets |
| `frontend/src/components/graph/*` | Implement graph visualization |
| `frontend/src/services/*.ts` | Implement API clients |
| `frontend/src/lib/mockData.ts` | Create mock data for development |

---

## Verification Checklist

- [ ] Dashboard shows brand health score, platform breakdown, trend chart
- [ ] Alerts page lists threats with severity badges
- [ ] Alert detail shows evaluation results, investigate/correct buttons
- [ ] Graph page renders interactive force-directed graph
- [ ] Click on graph node shows detail panel
- [ ] Monitoring page shows active scouts
- [ ] "Start Monitoring" creates a new scout
- [ ] Corrections page shows generated corrections
- [ ] Brand onboarding flow works end-to-end
- [ ] All pages have loading states and error handling
- [ ] Layout works at projector resolution (1920x1080)
- [ ] Navigation between all pages works smoothly
