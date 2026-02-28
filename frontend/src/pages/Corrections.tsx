import { useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { mockCorrections, type MockCorrection, type CorrectionStatus } from "@/lib/mockData";
import { api } from "@/lib/api";

const TYPE_LABELS: Record<string, string> = {
  blog:  "Blog Post",
  faq:   "FAQ",
  social:"Social Media",
  press: "Press Release",
};

function relativeTime(iso?: string) {
  if (!iso) return "";
  const h = Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function CorrectionCard({
  correction,
  onPublish,
}: {
  correction: MockCorrection;
  onPublish: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [publishing, setPublishing] = useState(false);

  async function handlePublish() {
    setPublishing(true);
    try {
      await api.post("/graph/corrections", {
        mention_id: correction.id,
        content: correction.correction,
        correction_type: correction.type,
        status: "published",
      });
      onPublish(correction.id);
      toast.success("Correction published!");
    } catch {
      // Fallback: still update UI for demo
      onPublish(correction.id);
      toast.success("Correction published (demo mode)");
    } finally {
      setPublishing(false);
    }
  }

  return (
    <Card>
      <CardContent className="pt-4 space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <Badge variant={correction.status === "published" ? "success" : "secondary"}>
              {correction.status}
            </Badge>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{correction.claim}</p>
              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                <span>{TYPE_LABELS[correction.type] ?? correction.type}</span>
                <span>·</span>
                <span>{correction.platform}</span>
                <span>·</span>
                <span>
                  {correction.status === "published"
                    ? `Published ${relativeTime(correction.published_at)}`
                    : `Created ${relativeTime(correction.created_at)}`}
                </span>
              </div>
            </div>
          </div>
          <button
            className="text-xs text-muted-foreground hover:text-foreground shrink-0"
            onClick={() => setExpanded((e) => !e)}
          >
            {expanded ? "▲" : "▼"}
          </button>
        </div>

        {/* Before / After preview */}
        {expanded && (
          <div className="space-y-3 pt-2 border-t">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">❌ Incorrect claim</p>
                <p className="text-sm bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400 rounded p-2">
                  {correction.claim}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">✅ Correction</p>
                <p className="text-sm bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400 rounded p-2">
                  {correction.correction}
                </p>
              </div>
            </div>
            {correction.status === "draft" && (
              <Button size="sm" onClick={handlePublish} disabled={publishing}>
                {publishing ? "Publishing…" : "Publish Correction"}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Corrections() {
  // No GET /graph/corrections endpoint exists — use mock data as initial state.
  // Corrections are created via POST /graph/corrections when publishing.
  const isLoading = false;

  const [corrections, setCorrections] = useState<MockCorrection[]>(mockCorrections);
  const [filterStatus, setFilterStatus] = useState<CorrectionStatus | "all">("all");

  function handlePublish(id: string) {
    setCorrections((prev) =>
      prev.map((c) =>
        c.id === id ? { ...c, status: "published" as const, published_at: new Date().toISOString() } : c
      )
    );
  }

  const filtered =
    filterStatus === "all" ? corrections : corrections.filter((c) => c.status === filterStatus);

  const publishedCount = corrections.filter((c) => c.status === "published").length;
  const draftCount     = corrections.filter((c) => c.status === "draft").length;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-bold tracking-tight">Corrections</h1>
            <p className="text-base text-muted-foreground mt-1">Review and publish AI-generated brand corrections.</p>
          </div>
          <div className="flex gap-3 text-sm">
            <div className="rounded-lg border px-3 py-2 text-center">
              <div className="text-2xl font-bold text-green-600">{publishedCount}</div>
              <div className="text-xs text-muted-foreground">Published</div>
            </div>
            <div className="rounded-lg border px-3 py-2 text-center">
              <div className="text-2xl font-bold text-yellow-600">{draftCount}</div>
              <div className="text-xs text-muted-foreground">Drafts</div>
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="flex gap-2">
          {(["all", "draft", "published"] as (CorrectionStatus | "all")[]).map((s) => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={`rounded-full border px-3 py-1 text-xs font-medium capitalize transition-colors ${
                filterStatus === s ? "bg-primary text-primary-foreground border-primary" : "hover:bg-muted"
              }`}
            >
              {s === "all" ? "All" : s}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
        ) : filtered.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No corrections match your filter.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filtered.map((c) => (
              <CorrectionCard key={c.id} correction={c} onPublish={handlePublish} />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
