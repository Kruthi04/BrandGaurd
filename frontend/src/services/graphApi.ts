/** API client for graph endpoints (Neo4j) */
import { api } from "@/lib/api";
import type { GraphData } from "@/types";

export async function getEntities(entityType?: string, limit = 50) {
  const params = new URLSearchParams();
  if (entityType) params.set("entity_type", entityType);
  params.set("limit", String(limit));
  return api.get(`/graph/entities?${params}`);
}

export async function addEntity(data: {
  name: string;
  entity_type: string;
  properties?: Record<string, unknown>;
}) {
  return api.post("/graph/entities", data);
}

export async function getBrandNetwork(brandId: string, depth = 2) {
  return api.get<GraphData>(`/graph/brand/${brandId}/network?depth=${depth}`);
}

export async function getThreats(brandId?: string) {
  const params = brandId ? `?brand_id=${brandId}` : "";
  return api.get(`/graph/threats${params}`);
}
