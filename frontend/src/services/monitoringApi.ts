/** API client for monitoring endpoints (Yutori scouts, Tavily search) */
import { api } from "@/lib/api";
import type { Scout, ScoutUpdate } from "@/types";

export async function createScout(data: {
  query: string;
  brand_name: string;
  output_interval?: number;
}) {
  return api.post<Scout>("/monitoring/scouts", data);
}

export async function listScouts() {
  return api.get<{ scouts: Scout[]; total: number }>("/monitoring/scouts");
}

export async function getScoutUpdates(scoutId: string, pageSize = 20) {
  return api.get<{ updates: ScoutUpdate[]; total_updates: number }>(
    `/monitoring/scouts/${scoutId}/updates?page_size=${pageSize}`
  );
}

export async function deleteScout(scoutId: string) {
  return api.delete<{ message: string }>(`/monitoring/scouts/${scoutId}`);
}

export async function webSearch(query: string, maxResults = 10) {
  return api.post("/monitoring/search", { query, max_results: maxResults });
}
