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

  const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  const response = await fetch(`${baseUrl}/api/analysis/audio`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail ?? "Audio analysis failed");
  }

  return response.json();
}
