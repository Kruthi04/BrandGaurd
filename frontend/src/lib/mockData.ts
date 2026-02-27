/** Mock data for BrandGuard — used when VITE_USE_MOCKS=true or API is unavailable */

export const MOCK_BRAND_ID = "brand-acme-corp";
export const MOCK_BRAND_NAME = "Acme Corp";

// ── Brand health ──────────────────────────────────────────────────────────────

export const mockBrandHealth = {
  overall_accuracy: 73.2,
  reputation_score: 73,
  total_mentions: 47,
  active_scouts: 3,
  by_platform: {
    chatgpt:    { accuracy: 68.5, mentions: 15, trend: "down"   as const },
    claude:     { accuracy: 82.1, mentions: 12, trend: "up"     as const },
    perplexity: { accuracy: 71.0, mentions: 10, trend: "stable" as const },
    gemini:     { accuracy: 65.0, mentions: 10, trend: "down"   as const },
  },
};

// ── Accuracy trend (7 days) ───────────────────────────────────────────────────

export const mockTrendData = [
  { date: "Feb 21", chatgpt: 64, claude: 78, perplexity: 67, gemini: 60 },
  { date: "Feb 22", chatgpt: 62, claude: 79, perplexity: 70, gemini: 58 },
  { date: "Feb 23", chatgpt: 67, claude: 80, perplexity: 68, gemini: 61 },
  { date: "Feb 24", chatgpt: 65, claude: 81, perplexity: 72, gemini: 63 },
  { date: "Feb 25", chatgpt: 69, claude: 83, perplexity: 71, gemini: 65 },
  { date: "Feb 26", chatgpt: 67, claude: 82, perplexity: 70, gemini: 64 },
  { date: "Feb 27", chatgpt: 69, claude: 82, perplexity: 71, gemini: 65 },
];

// ── Alerts ────────────────────────────────────────────────────────────────────

export type AlertSeverity = "critical" | "high" | "medium" | "low";
export type AlertStatus = "open" | "investigating" | "corrected" | "dismissed";

export interface MockAlert {
  id: string;
  severity: AlertSeverity;
  platform: string;
  claim: string;
  context: string;
  accuracy_score: number;
  status: AlertStatus;
  detected_at: string;
  source_url: string;
  suggested_correction: string;
}

export const mockAlerts: MockAlert[] = [
  {
    id: "alert-1",
    severity: "critical",
    platform: "Perplexity",
    claim: "Acme Corp was founded in 1990 by John Smith",
    context:
      "When asked about Acme Corp's history, Perplexity stated it was founded in 1990 by John Smith, with headquarters in New York.",
    accuracy_score: 24,
    status: "open",
    detected_at: "2026-02-27T08:12:00Z",
    source_url: "https://perplexity.ai",
    suggested_correction:
      "Acme Corp was founded in 2005 by Jane Doe, headquartered in San Francisco.",
  },
  {
    id: "alert-2",
    severity: "high",
    platform: "ChatGPT",
    claim: "Acme Corp acquired TechStart Inc. for $2B in 2022",
    context:
      "ChatGPT claimed Acme Corp made a major acquisition of TechStart Inc. for $2 billion in 2022.",
    accuracy_score: 38,
    status: "investigating",
    detected_at: "2026-02-26T14:33:00Z",
    source_url: "https://chat.openai.com",
    suggested_correction:
      "Acme Corp has not made any acquisitions exceeding $500M. The TechStart acquisition is fictional.",
  },
  {
    id: "alert-3",
    severity: "high",
    platform: "Gemini",
    claim: "Acme Corp's revenue declined 40% in 2025",
    context:
      "Gemini provided financial data suggesting Acme Corp experienced a sharp revenue decline in 2025.",
    accuracy_score: 41,
    status: "open",
    detected_at: "2026-02-26T09:45:00Z",
    source_url: "https://gemini.google.com",
    suggested_correction:
      "Acme Corp's revenue grew 15% in 2025, reaching $4.2B in annual revenue.",
  },
  {
    id: "alert-4",
    severity: "medium",
    platform: "Claude",
    claim: "Acme Corp's CEO is Robert Johnson",
    context: "Claude incorrectly identified Robert Johnson as the current CEO of Acme Corp.",
    accuracy_score: 55,
    status: "corrected",
    detected_at: "2026-02-25T11:20:00Z",
    source_url: "https://claude.ai",
    suggested_correction:
      "Acme Corp's CEO is Sarah Chen, who has held the position since 2019.",
  },
  {
    id: "alert-5",
    severity: "low",
    platform: "ChatGPT",
    claim: "Acme Corp operates in 15 countries",
    context: "ChatGPT slightly underreported Acme Corp's international presence.",
    accuracy_score: 72,
    status: "dismissed",
    detected_at: "2026-02-24T16:08:00Z",
    source_url: "https://chat.openai.com",
    suggested_correction: "Acme Corp operates in 23 countries across 6 continents.",
  },
];

// ── Graph data ────────────────────────────────────────────────────────────────

export const mockGraphData = {
  nodes: [
    { id: "brand-1",            label: "Acme Corp",       type: "brand"      },
    { id: "platform-chatgpt",   label: "ChatGPT",         type: "platform"   },
    { id: "platform-claude",    label: "Claude",          type: "platform"   },
    { id: "platform-perplexity",label: "Perplexity",      type: "platform"   },
    { id: "platform-gemini",    label: "Gemini",          type: "platform"   },
    { id: "mention-1",          label: "Founded 1990",    type: "mention"    },
    { id: "mention-2",          label: "TechStart Acq.",  type: "mention"    },
    { id: "mention-3",          label: "Revenue −40%",    type: "mention"    },
    { id: "mention-4",          label: "CEO Mismatch",    type: "mention"    },
    { id: "source-1",           label: "wikipedia.org",   type: "source"     },
    { id: "source-2",           label: "crunchbase.com",  type: "source"     },
    { id: "correction-1",       label: "Founding Fix",    type: "correction" },
  ],
  // Note: react-force-graph-2d uses "links" not "edges"
  links: [
    { source: "mention-1",          target: "brand-1",             relationship: "ABOUT"    },
    { source: "mention-1",          target: "platform-perplexity", relationship: "FOUND_ON" },
    { source: "mention-2",          target: "brand-1",             relationship: "ABOUT"    },
    { source: "mention-2",          target: "platform-chatgpt",    relationship: "FOUND_ON" },
    { source: "mention-3",          target: "brand-1",             relationship: "ABOUT"    },
    { source: "mention-3",          target: "platform-gemini",     relationship: "FOUND_ON" },
    { source: "mention-4",          target: "brand-1",             relationship: "ABOUT"    },
    { source: "mention-4",          target: "platform-claude",     relationship: "FOUND_ON" },
    { source: "source-1",           target: "platform-perplexity", relationship: "FEEDS"    },
    { source: "source-2",           target: "platform-chatgpt",    relationship: "FEEDS"    },
    { source: "correction-1",       target: "mention-1",           relationship: "CORRECTS" },
  ],
};

// ── Scouts ────────────────────────────────────────────────────────────────────

export const mockScouts = [
  {
    id: "s1",
    display_name: "Acme Corp — AI Monitors",
    query: "Monitor Acme Corp mentions on ChatGPT, Claude, Gemini, Perplexity",
    status: "active" as const,
    brand_id: "brand-1",
    output_interval: 3600,
    created_at: "2026-02-20T09:00:00Z",
    next_run: "2026-02-27T09:00:00Z",
  },
  {
    id: "s2",
    display_name: "Acme Corp — Social Media",
    query: "Track Acme Corp brand mentions on social media platforms",
    status: "active" as const,
    brand_id: "brand-1",
    output_interval: 7200,
    created_at: "2026-02-21T10:00:00Z",
    next_run: "2026-02-27T10:00:00Z",
  },
  {
    id: "s3",
    display_name: "Acme Corp — News & Press",
    query: "Monitor news articles and press releases about Acme Corp",
    status: "paused" as const,
    brand_id: "brand-1",
    output_interval: 86400,
    created_at: "2026-02-22T11:00:00Z",
  },
];

// ── Corrections ───────────────────────────────────────────────────────────────

export type CorrectionType   = "blog" | "faq" | "social" | "press";
export type CorrectionStatus = "draft" | "published";

export interface MockCorrection {
  id: string;
  type: CorrectionType;
  status: CorrectionStatus;
  platform: string;
  claim: string;
  correction: string;
  created_at: string;
  published_at?: string;
}

export const mockCorrections: MockCorrection[] = [
  {
    id: "c1",
    type: "blog",
    status: "published",
    platform: "Perplexity",
    claim: "Acme Corp was founded in 1990",
    correction:
      "Acme Corp was established in 2005 by Jane Doe with a vision to revolutionize enterprise software. The company has grown from a 5-person startup to a 10,000-employee global organization.",
    created_at: "2026-02-25T10:00:00Z",
    published_at: "2026-02-25T14:30:00Z",
  },
  {
    id: "c2",
    type: "faq",
    status: "draft",
    platform: "ChatGPT",
    claim: "Acme Corp acquired TechStart Inc. for $2B",
    correction:
      "Acme Corp has not acquired TechStart Inc. Our growth strategy focuses on organic expansion and strategic partnerships. Our largest acquisition to date was DataFlow Analytics in 2021 for $120M.",
    created_at: "2026-02-26T15:00:00Z",
  },
  {
    id: "c3",
    type: "social",
    status: "published",
    platform: "Claude",
    claim: "Acme Corp CEO is Robert Johnson",
    correction:
      "Sarah Chen has been leading Acme Corp as CEO since 2019, bringing 20+ years of enterprise software experience. Under her leadership, revenue has grown 3x.",
    created_at: "2026-02-24T09:00:00Z",
    published_at: "2026-02-24T12:00:00Z",
  },
];
