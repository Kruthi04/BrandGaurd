export type CorrectionType = "blog" | "faq" | "social" | "press";
export type CorrectionStatus = "draft" | "published";

export interface Correction {
  id: string;
  type: CorrectionType;
  status: CorrectionStatus;
  platform: string;
  claim: string;
  correction: string;
  created_at: string;
  published_at?: string;
}
