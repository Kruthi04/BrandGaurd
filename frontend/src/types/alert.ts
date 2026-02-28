export type AlertSeverity = "critical" | "high" | "medium" | "low";
export type AlertStatus = "open" | "investigating" | "corrected" | "dismissed";

export interface Alert {
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
