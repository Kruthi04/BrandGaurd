/** Threat severity levels */
export type ThreatLevel = "low" | "medium" | "high" | "critical";

/** A reputation threat */
export interface Threat {
  id: string;
  brand_id: string;
  title: string;
  description: string;
  source_url?: string;
  threat_level: ThreatLevel;
  detected_at: string;
  resolved: boolean;
  resolved_at?: string;
  related_mentions: string[];
}
