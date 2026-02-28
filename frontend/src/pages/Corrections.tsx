import { useState } from "react";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { useActiveBrand } from "@/lib/brand";
import type { Correction, CorrectionStatus } from "@/types";

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
  correction: Correction;
  onPublish: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [publishing, setPublishing] = useState(false);

  async function handlePublish() {
    setPublishing(true);
    await new Promise((r) => setTimeout(r, 1200));
    onPublish(correction.id);
    toast.success("Correction published!");
    setPublishing(false);
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
                <p className="text-xs font-medium text-muted-foreground mb-1">Incorrect claim</p>
                <p className="text-sm text-red-400 bg-red-500/10 rounded p-2">
                  {correction.claim}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">Correction</p>
                <p className="text-sm text-emerald-400 bg-emerald-500/10 rounded p-2">
                  {correction.correction}
                </p>
              </div>
            </div>
            {correction.status === "draft" && (
              <Button size="sm" onClick={handlePublish} disabled={publishing}>
                {publishing ? "Publishing..." : "Publish Correction"}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Corrections() {
  const brandId = useActiveBrand();
  const [localPublished, setLocalPublished] = useState<Record<string, string>>({});
  const [filterStatus, setFilterStatus] = useState<CorrectionStatus | "all">("all");

  const { data, isLoading } = useQuery({
    queryKey: ["corrections", brandId],
    queryFn: () => api.get<{ corrections: Correction[] }>(`/graph/brand/${brandId}/corrections`),
  });

  const corrections = (data?.corrections ?? []).map((c) =>
    localPublished[c.id]
      ? { ...c, status: "published" as const, published_at: localPublished[c.id] }
      : c
  );

  function handlePublish(id: string) {
    setLocalPublished((prev) => ({ ...prev, [id]: new Date().toISOString() }));
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
            <h1 className="text-3xl font-bold tracking-tight">Corrections</h1>
            <p className="text-muted-foreground">Review and publish AI-generated brand corrections.</p>
          </div>
          <div className="flex gap-3 text-sm">
            <div className="rounded-lg border bg-card px-3 py-2 text-center">
              <div className="text-2xl font-bold text-emerald-400">{publishedCount}</div>
              <div className="text-xs text-muted-foreground">Published</div>
            </div>
            <div className="rounded-lg border bg-card px-3 py-2 text-center">
              <div className="text-2xl font-bold text-yellow-400">{draftCount}</div>
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
                filterStatus === s
                  ? "bg-primary text-primary-foreground border-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
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
          </div>
        ) : filtered.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                {corrections.length === 0 ? "No corrections yet. Corrections will appear here after auto-correcting threats." : "No corrections match your filter."}
              </p>
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
