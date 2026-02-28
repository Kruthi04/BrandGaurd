import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import AppLayout from "@/components/layout/AppLayout";
import ScoutList from "@/components/monitoring/ScoutList";
import AudioSources from "@/components/monitoring/AudioSources";
import StartMonitoringDialog from "@/components/monitoring/StartMonitoringDialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useActiveBrand } from "@/lib/brand";
import type { Scout } from "@/types";

type Tab = "scouts" | "audio";

export default function Monitoring() {
  const brandId = useActiveBrand();
  const [activeTab, setActiveTab]  = useState<Tab>("scouts");
  const [showDialog, setShowDialog] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["monitoringStatus", brandId],
    queryFn: () => api.get<{ scouts: Scout[] }>(`/monitoring/status?brand_name=${encodeURIComponent(brandId)}`),
  });

  const scouts = data?.scouts ?? [];

  function handleScoutCreated() {
    queryClient.invalidateQueries({ queryKey: ["monitoringStatus", brandId] });
  }

  async function handleDelete(id: string) {
    try {
      await api.delete(`/monitoring/scouts/${id}`);
    } catch {
      // best-effort delete
    }
    queryClient.invalidateQueries({ queryKey: ["monitoringStatus", brandId] });
  }

  const activeCount = scouts.filter((s) => s.status === "active").length;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Monitoring</h1>
            <p className="text-muted-foreground">
              Manage Yutori scouts, Tavily web searches, and audio analysis.
            </p>
          </div>
          <Button onClick={() => setShowDialog(true)}>+ Start Monitoring</Button>
        </div>

        {/* Summary badges */}
        <div className="flex gap-3 text-sm">
          <div className="rounded-lg border bg-card px-3 py-2 text-center">
            <div className="text-2xl font-bold text-emerald-400">{activeCount}</div>
            <div className="text-xs text-muted-foreground">Active scouts</div>
          </div>
          <div className="rounded-lg border bg-card px-3 py-2 text-center">
            <div className="text-2xl font-bold">{scouts.length}</div>
            <div className="text-xs text-muted-foreground">Total scouts</div>
          </div>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 border-b">
          {([["scouts", "Scouts"], ["audio", "Audio Sources"]] as [Tab, string][]).map(([id, label]) => (
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
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
            </div>
          ) : scouts.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">No scouts running. Click "Start Monitoring" to create one.</p>
              </CardContent>
            </Card>
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
