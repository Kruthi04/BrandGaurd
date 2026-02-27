import AppLayout from "@/components/layout/AppLayout";
import ScoutList from "@/components/monitoring/ScoutList";

export default function Monitoring() {
  // TODO: Fetch scouts from API, handle create/delete
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Monitoring</h1>
          <p className="text-muted-foreground">
            Manage Yutori scouts and Tavily web searches.
          </p>
        </div>
        <ScoutList scouts={[]} />
      </div>
    </AppLayout>
  );
}
