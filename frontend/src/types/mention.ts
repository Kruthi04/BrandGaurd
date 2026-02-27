/** Sentiment categories for brand mentions */
export type Sentiment = "positive" | "neutral" | "negative" | "critical";

/** A tracked brand mention */
export interface Mention {
  id: string;
  brand_id: string;
  source_url: string;
  content: string;
  platform: string;
  author?: string;
  detected_at: string;
  sentiment: Sentiment;
  compliance_score?: number;
  threat_level?: string;
  scout_id?: string;
}
