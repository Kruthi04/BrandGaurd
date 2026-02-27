# Senso API Research - BrandGuard Hackathon

## Hackathon Context

- **Event**: MCP - AWS - Enterprise Agents Challenge
- **Date**: July 25, 2025, AWS Builder Loft, San Francisco
- **Senso Prize**: $2k credits for best Senso integration
- **Requirement**: Must use at least 3 sponsor tools
- **Hackathon Manager**: andy@senso.ai
- **Devpost**: https://mcp-aws-enterprise-agents.devpost.com/
- **Other Key Sponsors**: Tavily MCP, AWS (Bedrock, Q, Kiro), MongoDB, NLX, Bright Data MCP

---

## Senso Overview

Senso is an enterprise platform for **Generative Engine Optimization (GEO)** -- helping brands monitor, evaluate, and remediate how they appear in AI-generated answers across ChatGPT, Gemini, Perplexity, Claude, and 25+ AI platforms. It acts as a "Context OS" -- a single REST layer between your data and AI agents.

### Key Value Propositions
- Monitor brand visibility across AI platforms
- Evaluate citation accuracy and answer quality
- Detect brand misrepresentation in AI-generated content
- Auto-remediate content gaps with optimized content
- Rules engine to trigger actions on detection events

---

## TWO API Systems

Senso has **two distinct API systems**:

### 1. GEO Platform API (apiv2) - Brand Monitoring & Evaluation
- **Base URL**: `https://apiv2.senso.ai`
- **Auth**: `Authorization: Bearer YOUR_API_KEY`
- **Purpose**: Evaluate brand representation across AI platforms, remediate incorrect content

### 2. Context OS SDK API - Knowledge Management & Content Generation
- **Base URL**: `https://sdk.senso.ai/api/v1`
- **Auth**: `X-API-Key: tgr_live_xxx` or `X-API-Key: tgr_test_xxx`
- **Purpose**: Ingest knowledge, search content, generate new content, manage rules/triggers/webhooks
- **Docs**: https://sensoai.mintlify.app/introduction
- **Full Docs Index**: https://sensoai.mintlify.app/llms-full.txt

---

## GEO Platform API (apiv2)

### POST /evaluate
Runs conversation-level diagnostics to surface missing information, measure citation accuracy, and link outcomes to your identity graph.

**Endpoint**: `POST https://apiv2.senso.ai/evaluate`

**Headers**:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "best CRM software",
  "brand": "your-brand",
  "network": "chatgpt"
}
```

**Parameters**:
| Parameter | Type   | Description |
|-----------|--------|-------------|
| `query`   | string | The search query / prompt to evaluate (real user intent) |
| `brand`   | string | Your brand name to track |
| `network` | string | AI platform to query: `"chatgpt"`, `"perplexity"`, `"gemini"`, etc. |

**Response** (inferred from documentation):
- Brand mention presence/absence
- Citation accuracy metrics
- Share of voice data
- Sentiment analysis
- Competitive visibility scores
- Quality percentage scores

**Key Metrics Tracked**:
- GEO Share of Voice (SoV)
- GEO Authority Index
- Competitive visibility scores per engine/region
- Citation frequency
- Mention accuracy vs. ground truth

### POST /remediate
Generates agent-ready content based on ground-truth data to improve mentions, share of voice, and conversion performance.

**Endpoint**: `POST https://apiv2.senso.ai/remediate`

**Headers**:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "context": "your ground truth data",
  "optimize_for": "mentions",
  "target_networks": ["chatgpt", "perplexity"]
}
```

**Parameters**:
| Parameter          | Type     | Description |
|-------------------|----------|-------------|
| `context`         | string   | Ground truth data to base content on |
| `optimize_for`    | string   | Optimization target: `"mentions"`, `"share_of_voice"`, `"conversions"` |
| `target_networks` | string[] | AI platforms to optimize for |

---

## Context OS SDK API (sdk.senso.ai)

### Authentication

**Header**: `X-API-Key: tgr_live_a1b2c3d4e5...` or `X-API-Key: tgr_test_a1b2c3d4e5...`

- API keys generated internally and emailed to authorized contacts
- Use `tgr_test_...` keys for testing, `tgr_live_...` for production
- Store in environment variables or secret managers
- No OAuth flows or token refresh needed
- Environment variable: `API_KEY_USER_LOOKUP`

**Error Codes**:
| Status | Error Type |
|--------|-----------|
| 400 | BadRequestError |
| 401 | AuthenticationError |
| 403 | PermissionDeniedError |
| 404 | NotFoundError |
| 429 | RateLimitError |
| 500+ | InternalServerError |

### Content Management

#### POST /content/raw - Ingest Raw Text
```
POST https://sdk.senso.ai/api/v1/content/raw
```
```json
{
  "title": "Brand Guidelines 2025",
  "summary": "Official brand positioning and messaging",
  "text": "Markdown formatted content here..."
}
```
**Response**: `202 Accepted` with `{"id": "content_id"}`

#### POST /content/file - Upload File
```
POST https://sdk.senso.ai/api/v1/content/file
Content-Type: multipart/form-data
```
- Accepts: PDF, DOCX, TXT
- Max size: 20MB
- Response: `202 Accepted` with `{"id": "content_id"}`

#### GET /content - List Content
```
GET https://sdk.senso.ai/api/v1/content?limit=100&offset=0
```
Returns paginated items with `processing_status` and `created_at`.

#### GET /content/{content_id} - Get Content Details
Check `processing_status`: `completed`, `failed`, `processing`, `unknown`

#### PUT /content/raw/{content_id} - Full Update
#### PATCH /content/raw/{content_id} - Partial Update
#### PUT /content/file/{content_id} - Replace File
#### PATCH /content/file/{content_id} - Update File
#### DELETE /content/{content_id} - Delete Content

### Search & Query

#### POST /search - Natural Language Search
```
POST https://sdk.senso.ai/api/v1/search
```
```json
{
  "query": "What is our refund policy?",
  "max_results": 10
}
```
**Response** (`200 OK`):
```json
{
  "answer": "AI-generated answer with citations...",
  "processing_time_ms": 1234,
  "total_results": 5
}
```

### Content Generation

#### POST /generate - Generate from Knowledge Base
```
POST https://sdk.senso.ai/api/v1/generate
```
```json
{
  "content_type": "product overview",
  "instructions": "Write a comparison guide",
  "save": true,
  "max_results": 15
}
```
**Response** (`200 OK`):
```json
{
  "generated_text": "Generated content...",
  "processing_time_ms": 2000,
  "sources": [
    {
      "content_id": "abc123",
      "chunk_text": "relevant excerpt",
      "relevance": 0.95,
      "title": "Source Document"
    }
  ]
}
```

#### POST /generate/prompt - Generate with Prompt & Template
```
POST https://sdk.senso.ai/api/v1/generate/prompt
```
```json
{
  "prompt_id": "prompt_abc123",
  "template_id": "template_xyz789",
  "content_type": "FAQ",
  "category_id": "cat_001",
  "topic_id": "topic_001",
  "max_results": 10,
  "save": true
}
```

### Prompts Management

#### POST /prompts - Create Prompt
```json
{
  "name": "Brand FAQ Generator",
  "text": "Generate {{count}} frequently asked questions about {{topic}} for our brand."
}
```
Supports `{{variable}}` substitution syntax.

#### GET /prompts?limit=10 - List Prompts
#### GET /prompts/{prompt_id} - Get Prompt
#### PUT /prompts/{prompt_id} - Update Prompt
#### PATCH /prompts/{prompt_id} - Partial Update
#### DELETE /prompts/{prompt_id} - Delete Prompt

### Templates Management

#### POST /templates - Create Template
```json
{
  "name": "JSON FAQ Template",
  "text": "{\"questions\": [{{questions}}]}",
  "output_type": "json"
}
```

**Template Response Schema**:
```json
{
  "template_id": "uuid",
  "name": "string",
  "text": "string",
  "output_type": "json | text",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "deleted_at": "ISO-8601 or null"
}
```

#### GET /templates?limit=10&offset=0 - List Templates
#### GET /templates/{template_id} - Get Template
#### PUT /templates/{template_id} - Update Template
#### PATCH /templates/{template_id} - Partial Update
#### DELETE /templates/{template_id} - Delete Template

### Categories & Topics

#### POST /categories - Create Category
```json
{
  "name": "Product Information",
  "description": "All product-related knowledge"
}
```

#### POST /categories/batch-create - Batch Create with Topics
#### GET /categories - List (paginated)
#### GET /categories/all - Get All with Topics
#### GET /categories/{category_id} - Get Category
#### PUT /categories/{category_id} - Update
#### PATCH /categories/{category_id} - Partial Update
#### DELETE /categories/{category_id} - Delete (cascades to topics)

#### POST /categories/{category_id}/topics - Create Topic
#### POST /categories/{category_id}/topics/batch-create - Batch Create
#### GET /categories/{category_id}/topics - List Topics
#### GET /categories/{category_id}/topics/{topic_id} - Get Topic
#### PUT /categories/{category_id}/topics/{topic_id} - Update
#### PATCH /categories/{category_id}/topics/{topic_id} - Partial Update
#### DELETE /categories/{category_id}/topics/{topic_id} - Delete

### Rules Engine

Rules allow you to flag content that matches specific patterns or values.

#### POST /rules - Create Rule
```
POST https://sdk.senso.ai/api/v1/rules
```
```json
{
  "name": "Brand Misrepresentation Detector",
  "type": "keyword",
  "target": "response"
}
```

#### POST /rules/{rule_id}/values - Add Rule Values
```json
{
  "value": "incorrect brand claim"
}
```
Returns `rule_value_id` for use with triggers.

### Webhooks

Register external endpoints to receive notifications.

#### POST /webhooks - Register Webhook
```
POST https://sdk.senso.ai/api/v1/webhooks
```
```json
{
  "name": "Brand Alert Webhook",
  "url": "https://your-app.com/webhook/brand-alert",
  "auth": {
    "type": "bearer",
    "token": "your-webhook-secret"
  }
}
```

### Triggers

Link rules to webhooks so detections fire automated actions.

#### POST /triggers - Create Trigger
```
POST https://sdk.senso.ai/api/v1/triggers
```
```json
{
  "name": "Misrepresentation Alert",
  "rule_id": "rule_abc123",
  "rule_value_id": "rv_xyz789",
  "webhook_id": "wh_def456"
}
```

**Flow**: Rule detection -> Trigger fires -> Webhook called -> Your app responds

---

## Python SDK

### Installation
```bash
pip install --pre senso_developers
```

### Package Info
- **PyPI**: https://pypi.org/project/senso-developers/
- **Version**: 0.0.1a2 (pre-release)
- **License**: Apache-2.0
- **Python**: 3.8+
- **HTTP Client**: httpx
- **Generated via**: Stainless API framework

### Basic Usage
```python
from senso_developers import SensoDevelopers

client = SensoDevelopers()
org = client.orgs.create(name="my-org")
```

### Async Usage
```python
from senso_developers import AsyncSensoDevelopers

client = AsyncSensoDevelopers()
org = await client.orgs.create(name="my-org")
```

### Key Features
- Type-safe requests using TypedDicts
- Pydantic response models with `.to_json()`, `.to_dict()`
- Automatic retry (2 retries by default)
- Configurable timeout (default: 60s)
- Raw response access
- Streaming support

### Environment Variables
- `API_KEY_USER_LOOKUP` - API key
- `SENSO_DEVELOPERS_LOG` - Logging level
- `SENSO_DEVELOPERS_BASE_URL` - Base URL override

---

## Platform Capabilities (Non-API)

### Monitoring Scale
- 25+ AI platforms monitored
- 500+ brand networks tracked
- 10K+ questions analyzed daily

### GEO Metrics
- **Mention Rate**: How often brand appears in AI answers
- **Share of Voice**: Brand prominence vs. competitors in a topic
- **Citation Frequency**: How often your domains are cited as sources
- **Accuracy Score**: How well AI descriptions match ground truth
- **Sentiment**: Favorable vs. unfavorable framing
- **Quality %**: Overall content effectiveness

### Governance Features
- Role-based access controls
- Full audit trails
- Versioning and rollback
- GDPR/CCPA compliance-ready
- Review/approval workflows

### Content Remediation Workflow
1. **Benchmark** - Establish baseline visibility
2. **Diagnose** - Identify gaps and inaccuracies
3. **Optimize** - Generate corrected content
4. **Monitor** - Track changes across platforms
5. **Iterate** - Continuously improve

---

## Pagination (All List Endpoints)

```
?limit=10&offset=0
```
- `limit`: 1-100 (default: 10)
- `offset`: >= 0 (default: 0)

## Standard Error Response
```json
{
  "error": "Human-readable error description"
}
```

## HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200  | OK |
| 201  | Created |
| 202  | Accepted (async processing) |
| 204  | No Content (successful delete) |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 409  | Conflict |
| 429  | Rate Limited |
| 500  | Internal Server Error |

---

## BrandGuard Integration Strategy

### Core Flow
1. **Ingest** brand ground-truth data via `/content/raw` or `/content/file`
2. **Organize** with `/categories` and `/topics`
3. **Evaluate** brand representation via `POST /evaluate` (apiv2)
4. **Detect** misrepresentation using Rules Engine (`/rules`, `/triggers`, `/webhooks`)
5. **Remediate** with `POST /remediate` (apiv2) or `/generate` (SDK)
6. **Monitor** continuously for changes

### Key APIs for BrandGuard
| Feature | API | Endpoint |
|---------|-----|----------|
| Brand Evaluation | GEO (apiv2) | `POST /evaluate` |
| Content Remediation | GEO (apiv2) | `POST /remediate` |
| Knowledge Ingestion | SDK | `POST /content/raw` |
| AI Search | SDK | `POST /search` |
| Content Generation | SDK | `POST /generate` |
| Misrepresentation Rules | SDK | `POST /rules`, `/triggers`, `/webhooks` |
| Prompt Management | SDK | `POST /prompts` |
| Template Management | SDK | `POST /templates` |

### Networks/Platforms Supported
- ChatGPT
- Gemini
- Perplexity
- Claude
- And 20+ more AI platforms

---

## Documentation Links
- **SDK Docs (Mintlify)**: https://sensoai.mintlify.app/introduction
- **Full API Index**: https://sensoai.mintlify.app/llms-full.txt
- **GEO Platform**: https://geo.senso.ai/
- **About Page**: https://www.senso.ai/about
- **FAQs**: https://www.senso.ai/faqs
- **Auth-Protected Docs**: https://docs.senso.ai/api-reference/introduction
- **PyPI Package**: https://pypi.org/project/senso-developers/
- **Hackathon**: https://mcp-aws-enterprise-agents.devpost.com/
