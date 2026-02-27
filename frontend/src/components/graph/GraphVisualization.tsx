import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { GraphData } from "@/types";

interface GraphVisualizationProps {
  data?: GraphData;
}

export default function GraphVisualization({ data }: GraphVisualizationProps) {
  // TODO: Integrate a graph visualization library (e.g., react-force-graph, vis-network, or d3)
  return (
    <Card className="h-[600px]">
      <CardHeader>
        <CardTitle className="text-lg">Knowledge Graph</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-center h-full">
        {data ? (
          <p className="text-sm text-muted-foreground">
            Graph with {data.nodes.length} nodes and {data.edges.length} edges.
            Visualization coming soon.
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Select a brand to view its reputation graph.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
