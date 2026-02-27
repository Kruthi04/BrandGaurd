import { useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { analyzeAudio, type AudioAnalysisResult, type ModulateUtterance } from "@/services/analysisApi";

function formatMs(ms: number): string {
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function UtteranceRow({ u }: { u: ModulateUtterance }) {
  return (
    <li className="border-b pb-3 last:border-0 space-y-1">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm">{u.text}</p>
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {formatMs(u.start_ms)}
        </span>
      </div>
      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
        <span>Speaker {u.speaker}</span>
        {u.emotion && <span className="capitalize">{u.emotion}</span>}
        {u.accent && <span>{u.accent}</span>}
        {u.language && <span>{u.language.toUpperCase()}</span>}
      </div>
    </li>
  );
}

export default function AudioSources() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [brandName, setBrandName] = useState("");
  const [speakerDiarization, setSpeakerDiarization] = useState(true);
  const [emotionSignal, setEmotionSignal] = useState(true);
  const [fastEnglish, setFastEnglish] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AudioAnalysisResult | null>(null);
  const [showFull, setShowFull] = useState(false);

  async function handleAnalyze() {
    if (!selectedFile || !brandName.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeAudio(selectedFile, brandName.trim(), {
        speakerDiarization,
        emotionSignal,
        fastEnglish,
      });
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Audio analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          Audio Sources
          <span className="text-xs font-normal text-muted-foreground">powered by Modulate Velma-2</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Upload a podcast, video, or audio recording to detect brand mentions with speaker, emotion, and accent data.
        </p>

        {/* File picker */}
        <div className="flex items-center gap-3">
          <input
            ref={fileRef}
            type="file"
            accept="audio/*,video/mp4,video/quicktime,video/webm"
            className="hidden"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          />
          <Button variant="outline" onClick={() => fileRef.current?.click()}>
            Choose file
          </Button>
          <span className="text-sm text-muted-foreground truncate max-w-xs">
            {selectedFile ? selectedFile.name : "No file selected"}
          </span>
        </div>

        {/* Brand name */}
        <input
          className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Brand name to search for"
          value={brandName}
          onChange={(e) => setBrandName(e.target.value)}
        />

        {/* Options */}
        <div className="flex flex-wrap gap-4 text-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={speakerDiarization}
              onChange={(e) => setSpeakerDiarization(e.target.checked)}
            />
            Speaker diarization
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={emotionSignal}
              onChange={(e) => setEmotionSignal(e.target.checked)}
            />
            Emotion detection
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={fastEnglish}
              onChange={(e) => setFastEnglish(e.target.checked)}
            />
            Fast English model
          </label>
        </div>

        <Button
          onClick={handleAnalyze}
          disabled={loading || !selectedFile || !brandName.trim()}
        >
          {loading ? "Analyzing…" : "Analyze Audio"}
        </Button>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {result && (
          <div className="space-y-3">
            {/* Summary bar */}
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">
                {result.total_mentions} mention{result.total_mentions !== 1 ? "s" : ""} of &ldquo;{brandName}&rdquo;
                <span className="ml-2 text-xs text-muted-foreground">
                  ({formatMs(result.duration_ms)} total)
                </span>
              </p>
              <Button variant="ghost" size="sm" onClick={() => setShowFull((s) => !s)}>
                {showFull ? "Hide" : "Show"} full transcript
              </Button>
            </div>

            {/* Full transcript */}
            {showFull && result.text && (
              <div className="rounded-md bg-muted p-3 text-xs max-h-48 overflow-y-auto whitespace-pre-wrap">
                {result.text}
              </div>
            )}

            {/* Brand mention utterances */}
            {result.total_mentions === 0 ? (
              <p className="text-sm text-muted-foreground">
                No utterances mentioning &ldquo;{brandName}&rdquo; were detected.
              </p>
            ) : (
              <ul className="space-y-3">
                {result.brand_mentions.map((u) => (
                  <UtteranceRow key={u.utterance_uuid} u={u} />
                ))}
              </ul>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
