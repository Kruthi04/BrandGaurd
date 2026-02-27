# Phase 10: Demo Preparation & Polish

**Owner**: Kruthi (with help from Nihal + Sachin)
**Effort**: 2-3 hours
**Priority**: P0 (This is where you win or lose)
**Depends on**: Phase 9 (Deployment)
**Blocks**: Nothing — this is the final phase

---

## Overview

Prepare the 3-minute demo that will win the hackathon. Pre-seed data, script the flow, polish the UI, and record a backup video. Every second of the demo matters.

---

## Demo Flow (3 Minutes)

| Time | Action | What Judges See | Tools Shown |
|------|--------|----------------|-------------|
| 0:00-0:40 | Open dashboard | Brand health score (73/100), platform breakdown, 3 active alerts | Neo4j, React |
| 0:40-1:20 | Click Perplexity alert | "Acme Corp founded in 1990" — Senso accuracy: 34%, missing citations | **Senso Evaluate** |
| 1:20-2:00 | Click "Investigate" | Tavily finds source: outdated-blog.com. Switch to graph — see propagation path | **Tavily**, **Neo4j viz** |
| 2:00-2:40 | Click "Auto-Correct" | Senso generates GEO-optimized correction + FAQ | **Senso Remediate + Generate** |
| 2:40-3:00 | Trigger live scan | Yutori Browsing queries Claude. Webhook arrives in real-time. Close on graph. | **Yutori**, webhook live |

---

## Tasks

### 10.1 Master Seed Script

- [ ] Coordinate with Nihal and Sachin to create `scripts/seed_demo.py`:
  ```python
  """
  Run: python scripts/seed_demo.py
  Seeds ALL data stores for the demo in < 2 minutes
  """
  # 1. Neo4j: Acme Corp brand + 50+ mentions + 10 sources + propagation chains
  #    (Uses Sachin's Neo4j client)
  # 2. Senso SDK: Ground truth content, prompts, templates, rules
  #    (Uses Nihal's Senso client)
  # 3. Pre-compute: 5 "inaccurate" mentions with Senso evaluations cached
  # 4. Pre-generate: 2 corrections ready to show
  ```

### 10.2 Pre-Create Yutori Scouts

- [ ] Run 24-48 hours before demo:
  ```python
  # scripts/setup_demo_scouts.py
  # Create Yutori scouts for "Acme Corp" across all platforms
  # Let them accumulate real data before demo day
  ```

### 10.3 Demo-Specific UI Tweaks

- [ ] **Loading speed**: Pre-fetch dashboard data on app load
- [ ] **Loading skeletons**: Smooth skeleton screens while data loads (no blank screens)
- [ ] **Error recovery**: Toast with retry on any API failure
- [ ] **Smooth transitions**: Framer Motion fade-in for page changes
- [ ] **Projector-friendly**: Test at 1920x1080, ensure text is large enough
- [ ] **Pre-warm API**: Call health endpoints on app start to wake up Render free tier

### 10.4 Presentation Materials

- [ ] **1 Overview Slide** (per judging criteria):
  - Project name: BrandGuard
  - One-line description
  - Architecture diagram (from design doc)
  - Sponsor tools used (with logos): Senso, Tavily, Neo4j, Yutori, Render, (AssemblyAI)
  - Team names

- [ ] **Devpost Submission**:
  - Title: "BrandGuard — Autonomous AI Reputation Agent"
  - Description: 2-3 paragraphs explaining the problem and solution
  - Screenshots: Dashboard, graph, alert detail, correction
  - Tech stack section
  - Sponsor tool integration details (CRITICAL — judges look at this)
  - Link to live deployment
  - Link to GitHub repo

### 10.5 Backup Demo Video

- [ ] Record the full 3-minute demo flow as a video
  - Use screen recording (QuickTime / OBS)
  - Include narration explaining each step
  - This is insurance in case of live demo issues

### 10.6 Rehearse

- [ ] Run through the demo flow 3 times
- [ ] Time each section — must fit in 3 minutes
- [ ] Test on the actual demo machine / projector
- [ ] Have a plan B for each step (what if Yutori is slow? Show cached result)

---

## Coordination with Team

| Task | Who | When |
|------|-----|------|
| Neo4j seed data | Sachin | Provide `seed_neo4j.py` |
| Senso seed data | Nihal | Provide `seed_senso.py` |
| Create demo scouts | Sachin | 48 hours before demo |
| Master seed script | Kruthi | Combines both seeds |
| Demo rehearsal | Everyone | Night before demo |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `scripts/seed_demo.py` | Create — master seed combining all data |
| `scripts/setup_demo_scouts.py` | Create — pre-create Yutori scouts |
| Various frontend files | Polish: loading states, animations, responsive |

---

## Verification Checklist

- [ ] `python scripts/seed_demo.py` runs in < 2 minutes
- [ ] Dashboard loads with pre-seeded data in < 3 seconds
- [ ] Demo flow completes in under 3 minutes
- [ ] Every sponsor tool is visible during the demo
- [ ] "Investigate" shows Tavily results within 5 seconds
- [ ] "Auto-Correct" shows Senso correction within 5 seconds
- [ ] Graph visualization renders with color-coded nodes
- [ ] Yutori live scan works (or has cached fallback)
- [ ] Overview slide ready
- [ ] Devpost submission drafted
- [ ] Backup video recorded
- [ ] Tested on projector resolution
