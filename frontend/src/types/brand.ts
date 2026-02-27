/** Brand profile */
export interface Brand {
  id: string;
  name: string;
  description?: string;
  keywords: string[];
  domains: string[];
  created_at: string;
  updated_at: string;
  reputation_score?: number;
  active_scouts: number;
  total_mentions: number;
}

export interface BrandCreate {
  name: string;
  description?: string;
  keywords: string[];
  domains: string[];
}
