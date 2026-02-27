/** API client for monitoring endpoints (Yutori scouts) */
import { api } from "@/lib/api";
import type { Scout, ScoutUpdate } from "@/types";

// ── Start Monitoring ────────────────────────────────────────────

export interface StartMonitoringRequest {
  brand_id: string;
  brand_name: string;
  interval?: number;
  webhook_url?: string;
}

export async function startMonitoring(data: StartMonitoringRequest) {
  return api.post<{ scout_id: string; status: string }>(
    "/monitoring/start",
    data
  );
}

// ── Stop Monitoring ─────────────────────────────────────────────

export async function stopMonitoring(scoutId: string) {
  return api.post<{ status: string }>("/monitoring/stop", {
    scout_id: scoutId,
  });
}

// ── Monitoring Status ───────────────────────────────────────────

export async function getMonitoringStatus() {
  return api.get<{ scouts: Scout[] }>("/monitoring/status");
}

// ── Scout Updates ───────────────────────────────────────────────

export async function getScoutUpdates(scoutId: string, pageSize = 20) {
  return api.get<{ updates: ScoutUpdate[]; total_updates: number }>(
    `/monitoring/scouts/${scoutId}/updates?page_size=${pageSize}`
  );
}

// ── Delete Scout ────────────────────────────────────────────────

export async function deleteScout(scoutId: string) {
  return api.delete<{ status: string }>(
    `/monitoring/scouts/${scoutId}`
  );
}

// ── Web Search (Tavily — search router) ─────────────────────────

export async function webSearch(
  query: string,
  maxResults = 10,
  options?: {
    topic?: string;
    search_depth?: string;
    time_range?: string;
    include_domains?: string[];
    exclude_domains?: string[];
  }
) {
  return api.post("/search/web", {
    query,
    max_results: maxResults,
    ...options,
  });
}
