import AppLayout from "@/components/layout/AppLayout";
import GraphVisualization from "@/components/graph/GraphVisualization";

export default function GraphExplorer() {
  // TODO: Fetch graph data from Neo4j API
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Graph Explorer</h1>
          <p className="text-muted-foreground">
            Visualize brand entity relationships from Neo4j.
          </p>
        </div>
        <GraphVisualization />
      </div>
    </AppLayout>
  );
}
