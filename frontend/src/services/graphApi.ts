/** API client for graph endpoints (Neo4j) */
import { api } from "@/lib/api";
import type { GraphData } from "@/types";

// ── Schema Init ─────────────────────────────────────────────────

export async function initSchema(confirm = true) {
  return api.post<{ status: string; message: string }>("/graph/init", {
    confirm,
  });
}

// ── Store Mention ───────────────────────────────────────────────

export interface StoreMentionRequest {
  brand_id: string;
  brand_name?: string;
  platform: string;
  claim: string;
  accuracy_score: number;
  severity?: string;
  detected_at?: string;
  source_urls?: string[];
}

export async function storeMention(data: StoreMentionRequest) {
  return api.post("/graph/mentions", data);
}

// ── Store Correction ────────────────────────────────────────────

export interface StoreCorrectionRequest {
  mention_id: string;
  content?: string;
  correction_type?: string;
  status?: string;
  created_at?: string;
}

export async function storeCorrection(data: StoreCorrectionRequest) {
  return api.post("/graph/corrections", data);
}

// ── Brand Health ────────────────────────────────────────────────

export async function getBrandHealth(brandId: string) {
  return api.get(`/graph/brand/${brandId}/health`);
}

// ── Brand Sources ───────────────────────────────────────────────

export async function getBrandSources(brandId: string, limit = 20) {
  return api.get(`/graph/brand/${brandId}/sources?limit=${limit}`);
}

// ── Brand Network (graph visualization) ─────────────────────────

export async function getBrandNetwork(brandId: string) {
  return api.get<GraphData>(`/graph/brand/${brandId}/network`);
}
