# Tavily API Research - BrandGuard Project

## Overview

Tavily provides AI-optimized web search, extraction, crawling, mapping, and research APIs designed for RAG and agent workflows. All endpoints are REST-based with JSON request/response formats.

- **Base URL**: `https://api.tavily.com`
- **Auth**: Bearer token in header: `Authorization: Bearer tvly-YOUR_API_KEY`
- **Required Header**: `Content-Type: application/json`
- **Optional Header**: `X-Project-ID` (for multi-project tracking)
- **API Key Format**: `tvly-XXXXXXXXX` (obtained at https://app.tavily.com)
- **Free Tier**: 1,000 credits/month, no credit card required

---

## 1. Search API (`POST /search`)

**Purpose for BrandGuard**: Find source websites that AI models are citing about a brand. Detect where misinformation originates. Monitor brand mentions across the web.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `search_depth` | string | No | `"basic"` | `"basic"` (1 credit), `"advanced"` (2 credits), `"fast"`, `"ultra-fast"` (1 credit each) |
| `max_results` | integer | No | 5 | Number of results (0-20) |
| `topic` | string | No | `"general"` | `"general"`, `"news"`, `"finance"` |
| `time_range` | string | No | null | `"day"`, `"week"`, `"month"`, `"year"` |
| `start_date` | string | No | null | Format: `YYYY-MM-DD` |
| `end_date` | string | No | null | Format: `YYYY-MM-DD` |
| `include_answer` | bool/string | No | false | `true`/`false`, `"basic"`, `"advanced"` |
| `include_raw_content` | bool/string | No | false | `true`/`false`, `"markdown"`, `"text"` |
| `include_images` | boolean | No | false | Include image results |
| `include_image_descriptions` | boolean | No | false | Descriptions for images |
| `include_favicon` | boolean | No | false | Include favicon URLs |
| `include_domains` | array | No | [] | Whitelist (max 300 domains) |
| `exclude_domains` | array | No | [] | Blacklist (max 150 domains) |
| `country` | string | No | null | Boost results from country |
| `chunks_per_source` | integer | No | 3 | Content snippets per source (1-3, advanced only) |
| `auto_parameters` | boolean | No | false | Auto-configure query (2 credits) |
| `exact_match` | boolean | No | false | Exact phrase matching |
| `include_usage` | boolean | No | false | Credit usage info |

### Example Request

```json
POST https://api.tavily.com/search
Headers:
  Content-Type: application/json
  Authorization: Bearer tvly-YOUR_API_KEY

{
  "query": "BrandName AI reputation issues",
  "search_depth": "advanced",
  "max_results": 10,
  "topic": "news",
  "time_range": "month",
  "include_answer": true,
  "include_raw_content": "markdown",
  "include_domains": [],
  "exclude_domains": []
}
```

### Response Schema

```json
{
  "query": "string",
  "answer": "string (if include_answer=true)",
  "results": [
    {
      "title": "string",
      "url": "string",
      "content": "string (snippet)",
      "raw_content": "string (if include_raw_content=true)",
      "score": 0.81025416,
      "favicon": "string (if include_favicon=true)"
    }
  ],
  "images": [
    {
      "url": "string",
      "description": "string (if include_image_descriptions=true)"
    }
  ],
  "response_time": 1.67,
  "usage": { "credits": 1 },
  "request_id": "uuid-string"
}
```

### BrandGuard Use Cases

- Search for brand-related AI claims: `"What does [Brand] do?"` to see what sources appear
- Monitor news: topic=`"news"` with time_range=`"week"` for recent brand mentions
- Domain filtering: `include_domains` to check specific competitor/misinformation sites
- Answer generation: `include_answer=true` to see what AI-synthesized answers look like about the brand

---

## 2. Extract API (`POST /extract`)

**Purpose for BrandGuard**: Extract full content from URLs identified as misrepresenting a brand. Analyze the exact text and claims being made on specific pages.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `urls` | string/array | Yes | - | Single URL or list (max 20 URLs) |
| `query` | string | No | - | User intent for reranking chunks |
| `chunks_per_source` | integer | No | 3 | Chunks per source (1-5, requires query) |
| `extract_depth` | string | No | `"basic"` | `"basic"` or `"advanced"` |
| `include_images` | boolean | No | false | Include image URLs |
| `include_favicon` | boolean | No | false | Include favicon URL |
| `format` | string | No | `"markdown"` | `"markdown"` or `"text"` |
| `timeout` | number | No | - | Timeout in seconds (1.0-60.0) |
| `include_usage` | boolean | No | false | Credit usage data |

### Example Request

```json
POST https://api.tavily.com/extract
Headers:
  Content-Type: application/json
  Authorization: Bearer tvly-YOUR_API_KEY

{
  "urls": [
    "https://example.com/article-about-brand",
    "https://blog.example.com/brand-review"
  ],
  "query": "What claims does this page make about BrandName?",
  "chunks_per_source": 5,
  "extract_depth": "advanced",
  "format": "markdown"
}
```

### Response Schema

```json
{
  "results": [
    {
      "url": "string",
      "raw_content": "string (full extracted content)",
      "images": ["string"],
      "favicon": "string"
    }
  ],
  "failed_results": [
    {
      "url": "string",
      "error": "string"
    }
  ],
  "response_time": 0.02,
  "usage": { "credits": 1 },
  "request_id": "uuid-string"
}
```

### Credit Costs

- Basic: 1 credit per 5 successful URL extractions
- Advanced: 2 credits per 5 successful URL extractions
- Failed extractions: no charge

### BrandGuard Use Cases

- Extract full content from flagged URLs to analyze brand claims
- Query-based chunk reranking to focus on brand-relevant content
- Batch extract up to 20 URLs at once for efficiency
- Advanced depth for tables and embedded data (e.g., product comparison tables)

---

## 3. Map API (`POST /map`)

**Purpose for BrandGuard**: Discover all pages on a website that mention a brand. Build a site map of misrepresenting sources to understand the scope of misinformation.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Root URL to begin mapping |
| `instructions` | string | No | null | Natural language crawl guidance (2 credits/10 pages) |
| `max_depth` | integer | No | 1 | Traversal depth (1-5) |
| `max_breadth` | integer | No | 20 | Links per page level (1-500) |
| `limit` | integer | No | 50 | Total links to process (min 1) |
| `select_paths` | array | No | null | Regex patterns for URL path inclusion |
| `select_domains` | array | No | null | Regex for domain inclusion |
| `exclude_paths` | array | No | null | Regex for URL path exclusion |
| `exclude_domains` | array | No | null | Regex for domain exclusion |
| `allow_external` | boolean | No | true | Include external domain links |
| `timeout` | float | No | 150 | Wait time (10-150 seconds) |
| `include_usage` | boolean | No | false | Credit usage info |

### Example Request

```json
POST https://api.tavily.com/map
Headers:
  Content-Type: application/json
  Authorization: Bearer tvly-YOUR_API_KEY

{
  "url": "https://misleading-site.com",
  "instructions": "Find all pages mentioning BrandName",
  "max_depth": 3,
  "limit": 100
}
```

### Response Schema

```json
{
  "base_url": "string",
  "results": [
    "https://misleading-site.com/page1",
    "https://misleading-site.com/page2"
  ],
  "response_time": 1.23,
  "usage": { "credits": 1 },
  "request_id": "uuid-string"
}
```

### Credit Costs

- Without instructions: 1 credit per 10 successful pages
- With instructions: 2 credits per 10 successful pages

### BrandGuard Use Cases

- Map a suspicious website to find all brand-related pages
- Use `instructions` to guide crawler: "Find pages about [Brand]"
- Combine with Extract to get full content from discovered URLs
- `select_paths`/`exclude_paths` to focus on relevant sections

---

## 4. Crawl API (`POST /crawl`)

**Purpose for BrandGuard**: Combined Map + Extract in one call. Traverse a website and extract content from all discovered pages. Ideal for comprehensive site analysis of misrepresenting sources.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Root URL to crawl |
| `instructions` | string | No | null | Natural language guidance (increases cost) |
| `chunks_per_source` | integer | No | 3 | Content snippets per source (1-5, with instructions) |
| `max_depth` | integer | No | 1 | Crawl depth (1-5) |
| `max_breadth` | integer | No | 20 | Links per page level (1-500) |
| `limit` | integer | No | 50 | Total links to process (min 1) |
| `select_paths` | array | No | null | Regex for URL path inclusion |
| `select_domains` | array | No | null | Regex for domain inclusion |
| `exclude_paths` | array | No | null | Regex for URL path exclusion |
| `exclude_domains` | array | No | null | Regex for domain exclusion |
| `allow_external` | boolean | No | true | Include external links |
| `include_images` | boolean | No | false | Include images |
| `extract_depth` | string | No | `"basic"` | `"basic"` or `"advanced"` |
| `format` | string | No | `"markdown"` | `"markdown"` or `"text"` |
| `include_favicon` | boolean | No | false | Include favicons |
| `timeout` | float | No | 150 | Timeout (10-150 seconds) |
| `include_usage` | boolean | No | false | Credit usage info |

### Example Request

```json
POST https://api.tavily.com/crawl
Headers:
  Content-Type: application/json
  Authorization: Bearer tvly-YOUR_API_KEY

{
  "url": "https://misleading-blog.com",
  "instructions": "Find and extract all content about BrandName products",
  "max_depth": 2,
  "limit": 50,
  "extract_depth": "advanced",
  "format": "markdown"
}
```

### Response Schema

```json
{
  "base_url": "string",
  "results": [
    {
      "url": "string",
      "raw_content": "string (full extracted content)",
      "favicon": "string"
    }
  ],
  "response_time": 1.23,
  "usage": { "credits": 3 },
  "request_id": "uuid-string"
}
```

### Credit Costs

Combined mapping + extraction:
- 10 pages basic crawl = ~3 credits (1 map + 2 extract)
- With instructions and advanced: higher cost

### BrandGuard Use Cases

- One-call site analysis: crawl an entire misrepresenting site
- Instruction-guided crawling to focus on brand content
- Extract full page content for claim analysis
- Build comprehensive evidence database from problematic sources

---

## 5. Research API (`POST /research`) - BETA

**Purpose for BrandGuard**: Deep, end-to-end brand reputation analysis. Multi-search + analysis + synthesis into a comprehensive report with sources.

### Status: Private Beta

Access via waitlist at https://deepresearch.tavily.com/

### Key Features

- Multi-search: Performs multiple iterative searches automatically
- Analysis: Reasons over collected data
- Synthesis: Produces structured report with sources
- Streaming: Supports SSE (Server-Sent Events) for real-time updates
- Multi-agent coordination and deduplication

### Request (JavaScript SDK)

```javascript
const response = await tvly.research("Analyze brand reputation of [BrandName]", {
  model: "pro",          // "pro" or "mini"
  citationFormat: "apa", // Citation format
  stream: true           // Enable SSE streaming
});
```

### Retrieval

```javascript
const result = await tvly.getResearch(requestId);
// result.status, result.content, result.sources
```

### Credit Costs

- Model `pro`: 15-250 credits per request (dynamic)
- Model `mini`: 4-110 credits per request (dynamic)

### BrandGuard Use Cases

- Comprehensive brand reputation reports
- Automated research on how AI models perceive a brand
- Source gathering for brand citation analysis

---

## SDKs

### Python SDK

```bash
pip install tavily-python
```

```python
from tavily import TavilyClient, AsyncTavilyClient

# Synchronous
client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Or use environment variable TAVILY_API_KEY
client = TavilyClient()

# Async
async_client = AsyncTavilyClient(api_key="tvly-YOUR_API_KEY")
```

**Available Methods:**

| Method | Description |
|--------|-------------|
| `client.search(query, **kwargs)` | Web search |
| `client.get_search_context(query, max_tokens=4000)` | Search + format for RAG context |
| `client.qna_search(query)` | Concise Q&A answers |
| `client.extract(urls, **kwargs)` | Extract content from URLs |
| `client.crawl(url, **kwargs)` | Map + extract combined |
| `client.map(url, **kwargs)` | Discover site structure |
| `client.research(topic, **kwargs)` | Deep research reports |

### JavaScript/TypeScript SDK

```bash
npm install @tavily/core
```

```javascript
// CommonJS
const { tavily } = require("@tavily/core");

// ES Module
import { tavily } from "@tavily/core";

const tvly = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// All methods are async
await tvly.search(query, options);
await tvly.extract(urls);
await tvly.crawl(url, options);
await tvly.map(url, options);
await tvly.research(topic, options);
await tvly.getResearch(requestId);
```

**Supports**: CommonJS, ES Modules, TypeScript definitions included.

---

## Pricing & Credits

### Plans

| Plan | Monthly Credits | Cost | Per-Credit |
|------|----------------|------|------------|
| Researcher (Free) | 1,000 | $0 | - |
| Project | 4,000 | $30/mo | $0.0075 |
| Bootstrap | 15,000 | $100/mo | $0.0067 |
| Startup | 38,000 | $220/mo | $0.0058 |
| Growth | 100,000 | $500/mo | $0.005 |
| Pay-as-you-go | Per usage | - | $0.008 |
| Enterprise | Custom | Custom | Custom |

**Note**: Credits do NOT roll over month-to-month.

### Credit Costs Per Endpoint

| Endpoint | Basic | Advanced/With Instructions |
|----------|-------|---------------------------|
| Search | 1 credit/request | 2 credits/request |
| Extract | 1 credit/5 URLs | 2 credits/5 URLs |
| Map | 1 credit/10 pages | 2 credits/10 pages |
| Crawl | Map + Extract combined | Map + Extract combined |
| Research (pro) | 15-250 credits | - |
| Research (mini) | 4-110 credits | - |

### Rate Limits

| Environment | General Endpoints | Crawl Endpoint |
|-------------|------------------|----------------|
| Development | 100 RPM | 100 RPM |
| Production | 1,000 RPM | 100 RPM |

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request parameters |
| 401 | Missing or invalid API key |
| 403 | URL not supported |
| 429 | Rate limit exceeded |
| 432 | Plan usage limit exceeded |
| 433 | Pay-as-you-go limit exceeded |
| 500 | Server error |

---

## Environment Variables

```bash
# Required
TAVILY_API_KEY=tvly-YOUR_API_KEY

# Optional (for multi-project tracking)
TAVILY_PROJECT=your-project-id
```

---

## BrandGuard Integration Strategy

### Recommended Workflow

1. **Discovery Phase** (Search API)
   - Search for brand-related queries across web and news
   - Use `topic: "news"` and `time_range` for recent mentions
   - Use `include_answer: true` to see AI-synthesized narratives

2. **Source Mapping Phase** (Map API)
   - For flagged domains, map their site structure
   - Use `instructions` to focus on brand-relevant pages
   - Build a list of all URLs mentioning the brand

3. **Content Extraction Phase** (Extract API)
   - Extract full content from discovered URLs
   - Use `query` parameter for brand-relevant chunk reranking
   - Batch up to 20 URLs per request

4. **Deep Analysis Phase** (Crawl API)
   - For comprehensive site analysis, use crawl (map + extract)
   - Instruction-guided crawling for efficiency
   - Extract all brand claims from entire sites

5. **Report Generation Phase** (Research API - if available)
   - Generate comprehensive brand reputation reports
   - Multi-search synthesis for holistic analysis

### Hackathon Considerations

- Free tier gives 1,000 credits/month - sufficient for demo/prototype
- Basic search = 1 credit, so ~1,000 searches on free tier
- Extract is very efficient: 1 credit per 5 URLs (basic)
- Use `search_depth: "basic"` during development to conserve credits
- Switch to `"advanced"` for production/demo quality
- Crawl endpoint may be invite-only; fallback to Map + Extract separately

---

## References

- Official Docs: https://docs.tavily.com
- Python SDK: https://github.com/tavily-ai/tavily-python
- JavaScript SDK: https://github.com/tavily-ai/tavily-js
- PyPI: https://pypi.org/project/tavily-python/
- npm: https://www.npmjs.com/package/@tavily/core
- API Credits/Pricing: https://docs.tavily.com/documentation/api-credits
- Research Waitlist: https://deepresearch.tavily.com/
