import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import ScoutList from "@/components/monitoring/ScoutList";
import AudioSources from "@/components/monitoring/AudioSources";

type Tab = "scouts" | "audio";

export default function Monitoring() {
  const [activeTab, setActiveTab] = useState<Tab>("scouts");

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Monitoring</h1>
          <p className="text-muted-foreground">
            Manage Yutori scouts, Tavily web searches, and audio source analysis.
          </p>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 border-b">
          <button
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "scouts"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("scouts")}
          >
            Scouts
          </button>
          <button
            className={`flex items-center gap-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "audio"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab("audio")}
          >
            <span>🎙</span> Audio Sources
          </button>
        </div>

        {activeTab === "scouts" && <ScoutList scouts={[]} />}
        {activeTab === "audio" && <AudioSources />}
      </div>
    </AppLayout>
  );
}
