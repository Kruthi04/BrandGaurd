import AppLayout from "@/components/layout/AppLayout";
import ReputationScore from "@/components/dashboard/ReputationScore";
import MentionsFeed from "@/components/dashboard/MentionsFeed";
import ThreatSummary from "@/components/dashboard/ThreatSummary";

export default function Dashboard() {
  // TODO: Fetch real data from API
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Brand reputation overview at a glance.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <ReputationScore />
          <ThreatSummary threats={[]} />
          <div className="rounded-lg border bg-card p-6">
            <h3 className="text-lg font-semibold">Active Scouts</h3>
            <div className="text-3xl font-bold mt-2">0</div>
            <p className="text-sm text-muted-foreground">Yutori monitors running</p>
          </div>
        </div>

        <MentionsFeed mentions={[]} />
      </div>
    </AppLayout>
  );
}
