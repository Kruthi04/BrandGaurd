import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import ScoutList from "@/components/monitoring/ScoutList";
import AudioSources from "@/components/monitoring/AudioSources";
import StartMonitoringDialog from "@/components/monitoring/StartMonitoringDialog";
import { Button } from "@/components/ui/button";
import { mockScouts } from "@/lib/mockData";
import type { Scout } from "@/types";

type Tab = "scouts" | "audio";

export default function Monitoring() {
  const [activeTab, setActiveTab]  = useState<Tab>("scouts");
  const [scouts, setScouts]        = useState<Scout[]>(mockScouts as Scout[]);
  const [showDialog, setShowDialog] = useState(false);

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

  function handleDelete(id: string) {
    setScouts((prev) => prev.filter((s) => s.id !== id));
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
          <ScoutList
            scouts={scouts}
            onDelete={handleDelete}
          />
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
