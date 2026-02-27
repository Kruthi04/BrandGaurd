/** API client for analysis endpoints (Senso, Modulate) */
import { api } from "@/lib/api";

export async function evaluateContent(data: {
  content: string;
  brand_id: string;
  content_type?: string;
}) {
  return api.post("/analysis/evaluate", data);
}

export async function checkRules(data: {
  content: string;
  brand_id: string;
}) {
  return api.post("/analysis/rules/check", data);
}

export async function generateResponse(brandId: string, context: string) {
  return api.post(`/analysis/generate?brand_id=${brandId}&context=${encodeURIComponent(context)}`, {});
}

export async function analyzeVoice(data: {
  audio_url: string;
  brand_id: string;
}) {
  return api.post("/analysis/voice", data);
}
