/** A Yutori monitoring scout */
export interface Scout {
  id: string;
  brand_id: string;
  query: string;
  display_name: string;
  status: "active" | "paused" | "done";
  output_interval: number;
  created_at: string;
  next_run?: string;
}

/** An update from a scout */
export interface ScoutUpdate {
  id: string;
  scout_id: string;
  content: string;
  citations: Citation[];
  created_at: string;
}

export interface Citation {
  id: string;
  url: string;
  preview_data?: Record<string, unknown>;
}
