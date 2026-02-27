# Yutori Architecture Patterns — A Comprehensive Integration Guide

A pattern catalog for building production applications with the Yutori AI agent platform. Every pattern is grounded in real code from three hackathon-winning projects (LawSync, Access AI, Signal Trade Bot) and one reference implementation (ThreatGraph).

---

## Table of Contents

1. [Yutori Platform Overview](#1-yutori-platform-overview)
2. [Authentication & Client Patterns](#2-authentication--client-patterns)
3. [Pattern: Continuous Intelligence via Scouting](#3-pattern-continuous-intelligence-via-scouting)
4. [Pattern: Autonomous Browsing](#4-pattern-autonomous-browsing)
5. [Pattern: Deep Research](#5-pattern-deep-research)
6. [Pattern: n1 Pixel-to-Action](#6-pattern-n1-pixel-to-action)
7. [Pattern: Structured Output Schemas](#7-pattern-structured-output-schemas)
8. [Pattern: AI-on-AI Layering](#8-pattern-ai-on-ai-layering)
9. [Pattern: Webhook-Driven Pipelines](#9-pattern-webhook-driven-pipelines)
10. [Pattern: Resilient Async Operations](#10-pattern-resilient-async-operations)
11. [Comparative Matrix](#11-comparative-matrix)
12. [Lessons from Hackathon Winners](#12-lessons-from-hackathon-winners)
13. [Quick Reference](#13-quick-reference)

---

## 1. Yutori Platform Overview

Yutori is an AI company founded by Dhruv Batra, Abhishek Das, and Devi Parikh, backed by a $15M seed round. The platform provides always-on AI agents that monitor, browse, and research the web autonomously.

### The Four APIs

| API | Purpose | Pricing | Key Use Case |
|-----|---------|---------|-------------|
| **Scouting** | Persistent monitoring agents that run on a schedule | $0.35/scout-run | Continuous intelligence — track topics, competitors, threats over time |
| **Browsing** | On-demand browser automation | $0.015/step (n1), $0.10/step (Claude CU) | Form filling, data extraction, website interaction |
| **Research** | Deep one-time investigation using 100+ MCP tools | $0.35/task | Comprehensive research reports with citations |
| **n1 Model** | Vision-based LLM for pixel-to-action browser control | $0.75/1M input, $3/1M output tokens | Low-level browser automation via screenshot analysis |

### The n1 Model

Yutori's proprietary `n1` model is built on top of Qwen3-VL and trained with reinforcement learning on live websites. It benchmarks at 78.7% on Online-Mind2Web, 83.4% on Navi-Bench, and is 3.3x faster per-step than Claude 4.5 Sonnet. The backend orchestration uses DBOS + PostgreSQL, deploying 76 agents per scout run and consuming approximately 1M tokens per run.

### SDK & Tooling

- **Python SDK**: `pip install yutori` — provides `YutoriClient` and `AsyncYutoriClient` with namespaces (`client.chat`, `client.browsing`, `client.research`, `client.scouts`)
- **MCP Server**: `uvx yutori-mcp` — integrates directly with Claude Desktop and other MCP-compatible clients
- **CLI**: `yutori auth login`, `scouts list/get/create/delete`, `browse run/get`, `research run/get`

---

## 2. Authentication & Client Patterns

Every Yutori API call uses the same authentication mechanism: an `X-API-Key` header. API keys are generated at `platform.yutori.com/settings`.

> **Header capitalization**: HTTP headers are case-insensitive per RFC 7230, so `X-API-Key`, `X-API-KEY`, and `x-api-key` all work. The reference projects inconsistently use different capitalizations (Access AI browser routes use `X-API-KEY`, LawSync and Signal Trade Bot use `X-API-Key`). The official docs use lowercase `x-api-key`. Pick one and be consistent within your project.

### Pattern A: Inline Fetch (Simplest)

Used by Access AI for single-endpoint routes where a wrapper class adds no value.

```typescript
// Access AI — app/api/create-scout/route.ts
const response = await fetch('https://api.yutori.com/v1/scouting/tasks', {
  method: 'POST',
  headers: {
    'X-API-Key': process.env.YUTORI_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: query,
    task_spec: {
      output_schema: {
        type: "json",
        json_schema: schema
      }
    }
  })
});
```

**When to use**: Prototypes, single-route integrations, hackathons where speed matters more than abstraction.

### Pattern B: Typed Client Wrapper (Production TypeScript)

Used by ThreatGraph. A centralized client module with a generic `request<T>()` function, typed return values, abort-controller timeouts, and structured error handling.

```typescript
// ThreatGraph — src/lib/yutori.ts
const BASE_URL = "https://api.yutori.com";
const REQUEST_TIMEOUT_MS = 30_000;

function getApiKey(): string {
  const key = process.env.YUTORI_API_KEY;
  if (!key) throw new Error("YUTORI_API_KEY is not set");
  return key;
}

function headers() {
  return {
    "Content-Type": "application/json",
    "X-API-Key": getApiKey(),
  };
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: headers(),
      signal: controller.signal,
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Yutori ${method} ${path} failed (${res.status}): ${text}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}
```

Each API function then becomes a thin typed wrapper:

```typescript
export async function createScout(
  query: string,
  displayName?: string,
  outputSchema?: Record<string, unknown>,
  webhookUrl?: string,
  options?: { outputInterval?: number; userTimezone?: string; skipEmail?: boolean }
) {
  return request<{ id: string; status: string }>("POST", "/v1/scouting/tasks", {
    query,
    ...(displayName ? { display_name: displayName } : {}),
    ...(outputSchema ? { task_spec: { output_schema: { json_schema: outputSchema } } } : {}),
    ...(webhookUrl ? { webhook_url: webhookUrl } : {}),
    ...(options?.outputInterval != null ? { output_interval: options.outputInterval } : {}),
    ...(options?.userTimezone ? { user_timezone: options.userTimezone } : {}),
    ...(options?.skipEmail != null ? { skip_email: options.skipEmail } : {}),
  });
}
```

**Key design decisions**:
- Generic `request<T>` centralizes auth, error handling, and timeouts
- Optional parameters use conditional spread (`...(x ? {y} : {})`) to avoid sending `undefined`
- AbortController prevents hung requests (Yutori tasks can take minutes)
- Return types are explicitly typed for downstream consumers

**When to use**: Any project with 3+ Yutori API calls, or when multiple team members touch the integration.

### Pattern C: Class-Based SDK Wrapper (Python)

Used by LawSync. A class wraps all API calls with consistent headers and error handling, then decorates methods with `@tool` for agentic frameworks.

```python
# LawSync — backend/scout/tools/yutori_tools.py
class YutoriAPITools:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    @tool
    def create_scout(self, query: str, output_interval: int = 86400,
                     user_timezone: str = "America/Los_Angeles",
                     skip_email: bool = True) -> Dict[str, Any]:
        """Create a new scout task to monitor information."""
        payload = {
            "query": query,
            "output_interval": output_interval,
            "user_timezone": user_timezone,
            "skip_email": skip_email
        }
        response = requests.post(
            f"{self.base_url}/v1/scouting/tasks",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "content": [{"json": {
                "scout_id": data.get("id"),
                "query": data.get("query"),
                "display_name": data.get("display_name"),
                "next_run": data.get("next_run_timestamp"),
                "created_at": data.get("created_at")
            }}]
        }
```

**Key design decision**: Each method returns a standardized `{status, content}` envelope so the Strands agent framework can interpret results uniformly — the AI decides which tool to call based on the docstring.

**When to use**: Python backends, especially when integrating with agentic frameworks (Strands, LangChain, CrewAI) that discover tools via decorators.

### Pattern D: Official Python SDK

The official SDK provides the cleanest interface:

```python
from yutori import YutoriClient

client = YutoriClient(api_key="your-key")

# Scouting
scout = client.scouts.create(query="Monitor AI regulations")
updates = client.scouts.get_updates(scout.id)

# Browsing
task = client.browsing.create(task="Extract pricing", start_url="https://example.com")
result = client.browsing.get(task.id)

# Research
research = client.research.create(query="Analysis of quantum computing market")
result = client.research.get(research.id)
```

The async variant `AsyncYutoriClient` supports the same interface with `await`. Pydantic models can be passed directly to `output_schema` for type-safe structured output.

**When to use**: Greenfield Python projects, or when you want the least code and most guardrails.

### Pattern E: Config Singleton (Python)

Used by LawSync to centralize configuration with validation at startup:

```python
# LawSync — backend/scout/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    YUTORI_API_KEY = os.getenv("YUTORI_API_KEY", "")
    YUTORI_API_BASE_URL = os.getenv("YUTORI_API_BASE_URL", "https://api.yutori.com")

    @classmethod
    def validate(cls):
        if not cls.YUTORI_API_KEY:
            raise ValueError("YUTORI_API_KEY is required")

config = Config()
```

The server calls `config.validate()` at startup, preventing silent failures from missing credentials.

---

## 3. Pattern: Continuous Intelligence via Scouting

The Scouting API creates persistent AI agents that monitor the web on a schedule, returning structured intelligence reports with citations. This is Yutori's flagship product.

### Full Lifecycle

```
Create Scout → (wait for interval) → Poll Updates → Process Intelligence
     ↑                                                       |
     |                    ┌──────────────────────────────────┘
     |                    ↓
     ├── Edit (PUT — change query or full replacement)
     ├── Update (PATCH — change interval, timezone)
     ├── Pause / Resume (stop/restart scheduling)
     ├── Restart (re-initialize state, keep query)
     ├── Email Settings (manage subscribers)
     ├── Mark Done / Complete (archive)
     └── Delete (permanent removal)
```

### Scouting Endpoints Used by Reference Projects

The full API also includes `POST .../pause`, `POST .../resume`, `POST .../complete`, and discovery/subscription/invitation/replay endpoints not used in any reference project. See the [OpenAPI spec](https://docs.yutori.com/openapi.json) for complete coverage.

| Method | Endpoint | Purpose | Projects Using |
|--------|----------|---------|---------------|
| `POST` | `/v1/scouting/tasks` | Create a scout | All 4 projects |
| `GET` | `/v1/scouting/tasks` | List scouts (with `status`, `page_size`, `cursor` params) | LawSync |
| `GET` | `/v1/scouting/tasks/{id}` | Get scout detail | LawSync, ThreatGraph |
| `GET` | `/v1/scouting/tasks/{id}/updates` | Poll for updates (paginated with `page_size`, `cursor`) | All 4 projects |
| `PUT` | `/v1/scouting/tasks/{id}` | Edit/replace scout (full update, including changing query) | ThreatGraph |
| `PATCH` | `/v1/scouting/tasks/{id}` | Partial update (interval, timezone, is_public, etc.) | LawSync, ThreatGraph |
| `POST` | `/v1/scouting/tasks/{id}/done` | Archive scout (stops running) | LawSync |
| `DELETE` | `/v1/scouting/tasks/{id}` | Permanent deletion | LawSync, ThreatGraph |
| `PUT` | `/v1/scouting/tasks/{id}/email-settings` | Manage email notifications and subscribers | LawSync |

> **Code accuracy note**: ThreatGraph has a function named `restartScout()` in `src/lib/yutori.ts`, but it actually calls `PUT /v1/scouting/tasks/{id}` with `{ query: newQuery }` -- the "edit/replace" endpoint. The dedicated `POST /v1/scouting/tasks/{id}/restart` endpoint exists in the API but is not used by any reference project. The function name is misleading.

### Creating a Scout

**Minimal creation** (Access AI):

```typescript
const response = await fetch('https://api.yutori.com/v1/scouting/tasks', {
  method: 'POST',
  headers: { 'X-API-Key': apiKey, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Find URLs that potentially are inaccessible",
    task_spec: {
      output_schema: {
        type: "json",
        json_schema: {
          type: "object",
          properties: {
            inaccessible_urls: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  url: { type: "string" },
                  reason: { type: "string" }
                },
                required: ["url", "reason"]
              }
            }
          },
          required: ["inaccessible_urls"]
        }
      }
    }
  })
});
```

**Full-featured creation** (ThreatGraph):

```typescript
await createScout(
  "Monitor cybersecurity threat intelligence for APT groups targeting financial sector",
  "Financial Sector APT Monitor",           // display_name
  threatIntelligenceSchema,                 // output_schema
  "https://my-app.com/api/webhooks/yutori", // webhook_url
  {
    outputInterval: 3600,                   // hourly updates
    userTimezone: "America/New_York",
    skipEmail: true
  }
);
```

### Key Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | string | required | Natural language description of what to monitor |
| `display_name` | string | auto-generated | Human-readable name for the scout |
| `output_interval` | number | 86400 (daily) | Minimum 1800s (30 min) on create, 3600s (1 hr) on update |
| `start_timestamp` | string | now | ISO 8601 — when to start monitoring |
| `user_timezone` | string | UTC | IANA timezone (e.g., "America/Los_Angeles") |
| `user_location` | string | none | Location context for the scout |
| `output_schema` | object | none | JSON Schema for structured responses |
| `skip_email` | boolean | false | Disable email notifications |
| `webhook_url` | string | none | HTTPS URL for push notifications |
| `webhook_format` | string | "scout" | Options: "scout", "slack", "zapier" |
| `is_public` | boolean | false | Make scout publicly visible |

### How LawSync Wraps Scouts as Agentic Tools

LawSync's key architectural insight is registering 7 scouting endpoints as `@tool`-decorated methods (all except PUT edit and restart). The Strands agent framework then lets Gemini 2.0 Flash autonomously decide which endpoint to call based on natural language input:

```python
# The AI can autonomously call any of these based on user intent:
# "Create a scout to monitor Tesla lawsuits"  → create_scout()
# "Show me all my active scouts"              → list_scouts()
# "What's new from scout abc-123?"            → get_scout_updates("abc-123")
# "Change the update frequency to hourly"     → update_scout(id, output_interval=3600)
# "Stop monitoring that topic"                → mark_scout_done(id)
# "Delete the Tesla scout"                    → delete_scout(id)
```

The agent also uses Gemini to enhance simple user queries into 3-4 optimized monitoring prompts, creating multiple scouts from a single user request.

### How Signal Trade Bot Uses Scouts for Market Intelligence

Signal Trade Bot deploys one scout per data source (Twitter handle, subreddit, news topic), each with the same 150+ line intelligence report schema. The query is platform-contextualized:

```typescript
function buildQuery(source: DataSource): string {
  const platformContexts: Record<string, string> = {
    twitter: 'X/Twitter',
    reddit: 'Reddit',
    'google-news': 'Google News',
    telegram: 'Telegram',
    discord: 'Discord',
    github: 'GitHub',
    rss: 'RSS feed',
  };
  const platformName = platformContexts[source.platform] || source.platform;
  return `Get the latest updates from ${platformName}: ${source.identifier}`;
}
```

Multiple scouts are created concurrently. Signal Trade Bot caps at 2 concurrent creations via `sources.slice(0, 2)` -- this is an application-level limit, not an API-enforced constraint:

```typescript
const sourcesToProcess = sources.slice(0, 2);
const scoutPromises = sourcesToProcess.map(async (source) => {
  const response = await fetch('https://api.yutori.com/v1/scouting/tasks', {
    method: 'POST',
    headers: { 'X-API-Key': apiKey, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: buildQuery(source),
      task_spec: { output_schema: { json_schema: intelligenceReportSchema } },
    }),
  });
  return response.json();
});
const scouts = await Promise.all(scoutPromises);
```

### Polling for Updates

Updates are paginated. The response includes `next_cursor` and `prev_cursor` for traversal:

```typescript
// ThreatGraph — paginated polling with cursor support
export async function pollScout(scoutId: string, pageSize = 10, cursor?: string) {
  const params = new URLSearchParams({ page_size: String(pageSize) });
  if (cursor) params.set("cursor", cursor);
  return request<{
    updates: {
      id: string;
      task_id: string;
      content: string;
      created_at: string;
      update_type?: string;
    }[];
    total_count?: number;
    next_cursor?: string;
    prev_cursor?: string;
  }>("GET", `/v1/scouting/tasks/${scoutId}/updates?${params.toString()}`);
}
```

### Polling Multiple Scouts (Sequential to Avoid Rate Limits)

Signal Trade Bot polls all active scouts sequentially:

```typescript
// Signal Trade Bot — poll-all route
// Process scouts one at a time to avoid rate limiting
for (const scoutId of scoutIds) {
  try {
    const response = await fetch(
      `https://api.yutori.com/v1/scouting/tasks/${scoutId}/updates?page_size=10`,
      { method: 'GET', headers: { 'X-API-Key': apiKey } }
    );
    const data = await response.json();
    allUpdates.push({ scoutId, updates: data.updates || [] });
  } catch (err) {
    allUpdates.push({ scoutId, updates: [], error: err.message });
  }
}

// Flatten and sort by creation time (newest first)
const flatUpdates = allUpdates
  .flatMap(result => result.updates.map(update => ({ ...update, scoutId: result.scoutId })))
  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
```

**Critical pattern**: Sequential polling prevents rate-limit errors. Parallel polling of many scouts simultaneously will fail.

---

## 4. Pattern: Autonomous Browsing

The Browsing API creates on-demand browser automation tasks. An AI agent navigates to a URL, performs actions (click, type, scroll), and returns results — optionally as structured JSON.

### Creating a Browsing Task

**Basic task** (Access AI — multi-URL audit):

```typescript
// Access AI — app/api/yutori-browser-agent/route.ts
for (const url of urls) {
  const response = await fetch('https://api.yutori.com/v1/browsing/tasks', {
    method: 'POST',
    headers: { 'X-API-KEY': process.env.YUTORI_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start_url: url,
      task: goal  // e.g., "Audit this page for WCAG accessibility violations"
    })
  });
  const data = await response.json();
  createdTasks.push({ url, ...data });
}
```

**Task with structured output and agent selection** (LawSync — form analysis):

```python
# LawSync — backend/browsing/agents/form_screenshot_analyzer.py
payload = {
    "task": "Analyze this form and extract all form fields with their properties",
    "start_url": url,
    "max_steps": 30,
    "agent": "navigator-n1-preview-2025-11"  # Explicit agent selection
}

if output_schema:
    payload["task_spec"] = {
        "output_schema": {
            "type": "json",
            "json_schema": output_schema
        }
    }

response = requests.post(
    f"{self.base_url}/browsing/tasks",
    headers=self.headers,
    json=payload
)
```

### Agent Selection

| Agent ID | Engine | Cost | Best For |
|----------|--------|------|----------|
| `navigator-n1-latest` | Yutori n1 | $0.015/step | Most tasks — fastest, cheapest |
| `navigator-n1-preview-2025-11` | Yutori n1 (preview) | $0.015/step | Testing new n1 capabilities |
| `claude-sonnet-4-5-computer-use-2025-01-24` | Anthropic Claude | $0.10/step | Complex reasoning tasks |

LawSync explicitly selects `navigator-n1-preview-2025-11` for form analysis, choosing the preview agent for its newer capabilities. Access AI uses the default agent (implicitly `navigator-n1-latest`).

### Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `task` | string | required | Natural language description of what to do |
| `start_url` | string | required | Where to begin browsing |
| `max_steps` | number | 25 | Range: 2-100 |
| `agent` | string | "navigator-n1-latest" | See agent table above |
| `require_auth` | boolean | false | Pause for user authentication |
| `output_schema` | object | none | JSON Schema for structured result |
| `webhook_url` | string | none | HTTPS URL for completion notification |
| `webhook_format` | string | "scout" | Notification format |

### Polling for Completion

The browsing task status follows this state machine: `queued` -> `running` -> `succeeded` | `failed`

LawSync implements a polling loop with timeout:

```python
# LawSync — wait_for_task pattern
def wait_for_task(self, task_id: str, timeout: int = 300, poll_interval: int = 3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = self.get_task_status(task_id)
        if status["status"] in ["succeeded", "failed"]:
            return status
        time.sleep(poll_interval)
    raise TimeoutError(f"Task did not complete within {timeout} seconds")
```

Access AI uses the same pattern from the client side, polling every 3 seconds for up to 6 minutes (120 attempts).

### Response Structure

```typescript
{
  task_id: string;
  view_url: string;         // URL to watch the agent live
  status: "queued" | "running" | "succeeded" | "failed";
  result: string;            // Free-text result (when no schema)
  paused: boolean;           // True if waiting for auth
  structured_result: object; // Typed JSON (when output_schema provided)
  webhook_url: string;
}
```

### Trajectory Downloads

ThreatGraph integrates the lesser-known trajectory endpoint, which returns step-by-step screenshots of the agent's browsing session:

```typescript
// ThreatGraph — src/lib/yutori.ts
export async function getTrajectory(taskId: string) {
  return request<{
    steps: {
      url: string;
      action: string;
      data_extracted?: string;
      screenshot_url?: string;
      timestamp: string;
    }[];
  }>("GET", `/v1/browsing/tasks/${taskId}/trajectory`);
}
```

The trajectory endpoint also supports `output_type=zip` which returns a ZIP archive of WebP screenshots — useful for auditable compliance trails.

### Browsing for Automated Investigation (ThreatGraph)

ThreatGraph uses pre-defined URL templates to drive OSINT investigations via the Browsing API:

```typescript
// ThreatGraph — src/app/api/browse/investigate/route.ts
const INVESTIGATION_URLS: Record<string, (target: string) => string> = {
  whois: (target) => `https://who.is/whois/${encodeURIComponent(target)}`,
  dns: (target) => `https://who.is/dns/${encodeURIComponent(target)}`,
  ip: (target) => `https://who.is/whois-ip/ip-address/${encodeURIComponent(target)}`,
};

// Usage:
const startUrl = urlBuilder(target);  // e.g., "https://who.is/whois/example.com"
const task = `Investigate ${target} using ${type} lookup. Extract all registration details...`;
const browsingTask = await createBrowsingTask(startUrl, task);
```

This pattern shows how to combine parameterized URLs with natural language task instructions. The URL templates ensure the agent lands on the right page, while the task description guides what data to extract.

### The Two-Phase Form Workflow (LawSync)

LawSync demonstrates a sophisticated two-phase pattern for form automation:

1. **Phase 1 — Analyze**: Send a browsing task with a structured output schema describing form fields. The n1 agent navigates to the form, reads it, and returns typed JSON.
2. **Phase 2 — Fill**: Send a second browsing task with the collected user data as natural language instructions. The agent fills and submits the form.

```python
# Phase 1: Analyze
result = analyzer.analyze_form(url="https://example.com/contact")
# Returns: { form_type: "contact", fields: [{name: "email", type: "email", required: true}, ...] }

# Phase 2: Fill (after collecting user data)
result = analyzer.fill_form(
    url="https://example.com/contact",
    form_data={"email": "user@example.com", "name": "Jane Doe", "phone": "555-1234"}
)
```

This separation ensures the agent never submits incorrect data — the human reviews the form structure and confirms before submission.

---

## 5. Pattern: Deep Research

The Research API conducts one-time, wide-ranging investigations across the web. Unlike scouting (recurring) or browsing (single-site), research uses 100+ MCP tools and multiple web navigation agents to synthesize information from many sources.

### When to Use Research vs. Scouting

| Dimension | Research | Scouting |
|-----------|----------|----------|
| Frequency | One-time | Recurring (interval-based) |
| Depth | Very deep (100+ tools) | Moderate (monitoring-focused) |
| Output | Comprehensive markdown report | Periodic update snapshots |
| Latency | Minutes | Seconds to minutes per update |
| Cost | $0.35/task | $0.35/scout-run |
| Best for | "Tell me everything about X" | "Alert me when X changes" |

### Creating a Research Task

Access AI uses research to find website owner contact information:

```typescript
// Access AI — app/api/find-owners/route.ts
const query = `Find the contact person and email address responsible for accessibility
  or technical changes for the following websites: ${urls.join(', ')}.
  Return the url, contact name, email, and role for each.`;

const response = await fetch("https://api.yutori.com/v1/research/tasks", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YUTORI_API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    query: query,
    task_spec: {
      output_schema: {
        type: "json",
        json_schema: {
          type: "object",
          properties: {
            contacts: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  url: { type: "string" },
                  contact_name: { type: "string" },
                  email: { type: "string" },
                  role: { type: "string" }
                },
                required: ["url", "contact_name", "email"]
              }
            }
          },
          required: ["contacts"]
        }
      }
    }
  })
});
```

### Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | string | required | What to research |
| `user_timezone` | string | UTC | Timezone for context |
| `user_location` | string | none | Location for context |
| `output_schema` | object | none | JSON Schema for structured output |
| `webhook_url` | string | none | Completion notification URL |
| `webhook_format` | string | "scout" | Notification format |

### Response Structure

```typescript
{
  task_id: string;
  view_url: string;
  status: "queued" | "running" | "succeeded" | "failed";
  result: string;              // Markdown report (when no schema)
  structured_result: object;   // JSON (when schema provided)
  created_at: string;
  updates: Array<{             // Intermediate progress updates
    id: string;
    content: string;
    timestamp: string;
  }>;
}
```

### Parallel Research + Browsing (Access AI)

Access AI fires research tasks in parallel with browsing audit tasks. While the browser agent audits pages for accessibility violations, the research agent finds the site owner's contact information. Both results converge in the frontend:

```
URL submitted
    ├── Browsing API → Accessibility audit → Structured violations
    └── Research API → Contact discovery  → {name, email, role}
                                            ↓
                                  Combined into Linear ticket
```

This parallel execution pattern is a key optimization — research tasks typically take 1-3 minutes, which overlaps with browsing task duration.

---

## 6. Pattern: n1 Pixel-to-Action

The n1 API provides direct access to Yutori's vision-based browser control model via an OpenAI-compatible chat completions interface. Unlike the Browsing API (which is a managed service), n1 gives you raw control over the screenshot-to-action loop.

### How It Works

```
Send screenshot (base64 WebP) → n1 analyzes pixels → Returns action
    ↑                                                       |
    └───────────── Execute action in browser ←──────────────┘
```

### API Interface

```
POST https://api.yutori.com/v1/chat/completions
Authorization: Bearer <api-key>   (or X-API-Key header)
```

### Available Models

| Model ID | Description |
|----------|-------------|
| `n1-latest` | Current production model |
| `n1-experimental` | Experimental features |
| `n1-20260203` | Pinned version |

### Message Format

Messages follow the OpenAI multimodal format with text + image_url:

```json
{
  "model": "n1-latest",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "Click the login button" },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/webp;base64,<screenshot>"
          }
        }
      ]
    }
  ]
}
```

### Coordinate Space

n1 uses a **1000x1000 relative coordinate space** regardless of actual screen resolution. The recommended screenshot resolution is **1280x800** in WebP format for optimal performance.

### Supported Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `left_click` | Single left click | x, y |
| `double_click` | Double left click | x, y |
| `triple_click` | Triple left click | x, y |
| `right_click` | Right click | x, y |
| `drag` | Click and drag | start_x, start_y, end_x, end_y |
| `hover` | Move mouse without clicking | x, y |
| `scroll` | Scroll in a direction | x, y, direction, amount |
| `type` | Type text | text |
| `key_press` | Press a key | key |
| `goto_url` | Navigate to URL | url |
| `go_back` | Browser back | none |
| `refresh` | Refresh page | none |
| `wait` | Wait for page load | seconds |

### When to Use n1 vs. Browsing API

| Dimension | n1 API | Browsing API |
|-----------|--------|-------------|
| Control | Raw actions, you manage the loop | Managed end-to-end |
| Screenshots | You provide them | Agent captures its own |
| Error handling | You implement retries | Built-in |
| Structured output | Via prompt engineering | Native `output_schema` |
| Cost | Per-token ($0.75/$3 per 1M) | Per-step ($0.015) |
| Best for | Custom automation loops, complex UIs | Standard web tasks |

---

## 7. Pattern: Structured Output Schemas

Structured output is the most impactful pattern across all winning projects. It transforms free-text AI responses into typed, parseable JSON that downstream systems can process programmatically.

### Schema Placement (IMPORTANT: Deprecation Notice)

> **DEPRECATED**: The `task_spec.output_schema` wrapper format is deprecated. All three hackathon winners and ThreatGraph use this older format, but new projects should use the top-level `output_schema` field directly. The deprecated format still works but may be removed in a future API version.

```json
// DEPRECATED format (used by all 3 hackathon winners + ThreatGraph)
// Still works, but prefer the newer format for new code
{
  "task_spec": {
    "output_schema": {
      "type": "json",
      "json_schema": { ... }
    }
  }
}
```

```json
// PREFERRED format (current API docs)
{
  "output_schema": { ... }
}
```

The Python SDK handles the conversion automatically when you pass Pydantic models. If you are copying code from the reference projects, be aware they all use the deprecated `task_spec` wrapper.

### Schema Complexity Spectrum

The three winning projects demonstrate increasing schema sophistication:

#### Level 1: Simple (Access AI — Scout for Inaccessible URLs)

A flat array of objects — minimal but sufficient to drive downstream logic:

```json
{
  "type": "object",
  "properties": {
    "inaccessible_urls": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "url": { "type": "string" },
          "reason": { "type": "string" }
        },
        "required": ["url", "reason"]
      }
    }
  },
  "required": ["inaccessible_urls"]
}
```

#### Level 2: Medium (LawSync — Form Analysis via Browsing)

Nested objects with typed fields, enums, and nullable properties:

```json
{
  "type": "object",
  "properties": {
    "form_type": {
      "type": "string",
      "description": "Type of form (contact, registration, survey, application, other)"
    },
    "form_name": { "type": "string" },
    "fields": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "description": "Field name or ID" },
          "type": { "type": "string", "description": "text, email, tel, textarea, select, ..." },
          "label": { "type": "string" },
          "required": { "type": "boolean" },
          "placeholder": { "type": ["string", "null"] },
          "options": { "type": ["array", "null"], "items": { "type": "string" } }
        },
        "required": ["name", "type", "label", "required"]
      }
    },
    "submit_button_text": { "type": "string" }
  },
  "required": ["form_type", "form_name", "fields", "submit_button_text"]
}
```

#### Level 3: Complex (Signal Trade Bot — Intelligence Report)

150+ lines defining nested objects with enums, credibility ratings, sentiment analysis, and trading signals. This is the schema that most impressed judges:

```typescript
const intelligenceReportSchema = {
  type: 'object',
  properties: {
    headline: {
      type: 'string',
      description: 'Brief headline summarizing the current status',
    },
    status: {
      type: 'string',
      enum: ['no_change', 'escalation', 'de_escalation', 'critical_event', 'breaking'],
    },
    confidence_level: {
      type: 'number',
      description: 'Confidence in the assessment from 0-100',
    },
    summary: {
      type: 'string',
      description: 'Detailed paragraph summary of the overall situation',
    },
    key_findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          finding: { type: 'string' },
          source_url: { type: 'string' },
          source_author: { type: 'string' },
          timestamp: { type: 'string', description: 'ISO 8601' },
          credibility: {
            type: 'string',
            enum: ['verified', 'credible', 'unverified', 'disputed'],
          },
        },
        required: ['finding'],
      },
    },
    not_reported: {
      type: 'array',
      description: 'Important things NOT being reported (for ruling out scenarios)',
      items: { type: 'string' },
    },
    misinformation_alerts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          source_url: { type: 'string' },
          debunk_status: { type: 'string' },
        },
      },
    },
    community_sentiment: {
      type: 'object',
      properties: {
        overall: {
          type: 'string',
          enum: ['strongly_positive', 'positive', 'neutral', 'negative', 'strongly_negative', 'mixed'],
        },
        key_opinions: { type: 'array', items: { type: 'string' } },
      },
    },
    trading_signal: {
      type: 'object',
      properties: {
        direction: { type: 'string', enum: ['bullish', 'bearish', 'neutral', 'uncertain'] },
        confidence: { type: 'number' },
        rationale: { type: 'string' },
        key_triggers: { type: 'array', items: { type: 'string' } },
      },
    },
    baseline_status: { type: 'string' },
  },
  required: ['headline', 'status', 'summary', 'key_findings', 'baseline_status'],
};
```

#### Level 4: Graph-Oriented (ThreatGraph — Entity/Relationship Extraction)

ThreatGraph's schema is designed specifically to feed a Neo4j knowledge graph. It extracts typed entities, IOCs (indicators of compromise), and named relationships:

```typescript
// ThreatGraph — src/lib/schema.ts
export const threatIntelSchema = {
  type: "object" as const,
  properties: {
    entities: {
      type: "array" as const,
      items: {
        type: "object" as const,
        properties: {
          type: {
            type: "string" as const,
            enum: [
              "ThreatActor", "Vulnerability", "Exploit", "Software",
              "Organization", "Malware", "Campaign", "AttackTechnique",
            ],
          },
          name: { type: "string" as const },
          cve_id: { type: "string" as const },
          cvss: { type: "number" as const },
          severity: {
            type: "string" as const,
            enum: ["critical", "high", "medium", "low"],
          },
          exploited_in_wild: { type: "boolean" as const },
          source_url: { type: "string" as const },
        },
        required: ["type", "name"],
      },
    },
    iocs: {
      type: "array" as const,
      items: {
        type: "object" as const,
        properties: {
          type: {
            type: "string" as const,
            enum: ["ip", "domain", "hash_md5", "hash_sha256", "url", "email"],
          },
          value: { type: "string" as const },
          context: { type: "string" as const },
        },
        required: ["type", "value"],
      },
    },
    relationships: {
      type: "array" as const,
      items: {
        type: "object" as const,
        properties: {
          source: { type: "string" as const },
          target: { type: "string" as const },
          relationship: {
            type: "string" as const,
            enum: ["USES", "TARGETS", "AFFECTS", "EXPLOITS", "ATTRIBUTED_TO", "RELATED_TO"],
          },
        },
        required: ["source", "target", "relationship"],
      },
    },
    threat_brief: {
      type: "object" as const,
      properties: {
        headline: { type: "string" as const },
        summary: { type: "string" as const },
        severity: { type: "string" as const, enum: ["critical", "high", "medium", "low"] },
      },
      required: ["headline", "summary", "severity"],
    },
  },
  required: ["entities", "relationships", "threat_brief"],
};
```

This schema is notable because it extracts graph-native data: entities become nodes, relationships become edges, and the `type` enums map directly to Neo4j labels and relationship types. The IOCs array provides actionable intelligence (IP addresses, domains, file hashes) that can be cross-referenced across scout updates.

### Key Design Principles for Schemas

1. **Use `description` fields generously** — they guide the AI's output quality significantly
2. **Use `enum` for classification fields** — prevents the AI from inventing categories
3. **Mark only truly essential fields as `required`** — the AI may not always have data for every field
4. **Use `type: ["string", "null"]`** for optional fields that may be absent
5. **Design schemas for your downstream consumer** — the schema IS your API contract between Yutori and your application logic

### Pydantic Integration (Python SDK)

When using the official Python SDK, you can pass Pydantic models directly:

```python
from pydantic import BaseModel
from yutori import YutoriClient

class IntelligenceReport(BaseModel):
    headline: str
    status: str
    confidence_level: int
    key_findings: list[dict]

client = YutoriClient(api_key="...")
scout = client.scouts.create(
    query="Monitor AI regulation news",
    output_schema=IntelligenceReport
)
```

The SDK converts the Pydantic model to JSON Schema automatically.

---

## 8. Pattern: AI-on-AI Layering

The most distinctive pattern across all winning projects: layering a second AI model on top of Yutori's agents to transform raw intelligence into domain-specific decisions. Yutori provides the data; another model provides the reasoning.

### The Three Architectures

#### Architecture A: Pre-Processing Layer (LawSync)

Gemini enhances user queries BEFORE they reach Yutori:

```
User: "Monitor Tesla lawsuits"
    ↓
Gemini 2.0 Flash: Generates 3-4 optimized monitoring prompts
    ↓
Yutori Scouting API: Creates scouts for each prompt
    ↓
Updates flow back to user
```

The insight: simple user queries produce mediocre scouts. A pre-processing LLM can decompose vague requests into specific, multi-angle monitoring tasks.

#### Architecture B: Post-Processing Layer (Signal Trade Bot)

Yutori gathers intelligence, then Claude makes trading decisions:

```
Yutori Scouts: Gather intelligence from Twitter, Reddit, News
    ↓
Signal Trade Bot: Aggregates timeline of intelligence updates
    ↓
Claude 3.5 Sonnet: Analyzes timeline as "hedge fund analyst"
    ↓
Output: { action: "buy_yes" | "buy_no" | "hold", confidence: 0-100 }
    ↓
If confidence >= 75%: Execute trade via Kalshi API
```

The Claude prompt is carefully engineered as a role:

```typescript
const prompt = `
You are an expert hedge fund analyst for a prediction market trading bot.

**Context**
Strategy: "${strategy.name}"
${marketContext}

**Intelligence Timeline**
${eventsContext}

**Task**
Analyze the timeline and determine if there is a strong signal to trade.

Return JSON only:
{ "action": "buy_yes" | "buy_no" | "hold", "confidence": 0-100, "reasoning": "..." }
`;
```

#### Architecture C: Vision Analysis Layer (Access AI)

Yutori browses and audits, then GPT-5.2 analyzes both text AND screenshots:

```
Yutori Browsing API: Audits pages for accessibility violations
    ↓
Raw audit logs + screenshots captured during browsing
    ↓
GPT-5.2 (vision): Analyzes text logs AND visual screenshots
    ↓
Structured accessibility report with POUR categorization
    ↓
Linear API: Create prioritized engineering tickets
```

The vision layer catches issues that text-only analysis misses — color contrast problems, visual hierarchy issues, and layout-based accessibility failures.

### Why This Pattern Wins

1. **Yutori excels at web interaction** — navigating, monitoring, extracting. But it does not make domain-specific decisions.
2. **Domain LLMs excel at reasoning** — trading decisions, legal analysis, accessibility scoring. But they cannot browse the web.
3. **Combining them creates autonomous pipelines** — the whole exceeds the sum of its parts.

### Implementation Guideline

Choose your AI layer based on what you need:

| Need | Recommended Model | Why |
|------|-------------------|-----|
| Query enhancement before Yutori | Gemini Flash / GPT-4o Mini | Fast, cheap, good at rephrasing |
| Complex reasoning on Yutori output | Claude Opus / GPT-4o | Best at nuanced analysis |
| Visual analysis of screenshots | GPT-4o / GPT-5.2 Vision | Multimodal understanding |
| Structured decision making | Claude Sonnet / GPT-4o | Reliable JSON output |

---

## 9. Pattern: Webhook-Driven Pipelines

Instead of polling, webhooks push updates to your server the moment they're available. This is the most production-ready integration pattern but also the least used in hackathon projects.

### Configuration

Add `webhook_url` and `webhook_format` when creating a scout:

```typescript
await createScout("Monitor cybersecurity threats", undefined, schema,
  "https://your-app.com/api/webhooks/yutori",  // webhook_url
  { outputInterval: 3600 }
);
```

### Payload Structure

Yutori sends POST requests with these headers:

| Header | Value |
|--------|-------|
| `Content-Type` | `application/json` |
| `User-Agent` | `Scout-Webhook/1.0` |
| `X-Scout-Event` | `scout.update` |

### Webhook Formats

| Format | Use Case |
|--------|----------|
| `scout` | Raw JSON payload (default) |
| `slack` | Pre-formatted for Slack incoming webhooks |
| `zapier` | Compatible with Zapier webhook triggers |

### Requirements and Constraints

- **HTTPS required** (except `localhost` for development)
- **10-second response timeout** — your handler must respond within 10 seconds
- **No automatic retry** — if your endpoint is down, the update is lost
- **Test endpoint**: `POST /v1/scouting/webhooks/test` to verify your handler

### Webhooks vs. Polling: Trade-offs

| Dimension | Webhooks | Polling |
|-----------|----------|---------|
| Latency | Near-instant | Depends on interval (3s-30s typical) |
| Server load | Only on updates | Continuous requests |
| Reliability | No retry — updates can be lost | Always gets latest state |
| Infrastructure | Needs public HTTPS endpoint | Works from anywhere |
| Development | More complex (handler, validation) | Simpler (loop + sleep) |
| Best for | Production systems, real-time alerts | Prototypes, hackathons |

### Recommended Hybrid Pattern

For production systems, use webhooks as the primary notification mechanism but maintain a polling fallback:

```
Webhook received → Process update
    |
    └── If no webhook for 2x interval → Fall back to polling
```

---

## 10. Pattern: Resilient Async Operations

All Yutori APIs are asynchronous. Tasks take seconds to minutes to complete. Building resilient applications requires handling this asynchrony at every layer.

### Polling Intervals by API

| API | Recommended Interval | Timeout | Rationale |
|-----|---------------------|---------|-----------|
| Browsing | 3 seconds | 300-360 seconds | Tasks complete in 30-120 seconds typically |
| Scouting (updates) | 30 seconds | N/A (recurring) | Scouts run on their own schedule |
| Research | 5-10 seconds | 600 seconds | Deep research takes 1-5 minutes |

### Session Persistence (Access AI)

Access AI stores in-progress Yutori task IDs in `localStorage`, enabling recovery after page refreshes:

```
User starts audit → Task IDs saved to localStorage
    ↓
Page refresh / browser crash
    ↓
On load → Check localStorage for pending task IDs
    ↓
Resume polling for each stored task ID
```

This pattern is critical for any long-running Yutori task. Without it, a page refresh means lost progress and orphaned Yutori tasks that continue burning credits.

### Update Deduplication (Signal Trade Bot)

Scout updates have unique IDs. Signal Trade Bot deduplicates on the client:

```typescript
// Track seen update IDs to prevent re-processing
const seenUpdateIds = new Set<string>();

for (const update of newUpdates) {
  if (seenUpdateIds.has(update.id)) continue;
  seenUpdateIds.add(update.id);
  processUpdate(update);  // Only process truly new updates
}
```

### Rate Limit Awareness

Signal Trade Bot polls scouts **sequentially** (not in parallel) to avoid rate limits:

```typescript
// GOOD: Sequential polling
for (const scoutId of scoutIds) {
  const result = await pollScout(scoutId);
  // ...
}

// BAD: Parallel polling (will hit rate limits with many scouts)
// const results = await Promise.all(scoutIds.map(id => pollScout(id)));
```

### Error Recovery Patterns

ThreatGraph's client wrapper includes timeout-based abort:

```typescript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 30_000);
try {
  const res = await fetch(url, { signal: controller.signal, ... });
  // ...
} finally {
  clearTimeout(timeout);
}
```

LawSync wraps every API call in try/except with structured error responses:

```python
try:
    response = requests.post(url, headers=self.headers, json=payload, timeout=30)
    response.raise_for_status()
    return {"status": "success", "content": [{"json": response.json()}]}
except requests.exceptions.RequestException as e:
    return {"status": "error", "content": [{"text": f"Failed: {str(e)}"}]}
```

### Handling 422 Validation Errors

The Yutori API returns `422 Unprocessable Entity` with an `HTTPValidationError` body when request parameters fail validation (e.g., `output_interval` below the minimum, invalid `user_timezone`, malformed `json_schema`). None of the reference projects handle this specifically -- they all treat non-2xx responses generically. A production implementation should parse the 422 body:

```typescript
if (res.status === 422) {
  const body = await res.json();
  // body.detail is an array of { loc: string[], msg: string, type: string }
  const messages = body.detail?.map((d: any) => `${d.loc.join('.')}: ${d.msg}`);
  throw new Error(`Validation failed: ${messages?.join('; ')}`);
}
```

### Handling Task Failures

When a browsing or research task reaches `status: "failed"`, the `result` field contains an error message. None of the reference projects implement retry logic for failed tasks. For production use, consider:

1. Retrying with a simplified `task` description (complex prompts are more likely to fail)
2. Reducing `max_steps` if the agent ran out of steps
3. Logging the trajectory (browsing tasks) to understand what went wrong

---

## 11. Comparative Matrix

| Dimension | LawSync | Access AI | Signal Trade Bot | ThreatGraph |
|-----------|---------|-----------|-----------------|-------------|
| **Scouting Endpoints Used** | 7 (CRUD + email, no PUT edit or restart) | 1 (create) | 2 (create + poll) | 6 (create, list, detail, poll, PUT edit, PATCH, delete) |
| **Browsing Endpoints Used** | 2 (create + poll) | 2 (create + poll) | 0 | 3 (create + poll + trajectory) |
| **Research Endpoints Used** | 0 | 1 (create) | 0 | 1 (create + poll) |
| **APIs Used** | Scouting, Browsing | Scouting, Browsing, Research | Scouting | Scouting, Browsing, Research |
| **Schema Complexity** | Medium (form fields) | Simple (URL list) | Complex (150+ lines) | Medium-Complex |
| **AI Layer** | Gemini (pre-process) + GPT-4o (forms) | GPT-5.2 Vision (post-process) | Claude 3.5 (post-process) | OpenAI (post-process) |
| **Frontend** | React 18 + Vite | Next.js 16 | Next.js 16 | Next.js 16 |
| **Backend** | Python/FastAPI (4 microservices) | Next.js API Routes | Next.js API Routes | Next.js API Routes |
| **Client Pattern** | Class-based Python + @tool | Inline fetch | Inline fetch | Typed wrapper module |
| **Unique Features** | Agentic tool discovery, CUA sandbox | Session persistence, dual-agent | Auto-trading, RSA crypto | Webhooks, trajectory, D3 viz |

---

## 12. Lessons from Hackathon Winners

### 1. Use All 3 APIs

Access AI was the only project using Scouting + Browsing + Research in a unified pipeline. This breadth impressed judges. Each API serves a different temporal need: Research for one-time deep dives, Browsing for on-demand interaction, Scouting for ongoing monitoring.

### 2. Complex Structured Schemas Impress Judges

Signal Trade Bot's 150+ line intelligence report schema was singled out as the most sophisticated Yutori integration. The schema itself communicates ambition — it tells judges you understand the platform deeply enough to extract maximum structured value from it.

### 3. AI-on-AI Layering Is the Key Differentiator

Every winning project layered at least one additional LLM on top of Yutori:
- LawSync: Gemini enhances prompts, GPT-4o analyzes forms
- Access AI: GPT-5.2 vision analyzes audit logs + screenshots
- Signal Trade Bot: Claude generates trading decisions from intelligence

This pattern transforms Yutori from a data source into an intelligence engine.

### 4. End-to-End Pipelines Win Over Feature Demos

None of these projects just "fetch and display." Each built complete automation loops:
- LawSync: Query -> Enhanced prompts -> Scout creation -> Updates -> Legal insights
- Access AI: URL -> Sitemap -> Audit -> Vision analysis -> Report -> Linear tickets
- Signal Trade Bot: Strategy -> Scouts -> Intelligence -> AI analysis -> Trade execution

### 5. Production UI Signals Seriousness

All three winners had polished interfaces with loading states, error handling, and animations. LawSync had a full landing page with serif typography and warm earth tones. Signal Trade Bot had a professional trading terminal aesthetic. Access AI had interactive eye animations with trigonometric calculations.

### 6. Lesser-Known Features Stand Out

Features like trajectory downloads, webhooks, scout restart, email settings management, and the n1 model API are rarely used. Demonstrating them signals deep platform knowledge. Dhruv Batra (Yutori co-founder and judge) specifically values creative use of these capabilities.

### 7. Pre-Seed Data for Demo Day

Scout updates take time to accumulate. Browsing tasks take 30-120 seconds. For a 5-minute demo, have impressive pre-seeded data ready. All winning projects had enough data to show compelling results without waiting for live API responses.

---

## 13. Quick Reference

### Full Endpoint Map

```
Authentication:
  Header: X-API-Key: <key>
  Base URL: https://api.yutori.com

Scouting:
  POST   /v1/scouting/tasks                        Create scout
  GET    /v1/scouting/tasks                         List scouts
  GET    /v1/scouting/tasks/{id}                    Get scout detail
  GET    /v1/scouting/tasks/{id}/updates            Poll updates
  PUT    /v1/scouting/tasks/{id}                    Edit/replace scout
  PATCH  /v1/scouting/tasks/{id}                    Partial update
  POST   /v1/scouting/tasks/{id}/pause              Pause scout
  POST   /v1/scouting/tasks/{id}/resume             Resume scout
  POST   /v1/scouting/tasks/{id}/restart            Restart scout
  POST   /v1/scouting/tasks/{id}/done               Archive scout
  POST   /v1/scouting/tasks/{id}/complete           Mark complete
  DELETE /v1/scouting/tasks/{id}                    Delete scout
  PUT    /v1/scouting/tasks/{id}/email-settings     Email settings

Browsing:
  POST   /v1/browsing/tasks                         Create task
  GET    /v1/browsing/tasks/{id}                     Get status/result
  GET    /v1/browsing/tasks/{id}/trajectory          Download trajectory

Research:
  POST   /v1/research/tasks                         Create task
  GET    /v1/research/tasks/{id}                     Get status/result

n1 Model:
  POST   /v1/chat/completions                       Chat completions

Webhooks:
  POST   /v1/scouting/webhooks/test                 Test webhook
```

### Security Considerations

1. **API key handling**: Store `YUTORI_API_KEY` in environment variables, never in client-side code. All reference projects correctly use server-side API routes to proxy Yutori calls, keeping the key out of the browser.

2. **Path parameter injection**: When constructing URLs like `/v1/scouting/tasks/${scoutId}`, none of the reference projects validate that `scoutId` is a valid UUID before interpolating it into the URL path. A malicious input like `../../other/endpoint` could theoretically manipulate the URL. ThreatGraph's `request()` wrapper constructs the full URL as `${BASE_URL}${path}`, so a tampered path could reach unintended endpoints. Validate IDs server-side before using them in URL construction.

3. **Browsing API `start_url`**: The `start_url` parameter in browsing tasks tells Yutori's agent where to navigate. If this comes from user input, validate it against an allowlist of domains to prevent the agent from browsing unintended or malicious sites on your API credit.

### Environment Variables

```bash
YUTORI_API_KEY=yut_...         # Required — from platform.yutori.com/settings
```

### Status Enums

**Scout Status**: `active` -> `paused` (via `POST .../pause`) -> `active` (via `POST .../resume`) | `done` (via `POST .../done` or `POST .../complete`)

**Browsing/Research Task Status**: `queued`, `running`, `succeeded`, `failed`

**Browsing Task — `paused` field**: `true` when waiting for user authentication (`require_auth: true`)

### Default Values

| Parameter | Default |
|-----------|---------|
| Scout `output_interval` | 86400 (24 hours) |
| Scout `output_interval` minimum (create) | 1800 (30 minutes) |
| Scout `output_interval` minimum (update) | 3600 (1 hour) |
| Browsing `max_steps` | 25 |
| Browsing `max_steps` range | 2-100 |
| Browsing default `agent` | `navigator-n1-latest` |
| Email `subscribers_to_add` max | 200 per request |

### Agent Types (Browsing API)

| Agent ID | Provider |
|----------|----------|
| `navigator-n1-latest` | Yutori n1 (production) |
| `navigator-n1-preview-2025-11` | Yutori n1 (preview) |
| `claude-sonnet-4-5-computer-use-2025-01-24` | Anthropic Claude CU |

### n1 Model Versions

| Model ID | Description |
|----------|-------------|
| `n1-latest` | Current production |
| `n1-experimental` | Experimental features |
| `n1-20260203` | Pinned release |

### Webhook Headers

| Header | Value |
|--------|-------|
| `Content-Type` | `application/json` |
| `User-Agent` | `Scout-Webhook/1.0` |
| `X-Scout-Event` | `scout.update` |

### Pricing Summary

| API | Unit | Cost |
|-----|------|------|
| n1 Model (input) | Per 1M tokens | $0.75 |
| n1 Model (output) | Per 1M tokens | $3.00 |
| Browsing (n1) | Per step | $0.015 |
| Browsing (Claude CU) | Per step | $0.10 |
| Research | Per task | $0.35 |
| Scouting | Per scout-run | $0.35 |
| Free credits | On signup | $5.00 |

---

*Document compiled from source code analysis of LawSync, Access AI (accessibility-agent), Signal Trade Bot (signal-trade-bot), and ThreatGraph reference implementations. All code examples are drawn from actual project source files.*

---

## Review Notes (Devil's Advocate Review)

The following changes were made during a thorough code-accuracy and completeness review, cross-referencing every code example against actual source files and comparing API documentation claims against the [Yutori OpenAPI spec](https://docs.yutori.com/openapi.json).

### Issues Found and Fixed

1. **Scouting endpoint table miscounted and misattributed (Section 3)**
   - **Problem**: Table header said "All 8 Scouting Endpoints" but listed 9 rows. More importantly, `POST /v1/scouting/tasks/{id}/restart` was attributed to ThreatGraph, but ThreatGraph's `restartScout()` function actually calls `PUT /v1/scouting/tasks/{id}` (the edit/replace endpoint). The function is misleadingly named.
   - **Fix**: Added the missing `PUT .../tasks/{id}` (edit) endpoint, corrected attributions, added a code accuracy note explaining the naming mismatch, and noted that `POST .../restart` is not actually used by any reference project.

2. **`task_spec.output_schema` deprecation insufficiently flagged (Section 7)**
   - **Problem**: The doc said "Both formats work. The newer format is simpler." -- too neutral. The `task_spec` wrapper is deprecated per official docs. Every code example in the document uses the deprecated format, which could mislead developers copying code.
   - **Fix**: Added a prominent deprecation warning with DEPRECATED label. Clearly marked which format is preferred for new code.

3. **Missing `summary` property in Signal Trade Bot schema excerpt (Section 7)**
   - **Problem**: The schema's `required` array includes `'summary'`, but the `summary` property definition was omitted from the truncated code listing. A developer reading this would see a `required` field with no corresponding property definition.
   - **Fix**: Added the `summary` property definition between `confidence_level` and `key_findings`.

4. **API header capitalization inconsistency not flagged (Section 2)**
   - **Problem**: Access AI browser agent routes use `X-API-KEY` (all caps), while LawSync and Signal Trade Bot use `X-API-Key`. The doc presented one casing without noting the inconsistency.
   - **Fix**: Added a note explaining that HTTP headers are case-insensitive, documenting the actual variations found across projects, and recommending consistency.

5. **Missing scout lifecycle states (Section 13 Quick Reference)**
   - **Problem**: Scout status listed as simple enum `active, paused, done`. The OpenAPI spec reveals `pause`, `resume`, and `complete` endpoints, indicating richer status transitions.
   - **Fix**: Expanded to show the state machine: `active -> paused (via pause) -> active (via resume) | done (via done/complete)`.

6. **Missing endpoints in Quick Reference (Section 13)**
   - **Problem**: The endpoint map omitted `PUT .../tasks/{id}` (edit), `POST .../pause`, `POST .../resume`, and `POST .../complete`.
   - **Fix**: Added all missing endpoints to the Quick Reference map.

7. **Comparative Matrix endpoint counts inaccurate (Section 11)**
   - **Problem**: LawSync was listed as using "8 (full CRUD + email)" scouting endpoints. Actual count from code review: 7 (LawSync does not use PUT edit or restart). ThreatGraph was listed as "7 (all except email)" but actually uses 6 distinct endpoints.
   - **Fix**: Corrected both counts with specific breakdowns.

8. **No security considerations (Section 13)**
   - **Problem**: No mention of API key handling best practices, URL path parameter injection risks, or `start_url` validation for browsing tasks.
   - **Fix**: Added a Security Considerations subsection covering API key storage, path parameter validation, and `start_url` allowlisting.

9. **No error handling guidance for 422 responses (Section 10)**
   - **Problem**: The Yutori API returns `422 Unprocessable Entity` with structured validation errors, but none of the reference projects handle this specifically, and the doc didn't mention it.
   - **Fix**: Added a subsection on handling 422 validation errors with code example, and a subsection on handling task failures with retry guidance.

### Issues Reviewed But Not Changed

- **n1 model details and pricing**: Could not independently verify benchmark numbers (78.7% Online-Mind2Web, etc.) or exact pricing against current Yutori docs since the specific pricing/benchmarks pages were not accessible. Left as-is with the caveat that these may change.
- **Python SDK code examples (Pattern D, Pydantic integration)**: These are illustrative rather than sourced from reference projects. They appear reasonable but cannot be verified against actual SDK source. Left as-is since they are clearly labeled as SDK usage rather than reference project code.
- **Webhook details (Section 9)**: Webhook header values, 10-second timeout, and no-retry behavior could not be independently verified against official docs. Left as-is since they are plausible and ThreatGraph's code includes `webhook_url` support.
- **TypeScript/Python balance**: The document is heavier on TypeScript examples (3 of 4 reference projects are TypeScript). This is accurate to the source material, not a bias to correct.
