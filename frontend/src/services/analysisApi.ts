/** API client for analysis endpoints (Senso, Modulate) */
import { api } from "@/lib/api";

// ── Evaluate (Senso GEO) ────────────────────────────────────────

export interface EvaluateRequest {
  brand_id: string;
  query: string;
  platform: string;
}

export interface EvaluateResponse {
  accuracy_score: number;
  citations: unknown[];
  missing_info: unknown[];
}

export async function evaluateContent(data: EvaluateRequest) {
  return api.post<EvaluateResponse>("/evaluate", data);
}

// ── Remediate (Senso GEO) ───────────────────────────────────────

export interface RemediateRequest {
  mention_id: string;
  brand_id: string;
}

export interface RemediateResponse {
  correction_strategy: string;
  optimized_content: string;
}

export async function remediateContent(data: RemediateRequest) {
  return api.post<RemediateResponse>("/remediate", data);
}

// ── Content Ingest (Senso SDK) ──────────────────────────────────

export interface IngestContentRequest {
  brand_id: string;
  content: string;
  title: string;
}

export interface IngestContentResponse {
  content_id: string;
  status: string;
}

export async function ingestContent(data: IngestContentRequest) {
  return api.post<IngestContentResponse>("/content/ingest", data);
}

// ── Content Generate (Senso SDK) ────────────────────────────────

export interface GenerateContentRequest {
  brand_id: string;
  mention_id: string;
  format: "blog_post" | "faq" | "social_media";
}

export interface GenerateContentResponse {
  content: string;
  format: string;
}

export async function generateContent(data: GenerateContentRequest) {
  return api.post<GenerateContentResponse>("/content/generate", data);
}

// ── Content Search (Senso SDK) ──────────────────────────────────

export interface SearchContentRequest {
  brand_id: string;
  query: string;
}

export interface SearchResult {
  content: string;
  relevance: number;
}

export interface SearchContentResponse {
  results: SearchResult[];
}

export async function searchContent(data: SearchContentRequest) {
  return api.post<SearchContentResponse>("/content/search", data);
}

// ── Rules Setup (Senso SDK) ─────────────────────────────────────

export interface SetupRulesRequest {
  brand_id: string;
  rule_name: string;
  conditions: Record<string, unknown>;
  webhook_url: string;
}

export interface SetupRulesResponse {
  rule_id: string;
  trigger_id: string;
  status: string;
}

export async function setupRules(data: SetupRulesRequest) {
  return api.post<SetupRulesResponse>("/rules/setup", data);
}

// ── Audio Analysis (Modulate Velma-2) ───────────────────────────

export interface ModulateUtterance {
  utterance_uuid: string;
  text: string;
  start_ms: number;
  duration_ms: number;
  speaker: number;
  language: string;
  emotion: string;
  accent: string;
}

export interface AudioAnalysisResult {
  text: string;
  duration_ms: number;
  brand_mentions: ModulateUtterance[];
  total_mentions: number;
  all_utterances: ModulateUtterance[];
}

export async function analyzeAudio(
  file: File,
  brandName: string,
  options: { speakerDiarization?: boolean; emotionSignal?: boolean; fastEnglish?: boolean } = {}
): Promise<AudioAnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  form.append("brand_name", brandName);
  form.append("speaker_diarization", String(options.speakerDiarization ?? true));
  form.append("emotion_signal", String(options.emotionSignal ?? true));
  form.append("fast_english", String(options.fastEnglish ?? false));

  return api.postForm<AudioAnalysisResult>("/audio", form);
}
