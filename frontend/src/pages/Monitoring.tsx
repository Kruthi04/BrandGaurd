import { useState, useEffect } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import ScoutList from "@/components/monitoring/ScoutList";
import AudioSources from "@/components/monitoring/AudioSources";
import StartMonitoringDialog from "@/components/monitoring/StartMonitoringDialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { mockScouts } from "@/lib/mockData";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Scout } from "@/types";

type Tab = "scouts" | "audio";

export default function Monitoring() {
  const [activeTab, setActiveTab]  = useState<Tab>("scouts");
  const [scouts, setScouts]        = useState<Scout[]>([]);
  const [showDialog, setShowDialog] = useState(false);
  const [initialized, setInitialized] = useState(false);

  const { data: fetchedScouts, isLoading } = useQuery({
    queryKey: ["monitoringStatus"],
    queryFn: async () => {
      const res = await api.get<{ scouts: Scout[] } | Scout[]>("/monitoring/status");
      const list = Array.isArray(res) ? res : (res as { scouts: Scout[] }).scouts ?? [];
      return list.map((s: Record<string, unknown>) => ({
        id: (s.id ?? "") as string,
        brand_id: (s.brand_id ?? "") as string,
        query: (s.query ?? "") as string,
        display_name: (s.display_name ?? s.query ?? "") as string,
        status: (s.status ?? "active") as Scout["status"],
        output_interval: (s.output_interval ?? 3600) as number,
        created_at: (s.created_at ?? "") as string,
        next_run: (s.next_run ?? s.next_run_timestamp ?? undefined) as string | undefined,
      }));
    },
    retry: 1,
  });

  useEffect(() => {
    if (fetchedScouts && !initialized) {
      setScouts(fetchedScouts);
      setInitialized(true);
    }
  }, [fetchedScouts, initialized]);

  function handleScoutCreated(scout: { id: string; display_name: string; query: string }) {
    const newScout: Scout = {
      id: scout.id,
      brand_id: "brand-1",
      query: scout.query,
      display_name: scout.display_name,
      status: "active",
      output_interval: 3600,
      created_at: new Date().toISOString(),
    };
    setScouts((prev) => [newScout, ...prev]);
  }

  async function handleDelete(id: string) {
    try {
      await api.delete(`/monitoring/scouts/${id}`);
      setScouts((prev) => prev.filter((s) => s.id !== id));
      toast.success("Scout deleted");
    } catch {
      // Fallback: still remove from UI for demo
      setScouts((prev) => prev.filter((s) => s.id !== id));
      toast.success("Scout deleted (demo mode)");
    }
  }

  const activeCount = scouts.filter((s) => s.status === "active").length;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-bold tracking-tight">Monitoring</h1>
            <p className="text-base text-muted-foreground mt-1">
              Manage Yutori scouts, Tavily web searches, and audio analysis.
            </p>
          </div>
          <Button onClick={() => setShowDialog(true)}>+ Start Monitoring</Button>
        </div>

        {/* Summary badges */}
        <div className="flex gap-3 text-sm">
          <div className="rounded-lg border px-3 py-2 text-center">
            <div className="text-2xl font-bold text-green-600">{activeCount}</div>
            <div className="text-xs text-muted-foreground">Active scouts</div>
          </div>
          <div className="rounded-lg border px-3 py-2 text-center">
            <div className="text-2xl font-bold">{scouts.length}</div>
            <div className="text-xs text-muted-foreground">Total scouts</div>
          </div>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 border-b">
          {([["scouts", "Scouts"], ["audio", "🎙 Audio Sources"]] as [Tab, string][]).map(([id, label]) => (
            <button
              key={id}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === id
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
              onClick={() => setActiveTab(id)}
            >
              {label}
            </button>
          ))}
        </div>

        {activeTab === "scouts" && (
          isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </div>
          ) : (
            <ScoutList
              scouts={scouts}
              onDelete={handleDelete}
            />
          )
        )}
        {activeTab === "audio" && <AudioSources />}
      </div>

      {showDialog && (
        <StartMonitoringDialog
          onClose={() => setShowDialog(false)}
          onCreated={handleScoutCreated}
        />
      )}
    </AppLayout>
  );
}
